import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# データベース操作用の関数
def execute_query(query, params=()):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=()):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results


# Streamlitアプリ
st.title("ポーカーツール: ユーザー戦績管理")

# タブ
tab1, tab2 = st.tabs(["戦績登録", "戦績確認"])

# タブ1: 戦績登録
with tab1:
    st.header("戦績を登録する")
    
    # ユーザー選択
    user_options = fetch_query("SELECT id, name FROM Users")
    if user_options:
        selected_user = st.selectbox("ユーザーを選択してください", user_options, format_func=lambda x: x[1], key="user_selectbox")
        
        # ゲーム選択
        games = fetch_query("SELECT game_id, date FROM game")
        game_options = [(game[0], game[1]) for game in games]
        
        if game_options:
            selected_game = st.selectbox("ゲームを選択してください", game_options, format_func=lambda x: f"ゲームID: {x[0]} - 日付: {x[1]}", key="game_selectbox")
            
            # 日付と収支の入力
            date = st.date_input("日付を選択してください", datetime.now().date())
            result = st.number_input("収支を入力してください", value=0.0, step=0.1)
            
            # 戦績登録
            if st.button("戦績を登録する"):
                execute_query("INSERT INTO Records (user_id, game_id, date, result) VALUES (?, ?, ?, ?)",
                            (selected_user[0], selected_game[0], date, result))
                st.success(f"戦績を登録しました: ユーザー: {selected_user[1]}, ゲームID: {selected_game[0]}, 日付: {date}, 収支: {result}")

        else:
            st.error("登録されたゲームがありません。")
    else:
        st.error("まずはユーザーを登録してください。")

# タブ2: 戦績確認
with tab2:
    st.header("戦績確認")

    # 横軸の選択肢
    axis_option = st.radio("横軸を選択してください", ("日付", "ゲームID"))

    # ユーザー選択
    user_options = fetch_query("SELECT id, name FROM Users")
    if user_options:
        selected_user = st.selectbox("ユーザーを選択してください", user_options, format_func=lambda x: x[1], key="user_select_for_graph")
        records = fetch_query("SELECT id, date, result, game_id FROM Records WHERE user_id = ?", (selected_user[0],))

        if records:
            # データをDataFrameに変換
            df = pd.DataFrame(records, columns=["ID", "日付", "収支", "ゲームID"])
            df["日付"] = pd.to_datetime(df["日付"])  # 日付をDatetime型に変換
            df = df.sort_values(["日付"])  # 日付順に並び替え

            # 横軸が「日付」の場合
            if axis_option == "日付":
                # 同じ日の収支を合計
                df_grouped = df.groupby(["日付"]).agg({"収支": "sum"}).reset_index()

                # トータル収支を計算
                total_profit = df_grouped["収支"].sum()

                # グラフ表示
                st.subheader(f"{selected_user[1]} の収支合計（横軸: 日付）")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(df_grouped["日付"], df_grouped["収支"], marker='o', color="skyblue", linestyle='-', label="収支")
                ax.set_title(f"{selected_user[1]} Total Results(By:Date)", fontsize=16)
                ax.set_xlabel("Date", fontsize=12)
                ax.set_ylabel("Income", fontsize=12)
                ax.legend()
                plt.grid()
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # トータル収支を表示
                st.subheader(f"トータル収支: {total_profit:.2f}")

            # 横軸が「ゲームID」の場合
            elif axis_option == "ゲームID":
                # ゲームごとの収支
                df_grouped = df.groupby(["ゲームID"]).agg({"収支": "sum"}).reset_index()

                # トータル収支を計算
                total_profit = df_grouped["収支"].sum()

                # グラフ表示
                st.subheader(f"{selected_user[1]} の収支合計（横軸: ゲームID）")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(df_grouped["ゲームID"], df_grouped["収支"], marker='o', color="skyblue", linestyle='-', label="収支")
                ax.set_title(f"{selected_user[1]} Total Results(By:GameID)", fontsize=16)
                ax.set_xlabel("ゲームID", fontsize=12)
                ax.set_ylabel("収支", fontsize=12)
                ax.legend()
                plt.grid()
                st.pyplot(fig)

                # トータル収支を表示
                st.subheader(f"トータル収支: {total_profit:.2f}")

        else:
            st.info("このユーザーの戦績はまだありません。")
    else:
        st.error("まずはユーザーを登録してください。")
