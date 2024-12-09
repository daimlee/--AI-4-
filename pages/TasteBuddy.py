import streamlit as st
import requests
from dotenv import load_dotenv
import os
import re
import json

# 환경 변수 로드
load_dotenv()
PLACE_CLIENT_ID = os.getenv("PLACE_CLIENT_ID")  # Place Search API Client ID
PLACE_CLIENT_SECRET = os.getenv("PLACE_CLIENT_SECRET")  # Place Search API Client Secret

# 데이터 저장 파일 경로
RECORD_FILE = "records.json"

def load_records():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_records(records):
    with open(RECORD_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

def clean_html(text):
    """HTML 태그를 제거하는 함수"""
    return re.sub(r'<.*?>', '', text)

def search_nearby_places(query):
    """검색어를 기반으로 맛집 정보를 반환"""
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": PLACE_CLIENT_ID,
        "X-Naver-Client-Secret": PLACE_CLIENT_SECRET
    }
    params = {
        "query": query,
        "sort": "random",
        "display": 7,
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()['items']
    else:
        raise Exception("Place Search API 오류: " + response.text)

def taste_preference_survey():
    st.title('🍽️ 맛 프로필 만들기')
    
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {}

    st.header('맛 프로필 제목')
    profile_title = st.text_input('맛 프로필 제목을 입력해주세요')

    if 'profile_list' not in st.session_state:
        st.session_state.profile_list = []

    st.header('매운맛 선호도')
    spicy_level = st.slider(
        '얼마나 매운 음식을 좋아하시나요?', 
        min_value=0, 
        max_value=10, 
        value=5,
        help='0은 전혀 매운 음식을 못 먹음, 10은 아주 매운 음식도 OK'
    )
    st.session_state.preferences['spicy_level'] = spicy_level

    st.header('요리 스타일 선호도')
    cuisine_option = st.selectbox(
        '좋아하는 요리 스타일을 선택해주세요',
        ['한식', '중식', '일식', '양식', '동남아 음식', '인도 음식'],
        help='하나만 선택 가능'
    )
    st.session_state.preferences['cuisine_preferences'] = cuisine_option

    if st.button('맛 프로필 완성하기'):
        with st.spinner('맛 프로필을 생성하는 중...'):
            preference_str = generate_preference_string(profile_title)
            st.session_state.profile_list.append({'title': profile_title, 'preferences': preference_str})
            st.success(f'맛 프로필이 성공적으로 저장되었습니다! 🎉')

def generate_preference_string(profile_title):
    preferences = st.session_state.preferences
    
    if preferences['spicy_level'] <= 3:
        spicy_description = "맵지 않은"
    elif preferences['spicy_level'] >= 7:
        spicy_description = "매운"
    else:
        spicy_description = "적당한 매운맛"
    
    preference_str = f"{spicy_description} {preferences['cuisine_preferences']}"
    return f"{profile_title}: {preference_str}"

def recommend_restaurants():
    st.title('📍 지역 검색')

    if 'profile_list' not in st.session_state or len(st.session_state.profile_list) == 0:
        st.warning('먼저 맛 프로필을 생성해주세요!')
        return

    profile_titles = [profile['title'] for profile in st.session_state.profile_list]
    selected_profile_title = st.selectbox('프로필을 선택하세요', profile_titles)

    selected_profile = next(profile for profile in st.session_state.profile_list if profile['title'] == selected_profile_title)
    
    st.write(f"선택한 선호 프로필: {selected_profile['preferences']}")

    address = st.text_input("지역을 입력하세요")

    spicy_level = st.session_state.preferences.get('spicy_level', 5)
    cuisine_preferences = st.session_state.preferences.get('cuisine_preferences', '한식')

    if spicy_level <= 3:
        spicy_description = "맵지 않은"
    elif spicy_level >= 7:
        spicy_description = "매운"
    else:
        spicy_description = ""

    if st.button("검색하기"):
        try:
            query = f"{address} {spicy_description} {cuisine_preferences} 맛집"
            places = search_nearby_places(query)
            st.subheader("추천 맛집 목록")
            st.markdown("<p style='color: yellow;'>⚠️ 상세보기 링크는 실제 운영 링크와 다를 수 있습니다.</p>", unsafe_allow_html=True)
            
            records = load_records()
            
            for place in places:
                cleaned_title = clean_html(place['title'])
                cleaned_address = clean_html(place['address'])
                
                st.write(f"**{cleaned_title}** - {cleaned_address} ([상세보기]({place['link']}))")
                
                records.append({
                    "profile": selected_profile['preferences'],
                    "title": cleaned_title,
                    "address": cleaned_address,
                    "link": place['link']
                })
            
            save_records(records)
            st.success("추천 결과가 기록되었습니다!")
            
        except Exception as e:
            st.error(f"오류 발생: {e}")

def record_page():
    st.title("📝 기록페이지")
    
    # 로그인 관련 로직 제거 -> 누구나 접근 가능
    records = load_records()
    profiles = {record["profile"] for record in records}
    
    if profiles:
        for profile in profiles:
            with st.expander(f"{profile}"):
                profile_records = [record for record in records if record["profile"] == profile]
                
                if profile_records:
                    for record in profile_records:
                        st.write(f"**{record['title']}** - {record['address']} ([상세보기]({record['link']}))")
                        st.write("---")
                else:
                    st.info("해당 프로필에 대한 기록이 없습니다.")
    else:
        st.info("아직 기록된 내용이 없습니다.")

def main():
    # 로그인, 회원가입 관련 로직 제거
    # current_page 상태 제거 -> 사이드바 메뉴로만 페이지 전환
    st.sidebar.title("🍴 메뉴")
    menu = st.sidebar.radio("탭 선택", ["맛 프로필", "지역 검색", "기록"])

    if menu == "맛 프로필":
        taste_preference_survey()
    elif menu == "지역 검색":
        recommend_restaurants()
    elif menu == "기록":
        record_page()

if __name__ == '__main__':
    main()
