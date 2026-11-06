// Face track for the camera frames (Apple Vision), used by over-camera props (e.g. a hat on the head).
//   swift faces.swift <camDir> <out.json>
// Reads <camDir>/%05d.jpg in order, writes [[cx, cy, w, h, roll], ...] per frame in cam-frame px (y down),
// gaps filled from the nearest detection, then smoothed with a centred moving average (no jitter).
import Foundation
import Vision
import CoreImage

let a = CommandLine.arguments
guard a.count == 3 else { print("usage: swift faces.swift <camDir> <out.json>"); exit(1) }
let dir = URL(fileURLWithPath: a[1])
let files = (try FileManager.default.contentsOfDirectory(atPath: dir.path)).filter { $0.hasSuffix(".jpg") }.sorted()
var raw: [[Double]?] = []
for (i, f) in files.enumerated() {
  guard let img = CIImage(contentsOf: dir.appendingPathComponent(f)) else { raw.append(nil); continue }
  let W = Double(img.extent.width), H = Double(img.extent.height)
  let req = VNDetectFaceRectanglesRequest()
  try VNImageRequestHandler(ciImage: img, options: [:]).perform([req])
  let best = (req.results ?? []).max { $0.boundingBox.width < $1.boundingBox.width }
  if let b = best?.boundingBox {
    raw.append([Double(b.midX) * W, (1 - Double(b.midY)) * H, Double(b.width) * W, Double(b.height) * H, -(best?.roll?.doubleValue ?? 0)])
  } else { raw.append(nil) }
  if i % 200 == 0 { print("faces \(i + 1)/\(files.count)") }
}
// fill gaps
var filled = raw
var last: [Double]? = raw.first { $0 != nil } ?? nil
for i in 0..<filled.count { if let v = filled[i] { last = v } else { filled[i] = last } }
// centred moving average, radius 3 frames
let r = 3
var out: [[Double]] = []
for i in 0..<filled.count {
  var acc = [0.0, 0, 0, 0, 0], n = 0.0
  for j in max(0, i - r)...min(filled.count - 1, i + r) { if let v = filled[j] { for k in 0..<5 { acc[k] += v[k] }; n += 1 } }
  out.append(n > 0 ? acc.map { ($0 / n * 10).rounded() / 10 } : [0, 0, 0, 0, 0])
}
let data = try JSONSerialization.data(withJSONObject: out)
try data.write(to: URL(fileURLWithPath: a[2]))
print("faces done: \(out.count) frames, \(raw.filter { $0 != nil }.count) detected")
