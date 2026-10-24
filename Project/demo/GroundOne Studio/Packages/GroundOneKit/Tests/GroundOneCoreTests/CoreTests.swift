import XCTest
@testable import GroundOneCore

struct CharEncoder: TokenEncoder {
    func encode(_ text: String) -> [Int] { text.unicodeScalars.map { Int($0.value) } }
}

final class CoreTests: XCTestCase {
    func testSegmenterListsAndCheckable() {
        let s = Segmenter.segment("Sure! Here are the facts:\n1. The café opened in 2004. It costs $4.50 per cup.\n- Thanks")
        XCTAssertEqual(s.map(\.text), ["Sure!", "Here are the facts:", "The café opened in 2004.", "It costs $4.50 per cup.", "Thanks"])
        XCTAssertEqual(s.map(\.checkable), [false, false, true, true, false])
        let text = "Sure! Here are the facts:\n1. The café opened in 2004. It costs $4.50 per cup.\n- Thanks" as NSString
        for seg in s { XCTAssertEqual(text.substring(with: NSRange(location: seg.start, length: seg.end - seg.start)), seg.text) }
    }

    func testMarkedPromptPositions() {
        let enc = CharEncoder()
        let (ids, pos) = MarkedPrompt.encode(enc, document: "D", sentences: ["a b", "ok", "c d"], scored: [true, false, true])
        XCTAssertEqual(pos.count, 2)
        for p in pos { XCTAssertEqual(ids[p], Int(UnicodeScalar(":").value)) }
        let s = String(String.UnicodeScalarView(ids.map { UnicodeScalar($0)! }))
        XCTAssertTrue(s.hasSuffix("[1] a b Verdict:\n[2] ok\n[3] c d Verdict:\n"))
    }

    func testCalibrationAndDecision() {
        let c = Calibration(temperature: 1.035, bias: [0, -2.19, -2.06], threshold: 0.925)
        let p = c.probs([3, 0, 0])
        XCTAssertEqual(p.reduce(0, +), 1, accuracy: 1e-9)
        XCTAssertEqual(Decision.decide(p, threshold: 0.925), p[0] >= 0.925 ? .supported : (p[1] >= p[2] ? .contradicted : .notMentioned))
        XCTAssertEqual(Decision.decide([0.5, 0.3, 0.2], threshold: 0.9), .contradicted)
        XCTAssertEqual(Decision.decide([0.95, 0.03, 0.02], threshold: 0.9), .supported)
    }

    func testJudgeParse() {
        let p = JudgePrompt.parse("1: A\n[2]: B\n3. C because\n3: A\nnoise", check: [0, 1, 2, 3])
        XCTAssertEqual(p[0]!, .supported); XCTAssertEqual(p[1]!, .contradicted); XCTAssertEqual(p[2]!, .notMentioned)
        XCTAssertNil(p[3]!)
    }

    func testRevisionApplyKeepsOthers() {
        let answer = "Paris is in France. It has 90 million people. The Seine flows through it."
        let segs = Segmenter.segment(answer)
        let v = segs.enumerated().map { SentenceVerdict(index: $0.offset, text: $0.element.text, start: $0.element.start, end: $0.element.end, scored: true) }
        let out = Revision.apply("[2] It has about 2 million people.\n[3] ignored", to: answer, sentences: v, flagged: [1])
        XCTAssertEqual(out, "Paris is in France. It has about 2 million people. The Seine flows through it.")
        let del = Revision.apply("[2] DELETE", to: answer, sentences: v, flagged: [1])
        XCTAssertEqual(del, "Paris is in France. The Seine flows through it.")
    }

    func testPolicyJSON() throws {
        let json = #"{"name":"strict-legal","verifier":"g1-3b-b1","threshold":"calibrated","blocking":["contradicted","not_mentioned"],"max_attempts":2,"on_failure":"abstain","show_probabilities":true,"audit_log":true}"#
        let p = try JSONDecoder().decode(Policy.self, from: Data(json.utf8))
        XCTAssertEqual(p.tau(calibrated: 0.925), 0.925)
        XCTAssertTrue(p.isBlocking(.notMentioned))
        let q = try JSONDecoder().decode(Policy.self, from: Data(json.replacingOccurrences(of: "\"calibrated\"", with: "0.8").utf8))
        XCTAssertEqual(q.tau(calibrated: 0.925), 0.8)
    }
}

/// Fake engines: the loop is tested without any model, as the Python package is tested with the fake backend.
struct FakeGenerator: Generator {
    let name = "fake"
    let replies: [String]
    let counter = Counter()
    func generate(system: String, user: String, maxTokens: Int) -> AsyncThrowingStream<GenerationEvent, Error> {
        let i = counter.next()
        let r = replies[min(i, replies.count - 1)]
        return AsyncThrowingStream { c in c.yield(.text(r)); c.yield(.done(GenerationStats(generatedTokens: 5, seconds: 0.1))); c.finish() }
    }
}
final class Counter: @unchecked Sendable {
    private var n = 0; private let lock = NSLock()
    func next() -> Int { lock.lock(); defer { n += 1; lock.unlock() }; return n }
}
/// Flags every sentence containing "wrong" as contradicted.
struct FakeVerifier: Verifier {
    let name = "fake-g1"
    func verify(document: String, sentences: [Segment]) async throws -> Verdicts {
        let v = sentences.enumerated().map { i, s in
            SentenceVerdict(index: i, text: s.text, start: s.start, end: s.end, scored: s.checkable,
                            probs: s.checkable ? (s.text.contains("wrong") ? [0.1, 0.8, 0.1] : [0.97, 0.02, 0.01]) : nil)
        }
        return Verdicts(sentences: v, inputTokens: 10, seconds: 0.01, threshold: 0.925, model: name)
    }
}

final class LoopTests: XCTestCase {
    func testLoopRepairsAndStops() async throws {
        let gen = FakeGenerator(replies: ["The sky is blue today. The grass is wrong colour.", "[2] The grass is green."])
        let o = Orchestrator(retriever: nil, generator: gen, verifier: FakeVerifier(), judge: nil, calibratedThreshold: 0.925)
        let r = try await o.execute(.init(question: "q", document: "doc", compareWithJudge: false), policy: .strict)
        XCTAssertEqual(r.drafts.count, 2)
        XCTAssertEqual(r.status, .accepted)
        XCTAssertEqual(r.displayed, "The sky is blue today. The grass is green.")
        XCTAssertEqual(r.drafts[1].rewriteRequest, [1])
    }

    func testLoopGivesUpAndAbstains() async throws {
        let gen = FakeGenerator(replies: ["Fine sentence here. This is wrong for sure.", "[2] Still wrong though."])
        let o = Orchestrator(retriever: nil, generator: gen, verifier: FakeVerifier(), judge: nil, calibratedThreshold: 0.925)
        let r = try await o.execute(.init(question: "q", document: "doc", compareWithJudge: false), policy: .strict)
        XCTAssertEqual(r.drafts.count, 3)
        XCTAssertEqual(r.status, .abstained)
        var hide = Policy.strict; hide.onFailure = .hide
        let gen2 = FakeGenerator(replies: ["Fine sentence here. This is wrong for sure.", "[2] Still wrong though."])
        let r2 = try await Orchestrator(retriever: nil, generator: gen2, verifier: FakeVerifier(), judge: nil, calibratedThreshold: 0.925)
            .execute(.init(question: "q", document: "doc", compareWithJudge: false), policy: hide)
        XCTAssertEqual(r2.displayed, "Fine sentence here.")
    }

    func testAuditRoundTrip() async throws {
        let gen = FakeGenerator(replies: ["The sky is blue today."])
        let r = try await Orchestrator(retriever: nil, generator: gen, verifier: FakeVerifier(), judge: nil, calibratedThreshold: 0.925)
            .execute(.init(question: "q", document: "doc", compareWithJudge: false), policy: .lenient)
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("audit-\(UUID()).jsonl")
        let log = AuditLog(url: url)
        try await log.append(r); try await log.append(r)
        let back = try AuditLog.read(url)
        XCTAssertEqual(back.count, 2)
        XCTAssertEqual(back[0].drafts[0].verdicts.sentences[0].label, .supported)
    }
}

final class RevisionPromptTests: XCTestCase {
    let doc = "The settlement includes $196,365 for the complainant. Legal firms received over $49,000. The case closed in May."

    func testSentencePromptByErrorType() {
        let c = SentenceVerdict(index: 0, text: "Legal firms received over $73,500.", start: 0, end: 10, scored: true, label: .contradicted)
        let n = SentenceVerdict(index: 1, text: "The judge was Aiko Tanabe.", start: 11, end: 20, scored: true, label: .notMentioned)
        let pc = Revision.sentencePrompt(c, document: doc)
        XCTAssertTrue(pc.contains("Legal firms received over $49,000."))
        XCTAssertTrue(pc.contains("The SENTENCE contradicts the SOURCE."))
        XCTAssertFalse(pc.contains("DELETE"))
        XCTAssertTrue(Revision.sentencePrompt(n, document: doc).contains("write DELETE"))
    }

    func testCleanSentence() {
        XCTAssertEqual(Revision.cleanSentence("Corrected sentence: \"Legal firms received over $49,000.\"\nextra"), "Legal firms received over $49,000.")
        XCTAssertNil(Revision.cleanSentence("DELETE"))
        XCTAssertEqual(Revision.cleanSentence("[2] The grass is green."), "The grass is green.")
    }

    func testContradictedIsNeverDeleted() async throws {
        struct DeleteAll: Generator {
            let name = "delete"
            func generate(system: String, user: String, maxTokens: Int) -> AsyncThrowingStream<GenerationEvent, Error> {
                let r = user.contains("SENTENCE:") ? "DELETE" : "The sky is blue today. The grass is wrong colour."
                return AsyncThrowingStream { c in c.yield(.text(r)); c.yield(.done(GenerationStats())); c.finish() }
            }
        }
        struct Contra: Verifier {
            let name = "contra"
            func verify(document: String, sentences: [Segment]) async throws -> Verdicts {
                Verdicts(sentences: sentences.enumerated().map { i, s in
                    SentenceVerdict(index: i, text: s.text, start: s.start, end: s.end, scored: true,
                                    probs: s.text.contains("wrong") ? [0.1, 0.8, 0.1] : [0.97, 0.02, 0.01])
                }, inputTokens: 1, seconds: 0, threshold: 0.925, model: name)
            }
        }
        let r = try await Orchestrator(retriever: nil, generator: DeleteAll(), verifier: Contra(), judge: nil, calibratedThreshold: 0.925)
            .execute(.init(question: "q", document: "doc", compareWithJudge: false), policy: .lenient)
        XCTAssertTrue(r.final!.text.contains("wrong colour"), "a contradicted sentence must not be deleted")
    }
}
