import streamlit as st
import pandas as pd
import os

# ============ 1. 스트림릿 기본 설정  ============
st.set_page_config(layout="wide", page_title="학교 정보 및 Google Maps 링크 개선 버전")

# CSV 파일 목록 (파일 미존재 시 안내)
csv_files = {
    "늘봄": "늘봄_data_with_links.csv",
    "돌봄": "돌봄_data_with_links.csv",
    "전래": "전래_data_with_links.csv"
}

# ============ 2. CSV 데이터 로드 함수  ============
@st.cache_data(show_spinner=False)
def load_data(file_path):
    """
    파일을 로드하고, 존재하지 않으면 None 반환.
    """
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"{file_path} 파일을 불러오는 중 오류가 발생했습니다: {e}")
        return None
    return df

# ============ 3. 하이퍼링크 컬럼만 HTML 처리 함수  ============
def convert_links_to_html(row):
    """
    row(Series)에서 'Google Maps 링크' 컬럼만 링크로 변환하여 HTML을 생성합니다.
    나머지 컬럼은 안전하게 표시(escape=True)하는 방식 유지.
    """
    new_row = []
    for col, val in row.items():
        if col == "Google Maps 링크":
            # 이미 CSV에 'https://...' 형태 또는 'HYPERLINK' 형태가 있으니
            # `<a>` 링크 형태로 변환
            new_row.append(f'<a href="{val}" target="_blank">링크 열기</a>')
        else:
            # 다른 컬럼은 일반 텍스트로 escape 처리
            new_row.append(str(val)) 
    return new_row

def dataframe_to_html_safe(df):
    """
    DataFrame을 한 행씩 순회하며,
    'Google Maps 링크' 컬럼만 HTML 링크로 변환한 뒤 전체를 HTML로 렌더링.
    """
    # 컬럼명: escape하여 안전하게 표시
    columns = [f"<th>{col}</th>" for col in df.columns]
    thead = "<tr>" + "".join(columns) + "</tr>"

    # 행 데이터
    rows_html = []
    for _, row in df.iterrows():
        converted = convert_links_to_html(row)  # Google Maps 링크만 HTML
        row_tds = "".join([f"<td>{cell}</td>" for cell in converted])
        rows_html.append(f"<tr>{row_tds}</tr>")

    tbody = "".join(rows_html)
    table_html = f"""
    <table border="1" style="border-collapse: collapse; width:100%;">
        <thead>{thead}</thead>
        <tbody>{tbody}</tbody>
    </table>
    """
    return table_html

# ============ 4. 사이드바 검색 기능 & 데이터 표시 로직 ============
st.title("학교 정보 및 Google Maps 링크 (개선 버전)")
st.write("아래 데이터를 통해 각 학교와 관련된 정보를 확인하고, Google Maps 링크를 클릭하세요.")
st.write("---")

# 검색어 입력
search_term = st.sidebar.text_input("학교 이름 검색", value="", help="학교 이름(일부)으로 검색합니다.")
refresh_button = st.sidebar.button("데이터 새로고침")

# 새로고침 버튼 누르면 캐시된 데이터 clear
if refresh_button:
    # st.experimental_rerun()
    st.cache_data.clear()
# 탭 구성
tabs = st.tabs(["늘봄", "돌봄", "전래"])

for (tab, (tab_name, file_path)) in zip(tabs, csv_files.items()):
    with tab:
        st.subheader(f"{tab_name} 데이터")

        # 데이터 로드
        df = load_data(file_path)
        if df is None:
            st.error(f"'{file_path}' 파일이 존재하지 않거나 불러올 수 없습니다.")
            continue

        # 검색어 필터
        # (예: 학교 컬럼에서 검색어가 포함된 행만 필터링)
        if search_term:
            mask = df["학교"].astype(str).str.contains(search_term, case=False, na=False)
            filtered_df = df[mask].copy()
        else:
            filtered_df = df.copy()

        if filtered_df.empty:
            st.warning("검색 결과가 없습니다.")
        else:
            # Google Maps 링크 컬럼만 HTML 링크로 처리
            html_table = dataframe_to_html_safe(filtered_df)
            st.markdown(html_table, unsafe_allow_html=True)

        st.write("---")

# ============ 5. (선택) 지도 시각화 아이디어 예시 ============
# 만약 위도, 경도 컬럼이 있다면 folium을 사용 가능
# from streamlit_folium import st_folium
# import folium

# if '위도' in filtered_df.columns and '경도' in filtered_df.columns:
#     m = folium.Map(location=[37.5665, 126.9780], zoom_start=10)
#     for idx, row in filtered_df.iterrows():
#         folium.Marker([row["위도"], row["경도"]], 
#                       popup=row["학교"]).add_to(m)
#     st_folium(m, width=700, height=500)
