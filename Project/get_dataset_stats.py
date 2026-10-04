import json

paths = [
    "/Users/francescodedominicis/Desktop/THESIS/Project/data/processed_512/train.jsonl",
    "/Users/francescodedominicis/Desktop/THESIS/Project/data/processed_512/valid.jsonl",
    "/Users/francescodedominicis/Desktop/THESIS/Project/data/processed_512/test.jsonl"
]

total_options = 0
total_queries = 0

for path in paths:
    with open(path, 'r') as f:
        for line in f:
            data = json.loads(line)
            text = data['text']
            options = sum(1 for char in "ABCDEFGHIJKLMNOPQRSTUVWXY" if f"[{char}]" in text)
            total_options += options
            total_queries += 1

print(f"Total Queries: {total_queries}")
print(f"Average Options per Query: {total_options / total_queries:.2f}")
