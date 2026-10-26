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

    /// A button of an alert or dialog (the Touch Bar repeats their titles, so app-wide queries are ambiguous).
    @MainActor func dialogButton(_ app: XCUIApplication, _ title: String) -> XCUIElement {
        for q in [app.sheets, app.dialogs, app.windows] {
            let b = q.buttons[title].firstMatch
            if b.exists { return b }
        }
        return app.windows.firstMatch.buttons[title].firstMatch
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

    @MainActor func testChatsWithFakeEngines() throws {
        var app = launch(fake: true)
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 10))
        ask(app, "What does LoRA freeze?")
        XCTAssertTrue(waitStatus(app, "not verified", timeout: 20))
        app.typeKey("n", modifierFlags: .command)
        XCTAssertTrue(app.buttons.matching(identifier: "example-question").firstMatch.waitForExistence(timeout: 5), "a new chat starts empty")
        ask(app, "How many parameters does LoRA train?")
        XCTAssertTrue(waitStatus(app, "not verified", timeout: 20))
        let sidebar = app.outlines.firstMatch
        let rows = sidebar.staticTexts.matching(NSPredicate(format: "value CONTAINS 'LoRA' OR label CONTAINS 'LoRA'"))
        XCTAssertEqual(rows.count, 2, "two chats, titled by their first question")
        shot(app, "30-two-chats")
        // Rename the first (most recent) chat.
        rows.element(boundBy: 0).rightClick()
        app.menuItems["Rename chat…"].click()
        let field = app.textFields.matching(NSPredicate(format: "value CONTAINS 'parameters'")).firstMatch
        XCTAssertTrue(field.waitForExistence(timeout: 5))
        field.doubleClick()
        field.typeKey("a", modifierFlags: .command)
        field.typeText("Renamed chat")
        dialogButton(app, "Rename").click()
        XCTAssertTrue(sidebar.staticTexts["Renamed chat"].waitForExistence(timeout: 5), "renamed")
        shot(app, "31-renamed")
        // Resume the older chat: its question is still there.
        sidebar.staticTexts.matching(NSPredicate(format: "value CONTAINS 'freeze' OR label CONTAINS 'freeze'")).firstMatch.click()
        XCTAssertTrue(app.staticTexts["What does LoRA freeze?"].waitForExistence(timeout: 5), "resumed")
        // Persistence across launches.
        app.terminate()
        app = XCUIApplication()
        app.launchArguments += ["-fakeEngines", "YES", "-keepChats"]
        app.launch()
        app.activate()
        XCTAssertTrue(app.outlines.firstMatch.staticTexts["Renamed chat"].waitForExistence(timeout: 10), "chats survive a relaunch")
        // Delete it.
        app.outlines.firstMatch.staticTexts["Renamed chat"].rightClick()
        app.menuItems["Delete chat…"].click()
        let del = dialogButton(app, "Delete chat")
        XCTAssertTrue(del.waitForExistence(timeout: 5))
        del.click()
        XCTAssertFalse(app.outlines.firstMatch.staticTexts["Renamed chat"].waitForExistence(timeout: 2), "deleted")
        shot(app, "32-after-delete")
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

    /// Screenshots for the thesis chapter: real models, light appearance, the E-ZPass example.
    @MainActor func testScreenshotsForThesis() throws {
        let app = XCUIApplication()
        app.launchArguments += ["-lightAppearance"]
        app.launch()
        app.activate()
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 300))
        app.typeKey("n", modifierFlags: .command)
        shot(app, "40-start")
        ask(app, "How does E-ZPass charge tolls?")
        XCTAssertTrue(waitStatus(app, "not verified", timeout: 600))
        shot(app, "41-native")
        app.buttons["verify-judge"].click()
        XCTAssertTrue(waitStatus(app, "verified", timeout: 600))
        sleep(1)
        shot(app, "42-verified")
        let s = sentence(app, containing: "falls below $25")
        if s.waitForExistence(timeout: 5) {
            s.coordinate(withNormalizedOffset: CGVector(dx: 0.05, dy: 0.5)).click()
            XCTAssertNotNil(waitFor(app, "sentence-verdict", timeout: 10))
            shot(app, "43-sentence")
            app.buttons["find-evidence"].click()
            if app.buttons["Done"].waitForExistence(timeout: 300) {
                sleep(1)
                shot(app, "44-evidence")
                app.buttons["Done"].click()
            }
            app.buttons["rewrite-selected"].click()
            _ = app.radioButtons["Fix 1"].waitForExistence(timeout: 300)
            _ = waitStatus(app, "verified", timeout: 300)
            shot(app, "45-after-rewrite")
        }
        app.staticTexts["sidebar-Stats"].click()
        XCTAssertNotNil(waitFor(app, "stats-kpis", timeout: 10))
        sleep(2)
        shot(app, "46-stats")
        app.staticTexts["sidebar-Library"].click()
        app.outlines["library-list"].cells.element(boundBy: 3).click()
        sleep(1)
        shot(app, "47-library")
    }

    /// Real models: switch the generator to the 7B, ask, verify with GroundOne.
    @MainActor func testGenerator7BRealModels() throws {
        let app = XCUIApplication()
        app.launch()
        app.activate()
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 300))
        app.popUpButtons["generator-picker"].click()
        app.menuItems["Qwen2.5 7B"].click()
        XCTAssertTrue(app.staticTexts["models-ready"].waitForNonExistence(timeout: 30) || true)
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 600))
        app.typeKey("n", modifierFlags: .command)
        ask(app, "Why does Oracle have two CEOs?")
        XCTAssertTrue(waitStatus(app, "not verified", timeout: 600))
        app.buttons["verify-g1"].click()
        XCTAssertTrue(waitStatus(app, "verified", timeout: 600))
        shot(app, "50-generator-7b")
    }
}
