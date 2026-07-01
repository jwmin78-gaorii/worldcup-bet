import streamlit as st
import pandas as pd
import requests

# 구글 시트 웹 앱 URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwiIwAXyoMmkJ6sHrA7cKsWxVhEUoUlLDWHBCRtrVzzdoXH_EDnvixfO6UsjCG5MXVgmw/exec"

# 32강 팀 목록
teams_32 = sorted(["남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라가이", "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", "호주", "이집트", "아르헨티나", "카보베르데", "스위스", "알제리", "콜롬비아", "가나"])

# 배당률 예시 (상황에 맞게 조정 가능)
odds = 5.0 

st.title("🏆 2026 월드컵 우승팀 배팅")

def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        if len(data) > 1:
            return pd.DataFrame(data[1:], columns=data[0])
    except:
        pass
    return pd.DataFrame(columns=["이름", "예측 우승팀", "배팅 금액"])

tab1, tab2 = st.tabs(["🎲 배팅하기", "📊 현황판"])

with tab1:
    name = st.text_input("이름")
    team = st.selectbox("우승 예측 팀", teams_32)
    # 초기값을 0으로 설정하여 사용자가 직접 입력하게 함
    amount = st.number_input("배팅 금액 (1만 ~ 5만 원)", min_value=0, step=1000, value=0)
    
    if amount > 0:
        st.write(f"💰 예상 상금: {int(amount * odds):,}원 (배당률 {odds}배)")

    if st.button("배팅 제출"):
        # 유효성 검사 로직
        if not name:
            st.error("이름을 입력해주세요.")
        elif amount < 10000 or amount > 50000:
            st.error("배팅 금액은 10,000원에서 50,000원 사이로 입력해주세요.")
        else:
            # 데이터 전송
            payload = {"name": name, "team": team, "amount": amount}
            requests.post(WEB_APP_URL, json=payload)
            st.success(f"{name}님, {team}에 {amount:,}원 배팅 완료!")

with tab2:
    df = get_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        total_pool = df["배팅 금액"].sum()
        st.info(f"총 배팅액: {total_pool:,}원")
    else:
        st.write("아직 배팅 기록이 없습니다.")