import GroundOneCore
import SwiftUI

struct PoliciesView: View {
    @Environment(AppModel.self) private var model
    @State private var editing: Policy?

    var body: some View {
        @Bindable var model = model
        HSplitView {
            List(model.policies, selection: Binding(get: { editing?.name }, set: { n in editing = model.policies.first { $0.name == n } })) { p in
                VStack(alignment: .leading, spacing: 2) {
                    Text(p.name).font(.body.weight(.medium))
                    Text("blocks \(p.blocking.map(\.display).joined(separator: ", ")) · \(p.maxAttempts) rewrite\(p.maxAttempts == 1 ? "" : "s") · on failure: \(p.onFailure.rawValue)")
                        .font(.caption).foregroundStyle(.secondary)
                }
                .tag(p.name)
            }
            .frame(minWidth: 260, maxWidth: 340)
            Group {
                // not Binding($editing): it force-unwraps, and the editor is still updated once after the selection is cleared
                if let current = editing {
                    PolicyEditor(policy: Binding(get: { editing ?? current }, set: { editing = $0 }),
                                 calibrated: model.calibration?.threshold ?? 0.925) { model.save($0) }
                        .id(current.name)
                } else {
                    Text("Select a policy to edit it.").foregroundStyle(.secondary).frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .frame(minWidth: 420)
        }
        .navigationTitle("Policies")
        .onAppear { editing = editing ?? model.policy }
    }
}

struct PolicyEditor: View {
    @Binding var policy: Policy
    let calibrated: Double
    let save: (Policy) -> Void

    var body: some View {
        Form {
            Section("Decision") {
                Picker("Threshold τ", selection: Binding(get: { policy.threshold == .calibrated ? 0 : 1 },
                                                         set: { policy.threshold = $0 == 0 ? .calibrated : .value(calibrated) })) {
                    Text("Calibrated on dev (τ = \(calibrated.p2))").tag(0)
                    Text("Custom").tag(1)
                }
                if case .value(let v) = policy.threshold {
                    Slider(value: Binding(get: { v }, set: { policy.threshold = .value($0) }), in: 0.5...0.99) {
                        Text("τ = \(v.p2)")
                    }
                }
                Text("A sentence is supported iff GroundOne's calibrated P(supported) ≥ τ; otherwise it is contradicted or not mentioned, whichever is more probable.")
                    .font(.caption).foregroundStyle(.secondary)
            }
            Section("Blocking verdicts") {
                ForEach([Label.contradicted, .notMentioned], id: \.self) { l in
                    Toggle(l.display.capitalized, isOn: Binding(get: { policy.blocking.contains(l) },
                                                                set: { on in policy.blocking = on ? policy.blocking + [l] : policy.blocking.filter { $0 != l } }))
                }
                Text("Strict blocks both (anything the documents do not state); lenient blocks only contradictions (D20).")
                    .font(.caption).foregroundStyle(.secondary)
            }
            Section("Loop") {
                Stepper("Rewrites: \(policy.maxAttempts)", value: $policy.maxAttempts, in: 0...4)
                Picker("On failure", selection: $policy.onFailure) {
                    Text("Highlight the flagged sentences").tag(Policy.OnFailure.highlight)
                    Text("Hide the flagged sentences").tag(Policy.OnFailure.hide)
                    Text("Abstain").tag(Policy.OnFailure.abstain)
                }
                Toggle("Show probabilities", isOn: $policy.showProbabilities)
                Toggle("Write the audit log", isOn: $policy.auditLog)
            }
            HStack {
                Spacer()
                Button("Save policy") { save(policy) }.keyboardShortcut("s")
            }
        }
        .formStyle(.grouped)
    }
}
