import streamlit as st
import pandas as pd

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
    cuisine_options = st.multiselect(
        '좋아하는 요리 스타일을 선택해주세요',
        ['한식', '중식', '일식', '양식', '동남아 음식', '인도 음식'],
        help='여러 개 선택 가능'
    )
    st.session_state.preferences['cuisine_preferences'] = cuisine_options

    st.header('향신료 선호도')
    spice_intensity = st.radio(
        '향신료 강도 선호도',
        ['약한 향신료', '중간 강도', '강한 향신료'],
        help='음식의 향신료 강도를 선택해주세요'
    )
    st.session_state.preferences['spice_intensity'] = spice_intensity

    st.header('식단 선호도')
    diet_preference = st.radio(
        '식단 유형',
        ['육식', '채식', '비건'],
        help='주로 선호하는 식단 유형'
    )
    st.session_state.preferences['diet_preference'] = diet_preference

    st.header('알레르기 및 싫어하는 음식')
    disliked_foods = st.text_area(
        '피하고 싶은 음식이나 알레르기 음식을 적어주세요',
        help='예: 새우, 견과류, 우유 등'
    )
    st.session_state.preferences['disliked_foods'] = disliked_foods

    st.header('기타 선호도')
    additional_preferences = st.text_area(
        '추가로 알려주고 싶은 음식 취향이 있나요?',
        help='예: 건강식, 다이어트 음식, 특정 요리 스타일 등'
    )
    st.session_state.preferences['additional_preferences'] = additional_preferences

    if st.button('맛 프로필 완성하기'):
        st.success('맛 프로필이 성공적으로 저장되었습니다! 👍')
        st.json(st.session_state.preferences)
        
        preferences_df = pd.DataFrame.from_dict(st.session_state.preferences, orient='index').T
        preferences_df.to_csv('user_taste_preferences.csv', index=False)

def main():
    taste_preference_survey()

if __name__ == '__main__':
    main()
