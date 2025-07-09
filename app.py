import streamlit as st
import pandas as pd

# タイトルとページ設定
st.set_page_config("MAKE4フィルターシミュレーター", layout="centered")
st.title("MAKE4フィルターシミュレーター:非公式")

# データ読み込み
df = pd.read_csv("filters.csv")
types = df["type"].unique()

# ─── タブ構成 ───
tab1, tab2 = st.tabs(["▶ フィルターを選ぶ", "目標ステータスから探す"])

# ──────────────────────────────
# ▼ TAB1: 選択式シミュレート
# ──────────────────────────────
with tab1:
    st.sidebar.header("各フィルターを選択")
    selected = {}
    results = []

    for t in types:
        group = df[df["type"] == t].copy()
        group = group.sort_values("name")

        default_id = group[group["note"] == "基準"]["id"].values[0] if "基準" in group["note"].values else group["id"].iloc[0]

        name_to_id = dict(zip(group["name"], group["id"]))
        name_list = list(name_to_id.keys())
        default_index = name_list.index(df[df["id"] == default_id]["name"].values[0])

        selected_name = st.sidebar.selectbox(t.replace("_", " ").title(), name_list, index=default_index)
        selected_id = name_to_id[selected_name]
        selected[t] = selected_id

        row = df[df["id"] == selected_id].iloc[0]
        results.append({
            "種類": t.replace("_FILTER", "").title(),
            "名前": row["name"],
            "高音": row["high"],
            "低音": row["bass"]
        })

    total_high = sum(r["高音"] for r in results)
    total_bass = sum(r["低音"] for r in results)

    st.subheader("🔊合計ステータス")
    st.metric("高音域 (high)", f"{total_high:+.2f}")
    st.metric("低音域 (bass)", f"{total_bass:+.2f}")

    st.subheader("選択中のフィルター")
    df_summary = pd.DataFrame(results)

    def zebra(row):  # 明暗交互
        return ['background-color: #222222' if row.name % 2 else '' for _ in row]

st.dataframe(
    df_summary.style
        .apply(zebra, axis=1)
        .format("{:.2f}", subset=["高音", "低音"]),
    use_container_width=True
)
# ──────────────────────────────
# ▼ TAB2: 目標値から近い組合せを探す
# ──────────────────────────────
with tab2:
    st.header("目標ステータスに近いフィルター組合せ")

    goal_high = st.slider("目標 高音域", -10.0, 10.0, 0.0, 0.1)
    goal_bass = st.slider("目標 低音域", -10.0, 10.0, 0.0, 0.1)
    top_n = st.number_input("表示件数", 1, 50, 10, 1)

    # 各種ごとの選択肢を取得
    group_dict = {t: df[df["type"] == t].to_dict("records") for t in types}

    from itertools import product

    rows = []
    for combo in product(*group_dict.values()):
        total_h = sum(f["high"] for f in combo)
        total_b = sum(f["bass"] for f in combo)
        diff = ((total_h - goal_high)**2 + (total_b - goal_bass)**2)**0.5

        row = {
            "高音": round(total_h, 2),
            "低音": round(total_b, 2),
            "誤差": round(diff, 3)
        }
        for i, t in enumerate(types):
            row[t.replace("_FILTER", "").title()] = combo[i]["name"]
        rows.append(row)

    df_result = pd.DataFrame(rows).sort_values("誤差").head(int(top_n)).reset_index(drop=True)

    # 行交互カラー
    def zebra2(row):
        return ['background-color: #222222' if row.name % 2 else '' for _ in row]

    # 小数点第二位まで表示させる
    st.dataframe(
        df_result.style
            .apply(zebra2, axis=1)
            .format("{:.2f}", subset=["高音", "低音", "誤差"]),
        use_container_width=True
    )

