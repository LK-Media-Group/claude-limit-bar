import Foundation

struct LimitWindow: Decodable {
    let used_percentage: Double
    let resets_at: Double
    func valid(at now: TimeInterval) -> Bool {
        used_percentage.isFinite && (0...100).contains(used_percentage) && resets_at.isFinite && resets_at > now
    }
}
struct Snapshot: Decodable {
    let schema_version: Int
    let observed_at: Double
    let windows: [String: LimitWindow]
    func stale(at now: TimeInterval) -> Bool { now - observed_at > 600 || observed_at > now + 60 }
    func active(at now: TimeInterval) -> [LimitWindow] {
        guard schema_version == 1, observed_at.isFinite else { return [] }
        return [windows["five_hour"], windows["seven_day"]].compactMap { $0 }.filter { $0.valid(at: now) }
    }
    func label(at now: TimeInterval) -> String {
        guard let highest = active(at: now).map(\.used_percentage).max() else { return "CL —" }
        return "CL \(stale(at: now) ? "~" : "")\(Int(highest.rounded()))%"
    }
}
