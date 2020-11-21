# 가독성을 위해  __init__ 등은 제거함.

# class Note:
#     self.timing 노트의 타이밍
#     self.type 0: 단놋 1: 롱놋시작 2:롱놋끝
#     self.line 노트의 라인

# class Group: 그룹은 osu 에디터 기준 굵은 흰색 선.4개 마디가 1개 그룹으로 편성됨.
#     self.timing 그룹의 타이밍
#     self.bpmms 그룹의 bpm. 우리가 쓰는 형태로 하려면 60000을 bpmms로 나누면 됨.
#     self.notes 노트들의 리스트
#     self.single 노트들의 리스트중 단놋들의 리스트
#     self.LNstart 노트들의 리스트중 롱놋 시작의 리스트
#     self.LNend 노트들의 리스트중 롱놋 끝나는거의 리스트
#     self.diff 실수 형태의 난이도값.

# class Beatmap:
#     self.name 비트맵 이름. str 형태
#     self.OD OD 값.
#     self.Keys 키 갯수
#     self.groups 그룹들의 리스트
#     self.hash 해쉬값. 몰라도 됨
#     self.location 파일의 위치. 몰라도 됨
#     self.difficulty 최종 난이도.

# 구조

# Beatmap.groups
#       |
#  Group.notes
#       |
#     Note


# 각 난이도는 반드시 999미만의 정수가 나와야함.
# 레벨 형태일경우 결과된 선형값을 로그를 취하여 위로갈수록 난이도에 차이가 적게끔 해야함.
# (위로 갈수록 1레벨당 포함되는 난이도의 폭이 넓어져야함.) 최대 99레벨.



# 난이도 명을 지정할수 있음.
diff_name = "asdf"

# 난이도의 버전. 배포시 편의를 위해 넣음.
diff_version = 0.1

# 레벨형태인지 난이도 형태인지 정하는 패러미터. 0이면 난이도형 1이면 레벨형
diff_type = 1

# 난이도 계산 파일
def get_diff(bm):
    
