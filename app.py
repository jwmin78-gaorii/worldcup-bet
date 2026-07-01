import streamlit as st
import pandas as pd
import requests

# 전달해주신 최신 배포 주소를 적용했습니다.
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw0HiUT3_r_vqmWqRqNtcfidctUeSdz4ERrNF4QhQAuN8jadeAqr6tWsSP2Om64evf1/exec"

teams_32 = sorted(["남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라과이", "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", "호주", "이집트", "아르헨티나", "카보베르데", "스위스", "알제리", "콜롬비아", "가나"])

@st.cache_data(ttl=0)
def get_data():
    try:
        response = requests.get(WEB_APP_URL)
        if response.status_code == 200:
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
    name = st.text_input("이름을 입력하세요:")
    team = st.selectbox("우승팀 선택:", teams_32)
    amount = st.number_input("배팅 금액 (10,000 ~ 50,000):", min_value=10000, max_value=50000, step=5000)

    if st.button("배팅 제출"):
        if not name:
            st.error("이름을 입력해 주세요.")
        else:
            requests.post(WEB_APP_URL, json={"action": "add", "name": name, "team": team, "amount": int(amount)})
            st.success("배팅 완료! 새로고침하세요.")
            st.cache_data.clear()
            st.rerun()

with tab2:
    edit_name = st.text_input("수정/삭제할 이름:")
    df = get_data()
    if edit_name in df["이름"].values:
        user_row = df[df["이름"] == edit_name].iloc[0]
        st.info(f"현재: {user_row['예측 우승팀']} / {user_row['배팅 금액']:,}원")
        
        new_team = st.selectbox("새 팀 선택:", teams_32, index=teams_32.index(user_row['예측 우승팀']))
        new_amount = st.number_input("새 금액:", min_value=10000, max_value=50000, value=int(user_row['배팅 금액']), step=5000)
        
        c1, c2 = st.columns(2)
        if c1.button("✏️ 수정 적용"):
            requests.post(WEB_APP_URL, json={"action": "update", "name": edit_name, "team": new_team, "amount": int(new_amount)})
            st.success("수정 완료!")
            st.cache_data.clear()
            st.rerun()
        if c2.button("❌ 삭제"):
            requests.post(WEB_APP_URL, json={"action": "delete", "name": edit_name})
            st.success("삭제 완료!")
            st.cache_data.clear()
            st.rerun()
    elif edit_name:
        st.warning("등록되지 않은 이름입니다.")

st.subheader("📊 배팅 현황")
df = get_data()
if not df.empty:
    st.metric("총 판돈", f"{df['배팅 금액'].sum():,}원")
    st.dataframe(df, use_container_width=True)
else:
    st.info("참여자가 없습니다.")