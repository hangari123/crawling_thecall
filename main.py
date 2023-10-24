from datetime import datetime
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from pyvirtualdisplay import Display

# 서버에서 크론탭 돌리면 절대경로로 해줘야 제대로 작동함
# file_path = '/home/user/crawling_thecall/data.xlsx'
file_path = 'data.xlsx'




# 기존 데이터를 불러올 때, 데이터 타입을 문자열(str)로 변환합니다.
try:
    existing_data_df = pd.read_excel(file_path, dtype={'number': str})

except Exception as e:
    print("엑셀파일이 없어 새로운 파일을 만듭니다.")

    # 데이터프레임 생성
    data = {
        'number': [''],  # 예시 데이터, 원하는 데이터로 변경
        'description': ['']  # 예시 데이터, 원하는 데이터로 변경
    }

    df = pd.DataFrame(data)

    # 엑셀 파일로 저장
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')  # 데이터프레임을 엑셀 시트에 저장

    print("엑셀파일 생성완료")

    existing_data_df = pd.read_excel(file_path, dtype={'number': str})


data = []
url = 'https://www.thecall.co.kr/bbs/board.php?bo_table=phone'

chrome_options = webdriver.ChromeOptions()

# 헤더 설정
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
chrome_options.add_argument('referer=https://www.google.com/')  # Referer 설정

# 우분투에서 셀레니움 쓸라면 이거 설정해야함
display = Display(visible=0, size=(1920, 1080))
display.start()

chrome_driver_path = '/usr/local/bin/chromedriver'  # 적절한 경로로 변경
service = webdriver.chrome.service.Service(chrome_driver_path)

# 웹 드라이버 생성 및 옵션 설정
driver = webdriver.Chrome(options=chrome_options, service=service)

# driver = webdriver.Chrome()

driver.get(url)

html = driver.page_source

# BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(html, 'html.parser')

# 모든 <article> 태그를 선택
articles = soup.find_all('article')

# 각 <article> 태그에서 <a> 태그와 <p> 태그의 텍스트 가져오기
for article in articles:
    # <a> 태그의 텍스트 가져오기
    a_tag_text = article.find('a').text.strip()

    # <p> 태그의 텍스트 가져오기
    p_tag_text = article.find('p').text.strip()

    # 데이터를 딕셔너리로 저장
    item = {
        'number': a_tag_text,
        'description': p_tag_text
    }

    # 중복 데이터 확인
    if not existing_data_df['number'].str.contains(a_tag_text).any():
        data.append(item)



# 기존 데이터를 불러와서 데이터프레임으로 변환 (이전에 저장한 엑셀 파일을 읽어올 수 있도록 경로 설정 필요)
# existing_data_df = pd.read_excel('data.xlsx', dtype={'number': str})

# 새로운 데이터를 데이터프레임으로 변환
new_data_df = pd.DataFrame(data)

# 기존 데이터와 새로운 데이터를 합칩니다.
combined_df = pd.concat([existing_data_df, new_data_df], ignore_index=True)

# 데이터를 엑셀 파일로 저장 (ExcelWriter를 사용하여 원하는 파일 이름과 경로 지정)
file_path = 'data.xlsx'  # 원하는 파일 경로 및 이름 설정
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    combined_df.to_excel(writer, index=False, sheet_name='Sheet1')
    print("데이터가 추가됏습니다.1")


# 현재 시간 출력
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f'{current_time}: 데이터가 {file_path} 파일에 추가되었습니다.')

# 드라이버 종료
driver.quit()

# 가상 디스플레이 종료
display.stop()