import streamlit as st
import pandas as pd
import json
import os

DB_FILE = "bets.json"

# 데이터 불러오기 함수
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 데이터 저장하기 함수
def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 초기 데이터 로드
betting_data = load_data()
teams = ["브라질", "프랑스", "아르헨티나", "잉글랜드", "스페인"]

st.title("🏆 시사회 2026 월드컵 우승팀 배팅 시스템")
st.markdown("---")

# 1. 배팅 입력 폼
st.subheader("🎲 내 배팅 참여 / 수정 / 삭제")
col1, col2, col3 = st.columns(3)

with col1:
    user_name = st.text_input("이름 입력", value="").strip()

# 입력된 이름이 기존에 배팅했는지 확인
existing_bet = next((b for b in betting_data if b["name"] == user_name), None) if user_name else None

with col2:
    default_team_idx = teams.index(existing_bet["team"]) if existing_bet else 0
    selected_team = st.selectbox("우승 예측팀", teams, index=default_team_idx)
with col3:
    default_amount = int(existing_bet["amount"]) if existing_bet else 10000
    bet_amount = st.number_input("배팅 금액 (원)", min_value=10000, step=10000, value=default_amount)

# 기존 배팅 유무에 따른 안내 메시지 및 버튼 처리
if existing_bet:
    st.caption(f"💡 **{user_name}**님은 현재 **{existing_bet['team']}**에 **{existing_bet['amount']:,}원** 배팅되어 있습니다.")
    
    # 수정 버튼과 삭제 버튼을 나란히 배치
    btn_col1, btn_col2 = st.columns([1, 1])
    
    with btn_col1:
        if st.button("⚡ 배팅 수정하기", use_container_width=True):
            betting_data = [b for b in betting_data if b["name"] != user_name]
            betting_data.append({"name": user_name, "team": selected_team, "amount": bet_amount})
            save_data(betting_data)
            st.success(f"[{user_name}]님의 배팅 정보가 수정되었습니다!")
            st.rerun()
            
    with btn_col2:
        if st.button("❌ 배팅 취소(삭제)", use_container_width=True):
            betting_data = [b for b in betting_data if b["name"] != user_name]
            save_data(betting_data)
            st.warning(f"[{user_name}]님의 배팅 내역이 완전히 삭제되었습니다.")
            st.rerun()
else:
    if st.button("🎲 배팅 제출하기"):
        if not user_name:
            st.error("이름을 입력해주세요!")
        else:
            betting_data.append({"name": user_name, "team": selected_team, "amount": bet_amount})
            save_data(betting_data)
            st.success(f"[{user_name}]님 {selected_team}에 {bet_amount:,}원 배팅 완료!")
            st.rerun()

st.markdown("---")

# 2. 배팅 현황판
st.subheader("📊 현재 배팅 현황")
if betting_data:
    df = pd.DataFrame(betting_data)
    total_pool = df["amount"].sum()
    st.metric(label="💵 총 누적 상금 (판돈)", value=f"{total_pool:,} 원")
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    
    # 3. 우승 시 배당금 계산 시뮬레이터
    st.subheader("🧮 우승 시 배당금 예측 시뮬레이터")
    final_winner = st.selectbox("우승팀을 가정해보세요", teams)
    winner_total_bet = df[df["team"] == final_winner]["amount"].sum()
    
    if winner_total_bet == 0:
        st.warning(f"현재 {final_winner}에 배팅한 사람이 없습니다.")
    else:
        st.write(f"**{final_winner}** 우승 시 예상 수령액:")
        for item in betting_data:
            if item["team"] == final_winner:
                share = total_pool * (item["amount"] / winner_total_bet)
                st.write(f"- **{item['name']}**: {share:,.0f} 원 (수익률: {share/item['amount']*100:.1f}%)")
else:
    st.info("아직 배팅 참여자가 없습니다. 첫 배팅을 시작해보세요!")