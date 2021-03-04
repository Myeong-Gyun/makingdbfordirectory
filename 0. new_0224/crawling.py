# %%
from bs4 import BeautifulSoup
import urllib.request
import re
import datetime
import pandas as pd
import requests
from selenium import webdriver
import time
import numpy as np
import unicodedata

# %%
# 찾고자하는 학술집 url, HCIK 학술대회용

url = 'https://www.dbpia.co.kr/journal/voisDetail?voisId=VOIS00629640'
# %%
# 크롬 실행
# 크롬 버전 체크하여 웹드라이버 다운
# https://chromedriver.chromium.org/downloads
driver = webdriver.Chrome(
    '/Users/ryu/PycharmProjects/pythonstudy/chromedriver')
driver.implicitly_wait(3)

# %%
# 페이지 전체 로드하기
driver.get(url)

while str(driver.find_element_by_class_name('viewMore').text) != "":
    driver.find_element_by_class_name('viewMore').click()
    time.sleep(1)
# %%
# 전체 NODE 얻기
# 권호 내 총 논문수와 비교하기

html = driver.page_source
soup_html = BeautifulSoup(html, 'html.parser')
journal_title = soup_html.find(
    'div', class_="headingArea schDetail").text.strip()


node_div = soup_html.find_all('div', class_='titWrap')
creativeaward = int(str(soup_html.select(
    '.listBody > p + ul  .titWrap')[0].find('a'))[72:80])
node = []
count_creatieaward = 0
for i in range(1, len(node_div)):
    node_a = str(node_div[i].find('a'))
    node_number = int(node_a[72:80])
    if node_number < creativeaward:
        node.append(node_number)
    else:
        count_creatieaward += 1

print("[" + journal_title + "] 논문 수는 " + str(len(node)+count_creatieaward +
                                             1) + "개 입니다." + "(" + str(len(node))+"개 논문(목차, Creative award 제외)")

# %%
# 데이터 얻기, 교수명(대학명) / 논문명 / 키워드

df = pd.DataFrame()
df["교수명(대학명)"] = []
df["논문명"] = []
df["키워드"] = []

j = 0
journal_year_find = journal_title.find('20')
journal_year = journal_title[journal_year_find:journal_year_find+4]

for i in node:
    url = "https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE{}".format(
        i)
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
    title = soup.head.find("meta", {"name": "citation_title"}).get(
        'content').strip() + "(" + journal_year + ")"
    author = soup.find('p', class_="author").get_text().strip()
    author_re = unicodedata.normalize("NFC", author).strip().split(",")
    lastauthor = str(author_re[-1].strip())
    keyword = soup.head.find("meta", {"name": "citation_keywords"})
    if keyword == None:
        keyword = "키워드없음"
    else:
        keyword = keyword.get('content')
        print(title)
    df.loc[j, "교수명(대학명)"] = lastauthor
    df.loc[j, "논문명"] = title
    df.loc[j, "키워드"] = keyword
    j += 1
print("NODE 얻기 완료 (NODE0*******)")

# %%
modify_prof = df.copy()
# %%
# 교수명(대학명) 확인 작업
for i in range(0, len(df)):
    uni = modify_prof.loc[i, "교수명(대학명)"]
    title = modify_prof.loc[i, "논문명"]
    if uni == None:
        continue
    elif uni[-4:-1] == "대학교":
        continue
    elif uni[-5:-1] == "SMIT":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-6] + "(SMIT(서울미디어대학원대학교))"
    elif uni[-5:-2] == "기술원":
        continue
    elif uni[-6:-1] == "KAIST":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-7] + "(KAIST(한국과학기술원))"
    elif uni[-8:-1] == "한국과학기술원":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-9] + "(KAIST(한국과학기술원))"
    elif uni[-5:-1] == "카이스트":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-6] + "(KAIST(한국과학기술원))"
    elif uni[-5:-1] == "유니스트":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-6] + "(UNIST(울산과학기술원))"
    elif uni[-6:-1] == "UNIST":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-7] + "(UNIST(울산과학기술원))"
    elif uni[-8:-1] == "울산과학기술원":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-9] + "(UNIST(울산과학기술원))"
    elif uni[-5:-1] == "GIST":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-6] + "(GIST(광주과학기술원))"
    elif uni[-8:-1] == "광주과학기술원":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-9] + "(GIST(광주과학기술원))"
    elif uni[-10:-1] == "대구경북과학기술원":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-11] + "(DGIST(대구경북과학기술원))"
    else:
        print(uni, title)
        prof_eng_to_kor = input("새로운 교수명(대학명)을 입력하세요. 행을 지우고 싶으면 공백을 입력하세요.")
        if prof_eng_to_kor == "":
            modify_prof.loc[i, "교수명(대학명)"] = None
        else:
            modify_prof.loc[i, "교수명(대학명)"] = prof_eng_to_kor


# %%
# 한번더 체크

for i in range(0, len(df)):
    uni = modify_prof.loc[i, "교수명(대학명)"]
    if uni == None:
        continue
    elif uni[-4:-1] == "대학교":
        continue
    elif uni[-5:-1] == "SMIT":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-6] + "(SMIT(서울미디어대학원대학교))"
    elif uni[-5:-2] == "기술원":
        continue
    elif uni[-6:-1] == "KAIST":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-7] + "(KAIST(한국과학기술원))"
    elif uni[-8:-1] == "한국과학기술원":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-9] + "(KAIST(한국과학기술원))"
    elif uni[-5:-1] == "카이스트":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-6] + "(KAIST(한국과학기술원))"
    elif uni[-5:-1] == "유니스트":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-6] + "(UNIST(울산과학기술원))"
    elif uni[-6:-1] == "UNIST":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-7] + "(UNIST(울산과학기술원))"
    elif uni[-8:-1] == "울산과학기술원":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-9] + "(UNIST(울산과학기술원))"
    elif uni[-5:-1] == "GIST":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-6] + "(GIST(광주과학기술원))"
    elif uni[-8:-1] == "광주과학기술원":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-9] + "(GIST(광주과학기술원))"
    elif uni[-10:-1] == "대구경북과학기술원":
        modify_prof.loc[i, "교수명(대학명)"] = uni[:-11] + "(DGIST(대구경북과학기술원))"
    else:
        print(uni)
        prof_eng_to_kor = input("새로운 교수명(대학명)을 입력하세요. 행을 지우고 싶으면 공백을 입력하세요.")
        if prof_eng_to_kor == "":
            modify_prof.loc[i, "교수명(대학명)"] = None
        else:
            modify_prof.loc[i, "교수명(대학명)"] = prof_eng_to_kor
# %%
# 카피해서 저장
only_prof = modify_prof.copy()
only_prof = only_prof.dropna(subset=["교수명(대학명)"])
only_prof = only_prof.reset_index(drop=True)
only_prof.to_csv("{}.csv".format(journal_title), encoding="utf-8-sig")

# %%
