import AppKit
import Foundation

final class AppDelegate: NSObject, NSApplicationDelegate {
    var item: NSStatusItem!
    var timer: Timer?
    var snapshot: Snapshot?
    let path: URL
    let demo: Bool
    override init() {
        let args = CommandLine.arguments
        if let index = args.firstIndex(of: "--snapshot"), index + 1 < args.count {
            path = URL(fileURLWithPath: args[index + 1])
        } else {
            path = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Library/Application Support/ClaudeLimitBar/status.json")
        }
        demo = args.contains("--demo-label")
        super.init()
    }
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        update()
        timer = Timer.scheduledTimer(withTimeInterval: 10, repeats: true) { [weak self] _ in self?.update() }
    }
    func line(_ text: String, into menu: NSMenu) {
        let entry = NSMenuItem(title: text, action: nil, keyEquivalent: "")
        entry.isEnabled = false
        menu.addItem(entry)
    }
    func update() {
        let now = Date().timeIntervalSince1970
        snapshot = (try? Data(contentsOf: path)).flatMap { try? JSONDecoder().decode(Snapshot.self, from: $0) }
        if snapshot?.schema_version != 1 { snapshot = nil }
        let label = snapshot?.label(at: now) ?? "CL —"
        item.button?.title = (demo ? "DEMO " : "") + label
        item.button?.toolTip = "Claude Limit Bar · vyšší využití z dostupných oken"
        let menu = NSMenu()
        line(demo ? "Fiktivní ukázka · Claude Limit Bar" : "Claude Limit Bar", into: menu)
        menu.addItem(.separator())
        let format = DateFormatter()
        format.dateStyle = .short
        format.timeStyle = .short
        for (key, title) in [("five_hour", "5 hodin"), ("seven_day", "7 dní")] {
            if let window = snapshot?.windows[key], window.valid(at: now) {
                line("\(title): \(Int(window.used_percentage.rounded())) % využito", into: menu)
                line("Obnovení: \(format.string(from: Date(timeIntervalSince1970: window.resets_at)))", into: menu)
            } else {
                line("\(title): čeká na dostupný údaj", into: menu)
            }
        }
        menu.addItem(.separator())
        if let value = snapshot {
            line("Poslední vstup: \(format.string(from: Date(timeIntervalSince1970: value.observed_at)))", into: menu)
            if value.stale(at: now) { line("~ Starší vstup. Vyčkejte na data z Claude Code.", into: menu) }
        } else {
            line("Zatím bez dat. Viz instalace v README.", into: menu)
        }
        line("Údaje se mění při vstupu ze stavového řádku.", into: menu)
        menu.addItem(.separator())
        let refresh = NSMenuItem(title: "Načíst lokální soubor", action: #selector(refreshData), keyEquivalent: "r")
        refresh.target = self
        menu.addItem(refresh)
        let quit = NSMenuItem(title: "Ukončit", action: #selector(terminate), keyEquivalent: "q")
        quit.target = self
        menu.addItem(quit)
        item.menu = menu
    }
    @objc func refreshData() { update() }
    @objc func terminate() { NSApp.terminate(nil) }
}

let application = NSApplication.shared
let delegate = AppDelegate()
application.delegate = delegate
application.run()
