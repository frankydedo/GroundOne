"""Assemble EDA/report/eda_report.md from conclusions.md (hand-written), stats/*.json and figures/*.png.

Run after 01–04 (with the GroundOne venv). Only conclusions.md is edited by hand.
"""
import json
import time

from common import REPORT, STATS, TASKS

S = {p.stem: json.loads(p.read_text()) for p in STATS.glob("*.json")}


def table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


def figs(name):
    return "\n\n".join(f"![{f['caption']}]({f['file']})\n*{f['caption']}*" for f in S[name]["figures"])


r, a, v, d = S["ragtruth"], S["aggrefact"], S["vitaminc"], S["dataset"]
md = [f"# EDA report: the GroundOne dataset and its sources\n\nGenerated {time.strftime('%Y-%m-%d %H:%M')} by `EDA/scripts/make_report.py`. "
      "Scripts: `01_ragtruth.py`, `02_aggrefact.py`, `03_vitaminc.py` (part A, sources) and `04_dataset.py` (part B, built dataset). "
      "Raw numbers: `EDA/report/stats/`. Dataset specification: `Project/docs/dataset_plan.md`; counts: "
      "`Project/data/processed/groundone/DATACARD.md`.\n",
      (REPORT / "conclusions.md").read_text(),
      "---\n\n# Part A: source datasets\n\n## 4. RAGTruth (training source, test T1)\n",
      table([{"task": t, "answers train": r["responses_by_split_task"][t]["train"], "answers test": r["responses_by_split_task"][t]["test"],
              "hallucinated train": r["hallucinated_rate_by_task_split"]["train"][t], "hallucinated test": r["hallucinated_rate_by_task_split"]["test"][t],
              "context tokens p50 / p90": f"{r['context_tokens_by_task'][t]['50%']} / {r['context_tokens_by_task'][t]['90%']}"} for t in TASKS],
            ["task", "answers train", "answers test", "hallucinated train", "hallucinated test", "context tokens p50 / p90"]),
      f"\nSpans: {r['spans_total']:,} ({r['span_types']}); flags {r['span_flags']}. Hallucination rate by generator: "
      f"{r['hallucinated_rate_by_model']}. Quality flags: {r['quality']}. Prompts over 2,048 tokens: {r['share_prompts_over_2048_tokens']:.1%}.\n",
      f"Data2txt context example: `{r['example_data2txt_context'][:300]}…`\n",
      figs("ragtruth"),
      "---\n\n## 5. LLM-AggreFact test (test T2)\n",
      table(a["per_dataset"], ["dataset", "n", "supported", "docs", "claims_per_doc", "doc_tok_p50", "doc_tok_p90", "claim_tok_p50"]),
      f"\n{a['n']:,} claims, {a['supported_rate']:.1%} supported; documents over 2,048 tokens: {a['share_docs_over_2048_tokens']:.1%}.\n",
      figs("aggrefact"),
      "---\n\n## 6. VitaminC test split (source of test T3)\n",
      f"Test split by type and label: {v['test_by_type_label']}. Real part: {v['real']['n']:,} pairs over {v['real']['pages']:,} pages and "
      f"{v['real']['cases']:,} revision cases ({v['real']['pairs_per_case_mean']} pairs per case); {v['real']['claims_with_several_evidences']:,} "
      f"claims appear with more than one evidence (contrastive). Claim tokens median {v['real']['claim_tokens']['50%']}, evidence tokens median "
      f"{v['real']['evidence_tokens']['50%']}. Claims containing a digit by label: {v['real']['numeric_claim_share_by_label']}. "
      f"Claim-evidence word overlap by label: {v['real']['overlap_mean_by_label']}.\n",
      figs("vitaminc"),
      "---\n\n# Part B: the built dataset\n\n## 7. Segmentation, distribution shift, label origin and surface cues\n",
      f"- Segmentation over {d['segmentation']['answers']:,} good RAGTruth answers: regex splitter {d['segmentation']['regex_sentences']:,} "
      f"sentences, pysbd {d['segmentation']['pysbd_sentences']:,}; without checkable content {d['segmentation']['non_checkable_share']:.1%} "
      f"({d['segmentation']['non_checkable_by_reason']}).",
      "- Class shares by split and task: " + "; ".join(f"{k}: {v_}" for k, v_ in d["class_share_by_split_task"].items()) + ".",
      f"- Unsupported share by generator (train / T1): " + "; ".join(f"{k} {x['train']} / {x['T1']}" for k, x in d["unsupported_share_by_split_model"].items()) + ".",
      "- RAGTruth span types behind each class: " + "; ".join(f"{k}: {v_}" for k, v_ in d["span_types_behind_classes"].items()) + ".",
      f"- Word overlap by class: {d['overlap_mean_by_split_class']}; overlap-only AUROC (supported vs not): {d['overlap_auroc_supported_vs_not']}.",
      f"- Sentence-only classifier, strongest n-grams per class: {d['sentence_only_top_ngrams']}.\n",
      figs("dataset")]
(REPORT / "eda_report.md").write_text("\n\n".join(md) + "\n")
print("written", REPORT / "eda_report.md")
