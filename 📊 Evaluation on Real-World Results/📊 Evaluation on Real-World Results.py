import ast
from collections import defaultdict

# example path in my notebook
PATH = "/kaggle/input/devices1000/eval1000.txt"

with open(PATH, "r", encoding="utf-8") as f:
    text = f.read()

items = []
pos = 0

while True:
    start = text.find("{'index':", pos)
    if start == -1:
        break

    depth = 0
    started = False

    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
            started = True
        elif ch == "}":
            depth -= 1
            if depth == 0 and started:
                end = i + 1
                snippet = text[start:end]
                try:
                    obj = ast.literal_eval(snippet)
                    items.append(obj)
                except Exception as e:
                    print("Error with parsing, start =", start, ":", e)
                pos = end
                break

print("All examples:", len(items))

def safe_mean(values):
    return sum(values) / len(values) if values else float("nan")
    
overall_scores = [
    x.get("overall_score")
    for x in items
    if isinstance(x.get("overall_score"), (int, float))
]

dim_values = defaultdict(list)
dm_values = defaultdict(list)

for x in items:
    dims = x.get("dimensions") or {}
    for k, v in dims.items():
        if isinstance(v, (int, float)):
            dim_values[k].append(v)

    dm = x.get("derived_metrics") or {}
    for k, v in dm.items():
        if isinstance(v, bool):
            dm_values[k].append(1.0 if v else 0.0)
        elif isinstance(v, (int, float)):
            dm_values[k].append(v)

print("\n Average overall_score:")
print(f"  overall_score: {safe_mean(overall_scores):.3f}")

print("\n Average dimensions:")
for k, vals in dim_values.items():
    print(f"  {k}: {safe_mean(vals):.3f}")
