import Foundation
import GroundOneCore
import GroundOneEngines

// Command-line front end of the demo engines: conformance, ingestion, retrieval check, queries, case study.
setvbuf(stdout, nil, _IOLBF, 0)
let args = Array(CommandLine.arguments.dropFirst())
let rest = Array(args.dropFirst())
do {
    switch args.first ?? "help" {
    case "verify-fixture": try await Commands.verifyFixture(rest)
    case "ingest": try await Commands.ingest(rest)
    case "retrieval-check": try await Commands.retrievalCheck(rest)
    case "ask": try await Commands.ask(rest)
    case "casestudy": try await CaseStudy.run(rest)
    case "install": try Install.run(rest)
    case "bestofn": try await BestOfN.run(rest)
    case "examples": try await Examples.run(rest)
    case "retrieval-t1": try await RetrievalT1.run(rest)
    default:
        print("usage: g1studio verify-fixture <run> [n] | ingest <corpus> <embedder> <paths...> | retrieval-check [embedders...] | ask <question> [--policy p] [--verifier run] [--no-judge]")
    }
} catch {
    FileHandle.standardError.write("error: \(error)\n".data(using: .utf8)!)
    exit(1)
}
