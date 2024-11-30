import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import sqlite3

# SQLite データベースの初期化
# SQLite データベースの初期化
def init_db():
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()

    # ユーザーテーブル作成
    c.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 戦績テーブル作成（game_idカラムを追加）
    # 戦績テーブル作成（game_idカラムを追加）
    c.execute("""
    CREATE TABLE IF NOT EXISTS Records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,  -- game_idカラムを追加
        date DATE NOT NULL,
        result REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(id),
        FOREIGN KEY (game_id) REFERENCES game(game_id)
    )
""")


    # ゲームテーブル作成
    c.execute("""
        CREATE TABLE IF NOT EXISTS game (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            rate REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()

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

            ax.set_title("ALL USER RESULTS(BY: DATE)", fontsize=16)
            ax.set_xlabel("DATE", fontsize=12)
            ax.set_ylabel("RESULTS", fontsize=12)
            ax.legend(title="USER")
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

            ax.set_title("ALL USER RESULTS(BY: GAME ID)", fontsize=16)
            ax.set_xlabel("GAME ID", fontsize=12)
            ax.set_ylabel("RESULTS", fontsize=12)
            ax.legend(title="USER")
            plt.grid()
            st.pyplot(fig)

            # トータル収支を表示
            st.subheader("ユーザーごとのトータル収支")
            st.table(total_profit)

    else:
        st.info("戦績が登録されていません。")
else:
    st.error("まずはユーザーを登録してください。")
