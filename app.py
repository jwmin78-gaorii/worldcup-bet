import streamlit as st
import pandas as pd
import os

# 파일 저장 경로 설정
DATA_FILE = "betting_results.csv"

# 페이지 제목 설정
st.title("🏆 시사회 2026 월드컵 우승팀 배팅")

# 32강 진출국 목록
teams_32 = [
    "남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라과이", 
    "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", 
    "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", 
    "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", 
    "호주", "이집트", "아르헨티나", "이탈리아", "우루과이", "대한민국", "스위스", "덴마크"
]
teams_32.sort()

# 파일 읽기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["이름", "예측 우승팀", "배팅 금액"])

df_data = load_data()

# 가로선
st.markdown("---")

# 사용자 입력 UI
st.subheader("🎲 배팅 참여하기")
name = st.text_input("당신의 이름을 입력하세요:", placeholder="예: 홍길동")
selected_team = st.selectbox("우승할 것 같은 팀을 선택하세요:", teams_32)
amount = st.number_input("배팅할 금액을 입력하세요 (원/포인트):", min_value=1000, value=10000, step=1000)

if st.button("배팅 제출하기", use_container_width=True):
    if name.strip() == "":
        st.error("이름을 입력해 주세요!")
    else:
        new_data = pd.DataFrame([{"이름": name, "예측 우승팀": selected_team, "배팅 금액": amount}])
        df_data = pd.concat([df_data, new_data], ignore_index=True)
        df_data.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        st.success(f"🎉 {name}님의 배팅이 완료되었습니다! ({selected_team}에 {amount:,}원)")
        st.rerun()

st.markdown("---")

# 배팅 현황 및 실시간 배당금 계산 출력 UI
st.subheader("📊 현재 배팅 현황")

if not df_data.empty:
    # 전체 총 배팅 금액 계산
    total_pool = df_data["배팅 금액"].sum()
    st.metric(label="💰 총 누적 배팅 금액", value=f"{total_pool:,} 원")
    
    # 개인별 배팅 내역 출력 (금액 쉼표 포맷팅)
    df_display = df_data.copy()
    df_display["배팅 금액"] = df_display["배팅 금액"].map('{:,}원'.format)
    st.dataframe(df_display, use_container_width=True)
    
    # 팀별 통계 및 실시간 배당금 계산
    st.subheader("📈 실시간 팀별 배당률 및 예측 배당금")
    
    # 팀별 총 배팅액 계산
    team_stats = df_data.groupby("예측 우승팀")["배팅 금액"].sum().reset_index()
    team_stats.columns = ["팀명", "팀별 총 배팅액"]
    
    # 투표수(인원수) 추가
    team_counts = df_data["예측 우승팀"].value_counts().reset_index()
    team_counts.columns = ["팀명", "투표수"]
    team_stats = pd.merge(team_stats, team_counts, on="팀명")
    
    # 배당률 계산 (총 배팅액 / 팀별 총 배팅액)
    team_stats["실시간 배당률"] = (total_pool / team_stats["팀별 총 배팅액"]).round(2)
    team_stats["실시간 배당률"] = team_stats["실시간 배당률"].map('{:.2f}배'.format)
    
    # 표 표시용 금액 포맷팅
    team_stats["팀별 총 배팅액"] = team_stats["팀별 총 배팅액"].map('{:,}원'.format)
    
    # 투표수 많은 순으로 정렬하여 출력
    team_stats = team_stats.sort_values(by="투표수", ascending=False).reset_index(drop=True)
    st.table(team_stats)
    
    st.caption("ℹ️ 배당률과 배당금은 다른 사람들이 배팅을 추가할 때마다 실시간으로 변동됩니다.")
else:
    st.info("아직 배팅에 참여한 사람이 없습니다.")