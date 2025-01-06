import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import schedule
import time
import urllib.parse  # Google Maps 링크 생성용
from datetime import datetime

# 크롤링할 URL과 기본 파라미터
url = "https://www.goe.go.kr/home/job/jobOfferList.do"
base_params = {
    "menuId": "100000000000208",
    "menuInit": "12,2,1,2",
    "programId": "PGM_0000000002",
    "pageIndex": 1,
    "sJobOfferCd": "020",
    "jobOfferSeq": "",
    "sAreaCd": "화성오산",
    "sSchoolCd": "초등",
    "jobYn": "",
    "schKey": "SUBJECT",
}

# 헤더 추가
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Google Geocoding API 키 환경 변수에서 읽기
# import os
# GEOCODING_API_KEY = os.getenv("GEOCODING_API_KEY")
GEOCODING_API_KEY= "AIzaSyDCq55eaWc2NpJcflRt13JjnNG9-IRPksA"

# 학교 주소와 Google Maps 링크를 가져오는 함수
def fetch_school_address_and_link(school_name):
    google_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": school_name,
        "key": GEOCODING_API_KEY,
        "language": "ko"  # 주소를 한국어로 반환하도록 설정
    }
    response = requests.get(google_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK" and data["results"]:
            address = data["results"][0]["formatted_address"]
            # Google Maps 링크 생성
            google_maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(address)}"
            return address, google_maps_link
    return "주소를 찾을 수 없음", "링크를 생성할 수 없음"

# 데이터를 요청하고 처리하는 함수
def fetch_data(sch_val):
    params = base_params.copy()
    params["schVal"] = sch_val
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")

        # 게시글 목록 추출
        rows = soup.select("table tbody tr")
        posts = []
        if rows:
            for row in rows:
                columns = row.find_all("td")
                if len(columns) >= 6:
                    school_name = columns[2].get_text(strip=True)
                    title = columns[3].get_text(strip=True)
                    reg_date = columns[4].get_text(strip=True)
                    end_date = columns[5].get_text(strip=True)

                    # 학교 이름으로 주소와 링크 가져오기
                    address, google_maps_link = fetch_school_address_and_link(school_name)
                    time.sleep(1)  # API 호출 간 딜레이

                    posts.append({
                        "번호": columns[0].get_text(strip=True),
                        "학교": school_name,
                        "타이틀": title,
                        "등록일": reg_date,
                        "마감일": end_date,
                        "주소": address,
                        "Google Maps 링크": google_maps_link,
                        "수집일": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
        return posts
    else:
        print(f"HTTP 요청 실패: {response.status_code}")
        return []

# 새로운 데이터를 CSV에 추가
def update_csv(file_name, sch_val):
    new_data = fetch_data(sch_val)
    try:
        # 기존 데이터 읽기
        existing_data = pd.read_csv(file_name)
    except FileNotFoundError:
        # 파일이 없으면 새로운 데이터만 저장
        pd.DataFrame(new_data).to_csv(file_name, index=False, encoding="utf-8-sig")
        print(f"{file_name} 파일 생성 및 데이터 저장 완료")
        return

    # 데이터 비교 및 중복 제거
    existing_data = existing_data.astype(str)
    new_data_df = pd.DataFrame(new_data).astype(str)

    combined_data = pd.concat([new_data_df, existing_data]).drop_duplicates(subset=["번호", "학교", "타이틀"], keep="first")
    
    if len(combined_data) > len(existing_data):
        combined_data.to_csv(file_name, index=False, encoding="utf-8-sig")
        print(f"{file_name} 업데이트 완료: {len(combined_data) - len(existing_data)}개의 새로운 항목 추가됨")
    else:
        print(f"{file_name} 업데이트 없음: 변화없음")

# 5분마다 실행
def scheduled_task():
    print("데이터 업데이트 시작")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    update_csv("늘봄_data_with_links.csv", "늘봄")
    update_csv("돌봄_data_with_links.csv", "돌봄")
    update_csv("전래_data_with_links.csv", "전래")
    print("데이터 업데이트 완료")

# 스케줄 설정
scheduled_task()  # 처음 실행
# schedule.every(5).minutes.do(scheduled_task)
schedule.every().day.at("10:00").do(scheduled_task)  # 매일 10시에 실행
schedule.every().day.at("17:00").do(scheduled_task)  # 매일 17시에 실행
# 스케줄 실행
if __name__ == "__main__":
    print("스케줄러 시작")
    while True:
        schedule.run_pending()
        time.sleep(1)
