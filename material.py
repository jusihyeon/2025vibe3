import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="광종별 매장량 시각화", layout="wide")
st.title("⛏️ 광종별 매장량 분석 대시보드")

# 단위 환산 사전
unit_conversion = {
    "톤": 1, "천톤": 1_000, "천 톤": 1_000, "백만톤": 1_000_000,
    "천배럴": 1_000, "백만캐럿": 1_000_000, "만캐럿": 10_000,
    "톤 (metric tons)": 1, "metric tons": 1, "thousand metric tons": 1_000
}

# CSV 파일 경로 지정 (수동)
file_path = "상위5개국_매장량.csv"  # 예시 경로
korea_path = "한국_매장량.csv"       # 예시 경로

# 1️⃣ 상위 5개국 데이터 로드
df_total = pd.read_csv(file_path, encoding="cp949")
df_total.columns = df_total.columns.str.strip()
for col in df_total.select_dtypes(include="object"):
    df_total[col] = df_total[col].astype(str).str.strip()

df_total["상위5개국 매장량 합계"] = pd.to_numeric(
    df_total["상위5개국 매장량 합계"].astype(str).str.replace(",", ""),
    errors="coerce"
)
df_total["단위"] = df_total["단위"].fillna("기타")
df_total["환산상위5개국매장량"] = df_total.apply(
    lambda row: row["상위5개국 매장량 합계"] * unit_conversion.get(row["단위"], None)
    if row["단위"] in unit_conversion else None,
    axis=1
)

# 2️⃣ 시각화 전체 보기
st.subheader("📈 전체 광종별 매장량 (환산)")
df_sorted = df_total.sort_values("환산상위5개국매장량", ascending=False)
fig = px.bar(df_sorted, x="광종", y="환산상위5개국매장량", color="단위")
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# 3️⃣ 한국 점유율 비교
df_korea = pd.read_csv(korea_path, encoding="cp949")
df_korea["국가정제"] = df_korea["국가"].str.strip().str.upper()
df_korea = df_korea[df_korea["국가정제"] == "KOREA, REPUBLIC OF"]

mineral_mapping = {
    "GRAPHITE (NATURAL)": "흑연", "MOLYBDENUM": "몰리브덴", "INDIUM": "인듐",
    "DIATOMITE": "규조토", "TALC AND PYROPHYLLITE": "활석 및 피로필라이트",
    "MICA (NATURAL)": "운모", "FELDSPAR AND NEPHELINE SYENITE": "장석 및 네펠린반암"
}
df_korea["광종"] = df_korea["광종"].str.upper().str.strip()
df_korea["광종_한글"] = df_korea["광종"].map(mineral_mapping)

df_korea["환산매장량"] = df_korea.apply(
    lambda row: row["매장량"] * unit_conversion.get(row["단위"], None)
    if row["단위"] in unit_conversion else None,
    axis=1
)
df_korea["환산매장량"] = pd.to_numeric(df_korea["환산매장량"], errors="coerce")

df_compare = pd.merge(df_korea, df_total, how="inner", left_on="광종_한글", right_on="광종")
df_compare = df_compare.dropna(subset=["환산매장량", "환산상위5개국매장량"])
df_compare["한국 점유율 (%)"] = (
    df_compare["환산매장량"] / df_compare["환산상위5개국매장량"] * 100
)

st.subheader("🇰🇷 한국 점유율 비교")
st.dataframe(df_compare[[
    "광종_한글", "환산매장량", "환산상위5개국매장량", "한국 점유율 (%)"
]].rename(columns={
    "광종_한글": "광종",
    "환산매장량": "한국 매장량 (환산)",
    "환산상위5개국매장량": "상위 5개국 매장량 (환산)"
}).sort_values("한국 점유율 (%)", ascending=False))
