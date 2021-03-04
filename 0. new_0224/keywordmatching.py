# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %%
# 데이터셋 불러오기
df_2021 = pd.read_csv(
    '/Users/ryu/PycharmProjects/pythonstudy/paper/1. rawdata/2021.csv')
# df_2017 = pd.read_csv('2017.csv')
# df_2018 = pd.read_csv('2018.csv')
# df_2019 = pd.read_csv('2019.csv')
# df_2020 = pd.read_csv('2020.csv')

# %%
# 데이터셋 합치기
df_2021["연도"] = 2021
# df_2017["연도"] = 2017
# df_2018["연도"] = 2018
# df_2019["연도"] = 2019
# df_2020["연도"] = 2020

# df_concat = pd.concat([df_2016, df_2017, df_2018, df_2019, df_2020])
df_concat = df_2021[["교수명(대학명)", "논문명", "키워드", "연도"]]
# df_concat = df_concat[["교수명(대학명)", "논문명", "키워드", "연도"]]
# df_concat.groupby("연도").count()

# %%
# 데이터 클리닝
df_concat = df_concat.rename(columns={"교수명(대학명)": "KEY"})
df_concat["KEY"] = df_concat["KEY"].str.strip()
df_concat["KEY"] = df_concat["KEY"].str.replace(" ", "")
df_concat["키워드"] = df_concat["키워드"].fillna(value="")
df_concat.sort_values(by="연도", ascending=False, inplace=True)

for_category = df_concat.copy()
for_paper = df_concat.copy()
for_keyword = df_concat.copy()
for_category = for_category.rename(columns={"키워드": "논문키워드"})
for_category = for_category.reset_index(drop=True)

# %%
# mapping data 불러오기
matching_data = pd.read_csv(
    '/Users/ryu/PycharmProjects/pythonstudy/paper/1. rawdata/mappingdata_v3.csv')
matching_data
matching = matching_data[["논문키워드", "연구실키워드"]]
matching = matching.fillna("N/A")
matching["논문키워드"] = matching["논문키워드"].str.lower()
matching = matching.drop_duplicates(["논문키워드"], keep="first")  # 겹치는항목 제거
print("현재 매칭된 데이터 수는 " + str(len(matching_data)) + "개 입니다.")

# %%
# 키워드 데이터 쪼개기 (;을 기준으로)
for_category["논문키워드"] = for_category["논문키워드"].str.replace(" ", "")
for_category["논문키워드"] = for_category["논문키워드"].str.replace("\n", "")
for_category["논문키워드"] = for_category["논문키워드"].str.lower()
for i in range(0, len(for_category)):
    if for_category.loc[i, '논문키워드'] is None:  # 키워드가 비었을경우
        continue
    split_keyword = for_category.loc[i, '논문키워드'].split(';')  # ;을 기준으로 키워드 분리
    for j in range(0, len(split_keyword)):
        key = "keyword_{}".format(j)
        for_category.loc[i, key] = split_keyword[j]

# %%
# keyword_0 == "데이터없음"의 의미는 논문이 없는 경우

for_category_columns = for_category.columns.str.contains("keyword")
keyword_count = for_category_columns.sum()


a = for_category.count()
keyword_total = 0
for i in range(4, 3+keyword_count):
    print(a[i])
    keyword_total += a[i]

print("총 키워드 수 : {}개".format(keyword_total))
print("한 논문 최대 키워드 수 : {}개".format(keyword_count))

# %%
vlookup = for_category.copy()
vlookup
for i in range(0, keyword_count):
    key = "keyword_{}".format(i)
    vlookup_1 = vlookup.join(matching.set_index('논문키워드')['연구실키워드'], on=key)
    vlookup[i] = vlookup_1['연구실키워드']
vlookup.to_csv("확인필요.csv", encoding="utf-8-sig")

# %%
# 분류필요한 키워드 찾기 (need_mapping.csv로 저장)

x = 0
for j in range(0, keyword_count):
    for i in range(0, len(vlookup)):
        if pd.isnull(vlookup.loc[i, "keyword_{}".format(j)]) != pd.isnull(vlookup.loc[i, j]) and vlookup.loc[i, "keyword_{}".format(j)] != "" and vlookup.loc[i, "keyword_{}".format(j)] != "데이터없음":
            matching.loc[len(matching)+x, "논문키워드"] = vlookup.loc[i,
                                                                 "keyword_{}".format(j)]
            x += 1
print(str(x) + "개 분류필요")

need_mapping = matching.drop_duplicates(["논문키워드"])
need_mapping = need_mapping.reset_index(drop=True)
need_mapping = need_mapping[["논문키워드", "연구실키워드"]]
print(need_mapping)
need_mapping.to_csv("need_mapping.csv", encoding="utf-8-sig")

# %%
category_list = ["비즈니스/정책", "문화컨텐츠", "인지공학/심리", "소셜/SNS", "협업/CSCW", "Robot/HRI", "자동차/모빌리티", "IoT/정보가전",
                 "공간/환경", "게임/영상", "미디어아트", "인터랙션디자인", "사용자경험/서비스디자인", "지속가능/접근성/UD", "클라우드/엣지컴퓨팅",
                 "음성/비전/뇌인터페이스", "그래픽스/시각화", "감성디자인", "디자인방법론/문화", "모바일/웹", "유비쿼터스/웨어러블",
                 "헬스케어/의료", "NUI/Haptics", "교육/어린이/노인", "가상/증강현실", "빅데이터/인공지능"]

# %%
for j in range(0, len(vlookup)):
    for category in category_list:
        a = 0
        for i in range(0, keyword_count):
            if vlookup.loc[j, i] == category:
                a += 1
        vlookup.loc[j, category] = a
vlookup.to_csv("vlookup결과.csv", encoding="utf-8-sig")

# %%
# 연도별 통계내기
stats_2016 = vlookup[vlookup["연도"] == 2016]
stats_2017 = vlookup[vlookup["연도"] == 2017]
stats_2018 = vlookup[vlookup["연도"] == 2018]
stats_2019 = vlookup[vlookup["연도"] == 2019]
stats_2020 = vlookup[vlookup["연도"] == 2020]

# %%
stats_categ = 0
count_categ_2016 = []
count_categ_2017 = []
count_categ_2018 = []
count_categ_2019 = []
count_categ_2020 = []

for i in category_list:
    stats_categ = int(stats_2016[i].sum())
    count_categ_2016.append(stats_categ)

for i in category_list:
    stats_categ = int(stats_2017[i].sum())
    count_categ_2017.append(stats_categ)

for i in category_list:
    stats_categ = int(stats_2018[i].sum())
    count_categ_2018.append(stats_categ)

for i in category_list:
    stats_categ = int(stats_2019[i].sum())
    count_categ_2019.append(stats_categ)

for i in category_list:
    stats_categ = int(stats_2020[i].sum())
    count_categ_2020.append(stats_categ)


statstics_5year = pd.DataFrame({"2016": count_categ_2016, "2017": count_categ_2017, "2018": count_categ_2018,
                                "2019": count_categ_2019, "2020": count_categ_2020},  index=category_list)

statstics_5year.to_csv('statstics_5year.csv', encoding="utf-8-sig")

# %%
# 교수님 단위로 합치는 단계

for_pivot = vlookup[["KEY", "비즈니스/정책", "문화컨텐츠", "인지공학/심리", "소셜/SNS", "협업/CSCW", "Robot/HRI", "자동차/모빌리티", "IoT/정보가전",
                     "공간/환경", "게임/영상", "미디어아트", "인터랙션디자인", "사용자경험/서비스디자인", "지속가능/접근성/UD", "클라우드/엣지컴퓨팅",
                     "음성/비전/뇌인터페이스", "그래픽스/시각화", "감성디자인", "디자인방법론/문화", "모바일/웹", "유비쿼터스/웨어러블",
                     "헬스케어/의료", "NUI/Haptics", "교육/어린이/노인", "가상/증강현실", "빅데이터/인공지능"]]

count = for_pivot.groupby("KEY").sum()
count_reset = count.reset_index()
# count_reset[count_reset["prof"].str.contains("가천")]
count_reset = count_reset.sort_values(by="KEY")
# for category in category_list:    ## 키워드 1개인 항목 제거
#     for j in range(0,len(count_reset)):
#         if count_reset.loc[j,category] == 1:
#             count_reset.loc[j,category] -= 1
count_reset

count_reset.to_csv('statistics_prof.csv', encoding="utf-8-sig")

# %%
new = pd.DataFrame()
a = 0
for i in category_list:
    new.loc[a, 0] = i
    new.loc[a, 1] = int(count_reset[i].sum())
    a += 1

new.to_csv("statistics.csv", encoding="utf-8-sig")

print("분류된 논문 키워드 수는 " + str(int(new[1].sum())) + "개 입니다.")

# %%
final = count_reset.copy()
b = []
for i in range(0, len(count_reset)):
    a = []
    for category in category_list:
        if count_reset.loc[i, category] > 0:
            # 각 논문마다 키워드 합치기, 튜플형으로 (ex. 2,'IoT/정보가전')
            a.append((int(count_reset.loc[i, category]), category))
    b.append(a)
for i in range(0, len(final)):
    b[i] = sorted(b[i], reverse=True)

    if b[i] == []:
        continue

    final.loc[i, "interests"] = ""
    x = 0
    for j in range(0, len(b[i])):
        if x > 4:
            continue
        final.loc[i, "interests"] += ' #' + b[i][j][1]
#             + "(" + str(b[i][j][0]) + ") " ## 각 키워드당 몇번 나왔는지
        x += 1

final.to_csv("./result/연구실키워드추출.csv", encoding="utf-8-sig")

# %%
# 논문 합치기 시작

print(len(for_paper))
for_paper["논문명"]

# %%
for_paper_combine = for_paper

prof_list = for_paper_combine["KEY"].unique()  # 교수님 list화

prof_paper_dictionary = {}
paper_combine = pd.DataFrame()

for prof_detail in prof_list:
    prof_paper_df = for_paper[for_paper["KEY"] == prof_detail]
    prof_paper_df = prof_paper_df.reset_index()
    if pd.isnull(prof_paper_df.loc[0, "논문명"]) == True:
        continue
    else:
        prof_paper_dictionary[prof_detail] = prof_paper_df.loc[0, "논문명"]
        a = 0
        for i in range(1, len(prof_paper_df)):
            prof_paper_dictionary[prof_detail] += (
                "<br>" + prof_paper_df.loc[i, "논문명"])
            a += 1
#         print(prof_detail,a,len(prof_paper_df))

for prof_detail in prof_list:
    if (prof_detail in prof_paper_dictionary) == False:
        prof_paper_dictionary[prof_detail] = "논문없음"
        paper_combine.loc[prof_detail, 1] = prof_paper_dictionary[prof_detail]
    else:
        paper_combine.loc[prof_detail, 1] = prof_paper_dictionary[prof_detail]

paper = paper_combine.reset_index()
paper.columns = ["KEY", "논문명"]
paper.to_csv("./result/논문명 추출.csv", encoding="utf-8-sig")

# %%
# 키워드 합치기

for_keyword

prof_keyword_dictionary = {}
keyword_combine = pd.DataFrame()

for prof_detail in prof_list:
    prof_keyword_df = for_keyword[for_keyword["KEY"] == prof_detail]
    prof_keyword_df = prof_keyword_df.reset_index()

    if pd.isnull(prof_keyword_df.loc[0, "키워드"]) == True:
        continue

    else:
        prof_keyword_dictionary[prof_detail] = prof_keyword_df.loc[0, "키워드"]
        if prof_keyword_dictionary[prof_detail] == "키워드없음":
            prof_keyword_dictionary[prof_detail] = ""
        a = 0
        for i in range(1, len(prof_keyword_df)):
            if prof_keyword_df.loc[i, "키워드"] == "키워드없음":
                prof_keyword_df.loc[i, "키워드"] == ""
            else:
                prof_keyword_dictionary[prof_detail] += (
                    " " + prof_keyword_df.loc[i, "키워드"])
                a += 1


prof_keyword_dictionary

for prof_detail in prof_list:
    if (prof_detail in prof_keyword_dictionary) == False:
        prof_keyword_dictionary[prof_detail] = "논문없음"
        keyword_combine.loc[prof_detail,
                            1] = prof_keyword_dictionary[prof_detail]
    else:
        keyword_combine.loc[prof_detail,
                            1] = prof_keyword_dictionary[prof_detail]

keyword = keyword_combine.reset_index()


keyword[1] = keyword[1].str.replace(";", " #")
keyword[1] = keyword[1].str.strip()
keyword[1] = keyword[1].apply(lambda x: "#" + x)
keyword.columns = ["KEY", "논문키워드"]
keyword.to_csv("./result/키워드추출.csv", encoding="utf-8-sig")
keyword

# %%
prof_interests = final[["KEY", "interests"]]

# %%
###### 마무리 ########

complete = prof_interests.join(paper.set_index('KEY')['논문명'], on="KEY")
complete = complete.join(keyword.set_index('KEY')['논문키워드'], on="KEY")

complete.to_csv("./final/HCI_연구실_DB_v3.csv", encoding="utf-8-sig")
complete
