import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="Seoul Age Population", page_icon="📊", layout="centered")
st.title("📊 서울특별시 연령별 인구 시각화 (2025년 6월 기준)")

# CSV 파일 경로
csv_file = "translated_population_by_age_total.csv"

@st.cache_data
def load_data():
    return pd.read_csv(csv_file)

# 데이터 로드
try:
    df_total = load_data()
except FileNotFoundError:
    st.error(f"❌ '{csv_file}' 파일이 존재하지 않습니다.")
    st.stop()

# 서울특별시 데이터 필터링
try:
    seoul_row = df_total[df_total["Region"].str.contains("서울")].iloc[0]
except IndexError:
    st.error("❌ '서울' 데이터를 찾을 수 없습니다.")
    st.stop()

# 연령별 컬럼 추출
age_columns = [col for col in seoul_row.index if "Age_" in col]
if not age_columns:
    st.error("❌ 연령 관련 컬럼(Age_)이 존재하지 않습니다.")
    st.stop()

# 연령 라벨과 값 추출
age_labels = [col.split("_")[-1].replace("plus", "100+") for col in age_columns]
age_values = seoul_row[age_columns].astype(str).str.replace(",", "").astype(float)

# 데이터프레임 구성
df_plot = pd.DataFrame({
    "Age": age_labels,
    "Population": age_values
})

# 정렬을 위한 카테고리 설정
age_order = [str(i) for i in range(101)] + ["100+"]
df_plot["Age"] = pd.Categorical(df_plot["Age"], categories=age_order, ordered=True)
df_plot = df_plot.sort_values("Age")

# 타입 명확히 변환 (그래프 깨짐 방지)
df_plot["Age"] = df_plot["Age"].astype(str)
df_plot["Population"] = df_plot["Population"].astype(int)

# Plotly 그래프 그리기
fig = px.bar(
    df_plot,
    x="Age",
    y="Population",
    title="Total Population by Age in Seoul (June 2025)",
    labels={"Age": "Age", "Population": "Population"},
    height=600
)

fig.update_layout(xaxis_tickangle=-45)

# Streamlit에 출력
st.plotly_chart(fig, use_container_width=True)

# 데이터프레임 원본 보기
with st.expander("🔍 데이터프레임 보기"):
    st.dataframe(df_plot, use_container_width=True)
