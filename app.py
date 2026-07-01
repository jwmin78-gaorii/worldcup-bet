import streamlit as st
import pandas as pd
import requests

# 구글 시트 웹 앱 URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwiIwAXyoMmkJ6sHrA7cKsWxVhEUoUlLDWHBCRtrVzzdoXH_EDnvixfO6UsjCG5MXVgmw/exec"

# 32강 최종 완성국 목록
teams_32 = sorted([
    "남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라과이", 
    "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", 
    "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", 
    "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", 
    "호주", "이집트", "아르헨티나", "카보베르데", "스위스", "알제리", 
    "콜롬비아", "가나"
])

st.title("🏆 시사회 2026 월드컵 우승팀 배팅")

# 데이터 불러오기
def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        if len(data) > 1:
            return pd.DataFrame(data[1:], columns=data[0])
    except:
        pass
    return pd.DataFrame(columns=["이름", "예측 우승팀", "배팅 금액"])

df_data = get_data()

tab1, tab2 = st.tabs(["🎲 배팅하기", "📊 현황판"])

with tab1:
    name = st.text_input("이름")
    team = st.selectbox("우승 예측 팀", teams_32)
    amount = st.number_input("배팅 금액 (1만 ~ 5만 원)", min_value=10000, max_value=50000, step=5000)
    
    if st.button("배팅 제출"):
        if not name:
            st.error("이름을 입력하세요.")
        else:
            requests.post(WEB_APP_URL, json={"name": name, "team": team, "amount": amount})
            st.success("배팅 완료! 페이지를 새로고침하면 현황판에 반영됩니다.")

with tab2:
    if not df_data.empty:
        st.dataframe(df_data, use_container_width=True)
    else:
        st.write("아직 배팅 기록이 없습니다.")