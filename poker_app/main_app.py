import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import sqlite3

# SQLite データベースの操作関数
def fetch_query(query, params=()):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results

# Streamlitアプリ
st.title("全プレイヤー収支比較")

# 横軸の選択
axis_option = st.radio("横軸を選択してください", ("日付", "ゲームID"))

# ユーザー選択
users = fetch_query("SELECT id, name FROM Users")
if users:
    all_records = []
    for user in users:
        records = fetch_query("SELECT date, result, game_id FROM Records WHERE user_id = ?", (user[0],))
        if records:
            for record in records:
                all_records.append((user[1], record[0], record[1], record[2]))  # user name, date, result, game_id

    if all_records:
        # データをDataFrameに変換
        df = pd.DataFrame(all_records, columns=["ユーザー", "日付", "収支", "ゲームID"])
        df["日付"] = pd.to_datetime(df["日付"])  # 日付をDatetime型に変換
        df = df.sort_values(["ユーザー", "日付"])  # ユーザーごとに並び替え

        # 横軸が「日付」の場合
        if axis_option == "日付":
            # 同じ日の収支を合計
            df_grouped = df.groupby(["ユーザー", "日付"]).agg({"収支": "sum"}).reset_index()

            # トータル収支の計算
            total_profit = df_grouped.groupby("ユーザー")["収支"].sum().reset_index()
            total_profit = total_profit.rename(columns={"収支": "トータル収支"})

            # 折れ線グラフ作成
            st.subheader("全プレイヤーの収支折れ線グラフ（横軸: 日付）")
            fig, ax = plt.subplots(figsize=(12, 6))

            for user in df_grouped["ユーザー"].unique():
                user_data = df_grouped[df_grouped["ユーザー"] == user]
                ax.plot(user_data["日付"], user_data["収支"], marker='o', linestyle='-', label=user)

            ax.set_title("全プレイヤーの収支比較（横軸: 日付）", fontsize=16)
            ax.set_xlabel("日付", fontsize=12)
            ax.set_ylabel("収支", fontsize=12)
            ax.legend(title="ユーザー")
            plt.grid()
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # トータル収支を表示
            st.subheader("ユーザーごとのトータル収支")
            st.table(total_profit)

        # 横軸が「ゲームID」の場合
        elif axis_option == "ゲームID":
            # ゲームごとの収支を合計
            df_grouped = df.groupby(["ユーザー", "ゲームID"]).agg({"収支": "sum"}).reset_index()

            # トータル収支の計算
            total_profit = df_grouped.groupby("ユーザー")["収支"].sum().reset_index()
            total_profit = total_profit.rename(columns={"収支": "トータル収支"})

            # 折れ線グラフ作成
            st.subheader("全プレイヤーの収支折れ線グラフ（横軸: ゲームID）")
            fig, ax = plt.subplots(figsize=(12, 6))

            for user in df_grouped["ユーザー"].unique():
                user_data = df_grouped[df_grouped["ユーザー"] == user]
                ax.plot(user_data["ゲームID"], user_data["収支"], marker='o', linestyle='-', label=user)

            ax.set_title("全プレイヤーの収支比較（横軸: ゲームID）", fontsize=16)
            ax.set_xlabel("ゲームID", fontsize=12)
            ax.set_ylabel("収支", fontsize=12)
            ax.legend(title="ユーザー")
            plt.grid()
            st.pyplot(fig)

            # トータル収支を表示
            st.subheader("ユーザーごとのトータル収支")
            st.table(total_profit)

    else:
        st.info("戦績が登録されていません。")
else:
    st.error("まずはユーザーを登録してください。")
