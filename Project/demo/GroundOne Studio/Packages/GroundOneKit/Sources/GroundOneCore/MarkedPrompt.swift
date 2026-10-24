import Foundation

/// Port of `prompts.encode_marked` (design b, PROMPT_VERSION_MARKED = "groundone-v2-marked").
/// Pieces are tokenised separately and concatenated, exactly as in training: encoding the joined string would
/// give different ids at the piece boundaries.
public enum MarkedPrompt {
    public static let version = "groundone-v2-marked"
    public static let system = "You are a faithfulness verifier for retrieval-augmented answers."
    public static let instruction = "Check each sentence of the ANSWER against the DOCUMENT. After each sentence give a verdict: "
        + "A if the DOCUMENT supports it, B if the DOCUMENT contradicts it, C if the DOCUMENT does not mention it."
    public static let marker = " Verdict:"

    public static func head(document: String) -> String {
        "<|im_start|>system\n\(system)<|im_end|>\n<|im_start|>user\n\(instruction)\n\nDOCUMENT:\n\(document)\n\nANSWER:\n"
    }

    /// Token ids and the positions of the last marker token after every scored sentence.
    public static func encode(_ enc: TokenEncoder, document: String, sentences: [String], scored: [Bool])
        -> (ids: [Int], positions: [Int])
    {
        var ids = enc.encode(head(document: document))
        var pos: [Int] = []
        let markerIDs = enc.encode(marker)
        let newline = enc.encode("\n")
        for (k, (s, sc)) in zip(sentences, scored).enumerated() {
            ids += enc.encode("[\(k + 1)] \(s)")
            if sc {
                ids += markerIDs
                pos.append(ids.count - 1)
            }
            ids += newline
        }
        return (ids, pos)
    }
}

/// The B0a terse-judge prompt of `baselines/judges.py`, and its lenient parser.
public enum JudgePrompt {
    public static let instruction = "Check each listed sentence of the ANSWER against the DOCUMENT. For each sentence number write exactly one "
        + "line '<number>: <letter>', where A = supported by the DOCUMENT, B = contradicted by the DOCUMENT, "
        + "C = not mentioned in the DOCUMENT. Write nothing else."
    public static let tokensPerSentence = 8

    public static func user(document: String, sentences: [String], check: [Int]) -> String {
        let numbered = sentences.enumerated().map { "[\($0.offset + 1)] \($0.element)" }.joined(separator: "\n")
        let todo = check.map { String($0 + 1) }.joined(separator: ", ")
        return "\(instruction)\n\nDOCUMENT:\n\(document)\n\nANSWER (numbered sentences):\n\(numbered)\n\nSentences to check: \(todo)"
    }

    static let line = try! NSRegularExpression(pattern: #"^\s*\[?(\d+)\]?\s*[:.)\-]\s*(.*)$"#)
    static let letter = try! NSRegularExpression(pattern: #"\b([ABC])\b"#)

    /// Last A/B/C on the line "<n>: ..."; first occurrence of each number wins. Keys are 0-based sentence indices.
    public static func parse(_ text: String, check: [Int]) -> [Int: Label?] {
        var got: [Int: Label] = [:]
        for l in text.components(separatedBy: .newlines) {
            let ns = l as NSString
            guard let m = line.firstMatch(in: l, range: NSRange(location: 0, length: ns.length)),
                  let n = Int(ns.substring(with: m.range(at: 1))) else { continue }
            let rest = ns.substring(with: m.range(at: 2))
            let letters = letter.matches(in: rest, range: NSRange(location: 0, length: (rest as NSString).length))
            if let last = letters.last, got[n] == nil {
                let L = (rest as NSString).substring(with: last.range(at: 1))
                got[n] = Label(index: ["A", "B", "C"].firstIndex(of: L)!)
            }
        }
        var out: [Int: Label?] = [:]
        for i in check { out[i] = got[i + 1] }
        return out
    }
}
