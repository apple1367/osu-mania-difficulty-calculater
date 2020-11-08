#-*-coding: UTF-8-*-

import sys
import os
import os.path
import shutil
import hashlib
import math

if not os.path.exists("./TEMP/collection"):
    os.makedirs("./TEMP/collection")

def get_files(location,lists): 
    for (root, dirs, files) in os.walk(location):
        if len(files) > 0:
            for file_name in files:
                lists.append(root + "/" + file_name)
    del dirs

file_list = []
get_files("./songs/",file_list)
file_list_osu = [file for file in file_list if file.endswith(".osu")]

mania = "Mode: 3\n"

not_mania_files = []

for file in file_list_osu:
    osutxt_file = open(file,"r",encoding="utf8")
    osutxt_line = osutxt_file.readlines()
    # for line in osutxt_line:
    #     line.rstrip('\n')

    if mania in osutxt_line:
        print("{0} is mania".format(file))
    else:
        print("{0} is not mania.".format(file))
        file_list_osu.remove(file)
        not_mania_files.append(file)
#마니아 모드인지 확인. 아니라면 '마니아 아님' 리스트에 추가.

print("\n\nosu 마니아 파일이 로드되었습니다... 전체 파일 " + str(len(file_list_osu)) + "개")
print("osu mania files loaded... total " + str(len(file_list_osu)) + " files\n")

advanced = int(input("기본 설정으로 실행: 0\nstart with recommanded setting: 0\n사용자 지정 설정으로 실행: 1\nstart with costomized setting: 1\n"))
if advanced == 1:
    trill_number = int(input("\n상위 몇개 그룹을 제외할것인가요? (범위 0~20, 추천값 4)\nHow many groups to remove from above?\n(숫자가 클수록 순간 밀도 반영률이 떨어집니다. 5이상일시 난이도 계산이 매우 부정확해질수 있습니다.)\nhigher the number, lower peak density apply.\n"))
    max_group = int(input("몇번째 그룹까지 더할까요? (범위 20~200, 추천값 100)\nHow many groups to add?\n(숫자가 클수록 긴 곡이 고평가됩니다. 평균적인 리듬게임곡은 60~80개의 그룹을 가집니다.)\nhigher the number, long songs rated more.\n"))
    common_ratio = float(input("가중치는 얼마로 할까요? (범위 0.99~0.8, 추천값 0.965)\nWeighted common ratio?\n(숫자가 클수록 평균값의 반영률이 높아집니다.)\nhigher the number, mean density rated more.\n"))
else:
    trill_number = 4
    max_group = 100
    common_ratio = 0.965

def get_diff(file):

    Timing = []
    HitObjects = []
    chunk = []
    group = []
    group_cal = []

    osutxt_file = open(file,"r",encoding="utf8")
    osutxt_line = osutxt_file.readlines()
    location_timing = osutxt_line.index("[TimingPoints]\n")
    location_hitobj = osutxt_line.index("[HitObjects]\n")
    timing_points = osutxt_line[location_timing+1:location_hitobj-1]

    for values in timing_points:
        valuelist1 = values.split(',')
        if len(valuelist1) > 2:
            if float(valuelist1[1]) > 0:
                Timing.append(valuelist1[0:2])
            else:
                continue
    file_name = str(file).split('/')            
    print(str(file_name[3:]))
    #타이밍 포인트들을 읽어서 양수값 (BPM값)만 읽어오기.

    HitObject_lines = osutxt_line[location_hitobj + 1:]
    for values in HitObject_lines:
        valuelist2 = values.split(',')
        HitObjects.append(valuelist2[2])
        # if int(valuelist2[3]) != 128:
        #     HitObjects.append(valuelist2[2])
        # else:
        #     continue

    #롱노트 보정

    HitObjects.sort(key=int)


    song_len = int(HitObjects[-1]) + 15000
    first_timing = Timing[0]
    first_beat = float(first_timing[0])

    while first_beat > 0:
        first_beat -= float(first_timing[1])*4
    
    chunk.append(first_beat)

    for i in range(len(Timing)):
        timings = Timing[i]
        if len(Timing) > i+1:
            nexttiming = Timing[i+1]
        else:
            nexttiming = [song_len,timings[1]]

        chunklen = float(timings[1])*4

        while float(chunk[-1]) <= float(nexttiming[0]):
            chunk.append(float(chunk[-1])+chunklen)
        del chunk[-1]


    # print (Timing)
    # print(chunk)
    for i in range(len(chunk)-1):
        
        chunk_value = []
        del chunk_value[0:] 
        note_count = 0


        if i == 0:
            for notes in HitObjects:
                if float(chunk[i]) > int(notes):
                    note_count += 1
            chunk_value.append(note_count)
            chunk_value.append(float(chunk[1])-float(chunk[0]))
            del HitObjects[:note_count]

        elif i < len(chunk):
            for notes in HitObjects:
                if float(chunk[i]) > int(notes):
                    note_count += 1
            chunk_value.append(note_count)
            chunk_value.append(float(chunk[i+1])-float(chunk[i]))
            del HitObjects[:note_count]
            
        else:
            for notes in HitObjects:
                note_count += 1
            chunk_value.append(note_count)
            chunk_value.append(float(chunk[i])-float(chunk[i-1]))
            del HitObjects[:note_count]
        group.append(chunk_value)
    #노트 수 구하기
    # print (group)
    for gr in group:
        group_cal.append(int(gr[0])*(240000/float(gr[1])))
    
    group_cal.sort(key=float,reverse=True)

    if advanced ==1:
        print("Peak :" + str(group_cal[0]))
        print("Peak_alt :" + str(group_cal[trill_number]))

    del group_cal[:trill_number]
    #가장 높은 2개의 값 제거

    while len(group_cal) < max_group + 1:
        group_cal.append(0)
    #전체 그룹 갯수 맞춰주기

    weighted_group = []
    for i in range(max_group):
        a = group_cal[i]*pow(common_ratio ,i)
        weighted_group.append(a)

    songdiff = sum(weighted_group)

    return songdiff

for file in file_list_osu:
    try:
        diff = get_diff(file)
        print("diff :" + str(diff) + "\n")
        hash = hashlib.md5(open(file, "rb").read()).hexdigest()
    except:
        print("에러가 발생했습니다. 문제가 되는 파일을 apple191246@gmail.com 으로 보내주세요.\n")
        continue
    if advanced == 1:
        print("hash :" + str(hash) + "\n")









