import Foundation
import NaturalLanguage

/// One answer sentence. Offsets are UTF-16 offsets into the original text (NSRange-compatible).
public struct Segment: Codable, Sendable, Hashable {
    public var start: Int
    public var end: Int
    public var text: String
    public var checkable: Bool

    public init(start: Int, end: Int, text: String, checkable: Bool) {
        self.start = start; self.end = end; self.text = text; self.checkable = checkable
    }
}

/// Port of `groundone/data/segment.py` with `NLTokenizer` in place of pysbd (decision 7, §5.2):
/// split on line breaks, split each line into sentences, strip list markers, mark sentences without checkable content.
public enum Segmenter {
    static let list = try! NSRegularExpression(pattern: #"^(?:\d{1,2}[.)]|[a-z]\)|[*•\-–])\s+"#)
    static let citation = try! NSRegularExpression(
        pattern: #"^\(?\s*(passages?|source|document)\s*[\d,\s and]*\)?[.\s]*$"#, options: [.caseInsensitive])
    static let word = try! NSRegularExpression(pattern: #"[A-Za-z0-9][A-Za-z0-9'’\-]*"#)
    static let meta = try! NSRegularExpression(
        pattern: #"^(sure|certainly|of course|okay|ok|great|absolutely|yes|no problem)\b[\s!,.]*$"#
            + #"|^(here (is|are)|below (is|are)|i hope (this|that) helps|let me know|feel free|thank you|thanks)\b"#
            + #"|^(sure|certainly|of course|absolutely)[,!.]?\s*(i can|i'd be happy|i would be happy|i'll|here)\b"#
            + #"|^that'?s (it|all)\b[\s!.]*$"#
            + #"|^(i'?m sorry|sorry\b|unable to answer|i (cannot|can't|am unable to) (answer|provide|determine|find))"#
            + #"|\b(i am|i'm|we are) unable to (answer|provide|determine)\b"#
            + #"|^(the (given|provided) (passages?|information|text|context|data) (does|do) not (contain|provide|mention|include|specify|say))"#,
        options: [.caseInsensitive])

    static func matches(_ re: NSRegularExpression, _ s: String) -> Bool {
        re.firstMatch(in: s, range: NSRange(location: 0, length: (s as NSString).length)) != nil
    }

    /// False for fewer than 2 words, a heading that introduces a list (trailing colon), a citation, or a
    /// conversational / refusal formula.
    public static func isCheckable(_ s: String) -> Bool {
        let strip = CharacterSet(charactersIn: "*#-•> \t")
        let t = s.trimmingCharacters(in: .whitespacesAndNewlines).trimmingCharacters(in: strip)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let ns = t as NSString
        if word.numberOfMatches(in: t, range: NSRange(location: 0, length: ns.length)) < 2 { return false }
        if t.hasSuffix(":") || matches(citation, t) { return false }
        return !matches(meta, t)
    }

    static let markerOnly = try! NSRegularExpression(pattern: #"^\s*(?:\d{1,2}[.)]|[a-z]\)|[*•\-–])\s*$"#)

    static let abbreviation = try! NSRegularExpression(
        pattern: #"(?:^|[\s(])(?:[A-Z]\.|(?:[A-Za-z]\.){2,}|v\.|Capt\.|Lt\.|Col\.|Sgt\.|Adm\.|Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|St\.|Sr\.|Jr\.|Inc\.|Ltd\.|Co\.|Corp\.|vs\.|No\.|Nos\.|Gen\.|Gov\.|Sen\.|Rep\.|Rev\.|Mt\.|Ft\.|approx\.|etc\.|e\.g\.|i\.e\.|Jan\.|Feb\.|Mar\.|Apr\.|Aug\.|Sept?\.|Oct\.|Nov\.|Dec\.)$"#)

    /// NLTokenizer sentence ranges of one line; a span holding only a list marker ("1.") is merged into the next.
    static func sentenceRanges(_ line: String) -> [NSRange] {
        let tok = NLTokenizer(unit: .sentence)
        tok.string = line
        var ranges: [NSRange] = []
        var pending: NSRange?
        tok.enumerateTokens(in: line.startIndex..<line.endIndex) { range, _ in
            var r = NSRange(range, in: line)
            if let p = pending { r = NSRange(location: p.location, length: r.upperBound - p.location); pending = nil }
            if matches(markerOnly, (line as NSString).substring(with: r)) { pending = r } else { ranges.append(r) }
            return true
        }
        if let p = pending { ranges.append(p) }
        // pysbd rules NLTokenizer lacks: no break after initials or common abbreviations, or before a lowercase word.
        var merged: [NSRange] = []
        for r in ranges {
            if let last = merged.last {
                let prev = (line as NSString).substring(with: last).trimmingCharacters(in: .whitespaces)
                let next = (line as NSString).substring(with: r).trimmingCharacters(in: .whitespaces)
                if matches(abbreviation, prev) || next.first.map({ $0.isLowercase || $0.isNumber }) == true {
                    merged[merged.count - 1] = NSRange(location: last.location, length: r.upperBound - last.location)
                    continue
                }
            }
            merged.append(r)
        }
        return merged
    }

    public static func segment(_ text: String) -> [Segment] {
        var out: [Segment] = []
        var lineStart = 0
        for line in text.components(separatedBy: "\n") {
            let lineNS = line as NSString
            if !line.trimmingCharacters(in: .whitespaces).isEmpty {
                for r in sentenceRanges(line) {
                    let raw = lineNS.substring(with: r)
                    let lead = (raw as NSString).length
                        - (String(raw.drop(while: { $0.isWhitespace })) as NSString).length
                    var body = raw.trimmingCharacters(in: .whitespacesAndNewlines)
                    var offset = r.location + lead
                    if let m = list.firstMatch(in: body, range: NSRange(location: 0, length: (body as NSString).length)) {
                        let rest = (body as NSString).substring(from: m.range.upperBound)
                        offset += m.range.upperBound
                        offset += (rest as NSString).length
                            - (String(rest.drop(while: { $0.isWhitespace })) as NSString).length
                        body = rest.trimmingCharacters(in: .whitespacesAndNewlines)
                    }
                    if !body.isEmpty {
                        let a = lineStart + offset
                        out.append(Segment(start: a, end: a + (body as NSString).length, text: body,
                                           checkable: isCheckable(body)))
                    }
                }
            }
            lineStart += lineNS.length + 1
        }
        return out
    }
}
