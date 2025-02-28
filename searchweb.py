import streamlit as st
import requests
import pandas as pd

def fetch_data(region):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.diningcode.com',
        'Referer': 'https://www.diningcode.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    }
    
    all_data = []
    for page in range(1, 6):
        data = {
            'query': region,
            'addr': '',
            'keyword': '',
            'order': 'r_score',
            'distance': '',
            'rn_search_flag': 'on',
            'search_type': 'poi_search',
            'lat': '37.5152997',
            'lng': '127.0221591',
            'rect': '',
            's_type': '',
            'token': '',
            'mode': 'poi',
            'dc_flag': '1',
            'page': str(page),
            'size': '20',
        }
        
        response = requests.post('https://im.diningcode.com/API/isearch/', headers=headers, data=data)
        if response.status_code == 200:
            response_data = response.json()
            if 'result_data' in response_data and 'poi_section' in response_data['result_data']:
                poi_list = response_data['result_data']['poi_section']['list']
                for item in poi_list:
                    display_review = item.get("display_review")
                    review_text = display_review["review_cont"] if display_review and isinstance(display_review, dict) else ""
                    formatted_data = {
                        "이름": item.get("nm", ""),
                        "지점명": item.get("branch", ""),
                        "주소": item.get("addr", ""),
                        "도로명 주소": item.get("road_addr", ""),
                        "전화번호": item.get("phone", ""),
                        "카테고리": item.get("category", ""),
                        "점수": item.get("score", ""),
                        "리뷰": review_text,
                        "좋아요 수": item.get("favorites_cnt", ""),
                        "리뷰 수": item.get("review_cnt", ""),
                        "추천 수": item.get("recommend_cnt", ""),
                        "영업 상태": item.get("open_status", ""),
                        "이미지 URL": item.get("image", "")
                    }
                    all_data.append(formatted_data)
    return pd.DataFrame(all_data)

st.set_page_config(page_title="지역 검색", layout="wide")
st.title("지역 검색 및 추천 맛집")

region = st.text_input("검색할 지역을 입력하세요:")
if st.button("검색") and region:
    with st.spinner("데이터 불러오는 중..."):
        df = fetch_data(region)
        if df.empty:
            st.error("검색 결과가 없습니다. 다시 시도해주세요.")
        else:
            for _, row in df.iterrows():
                with st.container():
                    st.markdown("---")
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if row["이미지 URL"]:
                            st.image(row["이미지 URL"], use_container_width=True)
                    with col2:
                        st.subheader(row["이름"])
                        st.write(f"**카테고리:** {row['카테고리']}")
                        st.write(f"**주소:** {row['도로명 주소']} ({row['주소']})")
                        st.write(f"**전화번호:** {row['전화번호']}")
                        st.write(f"**점수:** {row['점수']}")
                        st.write(f"**리뷰:** {row['리뷰']}")
                        st.write(f"👍 좋아요: {row['좋아요 수']} | 📝 리뷰 수: {row['리뷰 수']} | ⭐ 추천 수: {row['추천 수']}")

            # CSV 다운로드 버튼 추가
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(label="📥 데이터 다운로드 (CSV)", data=csv, file_name=f"{region}_data.csv", mime='text/csv')
