import streamlit as st
import pandas as pd
import requests

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw0HiUT3_r_vqmWqRqNtcfidctUeSdz4ERrNF4QhQAuN8jadeAqr6tWsSP2Om64evf1/exec"

teams_32 = sorted(["남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라과이", "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", "호주", "이집트", "아르헨티나", "카보베르데", "스위스", "알제리", "콜롬비아", "가나"])

def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame()
    except: pass
    return pd.DataFrame(columns=["이름", "예측 우승팀", "배팅 금액"])

st.title("🏆 시사회 2026 월드컵 우승팀 배팅")

tab1, tab2 = st.tabs(["🎲 배팅 참여하기", "🛠️ 내 배팅 수정/취소"])

with tab1:
    # 키를 지정하여 스트림릿이 위젯을 추적하게 함
    n_in = st.text_input("이름", key="name_key")
    t_in = st.selectbox("우승팀", teams_32, key="team_key")
    a_in = st.number_input("배팅 금액 (10,000 ~ 50,000)", min_value=0, max_value=100000, value=10000, step=5000, key="amt_key")

    if st.button("배팅 제출하기"):
        # 1. 제출 버튼 누른 직후 '현재 입력값(a_in)'을 즉시 검사
        if not n_in:
            st.error("이름을 입력하세요.")
        elif a_in < 10000 or a_in > 50000:
            # 2. 범위를 벗어나면 여기서 딱 멈춤 (아무런 서버 요청 없음)
            st.error(f"입력하신 {a_in:,}원은 배팅 가능 범위(1~5만원)를 벗어났습니다!")
        else:
            # 3. 정상 범위일 때만 서버로 전송
            requests.post(WEB_APP_URL, json={"action": "add", "name": n_in, "team": t_in, "amount": int(a_in)})
            st.success("배팅 완료!")
            st.rerun()

with tab2:
    edit_name = st.text_input("조회할 이름", key="edit_key")
    df = get_data()
    if not df.empty and edit_name in df["이름"].values:
        row = df[df["이름"] == edit_name].iloc[0]
        new_team = st.selectbox("팀 수정", teams_32, index=teams_32.index(row['예측 우승팀']), key="team_up")
        new_amount = st.number_input("금액 수정", min_value=10000, max_value=50000, value=int(row['배팅 금액']), step=5000, key="amt_up")
        
        c1, c2 = st.columns(2)
        if c1.button("✏️ 수정 적용"):
            requests.post(WEB_APP_URL, json={"action": "update", "name": edit_name, "team": new_team, "amount": int(new_amount)})
            st.rerun()
        if c2.button("❌ 삭제"):
            requests.post(WEB_APP_URL, json={"action": "delete", "name": edit_name})
            st.rerun()

st.subheader("📊 현황")
st.dataframe(get_data(), use_container_width=True)