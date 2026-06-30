import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 파일 저장 경로 설정
DATA_FILE = "betting_results.csv"

# 페이지 제목 설정
st.title("🏆 시사회 2026 월드컵 우승팀 배팅")

# 보내주신 대진표 기준 실제 진출국 목록 (총 26개국)
teams_32 = [
    "남아프리카 공화국", "캐나다", "네덜란드", "모로코", "독일", "파라과이", 
    "프랑스", "스웨덴", "스페인", "오스트리아", "포르투갈", "크로아티아", 
    "벨기에", "세네갈", "미국", "보스니아 헤르체고비나", "브라질", "일본", 
    "코트디부아르", "노르웨이", "멕시코", "에콰도르", "잉글랜드", "콩고민주공화국", 
    "호주", "이집트","아르헨티나",카보베르데","스위스","알제리","콜롬비아","가나"
]
teams_32.sort()

# 파일 읽기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "배팅 금액" in df.columns:
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
            new_data = pd.DataFrame([{"이름": name.strip(), "예측 우승팀": selected_team, "배팅 금액": amount}])
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
                    df_data.loc[df_data["이름"] == edit_name.strip(), ["예측 우승팀", "배팅 금액"]] = [new_selected_team, new_amount]
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
    st.metric(label="💰 총 누적 배팅 금액", value=f"{total_pool:,} 원")
    
    df_display = df_data.copy()
    df_display["배팅 금액"] = df_display["배팅 금액"].map('{:,}원'.format)
    st.dataframe(df_display, use_container_width=True)
    
    st.subheader("📈 실시간 팀별 배당률 및 예측 상금")
    
    # 팀별 총 배팅액 계산
    team_stats = df_data.groupby("예측 우승팀")["배팅 금액"].sum().reset_index()
    team_stats.columns = ["팀명", "팀별 총 배팅액"]
    
    # 투표수 계산
    team_counts = df_data["예측 우승팀"].value_counts().reset_index()
    team_counts.columns = ["팀명", "투표수"]
    team_stats = pd.merge(team_stats, team_counts, on="팀명")
    
    # 배당률 계산
    team_stats["실시간 배당률"] = (total_pool / team_stats["팀별 총 배팅액"]).round(2)
    
    # 💡 [추가] 1인당 배당금 계산 (내가 건 금액 기준 배당액을 보여주기 위해 표에는 배당률 형식 적용 후 하단 안내)
    # 각자 배팅한 금액이 다르므로, 표에는 기본 배당률을 제공하고 사용자가 직관적으로 알 수 있게 포맷팅합니다.
    team_stats["1인당 배팅당 환급금"] = team_stats["실시간 배당률"].map('{:.2f}배 수령'.format)
    team_stats["실시간 배당률"] = team_stats["실시간 배당률"].map('{:.2f}배'.format)
    
    team_stats["팀별 총 배팅액"] = team_stats["팀별 총 배팅액"].map('{:,}원'.format)
    team_stats = team_stats.sort_values(by="투표수", ascending=False).reset_index(drop=True)
    
    # 표 컬럼 순서 변경하여 출력
    team_stats = team_stats