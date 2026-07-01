import streamlit as st
import pandas as pd
import requests

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwiIwAXyoMmkJ6sHrA7cKsWxVhEUoUlLDWHBCRtrVzzdoXH_EDnvixfO6UsjCG5MXVgmw/exec"

teams_32 = sorted(["남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라과이", "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", "호주", "이집트", "아르헨티나", "카보베르데", "스위스", "알제리", "콜롬비아", "가나"])

def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            df["배팅 금액"] = pd.to_numeric(df["배팅 금액"])
            return df
    except: pass
    return pd.DataFrame(columns=["이름", "예측 우승팀", "배팅 금액"])

st.title("🏆 2026 월드컵 우승팀 배팅")
tab1, tab2, tab3 = st.tabs(["🎲 배팅하기", "📊 현황판", "✏️ 삭제"])

with tab1:
    name = st.text_input("이름")
    team = st.selectbox("우승 예측 팀", teams_32)
    amount = st.number_input("배팅 금액 (10,000 ~ 50,000 원)", min_value=0, step=1000, value=0)
    if st.button("배팅 제출"):
        if not name: st.error("이름을 입력해주세요.")
        elif amount < 10000 or amount > 50000: st.error("10,000 ~ 50,000원 사이로 입력하세요.")
        else:
            requests.post(WEB_APP_URL, json={"action": "add", "name": name, "team": team, "amount": amount})
            st.success("배팅 완료! 새로고침하세요.")

with tab2:
    df = get_data()
    if not df.empty:
        total_pool = df["배팅 금액"].sum()
        summary = df.groupby("예측 우승팀").agg({"이름": "count", "배팅 금액": "sum"}).reset_index()
        summary.columns = ["팀명", "투표수", "팀별 총 배팅액"]
        summary["실시간 배당률"] = (total_pool / summary["팀별 총 배팅액"]).round(2).apply(lambda x: f"{x:.2f}배")
        
        df = df.merge(summary[["팀명", "실시간 배당률"]], left_on="예측 우승팀", right_on="팀명")
        df["적중 시 예상 상금"] = (df["배팅 금액"] * df["실시간 배당률"].str.replace("배", "").astype(float)).astype(int)
        
        st.metric("전체 배팅 금액", f"{total_pool:,}원")
        display_df = df[["이름", "예측 우승팀", "배팅 금액", "적중 시 예상 상금"]].copy()
        display_df["배팅 금액"] = display_df["배팅 금액"].apply(lambda x: f"{x:,}원")
        display_df["적중 시 예상 상금"] = display_df["적중 시 예상 상금"].apply(lambda x: f"{x:,}원")
        st.dataframe(display_df, use_container_width=True)
        st.dataframe(summary, use_container_width=True)

with tab3:
    del_name = st.text_input("삭제할 이름 입력")
    if st.button("내 기록 삭제"):
        requests.post(WEB_APP_URL, json={"action": "delete", "name": del_name})
        st.warning(f"{del_name}님의 기록이 삭제되었습니다. 새로고침하세요.")