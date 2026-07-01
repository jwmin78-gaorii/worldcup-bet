import streamlit as st
import pandas as pd
import requests

# 새로 발급받으신 주소를 여기에 넣으세요
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz9oBHLzdF3jR1_iQwFIRLs87Hde8ba_r6khsQEQmMHGULCuq15Bja6k9V9slgQb26Sug/exec"

teams_32 = sorted(["남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라과이", "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", "호주", "이집트", "아르헨티나", "카보베르데", "스위스", "알제리", "콜롬비아", "가나"])

def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            df["배팅 금액"] = pd.to_numeric(df["배팅 금액"])
            return df
    except: 
        pass
    return pd.DataFrame(columns=["이름", "예측 우승팀", "배팅 금액"])

st.title("🏆 시사회 2026 월드컵 우승팀 배팅")
tab1, tab2 = st.tabs(["🎲 배팅 참여하기", "🛠️ 내 배팅 수정/취소"])

with tab1:
    name = st.text_input("당신의 이름을 입력하세요:")
    selected_team = st.selectbox("우승할 것 같은 팀을 선택하세요:", teams_32)
    amount = st.number_input("배팅할 금액 (10,000 ~ 50,000 원):", min_value=10000, max_value=50000, step=5000)

    if st.button("배팅 제출하기"):
        df = get_data()
        if not name: 
            st.error("이름을 입력해 주세요!")
        elif name in df["이름"].values: 
            st.error("이미 배팅하셨습니다.")
        else:
            requests.post(WEB_APP_URL, json={"action": "add", "name": name, "team": selected_team, "amount": amount})
            st.success("배팅 완료! 새로고침하세요.")
            st.rerun()

with tab2:
    edit_name = st.text_input("수정/취소할 이름을 입력하세요:")
    df = get_data()
    if edit_name in df["이름"].values:
        row = df[df["이름"] == edit_name].iloc[0]
        st.info(f"현재: {row['예측 우승팀']}에 {row['배팅 금액']:,}원")
        new_team = st.selectbox("새로운 팀 선택:", teams_32, index=teams_32.index(row['예측 우승팀']))
        new_amount = st.number_input("새로운 금액 (10,000 ~ 50,000 원):", min_value=10000, max_value=50000, value=int(row['배팅 금액']), step=5000)
        
        c1, c2 = st.columns(2)
        if c1.button("✏️ 수정"):
            requests.post(WEB_APP_URL, json={"action": "update", "name": edit_name, "team": new_team, "amount": int(new_amount)})
            st.success("수정 완료!")
            st.rerun()
        if c2.button("❌ 삭제"):
            requests.post(WEB_APP_URL, json={"action": "delete", "name": edit_name})
            st.success("삭제 완료!")
            st.rerun()

st.subheader("📊 현재 배팅 현황")
df = get_data()
if not df.empty:
    total = df["배팅 금액"].sum()
    st.metric("총 누적 판돈", f"{total:,} 원")
    
    team_sums = df.groupby("예측 우승팀")["배팅 금액"].sum()
    def calc_prize(r):
        team_total = team_sums[r["예측 우승팀"]]
        return int((total / team_total) * r["배팅 금액"]) if team_total > 0 else 0
    
    df["적중 시 예상 상금"] = df.apply(calc_prize, axis=1)
    
    d = df.copy()
    d["배팅 금액"] = d["배팅 금액"].map('{:,}원'.format)
    d["적중 시 예상 상금"] = d["적중 시 예상 상금"].map('{:,}원'.format)
    st.dataframe(d, use_container_width=True)
else:
    st.info("데이터가 없습니다.")