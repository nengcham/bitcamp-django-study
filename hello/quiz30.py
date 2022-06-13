import random
import string

import numpy as np
import pandas as pd
from context.models import Model
from icecream import ic

from hello.domains import memberlist

'''
ic| df:     A   B   C
        1   1   2   3
        2   4   5   6
        3   7   8   9
        4  10  11  12
'''
class Quiz30:
    def quiz30_df_4_by_3(self) -> str:
        ls = [[j+i for j in range(3)] for i in range(1, 12, 3)]
        idx = range(1, 5)
        col = list(string.ascii_uppercase)[:3]
        df = pd.DataFrame(ls, index=idx, columns=col)
        ic(df)
        return None

    '''
    데이터프레임 문제 Q03.
    두자리 정수를 랜덤으로 2행 3열 데이터프레임을 생성
    ic| df:     0   1   2
            0  97  57  52
            1  56  83  80
    '''
    def quiz31_rand_2_by_3(self) -> str:
        # print(pd.DataFrame([[myRandom(10, 99) for i in range(3)] for i in range(2)]))
        print(pd.DataFrame(np.random.randint(10, 99, size=(2, 3))))
        return None

    '''
                데이터프레임 문제 Q04.
                국어, 영어, 수학, 사회 4과목을 시험치른 10명의 학생들의 성적표 작성.
                 단 점수 0 ~ 100이고 학생은 랜덤 알파벳 5자리 ID 로 표기

                  ic| df4:        국어  영어  수학  사회
                            lDZid  57  90  55  24
                            Rnvtg  12  66  43  11
                            ljfJt  80  33  89  10
                            ZJaje  31  28  37  34
                            OnhcI  15  28  89  19
                            claDN  69  41  66  74
                            LYawb  65  16  13  20
                            QDBCw  44  32   8  29
                            PZOTP  94  78  79  96
                            GOJKU  62  17  75  49
        '''
    @staticmethod
    def id(chr_size) -> str: return ''.join(random.choice(string.ascii_letters) for i in range(chr_size))

    def quiz32_df_grade(self) -> str:
        data1 = np.random.randint(0, 100, (10, 4))
        idx = [self.id(chr_size=5) for i in range(10)]
        col = ['국어', '영어', '수학', '사회']
        df1 = pd.DataFrame(data1, index=idx, columns=col)

        ###############################
        data2 = {i: j for i, j in zip(idx, data1)}
        df2 = pd.DataFrame.from_dict(data2, orient = 'index', columns=col)

        ic(df1)
        ic(df2)

        return None

    @staticmethod
    def create_df(keys, vals, len):
        return pd.DataFrame([dict(zip(keys, vals)) for _ in range(len)])

    def quiz33_df_loc(self) -> str:
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html

        # df = self.create_df(keys=['a', 'b', 'c', 'd'],
        #                     vals=np.random.randint(0, 100, 4),
        #                     len=3)
        # print(df)
        # ic(df.iloc[0])

        # subj = ['자바', '파이썬', 'JS', 'SQL']
        # stud = memberlist()
        # data = np.random.randint(0, 100, (len(stud), len(subj)))
        # df = pd.DataFrame(data, index=stud, columns=subj)
        # ic(df)
        # df.to_csv('./save/grade.csv', sep=',', na_rep='NaN')
        model = Model()
        # model.save_model(fname='grade.csv', dframe=df)

        grade_df = model.new_model('grade.csv')

        print('Q1. 파이썬의 점수만 출력하시오')
        # python_scores = grade_df['파이썬']
        python_scores = grade_df.loc[:, '파이썬']
        ic(type(python_scores))
        ic(python_scores)

        print('Q2. 조현국의 점수만 출력하시오')
        cho_scores = grade_df.loc['조현국']
        ic(type(cho_scores))
        ic(cho_scores)

        print('Q2. 조현국의 과목별 점수를 출력하시오')
        cho_subjects_scores = grade_df.loc[['조현국']]
        ic(type(cho_subjects_scores))
        ic(cho_subjects_scores)

        return None

    def quiz34(self) -> str: return None

    def quiz35(self) -> str: return None

    def quiz36(self) -> str: return None

    def quiz37(self) -> str: return None

    def quiz38(self) -> str: return None

    def quiz39(self) -> str: return None


