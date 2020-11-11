
import sys
import os
import os.path
import shutil
import hashlib
import math
import struct
import base64
import pickle

OSU_BYTE = 1
OSU_SHORT = 2
OSU_INT = 4
OSU_LONG = 8
OSU_SINGLE = 4
OSU_DOUBLE = 8
OSU_BOOLEAN = 1
OSU_DATETIME = 8

class Collections:
    def __init__(self):
        self.version = 0
        self.list = []
        self.newlist = []

class Collection:
    def __init__(self):
        self.name = ""
        self.beatmaps = []
        self.hashs = []

class CollectionMap:
    def __init__(self):
        self.hash = ""

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

start = input("press any key to start")

fobj = open("collection.db", 'rb')

version = int.from_bytes(fobj.read(OSU_INT), byteorder='little')

new = Collections()

new.version = version

collection_count = int.from_bytes(fobj.read(OSU_INT), byteorder='little')

collline = []

while True:
    coll = fobj.read(1024)
    collline.append(coll)  
    if len(collline) > 2048:
        break
    print(coll)           

for i in range(29,302):
    c = Collection()
    if i == 29:
        c.name = "zsd ~029"
    elif i == 301:
        c.name = "zsd 300+"
    else:
        c.name = "zsd " + str(i).zfill(3)
    
    new.newlist.append(c)

fobj.close()

print("무한 BPM 이나 0 BPM 에서는 작동이 보장되지 않습니다. \n무한에 가까운 BPM 이거나 0에 가까운 BPM에서는 큰 로딩시간이 필요하며\n몇몇 오투잼 컨버트 곡들은 정상 작동 하지 않습니다.\n")
print("This program does not work with infinite BPM or 0 BPM songs.\nif the beatmap has large(almost infinite) or extreamly small (almost 0) BPM, it takes long times.\nSome O2jam converts does not work.\n")
file_list = []
get_files("./Songs/",file_list)
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
    
    osutxt_file.close()
#마니아 모드인지 확인. 아니라면 '마니아 아님' 리스트에 추가.

print("\n\nosu 마니아 파일이 로드되었습니다... 전체 파일 " + str(len(file_list_osu)) + "개")
print("osu mania files loaded... total " + str(len(file_list_osu)) + " files\n")

advanced = int(input("기본 설정으로 실행: 0\nstart with recommanded setting: 0\n사용자 지정 설정으로 실행: 1\nstart with costomized setting: 1\n"))
if advanced == 1:
    trill_number = int(input("\n상위 몇개 그룹을 제외할것인가요? (범위 0~20, 추천값 4)\nHow many groups to remove from above?\n(숫자가 클수록 순간 밀도 반영률이 떨어집니다. 12이상일시 난이도 계산이 매우 부정확해질수 있습니다.)\nhigher the number, lower peak density apply.\n"))
    max_group = int(input("몇번째 그룹까지 더할까요? (범위 20~200, 추천값 100)\nHow many groups to add?\n(숫자가 클수록 긴 곡이 고평가됩니다. 평균적인 리듬게임곡은 60~80개의 그룹을 가집니다.)\nhigher the number, long songs rated more.\n"))
    common_ratio = float(input("가중치는 얼마로 할까요? (범위 0.99~0.8, 추천값 0.965)\nWeighted common ratio?\n(숫자가 클수록 평균값의 반영률이 높아집니다.)\nhigher the number, mean density rated more.\n"))
    show_groupcal = int(input("가중처리된 그룹을 보여줄까요? (예: 1 아니요: 0)\nshow weighted groups? (Y: 1, N: 0)\n"))
    limit1 = int(input("비트를 나눌때 허용할 갯수는 얼마로 할까요? (랙 방지)(추천값 1000)\nHow many beats to allow when spliting beats?(Anti-lag)(recommanded 1000)\n"))
    limit2 = int(input("허용할 전체 비트 갯수는 얼마로 할까요? (랙 방지)(추천값 60000)\nHow many total beats to allow?(Anti-lag)(recommanded 60000)\n"))

else:
    trill_number = 4
    max_group = 100
    common_ratio = 0.965
    show_groupcal = 0
    limit1 = 1000
    limit2 = 60000

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

    if "[Colours]\n" in osutxt_line:
        location_colours = osutxt_line.index("[Colours]\n")
        timing_points = osutxt_line[location_timing+1:location_colours-1]
    else:
        timing_points = osutxt_line[location_timing+1:location_hitobj-1]

    for values in timing_points:
        valuelist1 = values.split(',')
        if len(valuelist1) > 2:
            if valuelist1[1].find("E") == -1:
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
            if len(chunk) > limit1:
                break
        del chunk[-1]

    # print (Timing)
    # print(chunk)
    if len(chunk) > limit2:
        return 0

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

    if show_groupcal == 1:
        print ("weighted groups :",end="")
        for values in group_cal:
            print(round(values),end=", ")
        print("\b\b\b\n")
        print("{0} groups.".format(len(group_cal)))

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

    osutxt_file.close()

    return songdiff

diffdata = open("diffdata.pickle","wb")

for file in file_list_osu:
    try:
        true_diff = get_diff(file)
        diff = round(true_diff)
        if advanced == 0:
            print("diff :" + str(diff) + "\n")
        if advanced == 1:
            print("diff :" + str(true_diff) + "\n")
            
        hash = hashlib.md5(open(file, "rb").read()).hexdigest()
    except:
        print("에러가 발생했습니다. 무한 BPM이나 0 BPM에서는 정상작동하지 않습니다.\n")
        continue

    if advanced == 1:
        print("hash :" + str(hash) + "\n")
    ked_diff = round(diff/1000)
    for i in range(273):
        c = new.newlist[i]
        if ked_diff < 30:
            if str(c.name) == "zsd ~029":
                c.hashs.append(hash)
            
        elif ked_diff > 300:
            if str(c.name) == "zsd 300+":
                c.hashs.append(hash)

        elif str(c.name) == "zsd " + str(ked_diff).zfill(3):
            c.hashs.append(hash)
      
        
oldfile = int(input("계산이 완료되었습니다. 기존의 컬렉션도 포함할까요? (예: 1 아니요: 0)\n Calculation finished. include current collection? (Y: 1 N: 0)\n"))


fobjw = open("new.db", 'wb')

fobjw.write(get_int(new.version))

if int(oldfile) == 1:
    fobjw.write(get_int(collection_count+273))
if int(oldfile) == 0:
    fobjw.write(get_int(273))

if oldfile == 1:
    for coll in collline:
        fobjw.write(coll)

for c in new.newlist:

    fobjw.write(get_string(c.name))

    fobjw.write(get_int(len(c.hashs)))
    
    for k in c.hashs:
        fobjw.write(get_string(k))
    print("{0} has {1} beatmaps.".format(c.name,len(c.hashs)))

fobjw.close()

end = input("끝. new.db가 생성되었습니다.")







