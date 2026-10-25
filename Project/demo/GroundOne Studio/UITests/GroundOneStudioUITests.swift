import XCTest

/// UI tests. The first two run with fake engines (seconds, deterministic); the last one loads the real models and
/// answers an example question end to end. Every step saves a screenshot to the result bundle.
final class GroundOneStudioUITests: XCTestCase {
    override func setUp() { continueAfterFailure = false }

    @MainActor func shot(_ app: XCUIApplication, _ name: String) {
        let a = XCTAttachment(screenshot: app.windows.firstMatch.screenshot())
        a.name = name
        a.lifetime = .keepAlways
        add(a)
    }

    /// Typed queries only: `descendants(matching: .any)` snapshots the whole tree and can stall for minutes.
    @MainActor func element(_ app: XCUIApplication, _ id: String) -> XCUIElement {
        for q in [app.staticTexts, app.buttons, app.textFields, app.groups, app.radioGroups, app.outlines, app.tables,
                  app.scrollViews, app.otherElements, app.cells] where q[id].exists {
            return q[id].firstMatch
        }
        return app.staticTexts[id].firstMatch
    }

    /// Some element (static text, combined row, text view) whose label or value contains `text`.
    @MainActor func showsText(_ app: XCUIApplication, _ text: String, timeout: TimeInterval = 5) -> Bool {
        let p = NSPredicate(format: "label CONTAINS %@ OR value CONTAINS %@", text, text)
        let end = Date().addingTimeInterval(timeout)
        while Date() < end {
            for q in [app.staticTexts, app.textViews, app.groups, app.otherElements, app.cells]
            where q.matching(p).firstMatch.exists { return true }
            Thread.sleep(forTimeInterval: 0.5)
        }
        return false
    }

    @MainActor func waitFor(_ app: XCUIApplication, _ id: String, timeout: TimeInterval) -> XCUIElement? {
        let end = Date().addingTimeInterval(timeout)
        while Date() < end {
            let e = element(app, id)
            if e.exists { return e }
            Thread.sleep(forTimeInterval: 0.5)
        }
        return nil
    }

    @MainActor func launch(fake: Bool) -> XCUIApplication {
        let app = XCUIApplication()
        if fake { app.launchArguments += ["-fakeEngines", "YES"] }
        app.launch()
        app.activate()
        return app
    }

    @MainActor func ask(_ app: XCUIApplication, _ question: String) {
        let field = app.textFields["question-field"]
        XCTAssertTrue(field.waitForExistence(timeout: 10))
        field.click()
        field.typeText(question)
        field.typeKey(.return, modifierFlags: .command)
    }

    /// Waits until the status line under the answer reads `label` ("not verified" / "verified").
    @MainActor func waitStatus(_ app: XCUIApplication, _ label: String, timeout: TimeInterval) -> Bool {
        let end = Date().addingTimeInterval(timeout)
        while Date() < end {
            let e = element(app, "status-line")
            if e.exists, e.label == label { return true }
            Thread.sleep(forTimeInterval: 0.5)
        }
        return false
    }

    /// The sentence links of the answer text whose label contains `text` (any, if nil).
    @MainActor func sentence(_ app: XCUIApplication, containing text: String? = nil) -> XCUIElement {
        let q = text.map { app.links.matching(NSPredicate(format: "label CONTAINS %@", $0)) } ?? app.links
        return q.firstMatch
    }

    @MainActor func testAskFlowWithFakeEngines() throws {
        let app = launch(fake: true)
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 10), "models-ready")
        shot(app, "01-start")
        ask(app, "What does LoRA freeze?")
        XCTAssertTrue(waitStatus(app, "not verified", timeout: 20), "the native answer appears first, unverified")
        shot(app, "02-native-answer")
        app.buttons["verify-judge"].click()
        XCTAssertTrue(waitStatus(app, "verified", timeout: 20), "verified")
        XCTAssertNotNil(waitFor(app, "judge-agreement", timeout: 5), "judge comparison")
        shot(app, "03-verified-with-judge")
        let flagged = sentence(app, containing: "twelve benchmarks")
        XCTAssertTrue(flagged.waitForExistence(timeout: 5), "sentence link")
        flagged.coordinate(withNormalizedOffset: CGVector(dx: 0.05, dy: 0.5)).click()
        XCTAssertNotNil(waitFor(app, "sentence-verdict", timeout: 5), "sentence panel")
        shot(app, "04-sentence-selected")
        app.buttons["find-evidence"].click()
        XCTAssertTrue(app.buttons["Done"].waitForExistence(timeout: 10), "evidence preview")
        shot(app, "05-evidence-preview")
        app.buttons["Done"].click()
        app.buttons["rewrite-selected"].click()
        XCTAssertTrue(app.radioButtons["Fix 1"].waitForExistence(timeout: 20), "a new version after the rewrite")
        XCTAssertTrue(waitStatus(app, "verified", timeout: 10), "the rewrite is verified again")
        shot(app, "06-after-rewrite")
    }

    @MainActor func testSectionsWithFakeEngines() throws {
        let app = launch(fake: true)
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 10), "models-ready")
        ask(app, "What does LoRA freeze?")
        XCTAssertTrue(waitStatus(app, "not verified", timeout: 20))
        app.buttons["verify-judge"].click()
        XCTAssertTrue(waitStatus(app, "verified", timeout: 20))
        app.staticTexts["sidebar-Library"].click()
        XCTAssertNotNil(waitFor(app, "library-summary", timeout: 5), "library-summary")
        app.outlines["library-list"].cells.firstMatch.click()
        shot(app, "10-library-preview")
        app.staticTexts["sidebar-Policies"].click()
        XCTAssertTrue(app.staticTexts["strict"].waitForExistence(timeout: 5))
        shot(app, "11-policies")
        app.staticTexts["sidebar-Stats"].click()
        XCTAssertNotNil(waitFor(app, "stats-kpis", timeout: 5), "stats-kpis")
        shot(app, "12-stats")
        app.staticTexts["sidebar-Audit log"].click()
        XCTAssertNotNil(waitFor(app, "audit-list", timeout: 5), "audit-list")
        shot(app, "13-audit")
    }

    /// Real models and the T1 library: an example question, verification with the judge, a sentence, its evidence,
    /// Fix, Stats.
    @MainActor func testEndToEndRealModels() throws {
        let app = launch(fake: false)
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 300), "models must load")
        shot(app, "20-real-start")
        let example = app.buttons.matching(NSPredicate(format: "label CONTAINS 'clove tea'")).firstMatch
        XCTAssertTrue(example.waitForExistence(timeout: 10))
        example.click()
        XCTAssertTrue(waitStatus(app, "not verified", timeout: 600), "native answer")
        shot(app, "21-real-native")
        app.buttons["verify-judge"].click()
        XCTAssertTrue(waitStatus(app, "verified", timeout: 600), "verified")
        shot(app, "22-real-verified")
        let s = sentence(app)
        XCTAssertTrue(s.waitForExistence(timeout: 10))
        app.links.element(boundBy: min(1, app.links.count - 1)).coordinate(withNormalizedOffset: CGVector(dx: 0.05, dy: 0.5)).click()
        XCTAssertNotNil(waitFor(app, "sentence-verdict", timeout: 10), "sentence panel")
        shot(app, "23-real-sentence")
        app.buttons["find-evidence"].click()
        if app.buttons["Done"].waitForExistence(timeout: 300) {
            sleep(1)
            shot(app, "24-real-evidence")
            app.buttons["Done"].click()
        }
        (app.links["Deselect"].exists ? app.links["Deselect"] : app.buttons["Deselect"]).click()
        let fix = app.buttons["fix-flagged"]
        if fix.waitForExistence(timeout: 5), fix.isEnabled {
            fix.click()
            XCTAssertTrue(app.radioButtons["Fix 1"].waitForExistence(timeout: 600), "fixed version")
            XCTAssertTrue(waitStatus(app, "verified", timeout: 600))
            shot(app, "25-real-fixed")
        }
        app.staticTexts["sidebar-Stats"].click()
        XCTAssertNotNil(waitFor(app, "stats-kpis", timeout: 10))
        sleep(1)
        shot(app, "26-real-stats")
    }
}
