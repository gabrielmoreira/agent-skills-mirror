import AppKit
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8)); exit(1)
}
guard CommandLine.arguments.count == 2 else { fail("需要 render-spec.json") }
let data = try Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))
let spec = try JSONSerialization.jsonObject(with: data) as! [String: Any]
let width = spec["width"] as! Int, height = spec["height"] as! Int
let style = spec["style"] as! [String: Any]
func value(_ key: String) -> CGFloat { CGFloat((style[key] as! NSNumber).doubleValue) * CGFloat(width) }
func color(_ key: String) -> NSColor {
    let hex = String((style[key] as! String).dropFirst())
    let n = UInt32(hex, radix: 16)!
    return NSColor(srgbRed: CGFloat((n >> 16) & 255)/255, green: CGFloat((n >> 8) & 255)/255, blue: CGFloat(n & 255)/255, alpha: 1)
}
for row in spec["rows"] as! [[String: Any]] {
    let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: height, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    let context = NSGraphicsContext(bitmapImageRep: bitmap)!
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = context
    color("background").setFill(); NSRect(x: 0, y: 0, width: width, height: height).fill()
    var previousBottom: CGFloat = 0
    for (field, fontKey, sizeKey, topKey) in [("title", "font_title", "title_ratio", "title_top_ratio"), ("question", "font_question", "question_ratio", "question_top_ratio")] {
        if (row[field] as? String ?? "").isEmpty { continue }
        guard let font = NSFont(name: style[fontKey] as! String, size: value(sizeKey)) else { fail("找不到字体：\(style[fontKey]!)") }
        let str = NSAttributedString(string: row[field] as! String, attributes: [.font: font, .foregroundColor: color("foreground")])
        let size = str.size(), top = value(topKey), margin = value("margin_ratio")
        if size.width > CGFloat(width) - margin * 2 { fail("标题超宽，请精简或调整布局：\(row[field]!)") }
        if top < previousBottom || top + size.height > CGFloat(height) - value("track_bottom_ratio") - value("track_height_ratio") - 8 { fail("文字碰撞或导航高度不足") }
        str.draw(at: NSPoint(x: margin, y: CGFloat(height) - top - size.height))
        previousBottom = top + size.height
    }
    context.flushGraphics(); NSGraphicsContext.restoreGraphicsState()
    try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: row["png"] as! String), options: .withoutOverwriting)
}
