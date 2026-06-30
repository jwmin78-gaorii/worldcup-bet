import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 파일 저장 경로 설정
DATA_FILE = "betting_results.csv"

# 페이지 제목 설정
st.title("🏆 시사회 2026 월드컵 우승팀 배팅")

# 32강 최종 완성국 목록
teams_32 = [
    "남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라과이", 
    "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", 
    "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", 
    "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", 
    "호주", "이집트", "아르헨티나", "카보베르데", "스위스", "알제리", 
    "콜롬비아", "가나"
]
teams_32.sort()

# 파일 읽기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "배팅 금액" in df.columns:
                df["배팅 금액"] = df["배팅 금액"].astype(str).str.replace("원", "").str.replace(",", "")
                df["배팅 금액"] = pd.to_numeric(df["배팅 금액"], errors='coerce').fillna(10000).astype(int)
                return df
        except:
            pass
    return pd.DataFrame(columns=["이름", "예측 우승팀", "배팅 금액"])

df_data = load_data()

st.markdown("---")
tab1, tab2 = st.tabs(["🎲 배팅 참여하기", "🛠️ 내 배팅 수정/취소"])

with tab1:
    name = st.text_input("당신의 이름을 입력하세요:", placeholder="예: 홍길동", key="insert_name")
    selected_team = st.selectbox("우승할 것 같은 팀을 선택하세요:", teams_32, key="insert_team")
    
    # 💡 배팅 금액 입력란에 가이드 문구 명시
    amount = st.number_input(
        "배팅할 금액을 입력하세요 (1만 ~ 5만 원 사이):", 
        min_value=10000, 
        max_value=50000, 
        value=10000, 
        step=5000, 
        key="insert_amount",
        help="최소 10,000원에서 최대 50,000원까지 배팅 가능합니다."
    )

    if st.button("배팅 제출하기", use_container_width=True):
        if name.strip() == "":
            st.error("이름을 입력해 주세요!")
        elif name.strip() in df_data["이름"].values:
            st.error("이미 배팅하셨습니다. '내 배팅 수정/취소' 탭을 이용하세요.")
        else:
            new_data = pd.DataFrame([{"이름": name.strip(), "예측 우승팀": selected_team, "배팅 금액": int(amount)}])
            df_data = pd.concat([df_data, new_data], ignore_index=True)
            df_data.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
            st.success(f"🎉 {name}님의 배팅 완료! ({selected_team}에 {amount:,}원)")
            st.rerun()

with tab2:
    edit_name = st.text_input("수정/취소할 이름을 입력하세요:", placeholder="예: 홍길동", key="edit_name")
    
    if edit_name.strip() in df_data["이름"].values:
        user_row = df_data[df_data["이름"] == edit_name.strip()].iloc[0]
        st.info(f"📢 현재: {user_row['예측 우승팀']}에 {user_row['배팅 금액']:,}원")
        
        default_index = teams_32.index(user_row['예측 우승팀']) if user_row['예측 우승팀'] in teams_32 else 0
        new_selected_team = st.selectbox("새로운 팀 선택:", teams_32, index=default_index, key="update_team")
        
        # 수정란에도 가이드 명시
        new_amount = st.number_input(
            "새로운 금액 (1만 ~ 5만 원 사이):", 
            min_value=10000, 
            max_value=50000, 
            value=int(user_row['배팅 금액']), 
            step=5000, 
            key="update_amount"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 배팅 정보 수정", use_container_width=True):
                if datetime.now() > datetime(2026, 7, 4, 23, 59, 59):
                    st.error("⏰ 마감 기한이 지났습니다.")
                else:
                    df_data.loc[df_data["이름"] == edit_name.strip(), ["예측 우승팀", "배팅 금액"]] = [new_selected_team, int(new_amount)]
                    df_data.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                    st.success("수정 완료!")
                    st.rerun()
        with col2:
            if st.button("❌ 배팅 취소 (삭제)", use_container_width=True):
                if datetime.now() > datetime(2026, 7, 4, 23, 59, 59):
                    st.error("⏰ 마감 기한이 지났습니다.")
                else:
                    df_data = df_data[df_data["이름"] != edit_name.strip()]
                    df_data.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                    st.success("취소 완료.")
                    st.rerun()
    elif edit_name.strip() != "":
        st.warning("등록된 배팅 내역이 없습니다.")

st.markdown("---")
st.subheader("📊 현재 배팅 현황")

if not df_data.empty:
    total_pool = df_data["배팅 금액"].sum()
    st.metric(label="💰 총 누적 판돈", value=f"{total_pool:,} 원")
    
    team_total_dict = df_data.groupby("예측 우승팀")["배팅 금액"].sum().to_dict()
    df_display = df_data.copy()
    
    def calculate_personal_prize(row):
        team = row["예측 우승팀"]
        my_amount = row["배팅 금액"]
        team_total = team_total_dict.get(team, my_amount)
        return int((total_pool / team_total) * my_amount)

    df_display["적중 시 예상 상금"] = df_display.apply(calculate_personal_prize, axis=1)
    df_display["배팅 금액"] = df_display["배팅 금액"].map('{:,}원'.format)
    df_display["적중 시 예상 상금"] = df_display["적중 시 예상 상금"].map('{:,}원'.format)
    
    st.dataframe(df_display, use_container_width=True)
    
    st.subheader("📈 실시간 팀별 배당률 요약")
    team_stats = df_data.groupby("예측 우승팀")["배팅 금액"].sum().reset_index()
    team_stats.columns = ["팀명", "팀별 총 배팅액"]
    team_counts = df_data["예측 우승팀"].value_counts().reset_index()
    team_counts.columns = ["팀명", "투표수"]
    team_stats = pd.merge(team_stats, team_counts, on="팀명")
    team_stats["실시간 배당률"] = (total_pool / team_stats["팀별 총 배팅액"]).round(2).map('{:.2f}배'.format)
    team_stats["팀별 총 배팅액"] = team_stats["팀별 총 배팅액"].map('{:,}원'.format)
    team_stats = team_stats.sort_values(by="투표수", ascending=False).reset_index(drop=True)
    st.dataframe(team_stats, use_container_width=True)
else:
    st.info("아직 참여자가 없습니다. 첫 배팅을 입력해 보세요!")