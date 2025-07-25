# 💻 전체 Streamlit 앱 코드
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="광종별 매장량 시각화", layout="wide")
st.title("⛏️ 광종별 매장량 분석 대시보드")

unit_conversion = {
    "톤": 1,
    "천톤": 1_000,
    "천 톤": 1_000,
    "백만톤": 1_000_000,
    "천배럴": 1_000,
    "백만캐럿": 1_000_000,
    "만캐럿": 10_000,
    "톤 (metric tons)": 1,
    "metric tons": 1,
    "thousand metric tons": 1_000
}

# 🔽 파일 업로드
st.sidebar.header("📂 데이터 파일 업로드")
uploaded_file = st.sidebar.file_uploader("광종별 매장량 CSV 업로드", type=["csv"])
korea_file = st.sidebar.file_uploader("한국 매장량 CSV 업로드", type=["csv"])

if uploaded_file:
    try:
        df_total = pd.read_csv(uploaded_file, encoding="cp949")
        df_total.columns = df_total.columns.str.strip()
        for col in df_total.select_dtypes(include="object"):
            df_total[col] = df_total[col].astype(str).str.strip()
        df_total["상위5개국 매장량 합계"] = pd.to_numeric(
            df_total["상위5개국 매장량 합계"].str.replace(",", ""), errors="coerce"
        )
        df_total["단위"] = df_total["단위"].fillna("기타")
        df_total["환산상위5개국매장량"] = df_total.apply(
            lambda row: row["상위5개국 매장량 합계"] * unit_conversion.get(row["단위"], None)
            if row["단위"] in unit_conversion else None,
            axis=1
        )

        st.subheader("🔍 데이터 미리보기")
        st.dataframe(df_total)

        # 🔧 시각화 옵션
        st.subheader("📊 그래프 설정")
        orientation = st.radio("그래프 방향", ["세로 막대", "가로 막대"])
        filter_option = st.selectbox("데이터 범위", ["전체 보기", "상위 5개", "하위 5개", "직접 선택"])

        if filter_option == "상위 5개":
            df_vis = df_total.nlargest(5, "환산상위5개국매장량")
        elif filter_option == "하위 5개":
            df_vis = df_total.nsmallest(5, "환산상위5개국매장량")
        elif filter_option == "직접 선택":
            selected = st.multiselect("📌 광종 선택", df_total["광종"].unique())
            df_vis = df_total[df_total["광종"].isin(selected)]
        else:
            df_vis = df_total.copy()

        sort_order = st.radio("정렬 방식", ["내림차순", "오름차순"])
        df_vis = df_vis.sort_values("환산상위5개국매장량", ascending=(sort_order == "오름차순"))

        st.subheader("📈 시각화 결과")
        if orientation == "세로 막대":
            fig = px.bar(df_vis, x="광종", y="환산상위5개국매장량", color="단위")
            fig.update_layout(xaxis_tickangle=-45)
        else:
            fig = px.bar(df_vis, y="광종", x="환산상위5개국매장량", color="단위", orientation="h")

        st.plotly_chart(fig, use_container_width=True)

        # 📌 선택 광종 상세 정보
        st.subheader("📌 선택한 광종 상세 정보")
        selected_mineral = st.selectbox("자세히 볼 광종", df_vis["광종"].unique())
        row = df_vis[df_vis["광종"] == selected_mineral]
        if not row.empty:
            st.markdown(f"""
            **🔎 {selected_mineral}**
            - 합계: `{row['상위5개국 매장량 합계'].values[0]:,}` {row['단위'].values[0]}
            - 환산: `{int(row['환산상위5개국매장량'].values[0]):,}` 기준 단위
            """)

        # 🇰🇷 한국 점유율 비교
        if korea_file:
            df_country = pd.read_csv(korea_file, encoding="cp949")
            df_country["국가정제"] = df_country["국가"].str.strip().str.upper()
            df_korea = df_country[df_country["국가정제"] == "KOREA, REPUBLIC OF"].copy()

            mineral_mapping = {
                "GRAPHITE (NATURAL)": "흑연", "MOLYBDENUM": "몰리브덴", "INDIUM": "인듐",
                "DIATOMITE": "규조토", "TALC AND PYROPHYLLITE": "활석 및 피로필라이트",
                "MICA (NATURAL)": "운모", "FELDSPAR AND NEPHELINE SYENITE": "장석 및 네펠린반암"
            }
            df_korea["광종"] = df_korea["광종"].str.upper().str.strip()
            df_korea["광종_한글"] = df_korea["광종"].map(mineral_mapping)

            df_korea["환산매장량"] = df_korea.apply(
                lambda row: row["매장량"] * unit_conversion.get(row["단위"], None)
                if row["단위"] in unit_conversion else None, axis=1
            )

            df_korea["환산매장량"] = pd.to_numeric(df_korea["환산매장량"], errors="coerce")
            df_total["환산상위5개국매장량"] = pd.to_numeric(df_total["환산상위5개국매장량"], errors="coerce")

            comp = pd.merge(df_korea, df_total, how="inner", left_on="광종_한글", right_on="광종")
            comp = comp.dropna(subset=["환산매장량", "환산상위5개국매장량"])
            comp["한국 점유율 (%)"] = (comp["환산매장량"] / comp["환산상위5개국매장량"]) * 100

            st.subheader("🇰🇷 한국 점유율 비교")
            st.dataframe(comp[[
                "광종_한글", "환산매장량", "환산상위5개국매장량", "한국 점유율 (%)"
            ]].rename(columns={
                "광종_한글": "광종",
                "환산매장량": "한국 매장량",
                "환산상위5개국매장량": "상위 5개국 매장량"
            }).sort_values("한국 점유율 (%)", ascending=False))

    except Exception as e:
        st.exception(e)
else:
    st.info("📁 좌측 사이드바에서 파일을 업로드해주세요.")
