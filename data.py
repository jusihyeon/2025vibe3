import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="연령별 인구 분석", layout="wide")
st.title("📊 2025년 6월 연령별 인구 분석")

# 📁 파일 업로드
uploaded_sum = st.file_uploader("✅ 연령별 인구(합계) 파일 업로드", type=["csv"], key="sum")
uploaded_mf = st.file_uploader("✅ 연령별 인구(남녀) 파일 업로드", type=["csv"], key="mf")

# 📌 탭 구성
tab1, tab2 = st.tabs(["📌 전체 인구 합계", "📌 남녀 비교 분석"])

# -------------------------------------------------------------------
# TAB 1: 전체 인구 합계
# -------------------------------------------------------------------
with tab1:
    if uploaded_sum:
        try:
            df_total = pd.read_csv(uploaded_sum, encoding='cp949', engine='python')

            # 열 정리
            df_total = df_total.drop(columns=[df_total.columns[1]])  # 총인구수 열 제거
            df_total = df_total.rename(columns={df_total.columns[0]: "지역"})

            # 긴 형식으로 변환
            df_long = df_total.melt(id_vars="지역", var_name="연령", value_name="인구수")
            df_long["인구수"] = df_long["인구수"].str.replace(",", "").replace("", "0")
            df_long["인구수"] = df_long["인구수"].fillna(0).astype(int)

            # 지역 선택
            regions = df_long["지역"].unique()
            selected_region = st.selectbox("지역 선택", regions)

            filtered = df_long[df_long["지역"] == selected_region]

            # 📊 시각화
            fig = px.bar(filtered, x="연령", y="인구수",
                         title=f"{selected_region} 연령별 인구",
                         labels={"연령": "나이", "인구수": "명"})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
    else:
        st.info("왼쪽 사이드에서 합계 CSV 파일을 업로드해주세요.")

# -------------------------------------------------------------------
# TAB 2: 남녀 인구 비교
# -------------------------------------------------------------------
with tab2:
    if uploaded_mf:
        try:
            # 파일 읽기 (깨진 줄 무시)
            df_mf = pd.read_csv(uploaded_mf, encoding="ISO-8859-1", engine="python", on_bad_lines='skip')
            df_mf = df_mf.rename(columns={df_mf.columns[0]: "지역"})

            # 열 이름에서 '남_0세', '여_0세' 위치 자동 탐색
            male_start_idx = next(i for i, col in enumerate(df_mf.columns) if "남_0세" in col)
            female_start_idx = next(i for i, col in enumerate(df_mf.columns) if "여_0세" in col)

            male_cols = df_mf.columns[male_start_idx : male_start_idx + 101]
            female_cols = df_mf.columns[female_start_idx : female_start_idx + 101]

            # melt 및 병합
            male_df = df_mf[["지역"] + list(male_cols)].melt(id_vars="지역", var_name="연령", value_name="인구수")
            male_df["성별"] = "남자"

            female_df = df_mf[["지역"] + list(female_cols)].melt(id_vars="지역", var_name="연령", value_name="인구수")
            female_df["성별"] = "여자"

            df_gender = pd.concat([male_df, female_df])

            # 인구수 정리
            df_gender["인구수"] = df_gender["인구수"].astype(str).str.replace(",", "").replace("", "0")
            df_gender["인구수"] = df_gender["인구수"].fillna(0).astype(int)

            # 지역 선택
            regions = df_gender["지역"].unique()
            selected_region = st.selectbox("지역 선택 (남녀비교)", regions, key="mf_region")

            filtered_gender = df_gender[df_gender["지역"] == selected_region]

            # 📊 시각화
            fig2 = px.bar(filtered_gender, x="연령", y="인구수", color="성별", barmode="group",
                          title=f"{selected_region} 연령별 남녀 인구 비교")
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
    else:
        st.info("왼쪽 사이드에서 남녀 CSV 파일을 업로드해주세요.")
