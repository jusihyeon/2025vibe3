import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 제목
st.title("서울특별시 연령별 인구수 (2025년 6월 기준) 시각화")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (예: 합계 인구)", type=["csv"])

if uploaded_file:
    try:
        # CSV 읽기
        df = pd.read_csv(uploaded_file, encoding='cp949')

        # "서울특별시" 데이터 필터링
        df_seoul = df[df["행정구역"].str.contains("서울특별시  ")].copy()

        # 연령 컬럼만 추출 (3번째 컬럼 이후)
        age_columns = df_seoul.columns[3:]

        # Long-form으로 변환
        df_plot = df_seoul.melt(id_vars=["행정구역"], value_vars=age_columns,
                                var_name="연령", value_name="인구수")

        # 연령 이름 정리 (숫자 추출)
        df_plot["연령"] = df_plot["연령"].str.extract(r"(\d+세|100세 이상)")

        # 쉼표 제거 → 숫자로 변환
        df_plot["인구수"] = df_plot["인구수"].str.replace(",", "")
        df_plot = df_plot.dropna(subset=["인구수"])
        df_plot["인구수"] = df_plot["인구수"].astype(int)

        # Plotly 시각화
        fig = px.bar(df_plot, x="연령", y="인구수",
                     title="서울특별시 연령별 인구수 (2025년 6월)",
                     labels={"연령": "연령대", "인구수": "인구 수"})
        fig.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(fig)

        # 데이터 테이블 표시
        with st.expander("데이터 보기"):
            st.dataframe(df_plot)

    except Exception as e:
        st.error(f"오류 발생: {e}")
else:
    st.info("왼쪽 사이드바 또는 위에서 CSV 파일을 업로드하세요.")
