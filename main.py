import sys
import os
import os.path
import shutil
import hashlib
import math
import struct
import logging
from tqdm import tqdm, trange
from diff1 import get_diff, diff_name, diff_type, diff_version
import time

Thistime = time.ctime()
#형태
#get_diff(bm)
#bm 파일 내에는 모든게 다 있음.
#group 들은 note들을 포함함.
#beatmap 은 group 들을 포함함.


OSU_BYTE = 1
OSU_INT = 4


#할꺼
#diff 만들기.
#난이도에 따라 컬렉션에 추가하는 부분 만들기.
#가중치 매기는거 묻는 함수 diff 에 넣기.
#가중치 매기는 부분 diff에 넣기.

#멀티프로세싱

class Note:
    def __init__(self):
        self.timing = 0 # 노트의 타이밍
        self.type = 0 # 0: 단놋 1: 롱놋시작 2:롱놋끝
        self.line = 0 # 노트의 라인

class Group:
    def __init__(self):
        self.timing = 0
        self.bpmms = 600.0
        self.notes = []
        self.single = []
        self.LNstart = []
        self.LNend = []
        self.diff = 0.0

class Pattern:
    def __init__(self):
        self.isConnecter = False
        self.isFLN = False
        self.isJack = False
        self.isStream = False

class Beatmap:
    def __init__(self):
        self.name = ""
        self.OD = 0
        self.Keys = 0
        self.groups = [] # 타이밍 계산으로 그룹을 만듬.
        self.hash = ""
        self.location = ""
        self.difficulty = 0.0

class Collection:
    def __init__(self):
        self.name = ""
        self.beatmaps = []

class Collection_file:
    def __init__(self):
        self.version = 0
        self.collections = []

def parse_string(fileobj):
    indicator = fileobj.read(1)
    if ord(indicator) == 0:
        return ""
    elif ord(indicator) == 11:
        uleb = parse_uleb128(fileobj)
        s = fileobj.read(uleb).decode('utf-8')
        return s
    else:
        return

def parse_uleb128(fileobj):
    result = 0
    shift = 0
    while True:
        byte = fileobj.read(1)[0]
        result |= (byte & 0x7F) << shift

        if ((byte & 0x80) >> 7) == 0:
            break
        shift += 7
    return result

def get_int(integer):
    return struct.pack("I", integer)

def get_string(string):
    if not string:
        return bytes([0x00])
    else:
        result = bytes([0x0b])
        result += get_uleb128(len(string))
        result += string.encode('utf-8')
        return result

def get_uleb128(integer):
    cont_loop = True
    result = b''
    while cont_loop:
        byte = integer & 0x7F
        integer >>= 7
        if integer != 0:
            byte |= 0x80
        result += bytes([byte])
        cont_loop = integer != 0
    return result

def get_files(location,lists): 
    for (root, dirs, files) in os.walk(location):
        if len(files) > 0:
            for file_name in files:
                lists.append(root + "/" + file_name)

def parse_collections(path):
    fobj = open("collection.db", 'rb')
    colls = Collection_file()

    version = int.from_bytes(fobj.read(OSU_INT), byteorder='little')
    colls.version = version

    collection_count = int.from_bytes(fobj.read(OSU_INT), byteorder='little')

    for i in range(0, collection_count):
        c = Collection()
   
        collection_name = parse_string(fobj)
        c.name = collection_name

        collection_beatmap_count = int.from_bytes(fobj.read(OSU_INT), byteorder='little')

        for j in range(0, collection_beatmap_count):
            bm = Beatmap()
            bm.hash = parse_string(fobj)
            c.beatmaps.append(bm)

        colls.collections.append(c)

    return colls

print("무한 BPM 이나 0 BPM 에서는 작동이 보장되지 않습니다. \n무한에 가까운 BPM 이거나 0에 가까운 BPM에서는 큰 로딩시간이 필요하며\n몇몇 오투잼 컨버트 곡들은 정상 작동 하지 않습니다.\n")
print("This program does not work with infinite BPM or 0 BPM songs.\nif the beatmap has large(almost infinite) or extreamly small (almost 0) BPM, it takes long times.\nSome O2jam converts does not work.\n")
start = input("press any key to start")

# fobj = open("collection.db", 'rb')

# version = int.from_bytes(fobj.read(OSU_INT), byteorder='little')

# new = Collection_file()

# new.version = version

# collection_count = int.from_bytes(fobj.read(OSU_INT), byteorder='little')

# while True:
#     coll = fobj.read(1024)
#     collline.append(coll)  
#     if len(collline) > 2048:
#         break
#     print(coll)           
colls = parse_collections("collecion.db")
cname_list = []
for a in colls.collections:
    cname_list.append(a.name)

if diff_type == 1:
    for i in range(100):
        c = Collection()
        if i == 0:
            if str(diff_name + " ~01") not in cname_list:
                c.name = diff_name + " ~01"
        elif i == 99:
            if str(diff_name + " 99+") not in cname_list:
                c.name = diff_name + " 99+"
        else:
            if str(diff_name + " " + str(i+1).zfill(2)) not in cname_list:
                c.name = diff_name + " " + str(i+1).zfill(2)
        colls.collections.append(c)
if diff_type == 0:
    for i in range(1000):
        c = Collection()
        if i == 0:
            if str(diff_name + " ~001") not in cname_list:
                c.name = diff_name + " ~001"
        elif i == 999:
            if str(diff_name + " 999+") not in cname_list:
                c.name = diff_name + " 999+"
        else:
            if str(diff_name + " " + str(i+1).zfill(3)) not in cname_list:
                c.name = diff_name + " " + str(i+1).zfill(3)

        colls.collections.append(c)


file_list = []
get_files("./Songs/",file_list)
file_list_osu = [file for file in file_list if file.endswith(".osu")]

mania = "Mode: 3\n"

not_mania_files = []
file_list_mania = []

for i in trange(len(file_list_osu)):
    
    file = file_list_osu[i]
    osutxt_file = open(file,"r",encoding="utf8")
    osutxt_line = osutxt_file.readlines()
    # for line in osutxt_line:
    #     line.rstrip('\n')
    if mania in osutxt_line:
        file_list_mania.append(file)
    else:
        not_mania_files.append(file)
    
    osutxt_file.close()

beatmap_list = []

for file in file_list_mania:
    bm = Beatmap()
    bm.location = file
    beatmap_list.append(bm)

#마니아 모드인지 확인. 아니라면 '마니아 아님' 리스트에 추가.

print("\nosu 마니아 파일이 로드되었습니다...")
print("osu mania files loaded...\n\n")

advanced = int(input("기본 설정으로 실행: 0\nstart with recommanded setting: 0\n사용자 지정 설정으로 실행: 1\nstart with costomized setting: 1\n"))
if advanced == 1:
    trill_number = int(input("\n상위 몇개 그룹을 제외할것인가요? (범위 0~20, 추천값 4)\nHow many groups to remove from above?\n(숫자가 클수록 순간 밀도 반영률이 떨어집니다. 12이상일시 난이도 계산이 매우 부정확해질수 있습니다.)\nhigher the number, lower peak density apply.\n"))
    max_group = int(input("몇번째 그룹까지 더할까요? (범위 20~200, 추천값 100)\nHow many groups to add?\n(숫자가 클수록 긴 곡이 고평가됩니다. 평균적인 리듬게임곡은 60~80개의 그룹을 가집니다.)\nhigher the number, long songs rated more.\n"))
    common_ratio = float(input("가중치는 얼마로 할까요? (범위 0.99~0.8, 추천값 0.965)\nWeighted common ratio?\n(숫자가 클수록 평균값의 반영률이 높아집니다.)\nhigher the number, mean density rated more.\n"))
    show_groupcal = int(input("가중처리된 그룹을 보여줄까요? (예: 1 아니요: 0)\nshow weighted groups? (Y: 1, N: 0)\n"))
    limit1 = int(input("비트를 나눌때 허용할 갯수는 얼마로 할까요? (랙 방지)(추천값 10000)\nHow many beats to allow when spliting beats?(Anti-lag)(recommanded 1000)\n"))
    limit2 = int(input("허용할 전체 비트 갯수는 얼마로 할까요? (랙 방지)(추천값 60000)\nHow many total beats to allow?(Anti-lag)(recommanded 60000)\n"))

else:
    trill_number = 4
    max_group = 100
    common_ratio = 0.965
    show_groupcal = 0
    limit1 = 10000
    limit2 = 60000

ask = input("기존의 컬렉션을 백업할까요?\nBackup collection.db?\n[ Y: 1 / N: 0 ]\n")
if ask == "1" or ask == "y":
    shutil.copy2('collection.db','collection.backup')


def get_info(bm):

    Timing = []
    HitObjects = []

    file_name = str(bm.location).split('/')            

    bm.name = file_name

    bm.hash = hashlib.md5(open(file, "rb").read()).hexdigest()

    osutxt_file = open(file,"r",encoding="utf8")
    osutxt_line = osutxt_file.readlines()

    location_timing = osutxt_line.index("[TimingPoints]\n")
    location_hitobj = osutxt_line.index("[HitObjects]\n")
    location_diff = osutxt_line.index("[Difficulty]\n")
    location_events = osutxt_line.index("[Events]\n")

    Difficulty_lines = osutxt_line[location_diff+1: location_events-1]
    HitObject_lines = osutxt_line[location_hitobj + 1:]

    for values in Difficulty_lines:
        valuelist = []
        valuelist = values.split(':')
        if valuelist[0] == "CircleSize":
            bm.Keys = valuelist[1]
        if valuelist[0] == "OverallDifficulty":
            bm.OD = valuelist[1]

    if "[Colours]\n" in osutxt_line:
        location_colours = osutxt_line.index("[Colours]\n")
        timing_points = osutxt_line[location_timing+1:location_colours-1]
    else:
        timing_points = osutxt_line[location_timing+1:location_hitobj-1]

    for values in timing_points:
        valuelist = []
        minilist = []
        valuelist = values.split(',')
        if len(valuelist) > 2:
            if valuelist[1].find("E") == -1:
                if float(valuelist[1]) > 0:
                    minilist.append(valuelist[0])
                    if float(valuelist[1]) >= 1120:
                        minilist.append(float(valuelist[0])/4)
                    elif float(valuelist[1]) >= 560:
                        minilist.append(float(valuelist[0])/4)
                    elif float(valuelist[1]) >= 280:
                        minilist.append(float(valuelist[0])/2)
                    elif float(valuelist[1]) < 70:
                        minilist.append(float(valuelist[0])*2)
                    else:
                        minilist.append(valuelist[0])
                    Timing.append(minilist)
                else:
                    continue
    
    for i in HitObject_lines:
        if i == "":
            HitObject_lines.remove(i)
    
    first_timing = Timing[0]
    first_beat = float(first_timing[0])
    song_len = int(HitObjects[-1]) + float(first_timing[1])*4

    while first_beat > 0:
        first_beat -= float(first_timing[1])*4
    
    G1 = Group()
    G1.timing = first_beat
    bm.groups.append(G1)

    for i in range(len(Timing)):
        bpmdata = Timing[i]
        if len(Timing) > i+1:
            nextbpmdata = Timing[i+1]
        else:
            nextbpmdata = [song_len,bpmdata[1]]

        chunklen = float(bpmdata[1])*4

        while float(bm.groups[-1].timing) <= float(nextbpmdata[0]):
            G = Group()
            G.timing = (float(bm.groups[-1].timing)+chunklen)
            G.bpmms = bpmdata[1]
            bm.groups.append(G)
            #그룹 만들기
            if len(bm.groups) > limit1:
                break
        del bm.group[-1]

    if len(bm.group) > limit2:
        return bm
    
    #타이밍 포인트들을 읽어서 양수값 (BPM값)만 읽어오기.
    notelist = []
    for values in HitObject_lines:
        bnote = Note()
        valuelist = []
        valuelist = values.split(',')
        key_range = 512/int(bm.Keys)
        #라인 정하기
        for i in range(1,int(bm.Keys)+1):
            if i*key_range <= valuelist[0] < (i+1)*key_range:
                bnote.line = i+1
        #노트 타이밍 입력
        bnote.timing = valuelist[2]
        if valuelist[3] == 1:
            bnote.type = 0
        
        elif valuelist[3] == 128:
            endnote = Note()
            bnote.type = 1
            endnote.type = 2
            endnote.line = bnote.line
            endnote.timing = valuelist[5]
        notelist.append(bnote)
        
    #그룹에 노트 배정.
    for i in len(bm.groups)-1:
        gr = bm.groups[i]
        if i == len(bm.groups)-1:
            nxtgr = Group()
            nxtgr.timing = bm.groups[i].timing + 4*float(bm.groups[i].bpmms)
            nxtgr.bpmms = bm.groups[i].bpmms
        else:
            nxtgr = bm.groups[i+1]
        for note in notelist:
            if gr.timing <= note.timing < nxtgr.timing:
                gr.notes.append(note)
                #노트 타입에 따라 배정
                if note.type == 0:
                    gr.single.append(note)
                elif note.type == 1:
                    gr.LNstart.append(note)
                elif note.type == 2:
                    gr.LNend.append(note)
    return bm

for i in trange(len(file_list_mania)):
    file = file_list_mania[i]
    bm = Beatmap()
    bm.location = file
    bm = get_info(bm)
    diff = bm.difficulty
    diff_int = math.floor(diff)
    
    for i in range(len(colls.collections)): 
        c = colls.collections[i]

        if diff_type == 0:
            if diff < 1:
                if str(c.name) == diff_name + " ~001":
                    c.beatmaps.append(bm)
            elif diff >= 999:
                if str(c.name) == diff_name + " 999+":
                    c.beatmaps.append(bm)
            elif str(c.name) == diff_name + " " + str(diff_int).zfill(3):
                    c.beatmaps.append(bm)
        if diff_type == 1:
            if diff < 1:
                if str(c.name) == diff_name + " ~01":
                    c.beatmaps.append(bm)
            elif diff > 100:
                if str(c.name) == diff_name + " 99+":
                    c.beatmaps.append(bm)
            elif str(c.name) == diff_name + " " + str(diff_int).zfill(2):
                    c.beatmaps.append(bm)
            
# end = input("press any key to continue")
# print(colls.collections)
diftype = ""
if diff_type == 1:
    diftype = "레벨형"
if diff_type == 0:
    diftype = "난이도형"


print("\n비트맵 분석이 완료되었습니다.\n")
a = input("계산기명 : {0}\n버전 : {1}\n타입 : {2} 으로 계산합니다.".format(diff_name, diff_version, diftype))


fobjw = open("new.db", 'wb')

fobjw.write(get_int(colls.version))
    
fobjw.write(get_int(len(colls.collections)))


for c in colls.collections:
    fobjw.write(get_string(c.name))
    fobjw.write(get_int(len(c.beatmaps)))
    for b in c.beatmaps:
        fobjw.write(get_string(b.hash))
    print("{0} has {1} beatmaps.".format(c.name,len(c.beatmaps)))
fobjw.close()

# print("컬렉션에 추가가 완료되었습니다. 기존의 collection.db는 백업해두시고 new.db를 collection.db으로 이름 바꿔 주세요.")
# print("Binished. Backup your 'collection.db' and rename 'new.db' to 'collection.db'.")

end = input("작업이 전부 끝났습니다.. 이제 프로그램을 닫고 osu! 를 켜도 됩니다.\nFinished. now you can run osu!\n")
