import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="2025년 인구 분석", layout="wide")
st.title("📊 2025년 6월 연령별 인구 분석")

# 📁 파일 업로드
uploaded_sum = st.file_uploader("✅ 연령별 인구(합계) CSV 업로드", type=["csv"], key="sum")
uploaded_mf = st.file_uploader("✅ 연령별 인구(남녀) CSV 업로드", type=["csv"], key="mf")

# ✅ 연령 그룹 묶기 여부
group_age = st.checkbox("🔢 연령대를 10세 단위로 묶어서 보기 (0–9세, 10–19세...)", value=False)

# 🔧 연령 그룹화 함수
def group_age_range(age_str):
    if "이상" in age_str or "plus" in age_str:
        return "100+"
    digits = ''.join(filter(str.isdigit, age_str))
    if digits == '':
        return "Unknown"
    age = int(digits)
    return f"{(age//10)*10}-{(age//10)*10 + 9}" if age < 100 else "100+"

# ✅ 정렬 순서 명시
age_order = [f"{i}-{i+9}" for i in range(0, 100, 10)] + ["100+"]

# 📌 탭 구성
tab1, tab2 = st.tabs(["📌 전체 인구 합계 분석", "📌 남녀 인구 비교 분석"])

# -------------------------------------------------------------
# 📊 TAB 1: 전체 인구 분석
# -------------------------------------------------------------
with tab1:
    if uploaded_sum:
        try:
            df_total = pd.read_csv(uploaded_sum, encoding='cp949', engine='python')
            df_total = df_total.rename(columns={df_total.columns[0]: "지역"})
            if "총인구수" in df_total.columns[1]:
                df_total = df_total.drop(columns=[df_total.columns[1]])

            df_long = df_total.melt(id_vars="지역", var_name="연령", value_name="인구수")
            df_long["인구수"] = df_long["인구수"].astype(str).str.replace(",", "").replace("", "0")
            df_long["인구수"] = pd.to_numeric(df_long["인구수"], errors="coerce").fillna(0).astype(int)

            if group_age:
                df_long["연령그룹"] = df_long["연령"].apply(group_age_range)
                df_long["연령그룹"] = pd.Categorical(df_long["연령그룹"], categories=age_order, ordered=True)
                df_plot = df_long.groupby(["지역", "연령그룹"], as_index=False)["인구수"].sum()
                x_col = "연령그룹"
            else:
                df_plot = df_long
                x_col = "연령"

            selected_region = st.selectbox("지역 선택 (합계)", sorted(df_plot["지역"].unique()), key="sum_region")
            filtered = df_plot[df_plot["지역"] == selected_region]

            fig = px.bar(filtered, x=x_col, y="인구수",
                         title=f"{selected_region} 연령별 전체 인구",
                         labels={x_col: "연령", "인구수": "인구 수"},
                         category_orders={x_col: age_order} if group_age else None)
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.exception(e)
    else:
        st.info("왼쪽에서 연령별 인구 합계 CSV를 업로드하세요.")

# -------------------------------------------------------------
# 📊 TAB 2: 남녀 인구 비교 분석
# -------------------------------------------------------------
with tab2:
    if uploaded_mf:
        try:
            df = pd.read_csv(uploaded_mf, encoding="cp949", engine="python", on_bad_lines="skip")
            df = df.rename(columns={df.columns[0]: "지역"})

            try:
                male_start_idx = next(i for i, col in enumerate(df.columns) if "남" in col and "0세" in col)
                female_start_idx = next(i for i, col in enumerate(df.columns) if "여" in col and "0세" in col)
            except StopIteration:
                st.error("❌ '남_0세' 또는 '여_0세' 열을 찾을 수 없습니다. CSV 구조를 확인하세요.")
                st.stop()

            male_cols = df.columns[male_start_idx : male_start_idx + 101]
            female_cols = df.columns[female_start_idx : female_start_idx + 101]

            male_df = df[["지역"] + list(male_cols)].melt(id_vars="지역", var_name="연령", value_name="인구수")
            male_df["성별"] = "남자"
            female_df = df[["지역"] + list(female_cols)].melt(id_vars="지역", var_name="연령", value_name="인구수")
            female_df["성별"] = "여자"

            df_gender = pd.concat([male_df, female_df])
            df_gender["인구수"] = (
                pd.to_numeric(df_gender["인구수"].astype(str)
                              .replace({",": "", "None": "0", "": "0"}, regex=True),
                              errors="coerce")
                .fillna(0)
                .astype(int)
            )

            if group_age:
                df_gender["연령그룹"] = df_gender["연령"].apply(group_age_range)
                df_gender["연령그룹"] = pd.Categorical(df_gender["연령그룹"], categories=age_order, ordered=True)
                df_plot = df_gender.groupby(["지역", "연령그룹", "성별"], as_index=False)["인구수"].sum()
                x_col = "연령그룹"
            else:
                df_plot = df_gender
                x_col = "연령"

            selected_region = st.selectbox("지역 선택 (남녀비교)", sorted(df_plot["지역"].unique()), key="mf_region")
            filtered_gender = df_plot[df_plot["지역"] == selected_region]

            fig2 = px.bar(filtered_gender, x=x_col, y="인구수", color="성별", barmode="group",
                          title=f"{selected_region} 연령별 남녀 인구 비교",
                          labels={x_col: "연령", "인구수": "인구 수"},
                          category_orders={x_col: age_order} if group_age else None)
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.exception(e)
    else:
        st.info("왼쪽에서 남녀 인구 CSV를 업로드하세요.")
