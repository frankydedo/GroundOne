import XCTest
@testable import GroundOneCore

/// Agreement of the NLTokenizer segmentation with pysbd on every T1 answer (§5.2): reported, not gated.
final class SegmentationAgreementTests: XCTestCase {
    struct Fixture: Decodable {
        struct Item: Decodable { let id: String; let text: String; let sentences: [String]; let checkable: [Bool] }
        let items: [Item]
    }

    func testAgreementWithPysbd() throws {
        let project = Workspace.project(from: #filePath)
        let url = project.appendingPathComponent("outputs/demo/fixtures/segmentation-t1.json")
        guard FileManager.default.fileExists(atPath: url.path) else { throw XCTSkip("no fixture at \(url.path)") }
        let fx = try JSONDecoder().decode(Fixture.self, from: Data(contentsOf: url))
        var sameSentences = 0, sameScored = 0, sameCount = 0, pyScored = 0, swScored = 0
        var examples: [[String: Any]] = []
        for it in fx.items {
            let s = Segmenter.segment(it.text)
            let a = it.sentences.enumerated().filter { it.checkable[$0.offset] }.map(\.element)
            let b = s.filter(\.checkable).map(\.text)
            pyScored += a.count; swScored += b.count
            if s.map(\.text) == it.sentences { sameSentences += 1 }
            if a == b { sameScored += 1 } else if examples.count < 15 { examples.append(["id": it.id, "pysbd": a, "swift": b]) }
            if a.count == b.count { sameCount += 1 }
        }
        let n = Double(fx.items.count)
        let report: [String: Any] = [
            "answers": fx.items.count,
            "identical_segmentation": Double(sameSentences) / n,
            "identical_scored_sentences": Double(sameScored) / n,
            "same_number_of_scored_sentences": Double(sameCount) / n,
            "scored_sentences": ["pysbd": pyScored, "nltokenizer": swScored],
            "protocol": "T1 answers (RAGTruth test), raw response text; Swift Segmenter (NLTokenizer + list markers + checkable rule) vs data/segment.py (pysbd)",
            "examples_of_disagreement": examples,
        ]
        let out = project.appendingPathComponent("outputs/demo/results/segmentation_agreement.json")
        try FileManager.default.createDirectory(at: out.deletingLastPathComponent(), withIntermediateDirectories: true)
        try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys]).write(to: out)
        print("segmentation agreement: identical \(sameSentences)/\(fx.items.count), scored identical \(sameScored), same scored count \(sameCount)")
    }
}
