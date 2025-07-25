import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# -------------------------------
# 📍 주소 → 좌표 변환 함수 (Nominatim 사용)
def geocode_nominatim(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "streamlit-bookmark-app"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return float(result["lat"]), float(result["lon"])
    else:
        return None, None

# -------------------------------
# 🌐 Streamlit UI
st.set_page_config(page_title="주소 기반 북마크 지도", page_icon="📍", layout="centered")
st.title("📍 주소로 북마크 지도 만들기 (API 키 없이)")

# 세션 상태 초기화
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# -------------------------------
# 입력 폼
with st.form("bookmark_form"):
    st.subheader("➕ 북마크 추가")
    name = st.text_input("장소 이름")
    address = st.text_input("주소 입력")
    submitted = st.form_submit_button("추가하기")

    if submitted:
        if name and address:
            lat, lon = geocode_nominatim(address)
            if lat and lon:
                st.session_state.bookmarks.append({
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "address": address
                })
                st.success(f"✅ '{name}' 추가 완료!")
            else:
                st.error("⚠️ 주소를 찾을 수 없습니다. 다시 확인해주세요.")
        else:
            st.warning("❗ 모든 항목을 입력하세요.")

# -------------------------------
# 지도 중심 위치 설정
if st.session_state.bookmarks:
    center = st.session_state.bookmarks[-1]
    center_lat = center["lat"]
    center_lon = center["lon"]
else:
    center_lat, center_lon = 37.5665, 126.9780  # 서울 기본값

# 지도 생성
m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# 마커 추가
for bm in st.session_state.bookmarks:
    folium.Marker(
        location=[bm["lat"], bm["lon"]],
        popup=f"{bm['name']}<br>{bm['address']}",
        icon=folium.Icon(color="blue", icon="bookmark")
    ).add_to(m)

# 지도 표시
st.subheader("🗺️ 북마크 지도")
st_folium(m, width=700, height=500)

# 북마크 목록
if st.session_state.bookmarks:
    st.markdown("---")
    st.subheader("📋 북마크 목록")
    for i, bm in enumerate(st.session_state.bookmarks):
        st.write(f"{i+1}. {bm['name']} - {bm['address']}")

# 초기화 버튼
if st.button("❌ 모든 북마크 초기화"):
    st.session_state.bookmarks.clear()
    st.success("모든 북마크가 삭제되었습니다.")
