import streamlit as st
import pandas as pd

# Streamlit 화면 설정
st.set_page_config(layout="wide")

# CSV 파일 읽기
늘봄_data = pd.read_csv("늘봄_data_with_links.csv")
돌봄_data = pd.read_csv("돌봄_data_with_links.csv")
전래_data = pd.read_csv("전래_data_with_links.csv")

# 데이터프레임에 하이퍼링크 추가
def add_hyperlinks(df):
    df["Google Maps 링크"] = df["Google Maps 링크"].apply(
        lambda x: f'<a href="{x}" target="_blank">Google Maps 열기</a>'
    )
    return df

늘봄_data = add_hyperlinks(늘봄_data)
돌봄_data = add_hyperlinks(돌봄_data)
전래_data = add_hyperlinks(전래_data)

# Streamlit UI
st.title("학교 정보 및 Google Maps 링크")
st.write("아래 데이터를 통해 각 학교와 관련된 정보를 확인하고, Google Maps 링크를 클릭하세요.")

# 탭으로 구분하여 데이터 표시
tabs = st.tabs(["늘봄", "돌봄", "전래"])
for tab, data, title in zip(tabs, [늘봄_data, 돌봄_data, 전래_data], ["늘봄", "돌봄", "전래"]):
    with tab:
        st.subheader(f"{title} 데이터")
        # HTML을 포함하여 테이블 표시
        st.markdown(
            data.to_html(escape=False, index=False), unsafe_allow_html=True
        )