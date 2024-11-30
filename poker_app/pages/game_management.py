import sqlite3
import streamlit as st
from datetime import datetime

# データベース操作用関数
def fetch_query(query, params=()):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results

def insert_game(date, rate):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    # game_idを指定せず、SQLiteが自動で採番するように修正
    c.execute("INSERT INTO game (date, rate) VALUES (?, ?)", (date, rate))
    conn.commit()
    conn.close()

def update_game(game_id, new_date, new_rate):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute("UPDATE game SET date = ?, rate = ? WHERE game_id = ?", (new_date, new_rate, game_id))
    conn.commit()
    conn.close()

def delete_game(game_id):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute("DELETE FROM game WHERE game_id = ?", (game_id,))
    conn.commit()
    conn.close()

# ゲーム登録ページ
st.title("ゲーム登録")

# ゲーム登録フォーム
game_date = st.date_input("ゲームの日付")
game_rate = st.number_input("レート（100bbあたりの円）", min_value=0.0, step=0.1)

if st.button("ゲームを登録"):
    if game_date and game_rate > 0:
        insert_game(game_date, game_rate)
        st.success("ゲームが登録されました！")
    else:
        st.error("すべてのフィールドに入力してください。")

# 登録済みゲームの表示と編集・削除
st.header("登録済みゲームの管理")

# 登録されたゲームを取得
games = fetch_query("SELECT game_id, date, rate FROM game")
if games:
    # ゲームを選択
    selected_game_id = st.selectbox("編集・削除するゲームを選択", [f"ゲームID: {game[0]} - 日付: {game[1]} - レート: {game[2]}" for game in games])

    # 選択されたゲームIDを取得
    selected_game_id = int(selected_game_id.split(" ")[1])

    # 編集フォーム
    st.subheader("ゲーム編集")
    selected_game = next(game for game in games if game[0] == selected_game_id)

    # selected_game[1]（日付）をdatetime型に変換
    selected_game_date = datetime.strptime(selected_game[1], "%Y-%m-%d").date()

    new_game_date = st.date_input("新しいゲームの日付", selected_game_date)
    
    # ここで、rateをfloat型で設定する
    new_game_rate = st.number_input("新しいレート（100bbあたりの円）", min_value=0.0, value=float(selected_game[2]), step=0.1)

    if st.button("ゲームを更新"):
        update_game(selected_game_id, new_game_date, new_game_rate)
        st.success(f"ゲームID: {selected_game_id} が更新されました！")

    # 削除ボタン
    if st.button("ゲームを削除"):
        delete_game(selected_game_id)
        st.success(f"ゲームID: {selected_game_id} が削除されました！")
else:
    st.info("登録されているゲームはありません。")
