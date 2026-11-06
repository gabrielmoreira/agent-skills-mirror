// Person matte for the camera frames, with Apple Vision (no model download, runs on the Neural Engine).
//   swiftc -O matte.swift -o matte      (short.mjs compiles and caches it)
//   matte <camDir> <outDir> <jobFile>   job lines: "<frame> <rawMaskPath> <write 0|1>", consecutive frames
// Two stages per frame:
//   1. raw mask: Vision person segmentation (~34 ms, the bottleneck), resized to the cam frame on the CPU (vImage;
//      Core Image cost more than Vision itself). Cached as a gray PNG at rawMaskPath, keyed by the cam JPG content,
//      so a new `cut` only runs Vision on frames it has never seen.
//   2. output (~5 ms): temporal EMA (40% previous, so hair and shoulder edges do not flicker), 5x5 gaussian (sigma
//      ~1.2, a soft clean edge), written as <outDir>/%05d.png gray+alpha (alpha = person). The runtime composites it
//      over the cam JPG. Lines with write 0 only prime the EMA, so parallel slices join without a seam.
// MATTE_QUALITY=balanced is ~2x faster on Vision, coarser edges.
import Foundation
import Vision
import Accelerate
import ImageIO
import UniformTypeIdentifiers

let a = CommandLine.arguments
guard a.count == 4, let job = try? String(contentsOfFile: a[3], encoding: .utf8) else {
  print("usage: matte <camDir> <outDir> <jobFile>"); exit(1)
}
let camDir = URL(fileURLWithPath: a[1]), outDir = URL(fileURLWithPath: a[2])
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)
let req = VNGeneratePersonSegmentationRequest()
req.qualityLevel = ProcessInfo.processInfo.environment["MATTE_QUALITY"] == "balanced" ? .balanced : .accurate
req.outputPixelFormat = kCVPixelFormatType_OneComponent8
let gray = CGColorSpaceCreateDeviceGray()
let g: [Float] = [0.0398, 0.2420, 0.4364, 0.2420, 0.0398]
let kernel: [Int16] = g.flatMap { y in g.map { x in Int16((x * y * 4096).rounded()) } }
let kDiv = Int32(kernel.reduce(0) { $0 + Int32($1) })

func writePNG(_ bytes: [UInt8], _ w: Int, _ h: Int, alpha: Bool, to url: URL) {
  let bpp = alpha ? 2 : 1
  let img = CGImage(width: w, height: h, bitsPerComponent: 8, bitsPerPixel: 8 * bpp, bytesPerRow: w * bpp, space: gray,
                    bitmapInfo: CGBitmapInfo(rawValue: (alpha ? CGImageAlphaInfo.last : .none).rawValue),
                    provider: CGDataProvider(data: CFDataCreate(nil, bytes, bytes.count))!, decode: nil, shouldInterpolate: false, intent: .defaultIntent)!
  let tmp = url.appendingPathExtension("tmp")
  guard let dest = CGImageDestinationCreateWithURL(tmp as CFURL, UTType.png.identifier as CFString, 1, nil) else { print("cannot write \(url.path)"); exit(1) }
  CGImageDestinationAddImage(dest, img, nil); CGImageDestinationFinalize(dest)
  _ = try? FileManager.default.removeItem(at: url); try! FileManager.default.moveItem(at: tmp, to: url)
}

// raw mask (W*H bytes) for one cam frame: from the cache, or Vision + resize, then cached
func rawMask(_ cam: URL, _ cache: URL, _ W: inout Int, _ H: inout Int) -> [UInt8]? {
  if let s = CGImageSourceCreateWithURL(cache as CFURL, nil), let im = CGImageSourceCreateImageAtIndex(s, 0, nil) {
    W = im.width; H = im.height
    var out = [UInt8](repeating: 0, count: W * H)
    let c = CGContext(data: &out, width: W, height: H, bitsPerComponent: 8, bytesPerRow: W, space: gray, bitmapInfo: CGImageAlphaInfo.none.rawValue)!
    c.draw(im, in: CGRect(x: 0, y: 0, width: W, height: H)); return out
  }
  guard let s = CGImageSourceCreateWithURL(cam as CFURL, nil), let img = CGImageSourceCreateImageAtIndex(s, 0, nil) else { return nil }
  W = img.width; H = img.height
  guard (try? VNImageRequestHandler(cgImage: img, options: [:]).perform([req])) != nil, let buf = req.results?.first?.pixelBuffer else { return nil }
  var out = [UInt8](repeating: 0, count: W * H)
  CVPixelBufferLockBaseAddress(buf, .readOnly)
  var src = vImage_Buffer(data: CVPixelBufferGetBaseAddress(buf), height: vImagePixelCount(CVPixelBufferGetHeight(buf)),
                          width: vImagePixelCount(CVPixelBufferGetWidth(buf)), rowBytes: CVPixelBufferGetBytesPerRow(buf))
  out.withUnsafeMutableBytes { p in
    var dst = vImage_Buffer(data: p.baseAddress, height: vImagePixelCount(H), width: vImagePixelCount(W), rowBytes: W)
    _ = vImageScale_Planar8(&src, &dst, nil, vImage_Flags(kvImageHighQualityResampling))
  }
  CVPixelBufferUnlockBaseAddress(buf, .readOnly)
  writePNG(out, W, H, alpha: false, to: cache)
  return out
}

var W = 0, H = 0, prevFrame = -2, written = 0
var ema: [Float] = [], cur: [Float] = [], u8: [UInt8] = [], soft: [UInt8] = [], ga: [UInt8] = []
for line in job.split(separator: "\n") {
  let f = line.split(separator: " ", maxSplits: 2)
  guard f.count == 3, let i = Int(f[0]) else { continue }
  let name = String(format: "%05d", i)
  guard let raw = rawMask(camDir.appendingPathComponent(name + ".jpg"), URL(fileURLWithPath: String(f[1])), &W, &H) else { print("no mask \(name)"); exit(1) }
  if ema.count != W * H { ema = [Float](repeating: 0, count: W * H); cur = ema; u8 = [UInt8](repeating: 0, count: W * H); soft = u8; ga = [UInt8](repeating: 0, count: 2 * W * H) }
  vDSP_vfltu8(raw, 1, &cur, 1, vDSP_Length(W * H))
  if i != prevFrame + 1 { ema = cur } else { var k: Float = 0.6; vDSP_vintb(ema, 1, cur, 1, &k, &ema, 1, vDSP_Length(W * H)) }
  prevFrame = i
  if f[2] != "1" { continue }
  vDSP_vfixu8(ema, 1, &u8, 1, vDSP_Length(W * H))
  u8.withUnsafeMutableBytes { ps in soft.withUnsafeMutableBytes { pd in
    var s = vImage_Buffer(data: ps.baseAddress, height: vImagePixelCount(H), width: vImagePixelCount(W), rowBytes: W)
    var d = vImage_Buffer(data: pd.baseAddress, height: vImagePixelCount(H), width: vImagePixelCount(W), rowBytes: W)
    _ = vImageConvolve_Planar8(&s, &d, nil, 0, 0, kernel, 5, 5, kDiv, 0, vImage_Flags(kvImageEdgeExtend))
  } }
  for j in 0..<(W * H) { ga[2 * j + 1] = soft[j] }   // gray 0, alpha = mask
  writePNG(ga, W, H, alpha: true, to: outDir.appendingPathComponent(name + ".png"))
  written += 1
  if written % 10 == 0 { print("matte \(written)"); fflush(stdout) }
}
print("matte done")
