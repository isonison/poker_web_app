import streamlit as st

def calculate_total_points(chip_counts, chip_values):
    return sum(count * value for count, value in zip(chip_counts, chip_values))

# Streamlitアプリ
st.title("ポーカーツール")
st.write("ゲーム終了時のチップ合計点数を簡単に計算します。")

# チップの点数
chip_values = [1, 5, 10, 25, 100, 500, 1000]

st.header("プレイヤーのチップ計算")
st.write("各チップの枚数を入力してください：")

# チップの枚数を入力
chip_counts = []
for value in chip_values:
    count = st.number_input(f"{value}点チップの枚数", min_value=0, value=0, step=1)
    chip_counts.append(count)

# 合計点数を計算
if st.button("合計点数を計算"):
    total_points = calculate_total_points(chip_counts, chip_values)
    st.success(f"このプレイヤーの合計点数: {total_points} 点")

st.header("全プレイヤーの点数計算")
st.write("他のプレイヤーの合計点数を入力してください：")

# 他のプレイヤーの点数を入力
num_players = st.number_input("プレイヤー人数（このプレイヤーを含む）", min_value=1, value=1, step=1)
total_scores = []

for i in range(num_players):
    score = st.number_input(f"プレイヤー {i + 1} の合計点数", min_value=0, value=0, step=1)
    total_scores.append(score)

if st.button("全プレイヤーの合計点数を計算"):
    total_score_sum = sum(total_scores)
    st.success(f"全プレイヤーの合計点数: {total_score_sum} 点")
