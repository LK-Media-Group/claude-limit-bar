import Foundation

func check(_ condition: @autoclosure () -> Bool, _ message: String) {
    if !condition() { fatalError(message) }
}
let now = 1_800_000_000.0
let fresh = Snapshot(schema_version: 1, observed_at: now, windows: [
    "five_hour": LimitWindow(used_percentage: 23, resets_at: now + 7200),
    "seven_day": LimitWindow(used_percentage: 61, resets_at: now + 172800)])
check(fresh.label(at: now) == "CL 61%", "Highest window")
check(fresh.label(at: now + 601) == "CL ~61%", "Stale marker")
check(fresh.label(at: now + 172801) == "CL —", "Expired windows must not become zero")
check(Snapshot(schema_version: 1, observed_at: now, windows: [:]).label(at: now) == "CL —", "Missing windows")
check(!LimitWindow(used_percentage: 101, resets_at: now + 1).valid(at: now), "Invalid percentage")
check(!LimitWindow(used_percentage: 10, resets_at: now).valid(at: now), "Reset boundary")
check(Snapshot(schema_version: 2, observed_at: now, windows: fresh.windows).active(at: now).isEmpty, "Unsupported schema")
print("7 Swift checks passed")
