"""Demo library from the T1 sources (author, 2026-10-25): the CNN/DailyMail news articles of the Summary task and the
MS MARCO passages of the QA task, one text file per article or passage. Yelp records (Data2txt, structured JSON) are left
out: they are not documents to chat with. Output: outputs/demo/corpus/{news,msmarco}/*.txt and questions.json (the real
MS MARCO questions, used to choose the example questions shown in the app).

Usage (from Project/): GroundOne/.venv/bin/python experiments/demo/scripts/build_corpus.py
"""
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parents[3]
T1 = P / "data/processed/groundone/test_ragtruth.jsonl"
OUT = P / "outputs/demo/corpus"


def title_of(text, n=9):
    first = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0]
    first = re.sub(r"^\(CNN\)\s*|^By\s.*?\.\s", "", first).strip()
    words = first.split()
    return " ".join(words[:n]) + ("…" if len(words) > n else "")


def main():
    recs = [json.loads(l) for l in open(T1)]
    news, qa = {}, {}
    for r in recs:
        if r["task"] == "Summary":
            news.setdefault(r["doc"], r["meta"]["source_id"])
        elif r["task"] == "QA":
            qa.setdefault(r["doc"], r["meta"]["source_id"])
    (OUT / "news").mkdir(parents=True, exist_ok=True)
    (OUT / "msmarco").mkdir(parents=True, exist_ok=True)
    for doc, sid in news.items():
        (OUT / "news" / f"news-{sid}.txt").write_text(f"{title_of(doc)}\n\n{doc.strip()}\n")
    questions = []
    for doc, sid in qa.items():
        m = re.match(r"Question:\s*(.*?)\n\n(.*)", doc, re.S)
        if not m:
            continue
        q, body = m.group(1).strip(), m.group(2)
        parts = [p.strip() for p in re.split(r"\n*passage \d+:\s*", body) if p.strip()]
        for k, p in enumerate(parts, 1):
            (OUT / "msmarco" / f"msmarco-{sid}-{k}.txt").write_text(f"{q.capitalize()} (passage {k})\n\n{p}\n")
        questions.append({"source_id": sid, "question": q, "passages": len(parts)})
    (OUT / "questions.json").write_text(json.dumps(questions, indent=1))
    print(f"{len(news)} news articles, {sum(q['passages'] for q in questions)} MS MARCO passages for {len(questions)} questions")


if __name__ == "__main__":
    main()
