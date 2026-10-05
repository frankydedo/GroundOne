"""Assemble EDA/report/eda_report.md from conclusions.md (hand-written), stats/*.json and figures/*.png.

Run after 01–04. Re-running regenerates the report; only conclusions.md is edited by hand.
"""
import json
import time

from common import EXPERIMENTS, REPORT, STATS

S = {p.stem: json.loads(p.read_text()) for p in STATS.glob("*.json")}


def table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


def figs(name):
    return "\n\n".join(f"![{f['caption']}]({f['file']})\n*{f['caption']}*" for f in S[name]["figures"])


a, r, m, c = S["anli"], S["ragtruth"], S["minicheck_aggrefact"], S["cross"]
md = [f"# EDA report: datasets for GroundOne (Phase 1a)\n\nGenerated {time.strftime('%Y-%m-%d %H:%M')} by `EDA/scripts/make_report.py`. "
      "Scripts: `EDA/scripts/01_anli.py`, `02_ragtruth.py`, `03_minicheck_aggrefact.py`, `04_cross.py`. Raw numbers: `EDA/report/stats/`. "
      "Data: `Project/data/raw/` (see `Project/data/manifest.json`).\n",
      "## 0. Experiments the data must serve\n\n" + table([{"ID": k, "Experiment": v} for k, v in EXPERIMENTS.items()], ["ID", "Experiment"]),
      (REPORT / "conclusions.md").read_text(),
      "---\n\n## 5. ANLI in detail\n",
      table([{"split": s, **{rd: a["sizes"][rd][s] for rd in ["r1", "r2", "r3"]}} for s in ["train", "dev", "test"]], ["split", "r1", "r2", "r3"]),
      f"\nPremise tokens: median {a['premise_tokens']['50%']}, p90 {a['premise_tokens']['90%']}, max {a['premise_tokens']['max']}. "
      f"Hypothesis tokens: median {a['hypothesis_tokens']['50%']}, p90 {a['hypothesis_tokens']['90%']}. "
      f"Unique premises: {a['premises_unique']:,} ({a['hypotheses_per_premise_mean']} hypotheses each on average); "
      f"dev/test premises also in train: {a['dev_test_premises_also_in_train']}. Negation rate by class: {a['negation_rate_by_label']}. "
      f"Word overlap claim→document by class: {a['overlap_mean_by_label']}. Annotator reason available for {a['reason_field_nonempty']:.0%} of pairs.\n",
      "Examples (dev):\n\n" + "\n".join(f"- **{k}**: premise \"{v['premise'][:160]}…\" / claim \"{v['hypothesis']}\"" for k, v in a["examples"].items()),
      figs("anli"),
      "---\n\n## 6. RAGTruth in detail\n",
      table([{"task": t, "train": r["responses_by_split_task"][t]["train"], "test": r["responses_by_split_task"][t]["test"],
              "hallucinated (train)": r["hallucinated_rate_by_task_split"]["train"][t], "hallucinated (test)": r["hallucinated_rate_by_task_split"]["test"][t],
              "context tokens p50 / p90": f"{r['context_tokens_by_task'][t]['50%']} / {r['context_tokens_by_task'][t]['90%']}",
              "K p50 / p90": f"{r['K_by_task'][t]['50%']} / {r['K_by_task'][t]['90%']}"} for t in ["QA", "Summary", "Data2txt"]],
            ["task", "train", "test", "hallucinated (train)", "hallucinated (test)", "context tokens p50 / p90", "K p50 / p90"]),
      f"\nSpans: {r['spans_total']:,} ({r['span_types']}); flags {r['span_flags']}; "
      f"{r['spans_crossing_sentence_boundary']['share']:.1%} cross a sentence boundary. "
      f"Sentences: {r['sentences_total']:,}; train {r['sentence_class_counts_train']}; test {r['sentence_class_counts_test']}. "
      f"Hallucination rate by generator: {r['hallucinated_rate_by_model']}. Quality flags: {r['quality']}. "
      f"Prompts over 1,024 tokens: {r['share_prompts_over_1024_tokens']:.0%}; over 2,048: {r['share_prompts_over_2048_tokens']:.0%}.\n",
      f"Data2txt context example: `{r['example_data2txt_context'][:300]}…`\n",
      figs("ragtruth"),
      "---\n\n## 7. MiniCheck synthetic data and LLM-AggreFact\n",
      f"MiniCheck synthetic: {m['minicheck']['sizes']}, supported rate {m['minicheck']['supported_rate']}, document tokens median "
      f"{m['minicheck']['doc_tokens']['50%']} (p90 {m['minicheck']['doc_tokens']['90%']}), claim tokens median {m['minicheck']['claim_tokens']['50%']}, "
      f"{m['minicheck']['claims_per_doc_mean']} claims per document.\n",
      table([x for x in m["aggrefact"]["per_dataset"] if x["split"] == "test"], ["dataset", "n", "supported", "doc_tok_p50", "doc_tok_p90", "claim_tok_p50"]),
      f"\nLLM-AggreFact test documents over 2,048 tokens: {m['aggrefact']['share_docs_over_2048_tokens_test']:.1%}.\n",
      figs("minicheck_aggrefact"),
      "---\n\n## 8. Cross-dataset checks\n",
      f"- LLM-AggreFact RAGTruth subset: {c['aggrefact_ragtruth_subset']['n']:,} claims, {c['aggrefact_ragtruth_subset']['by_split']}; "
      f"matched to RAGTruth sentences by split: {c['aggrefact_ragtruth_subset']['claims_equal_to_a_ragtruth_sentence']}.",
      f"- Label agreement (our span-derived binary label vs LLM-AggreFact): {c['label_agreement_ours_vs_aggrefact']['agreement']:.1%} on "
      f"{c['label_agreement_ours_vs_aggrefact']['matched_sentences']:,} sentences; cross-tab (rows ours, columns LLM-AggreFact; 1 = supported): "
      f"{c['label_agreement_ours_vs_aggrefact']['crosstab_rows_ours_cols_aggrefact']}.",
      f"- Overlap with LLM-AggreFact: MiniCheck documents {c['minicheck_docs_in_aggrefact']}, MiniCheck claims {c['minicheck_claims_in_aggrefact']}, ANLI premises {c['anli_premises_in_aggrefact']}.",
      f"- Median document tokens: {c['doc_tokens_median']}.\n",
      figs("cross"),
      "---\n\n## 9. Label schemes\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in c["label_schemes"].items())]
(REPORT / "eda_report.md").write_text("\n\n".join(md) + "\n")
print("written", REPORT / "eda_report.md")
