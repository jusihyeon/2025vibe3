# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit 설정
st.set_page_config(page_title="연령별 인구 분석", layout="wide")

st.title("📊 2025년 6월 연령별 인구 분석")

# 파일 업로드
uploaded_sum = st.file_uploader("✅ 연령별 인구(합계) 파일 업로드", type=["csv"], key="sum")
uploaded_mf = st.file_uploader("✅ 연령별 인구(남녀) 파일 업로드", type=["csv"], key="mf")

# 탭 UI
tab1, tab2 = st.tabs(["📌 전체 인구 합계", "📌 남녀 비교 분석"])

with tab1:
    if uploaded_sum:
        try:
            df_total = pd.read_csv(uploaded_sum, encoding='cp949', engine='python')
            df_total = df_total.drop(columns=[df_total.columns[1]])  # 전체 인구 합계 열 제거
            df_total = df_total.rename(columns={df_total.columns[0]: "지역"})
            df_long = df_total.melt(id_vars="지역", var_name="연령", value_name="인구수")
            df_long["인구수"] = df_long["인구수"].str.replace(",", "").astype(int)

            regions = df_long["지역"].unique()
            selected_region = st.selectbox("지역 선택", regions)

            filtered = df_long[df_long["지역"] == selected_region]

            fig = px.bar(filtered, x="연령", y="인구수", title=f"{selected_region} 연령별 인구", labels={"연령": "나이", "인구수": "명"})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.info("왼쪽 사이드에서 합계 CSV 파일을 업로드해주세요.")

with tab2:
    if uploaded_mf:
        try:
            df_mf = pd.read_csv(uploaded_mf, encoding="ISO-8859-1", engine="python")
            df_mf = df_mf.rename(columns={df_mf.columns[0]: "지역"})
            
            # 남/여 열 분리
            mid_idx = df_mf.columns.get_loc("2025년06월_남_총인구수")  # 기준 지점
            male_cols = df_mf.columns[mid_idx+1:mid_idx+102]
            female_cols = df_mf.columns[mid_idx+103:]

            male_df = df_mf[["지역"] + list(male_cols)].copy()
            female_df = df_mf[["지역"] + list(female_cols)].copy()

            male_df = male_df.melt(id_vars="지역", var_name="연령", value_name="인구수")
            male_df["성별"] = "남자"
            female_df = female_df.melt(id_vars="지역", var_name="연령", value_name="인구수")
            female_df["성별"] = "여자"

            df_gender = pd.concat([male_df, female_df])
            df_gender["인구수"] = df_gender["인구수"].str.replace(",", "").astype(int)

            regions = df_gender["지역"].unique()
            selected_region = st.selectbox("지역 선택 (남녀비교)", regions, key="mf_region")

            filtered_gender = df_gender[df_gender["지역"] == selected_region]

            fig2 = px.bar(filtered_gender, x="연령", y="인구수", color="성별", barmode="group",
                          title=f"{selected_region} 연령별 남녀 인구 비교")
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.info("왼쪽 사이드에서 남녀 CSV 파일을 업로드해주세요.")
