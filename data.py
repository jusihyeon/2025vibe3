import plotly.express as px

# Age를 문자열로, Population은 정수로 변환
df_plot["Age"] = df_plot["Age"].astype(str)
df_plot["Population"] = pd.to_numeric(df_plot["Population"], errors="coerce").fillna(0).astype(int)

fig = px.bar(
    df_plot,
    x="Age",
    y="Population",
    title="Total Population by Age in Seoul (June 2025)",
    labels={"Age": "Age", "Population": "Population"},
    height=600
)

fig.update_layout(
    xaxis_title="Age",
    yaxis_title="Population",
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True)
