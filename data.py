import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="서울 인구 시각화", layout="wide")
st.title("서울특별시 연령별 인구수 (2025년 6월 기준)")

# CSV 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (예: 202506_연령별인구현황_월간_합계)", type=["csv"])

if uploaded_file:
    try:
        # CSV 읽기 (구문 오류 방지를 위해 engine='python' 사용)
        df = pd.read_csv(uploaded_file, encoding='cp949', engine='python')

        # '서울특별시  (1100000000)' 행만 선택
        df_seoul = df[df["행정구역"].str.contains("서울특별시  ")].copy()

        # 연령별 열만 선택 (3번째 열 이후)
        age_columns = df_seoul.columns[3:]

        # Long-form 변환
        df_plot = df_seoul.melt(id_vars=["행정구역"], value_vars=age_columns,
                                var_name="연령", value_name="인구수")

        # 연령 라벨 정제
        df_plot["연령"] = df_plot["연령"].str.extract(r"(\d+세|100세 이상)")

        # 쉼표 제거 후 숫자 변환
        df_plot["인구수"] = df_plot["인구수"].str.replace(",", "")
        df_plot = df_plot.dropna(subset=["인구수"])
        df_plot["인구수"] = df_plot["인구수"].astype(int)

        # 시각화
        fig = px.bar(df_plot, x="연령", y="인구수",
                     title="서울특별시 연령별 인구수 (2025년 6월)",
                     labels={"연령": "연령대", "인구수": "인구 수"})

        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        # 데이터 보기
        with st.expander("📋 연령별 인구수 데이터 보기"):
            st.dataframe(df_plot)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

else:
    st.info("왼쪽에서 CSV 파일을 업로드하세요.")
