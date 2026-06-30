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

# 국가명 가나다순 정렬 (찾기 편하도록 정렬했습니다)
teams_32.sort()

# 가로선
st.markdown("---")

# 사용자 입력 UI
st.subheader("🎲 배팅 참여하기")
name = st.text_input("당신의 이름을 입력하세요:", placeholder="예: 홍길동")
selected_team = st.selectbox("우승할 것 같은 팀을 선택하세요:", teams_32)

if st.button("배팅 제출하기", use_container_width=True):
    if name.strip() == "":
        st.error("이름을 입력해 주세요!")
    else:
        # 기존 데이터 불러오기 또는 새로 만들기
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
        else:
            df = pd.DataFrame(columns=["이름", "예측 우승팀"])
        
        # 새로운 데이터 추가
        new_data = pd.DataFrame([{"이름": name, "예측 우승팀": selected_team}])
        df = pd.concat([df, new_data], ignore_index=True)
        
        # 저장
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        st.success(f"🎉 {name}님의 배팅({selected_team})이 완료되었습니다!")

st.markdown("---")

# 배팅 현황 출력 UI
st.subheader("📊 현재 배팅 현황")
if os.path.exists(DATA_FILE):
    df_display = pd.read_csv(DATA_FILE)
    if not df_display.empty:
        st.dataframe(df_display, use_container_width=True)
        
        # 팀별 득표수 통계
        st.subheader("📈 팀별 정배 현황 (득표수 순)")
        stats = df_display["예측 우승팀"].value_counts().reset_index()
        stats.columns = ["팀명", "투표수"]
        st.table(stats)
    else:
        st.info("아직 배팅에 참여한 사람이 없습니다.")
else:
    st.info("아직 배팅에 참여한 사람이 없습니다.")