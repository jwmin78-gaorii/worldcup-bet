import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 파일 저장 경로 설정
DATA_FILE = "betting_results.csv"

# 페이지 제목 설정
st.title("🏆 시사회 2026 월드컵 우승팀 배팅")

# 32강 최종 완성국 목록 (총 32개국)
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

# 가로선
st.markdown("---")

# 탭 구성 (배팅하기 / 수정 및 취소)
tab1, tab2 = st.tabs(["🎲 배팅 참여하기", "🛠️ 내 배팅 수정/취소"])

with tab1:
    name = st.text_input("당신의 이름을 입력하세요:", placeholder="예: 홍길동", key="insert_name")
    selected_team = st.selectbox("우승할 것 같은 팀을 선택하세요:", teams_32, key="insert_team")
    amount = st.number_input("배팅할 금액을 입력하세요 (원/포인트):", min_value=1000, value=10000, step=1000, key="insert_amount")

    if st.button("배팅 제출하기", use_container_width=True):
        if name.strip() == "":
            st.error("이름을 입력해 주세요!")
        elif name.strip() in df_data["이름"].values:
            st.error("이미 배팅을 하셨습니다! 수정을 원하시면 '내 배팅 수정/취소' 탭을 이용해 주세요.")
        else:
            new_data = pd.DataFrame([{"이름": name.strip(), "예측 우승팀": selected_team, "배팅 금액": int(amount)}])
            df_data = pd.concat([df_data, new_data], ignore_index=True)
            df_data.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
            st.success(f"🎉 {name}님의 배팅이 완료되었습니다! ({selected_team}에 {amount:,}원)")
            st.rerun()

with tab2:
    edit_name = st.text_input("배팅을 수정/취소할 이름을 입력하세요:", placeholder="예: 홍길동", key="edit_name")
    
    if edit_name.strip() in df_data["이름"].values:
        user_row = df_data[df_data["이름"] == edit_name.strip()].iloc[0]
        st.info(f"📢 현재 배팅 내역: **{user_row['예측 우승팀']}**에 **{user_row['배팅 금액']:,}원**")
        
        default_index = teams_32.index(user_row['예측 우승팀']) if user_row['예측 우승팀'] in teams_32 else 0
        
        new_selected_team = st.selectbox("새로운 우승 예측팀 선택:", teams_32, index=default_index, key="update_team")
        new_amount = st.number_input("새로운 배팅 금액 입력:", min_value=1000, value=int(user_row['배팅 금액']), step=1000, key="update_amount")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 배팅 정보 수정", use_container_width=True):
                if datetime.now() > datetime(2026, 7, 4, 23, 59, 59):
                    st.error("⏰ 7월 4일이 지나 배팅 수정이 불가능합니다.")
                else:
                    df_data.loc[df_data["이름"] == edit_name.strip(), ["예측 우승팀", "배팅 금액"]] = [new_selected_team, int(new_amount)]
                    df_data.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                    st.success("배팅 정보가 수정되었습니다!")
                    st.rerun()
        with col2:
            if st.button("❌ 배팅 취소 (삭제)", use_container_width=True):
                if datetime.now() > datetime(2026, 7, 4, 23, 59, 59):
                    st.error("⏰ 7월 4일이 지나 배팅 취소가 불가능합니다.")
                else:
                    df_data = df_data[df_data["이름"] != edit_name.strip()]
                    df_data.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                    st.success("배팅이 정상적으로 취소되었습니다.")
                    st.rerun()
    elif edit_name.strip() != "":
        st.warning("입력하신 이름으로 등록된 배팅 내역이 없습니다.")

st.markdown("---")

# 배팅 현황 및 실시간 배당금 계산 출력 UI
st.subheader("📊 현재 배팅 현황")

if not df_data.empty:
    total_pool = df_data["배팅 금액"].sum()
    st.metric(label="💰 총 누적 판돈 (전체 배팅 금액)", value=f"{total_pool:,} 원")
    
    # 팀별 총 판돈 사전 계산 (개인별 상금 계산용)
    team_total_dict = df_data.groupby("예측 우승팀")["배팅 금액"].sum().to_dict()
    
    # 1. 개인별 배팅 현황 표 구성 (실제 받는 예상 금액 포함)
    df_display = df_data.copy()
    
    def calculate_personal_prize(row):
        team = row["예측 우승팀"]
        my_amount = row["배팅 금액"]
        team_total = team_total_dict.get(team, my_amount)
        # 내 상금 = 총 판돈 * (내가 해당 팀에 기여한 지분율)
        # 즉, 내 상금 = 총 판돈 * (내 배팅금 / 팀 총 배팅금) -> (총 판돈 / 팀 총 배팅금) * 내 배팅금 = 배당률 * 내 배팅금
        if team_total > 0:
            return int((total_pool / team_total) * my_amount)
        return my_amount

    df_display["적중 시 예상 상금"] = df_display.apply(calculate_personal_prize, axis=1)
    
    # 포맷팅 적용
    df_display["배팅 금액"] = df_display["배팅 금액"].map('{:,}원'.format)
    df_display["적중 시 예상 상금"] = df_display["적중 시 예상 상금"].map('{:,}원'.format)
    
    st.dataframe(df_display, use_container_width=True)
    
    # 2. 팀별 실시간 요약 정보 표 구성
    st.subheader("📈 실시간 팀별 배당률 요약")
    try:
        team_stats = df_data.groupby("예측 우승팀")["배팅 금액"].sum().reset_index()
        team_stats.columns = ["팀명", "팀별 총 배팅액"]
        
        team_counts = df_data["예측 우승팀"].value_counts().reset_index()
        team_counts.columns = ["팀명", "투표수"]
        team_stats = pd.merge(team_stats, team_counts, on="팀명")
        
        team_stats["실시간 배당률"] = (total_pool / team_stats["팀별 총 배팅액"]).round(2)
        team_stats["실시간 배당률"] = team_stats["실시간 배당률"].map('{:.2f}배'.format)
        team_stats["팀별 총 배팅액"] = team_stats["팀별 총 배팅액"].map('{:,}원'.format)
        team_stats = team_stats.sort_values(by="투표수", ascending=False).reset_index(drop=True)
        
        team_result = team_stats[["팀명", "투표수", "팀별 총 배팅액", "실시간 배당률"]]
        st.dataframe(team_result, use_container_width=True)
    except Exception as e:
        st.warning("배당률 데이터를 요약하는 중입니다...")
        
    st.caption("ℹ️ 상단 표의 **[적중 시 예상 상금]**은 본인이 낸 배팅 금액의 크기에 맞춰 실시간으로 차등 계산된 금액입니다.")
else:
    st.info("아직 배팅에 참여한 사람이 없습니다. 첫 배팅을 입력해 보세요!")