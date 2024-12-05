from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value
import pandas as pd
import pprint

# 問題のパラメータ
bin_count = 5
bin_capacity = 10
items = [
    {"item": "A", "size": 12},
    {"item": "B", "size": 8},
    {"item": "C", "size": 7},
    {"item": "D", "size": 6},
    {"item": "E", "size": 5},
    {"item": "F", "size": 3},
]

# ビンデータ
bins = list(range(bin_count))

# 問題定義
problem = LpProblem("Min_FIBP", LpMinimize)

# 変数定義
x = LpVariable.dicts("x", ((i["item"], b) for i in items for b in bins), lowBound=0, cat="Continuous")
y = LpVariable.dicts("y", ((i["item"], b) for i in items for b in bins), cat="Binary")

# 目的関数: 分割数を最小化
problem += lpSum(y[i["item"], b] for i in items for b in bins)

# 制約: 各アイテムの合計サイズは元のサイズに等しい
for i in items:
    problem += lpSum(x[i["item"], b] for b in bins) == i["size"]

# 制約: 各ビンの容量制限
for b in bins:
    problem += lpSum(x[i["item"], b] for i in items) <= bin_capacity

# 制約: x_ij > 0 のとき y_ij = 1
for i in items:
    for b in bins:
        problem += x[i["item"], b] <= i["size"] * y[i["item"], b]

# 問題を解く
problem.solve()

# 結果の出力
status = LpStatus[problem.status]
used_bins = [b for b in bins if sum(value(x[i["item"], b]) for i in items) > 0]
packed_items = {
    b: {i["item"]: value(x[i["item"], b]) for i in items if value(x[i["item"], b]) > 0}
    for b in used_bins
}

results = {
    "status": status,
    "number_of_fragments": problem.objective.value(),
    "packed_items": packed_items,
}

# Packed items をCSVに保存
packed_items_df = pd.DataFrame(
    [
        {"bin": b, "item": i, "packed_size": packed_items[b][i]}
        for b in packed_items
        for i in packed_items[b]
    ]
)
packed_items_csv_path = "./data/min_fibp_packed_items.csv"
packed_items_df.to_csv(packed_items_csv_path, index=False)

pprint.pprint(results)
print(packed_items_df)
