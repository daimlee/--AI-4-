import streamlit as st
import requests
from dotenv import load_dotenv
import os
import re

# 환경 변수 로드
load_dotenv()
PLACE_CLIENT_ID = os.getenv("PLACE_CLIENT_ID")  # Place Search API Client ID
PLACE_CLIENT_SECRET = os.getenv("PLACE_CLIENT_SECRET")  # Place Search API Client Secret
api_key = os.getenv("api")

if api_key:
    st.session_state['api_key'] = api_key
    if 'openai_client' in st.session_state:
        client = st.session_state['openai_client']
    else:
        client = OpenAI(api_key=api_key)
        st.session_state['openai_client'] = client
# HTML 태그 제거 함수
def clean_html(text):
    """HTML 태그를 제거하는 함수"""
    return re.sub(r'<.*?>', '', text)  # <b>와 같은 HTML 태그를 제거

# Place Search API (맛집 검색)
def search_nearby_places(query):
    """검색어와 좌표를 기반으로 맛집 정보를 반환"""
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": PLACE_CLIENT_ID,
        "X-Naver-Client-Secret": PLACE_CLIENT_SECRET
    }
    params = {
        "query": query,  # 검색어 (예: "맛집")
        "sort": "random",  # 정렬 방식
        "display": 7,  # 결과 개수
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()['items']
    else:
        raise Exception("Place Search API 오류: " + response.text)

# Streamlit 앱
def recommend_restaurants():
    st.header("🍴 맛집 추천")
    
    # 주소 입력
    address = st.text_input("주소를 입력하세요")
    
    # 맛 프로필 정보 가져오기
    spicy_level = st.session_state.preferences.get('spicy_level', 5)
    cuisine_preferences = st.session_state.preferences.get('cuisine_preferences', '한식')

    # 매운맛 선호도 변환
    if spicy_level <= 3:
        spicy_description = "맵지 않은"
    elif spicy_level >= 7:
        spicy_description = "매운"
    else:
        spicy_description = ""
    
    # 추천 버튼
    if st.button("추천받기"):
        try:
            # 검색어 생성: 주소 + 맛 프로필
            query = f"{address} {spicy_description} {cuisine_preferences} 맛집"
            # 2. Place Search API로 맛집 검색
            places = search_nearby_places(query)
            st.subheader("추천 맛집 목록")
            st.markdown("<p style='color: yellow;'>⚠️ 상세보기는 링크로 제대로 된 링크가 포함되어 있지 않을 수 있습니다.</p>", unsafe_allow_html=True)
            
            # 3. 결과 출력
            for place in places:
                # HTML 태그 제거
                cleaned_title = clean_html(place['title'])
                cleaned_address = clean_html(place['address'])
                
                st.write(f"**{cleaned_title}** - {cleaned_address} ([상세보기]({place['link']}))")
            
        except Exception as e:
            st.error(f"오류 발생: {e}")

def taste_preference_survey():
    st.title('🍽️맛 프로필 만들기')
    
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {}

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
        st.success('맛 프로필이 성공적으로 저장되었습니다! 👍')
        preference_str = generate_preference_string()

def generate_preference_string():
    preferences = st.session_state.preferences
    
    # 매운맛 선호도 변환
    if preferences['spicy_level'] <= 3:
        spicy_description = "맵지 않은"
    elif preferences['spicy_level'] >= 7:
        spicy_description = "매운"
    else:
        spicy_description = "적당한 매운맛"
    
    # 각 항목을 문자열로 변환하여 하나의 문자열로 합침
    preference_str = f"{spicy_description} {preferences['cuisine_preferences']}"
    
    return preference_str

# Main 실행
def main():
    st.sidebar.title("🍴 메뉴")
    menu = st.sidebar.radio("탭 선택", ["맛 프로필","맛집 추천"])

    if menu == "맛 프로필":
        taste_preference_survey()
    
    if menu == "맛집 추천":
        recommend_restaurants()

if __name__ == '__main__':
    main()
