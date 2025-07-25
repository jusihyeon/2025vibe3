import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="남녀 연령별 인구 분석", layout="wide")
st.title("📊 2025년 6월 연령별 남녀 인구 분석")

# 📁 파일 업로드
uploaded_file = st.file_uploader("✅ 남녀 인구 CSV 업로드", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949", engine="python", on_bad_lines="skip")
        df = df.rename(columns={df.columns[0]: "지역"})

        # 열 위치 자동 탐색
        male_start_idx = next(i for i, col in enumerate(df.columns) if "남_0세" in col)
        female_start_idx = next(i for i, col in enumerate(df.columns) if "여_0세" in col)

        male_cols = df.columns[male_start_idx : male_start_idx + 101]
        female_cols = df.columns[female_start_idx : female_start_idx + 101]

        # 데이터 가공
        male_df = df[["지역"] + list(male_cols)].melt(id_vars="지역", var_name="연령", value_name="인구수")
        male_df["성별"] = "남자"
        female_df = df[["지역"] + list(female_cols)].melt(id_vars="지역", var_name="연령", value_name="인구수")
        female_df["성별"] = "여자"

        df_gender = pd.concat([male_df, female_df])

        # 인구수 전처리 (숫자 변환)
        df_gender["인구수"] = (
            pd.to_numeric(df_gender["인구수"].astype(str)
                          .replace({",": "", "None": "0", "": "0"}, regex=True),
                          errors="coerce")
            .fillna(0)
            .astype(int)
        )

        # 📍 지역 선택
        region = st.selectbox("지역 선택", sorted(df_gender["지역"].unique()))
        filtered = df_gender[df_gender["지역"] == region]

        # 📊 시각화
        fig = px.bar(filtered, x="연령", y="인구수", color="성별", barmode="group",
                     title=f"{region} 연령별 남녀 인구 분포", labels={"연령": "나이", "인구수": "인구 수"})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.exception(e)
else:
    st.info("좌측에서 남녀 인구 CSV 파일을 업로드하세요.")
