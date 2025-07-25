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
    df = pd.read_csv(csv_file)
    return df

# 데이터 불러오기
try:
    df_total = load_data()
except FileNotFoundError:
    st.error(f"❌ 파일 '{csv_file}'을(를) 찾을 수 없습니다.")
    st.stop()

# 서울특별시 데이터만 추출
try:
    df_seoul = df_total[df_total["Region"].str.contains("서울")].iloc[0]
except IndexError:
    st.error("❌ 서울특별시 데이터를 찾을 수 없습니다.")
    st.stop()

# 연령별 컬럼 추출
age_columns = [col for col in df_seoul.index if "Age_" in col]
age_labels = [col.split("_")[-1].replace("plus", "100+") for col in age_columns]
age_values = df_seoul[age_columns].astype(int)

# 시각화용 데이터프레임
df_plot = pd.DataFrame({
    "Age": age_labels,
    "Population": age_values.values
})

# 정렬
age_order = [str(i) for i in range(101)] + ["100+"]
df_plot["Age"] = pd.Categorical(df_plot["Age"], categories=age_order, ordered=True)
df_plot = df_plot.sort_values("Age")

# Plotly 시각화
fig = px.bar(df_plot, x="Age", y="Population",
             title="Total Population by Age in Seoul (June 2025)",
             labels={"Age": "Age", "Population": "Population"},
             height=600)

# Streamlit에 그래프 표시
st.plotly_chart(fig, use_container_width=True)

# 데이터프레임 확인용
with st.expander("🔍 원본 데이터 보기"):
    st.dataframe(df_plot, use_container_width=True)
