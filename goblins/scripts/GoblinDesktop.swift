import Cocoa
import Darwin

let spriteSize: CGFloat = 128
let appDir = FileManager.default.homeDirectoryForCurrentUser
    .appendingPathComponent(".codex")
    .appendingPathComponent("goblins")
let spritePath = appDir.appendingPathComponent("goblin_spritesheet.png").path

func color(_ hex: UInt32) -> NSColor {
    let r = CGFloat((hex >> 16) & 0xff) / 255
    let g = CGFloat((hex >> 8) & 0xff) / 255
    let b = CGFloat(hex & 0xff) / 255
    return NSColor(calibratedRed: r, green: g, blue: b, alpha: 1)
}

func oval(_ rect: NSRect, fill: NSColor, stroke: NSColor? = nil, width: CGFloat = 1) {
    let path = NSBezierPath(ovalIn: rect)
    fill.setFill()
    path.fill()
    if let stroke {
        stroke.setStroke()
        path.lineWidth = width
        path.stroke()
    }
}

func polygon(_ points: [NSPoint], fill: NSColor, stroke: NSColor? = nil, width: CGFloat = 1) {
    guard let first = points.first else { return }
    let path = NSBezierPath()
    path.move(to: first)
    for point in points.dropFirst() {
        path.line(to: point)
    }
    path.close()
    fill.setFill()
    path.fill()
    if let stroke {
        stroke.setStroke()
        path.lineWidth = width
        path.stroke()
    }
}

func line(_ from: NSPoint, _ to: NSPoint, color: NSColor, width: CGFloat) {
    let path = NSBezierPath()
    path.move(to: from)
    path.line(to: to)
    path.lineCapStyle = .round
    path.lineWidth = width
    color.setStroke()
    path.stroke()
}

final class GoblinView: NSView {
    var phase: CGFloat = 0
    var facing: CGFloat = 1
    private var frames: [NSImage] = []

    override var isOpaque: Bool { false }
    override var isFlipped: Bool { true }

    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        wantsLayer = true
        layer?.backgroundColor = NSColor.clear.cgColor
        frames = Self.loadFrames()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    static func loadFrames() -> [NSImage] {
        guard let sheet = NSImage(contentsOfFile: spritePath),
              let cg = sheet.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            return []
        }
        let cell = Int(spriteSize)
        guard cg.width >= cell, cg.height >= cell else { return [] }
        let cols = cg.width / cell
        let rows = cg.height / cell
        var result: [NSImage] = []
        for row in 0..<rows {
            for col in 0..<cols {
                let rect = CGRect(x: col * cell, y: row * cell, width: cell, height: cell)
                guard let crop = cg.cropping(to: rect) else { continue }
                result.append(NSImage(cgImage: crop, size: NSSize(width: cell, height: cell)))
            }
        }
        return result
    }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.clear.setFill()
        bounds.fill()

        if !frames.isEmpty {
            let index = Int(phase * 4) % frames.count
            frames[index].draw(in: bounds)
            return
        }

        let bob = sin(phase * 2) * 3
        let walk = sin(phase)
        let outline = color(0x20351f)

        oval(NSRect(x: 28, y: 121, width: 72, height: 10), fill: color(0x1b1f18))
        polygon([NSPoint(x: 39, y: 40), NSPoint(x: 8, y: 28), NSPoint(x: 32, y: 58)], fill: color(0x6fa443), stroke: outline, width: 2)
        polygon([NSPoint(x: 89, y: 40), NSPoint(x: 120, y: 28), NSPoint(x: 96, y: 58)], fill: color(0x6fa443), stroke: outline, width: 2)

        line(NSPoint(x: 53, y: 106 + bob), NSPoint(x: 47 - walk * 7, y: 122), color: color(0x1c2416), width: 11)
        line(NSPoint(x: 53, y: 106 + bob), NSPoint(x: 47 - walk * 7, y: 122), color: color(0x394427), width: 9)
        line(NSPoint(x: 74, y: 106 + bob), NSPoint(x: 81 + walk * 7, y: 122), color: color(0x1c2416), width: 11)
        line(NSPoint(x: 74, y: 106 + bob), NSPoint(x: 81 + walk * 7, y: 122), color: color(0x394427), width: 9)

        oval(NSRect(x: 42, y: 58 + bob, width: 44, height: 50), fill: color(0x66733a), stroke: color(0x1e2617), width: 2)
        polygon([
            NSPoint(x: 39, y: 76 + bob), NSPoint(x: 89, y: 76 + bob),
            NSPoint(x: 80, y: 111 + bob), NSPoint(x: 48, y: 111 + bob)
        ], fill: color(0x5b3f65), stroke: color(0x211629), width: 2)
        line(NSPoint(x: 64, y: 77 + bob), NSPoint(x: 64, y: 107 + bob), color: color(0x2a1d31), width: 2)

        line(NSPoint(x: 45, y: 75 + bob), NSPoint(x: 30, y: 88 + walk * 6), color: color(0x1c2416), width: 10)
        line(NSPoint(x: 45, y: 75 + bob), NSPoint(x: 30, y: 88 + walk * 6), color: color(0x6fa443), width: 8)
        line(NSPoint(x: 83, y: 75 + bob), NSPoint(x: 100, y: 88 - walk * 6), color: color(0x1c2416), width: 10)
        line(NSPoint(x: 83, y: 75 + bob), NSPoint(x: 100, y: 88 - walk * 6), color: color(0x6fa443), width: 8)

        oval(NSRect(x: 31, y: 28 + bob, width: 66, height: 54), fill: color(0x79ad47), stroke: outline, width: 3)
        oval(NSRect(x: 38, y: 48 + bob, width: 12, height: 13), fill: color(0xf0d45b), stroke: color(0x1a1a10), width: 1)
        oval(NSRect(x: 78, y: 48 + bob, width: 12, height: 13), fill: color(0xf0d45b), stroke: color(0x1a1a10), width: 1)
        let pupilShift = 2 * facing
        oval(NSRect(x: 44 + pupilShift, y: 52 + bob, width: 4, height: 6), fill: NSColor.black)
        oval(NSRect(x: 84 + pupilShift, y: 52 + bob, width: 4, height: 6), fill: NSColor.black)
        polygon([NSPoint(x: 62, y: 58 + bob), NSPoint(x: 56, y: 67 + bob), NSPoint(x: 69, y: 67 + bob)], fill: color(0x4f7d31), stroke: outline)

        let mouth = NSBezierPath()
        mouth.move(to: NSPoint(x: 50, y: 67 + bob))
        mouth.curve(to: NSPoint(x: 78, y: 67 + bob), controlPoint1: NSPoint(x: 58, y: 76 + bob), controlPoint2: NSPoint(x: 70, y: 76 + bob))
        color(0x221111).setStroke()
        mouth.lineWidth = 2
        mouth.stroke()
        polygon([NSPoint(x: 55, y: 69 + bob), NSPoint(x: 59, y: 69 + bob), NSPoint(x: 57, y: 75 + bob)], fill: color(0xefe7c2))
        polygon([NSPoint(x: 70, y: 69 + bob), NSPoint(x: 74, y: 69 + bob), NSPoint(x: 72, y: 75 + bob)], fill: color(0xefe7c2))

        for offset in [-12.0, 0.0, 12.0] {
            line(NSPoint(x: 64 + offset, y: 22 + bob), NSPoint(x: 64 + offset / 2, y: 8 + bob + abs(offset) / 5), color: color(0x242018), width: 4)
        }
    }
}

final class GoblinController {
    private let window: NSWindow
    private let view: GoblinView
    private var x: CGFloat
    private var y: CGFloat
    private var vx: CGFloat
    private var vy: CGFloat
    private var phase: CGFloat = 0
    private var nextTurn = Date().addingTimeInterval(Double.random(in: 3...7))
    private let screenFrame: NSRect

    init() {
        screenFrame = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        x = CGFloat.random(in: screenFrame.minX...(screenFrame.maxX - spriteSize))
        y = CGFloat.random(in: (screenFrame.minY + 40)...(screenFrame.maxY - spriteSize))
        vx = Bool.random() ? CGFloat.random(in: 1.2...2.6) : -CGFloat.random(in: 1.2...2.6)
        vy = CGFloat.random(in: -0.5...0.5)

        view = GoblinView(frame: NSRect(x: 0, y: 0, width: spriteSize, height: spriteSize))
        window = NSWindow(
            contentRect: NSRect(x: x, y: y, width: spriteSize, height: spriteSize),
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        window.isOpaque = false
        window.backgroundColor = .clear
        window.hasShadow = false
        window.level = .floating
        window.ignoresMouseEvents = true
        window.collectionBehavior = [.canJoinAllSpaces, .stationary, .fullScreenAuxiliary]
        window.contentView = view
        window.orderFrontRegardless()
    }

    func start() {
        Timer.scheduledTimer(withTimeInterval: 1.0 / 30.0, repeats: true) { [weak self] _ in
            self?.tick()
        }
    }

    private func tick() {
        if Date() > nextTurn {
            nextTurn = Date().addingTimeInterval(Double.random(in: 3...8))
            vx = Bool.random() ? CGFloat.random(in: 1.0...2.8) : -CGFloat.random(in: 1.0...2.8)
            vy = CGFloat.random(in: -0.65...0.65)
        }

        x += vx
        y += vy + sin(phase * 0.7) * 0.18

        if x <= screenFrame.minX || x >= screenFrame.maxX - spriteSize {
            vx *= -1
            x = min(max(x, screenFrame.minX), screenFrame.maxX - spriteSize)
        }
        if y <= screenFrame.minY + 24 || y >= screenFrame.maxY - spriteSize {
            vy *= -1
            y = min(max(y, screenFrame.minY + 24), screenFrame.maxY - spriteSize)
        }

        phase += 0.16
        view.phase = phase
        view.facing = vx >= 0 ? 1 : -1
        view.needsDisplay = true
        window.setFrameOrigin(NSPoint(x: x, y: y))
    }
}

signal(SIGTERM) { _ in
    NSApplication.shared.terminate(nil)
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let controller = GoblinController()
controller.start()
app.run()
