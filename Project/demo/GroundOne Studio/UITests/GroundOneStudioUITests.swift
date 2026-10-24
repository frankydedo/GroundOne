import XCTest

/// UI tests. The first two run with fake engines (seconds, deterministic); the last one loads the real models and
/// answers a question from the research library end to end. Every step saves a screenshot to the result bundle.
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

    @MainActor func testAskFlowWithFakeEngines() throws {
        let app = launch(fake: true)
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 10), "models-ready")
        shot(app, "01-empty")
        ask(app, "What does LoRA freeze?")
        let banner = try XCTUnwrap(waitFor(app, "status-banner", timeout: 20), "the loop must finish with a status")
        XCTAssertTrue(banner.label.contains("Accepted by GroundOne after 1 rewrite"), banner.label)
        XCTAssertTrue(app.radioButtons["First draft"].exists, "two drafts → draft picker")
        shot(app, "02-answer-accepted-after-rewrite")
        // First draft: the flagged sentence and the judge's verdicts.
        app.radioButtons["First draft"].click()
        XCTAssertTrue(showsText(app, "twelve benchmarks"), "the first draft holds the flagged sentence")
        shot(app, "03-first-draft-flagged")
        // Inspector tabs.
        app.radioButtons["Judge"].click()
        XCTAssertNotNil(waitFor(app, "judge-stats", timeout: 5), "judge-stats")
        shot(app, "04-inspector-judge")
        app.radioButtons["Passages"].click()
        shot(app, "05-inspector-passages")
        app.radioButtons["Timing"].click()
        XCTAssertNotNil(waitFor(app, "timing-stats", timeout: 5), "timing-stats")
        shot(app, "06-inspector-timing")
        // Source links (M3b) and the source viewer.
        let find = app.buttons.matching(NSPredicate(format: "label CONTAINS 'Find evidence'")).firstMatch
        XCTAssertTrue(find.waitForExistence(timeout: 10), "evidence button")
        find.click()
        let linkLabel = NSPredicate(format: "label CONTAINS 'Supported by' OR label CONTAINS 'Contradicted by'")
        let link = app.links.matching(linkLabel).firstMatch.waitForExistence(timeout: 2)
            ? app.links.matching(linkLabel).firstMatch : app.buttons.matching(linkLabel).firstMatch
        XCTAssertTrue(link.waitForExistence(timeout: 10))
        link.click()
        sleep(1)
        shot(app, "07-source-viewer")
        XCTAssertTrue(app.buttons["Done"].waitForExistence(timeout: 5) || app.sheets.firstMatch.exists, "source viewer sheet")
        app.buttons["Done"].click()
    }

    @MainActor func testSectionsWithFakeEngines() throws {
        let app = launch(fake: true)
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 10), "models-ready")
        ask(app, "What does LoRA freeze?")
        XCTAssertNotNil(waitFor(app, "status-banner", timeout: 20), "status-banner")
        app.staticTexts["sidebar-Library"].click()
        XCTAssertNotNil(waitFor(app, "library-summary", timeout: 5), "library-summary")
        shot(app, "10-library")
        app.staticTexts["sidebar-Policies"].click()
        XCTAssertTrue(app.staticTexts["strict"].waitForExistence(timeout: 5))
        app.staticTexts["lenient"].click()
        shot(app, "11-policies")
        app.staticTexts["sidebar-Measurements"].click()
        XCTAssertNotNil(waitFor(app, "export-button", timeout: 5), "export-button")
        shot(app, "12-measurements")
        app.staticTexts["sidebar-Audit log"].click()
        XCTAssertNotNil(waitFor(app, "audit-list", timeout: 5), "audit-list")
        shot(app, "13-audit")
    }

    /// Real models, real library: loads GroundOne 3B, the 4-bit generator and the embedding model.
    @MainActor func testEndToEndRealModels() throws {
        let app = launch(fake: false)
        XCTAssertNotNil(waitFor(app, "models-ready", timeout: 300), "models must load")
        shot(app, "20-real-ready")
        ask(app, "Which post-processing method calibrates modern neural networks, and how does it work?")
        _ = try XCTUnwrap(waitFor(app, "status-banner", timeout: 600), "the loop must finish")
        shot(app, "21-real-answer")
        app.radioButtons["Judge"].click()
        XCTAssertNotNil(waitFor(app, "judge-stats", timeout: 10), "judge-stats")
        shot(app, "22-real-judge")
        app.radioButtons["Timing"].click()
        shot(app, "23-real-timing")
        let find = app.buttons.matching(NSPredicate(format: "label CONTAINS 'Find evidence'")).firstMatch
        XCTAssertTrue(find.waitForExistence(timeout: 10), "evidence button")
        find.click()
        let linkLabel = NSPredicate(format: "label CONTAINS 'Supported by' OR label CONTAINS 'Contradicted by'")
        let link = app.links.matching(linkLabel).firstMatch.waitForExistence(timeout: 2)
            ? app.links.matching(linkLabel).firstMatch : app.buttons.matching(linkLabel).firstMatch
        if link.waitForExistence(timeout: 300) {
            link.click()
            XCTAssertTrue(app.buttons["Done"].waitForExistence(timeout: 10))
            sleep(2)
            shot(app, "24-real-source-pdf")
            app.buttons["Done"].click()
        } else {
            shot(app, "24-real-no-source-link")
        }
    }
}
