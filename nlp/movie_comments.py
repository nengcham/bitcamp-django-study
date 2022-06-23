import math

from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
from icecream import ic
from matplotlib import rc, font_manager
rc('font', family=font_manager.FontProperties(fname='C:/Windows/Fonts/malgunsl.ttf').get_name())
import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False
import numpy as np
import re
from konlpy.tag import Okt
from collections import Counter, defaultdict
from wordcloud import WordCloud


from context.domains import Reader, File


class Solution(Reader):
    def __init__(self, k=0.5):
        self.file = File()
        self.file.context = './save/'
        self.movie_comments = pd.DataFrame()
        self.top10_title = []
        self.top10_reviews = pd.DataFrame()
        self.avg_score = {}
        # naive bayes context
        self.k = k
        self.word_probs = []

    def hook(self):
        def print_menu():
            print('0. Exit')
            print('1. 전처리 : 네이버 리뷰사이트를 크롤링하여 txt파일로 저장')
            print('2. 전처리 : 데이터 분석후 정형화(df)')
            print('3. 데이터 시각화')
            print('4. 임베딩')
            print('5. 형태소 시각화')
            print('6. 워드클라우드')
            print('7. 다음 영화 댓글이 긍정인지 부정인지 ratio 값으로 판단하시오\n')
            return input('메뉴 선택 \n')

        while 1:
            menu = print_menu()
            if menu == '1':
                self.crawling()

            elif menu == '2':
                self.stereotype()

            elif menu == '3':
                self.visualization()

            elif menu == '4':
                self.embedding()

            elif menu == '5':
                self.draw_frequency()

            elif menu == '6':
                self.draw_wordcloud()

            elif menu == '7':
                self.naive_bayes_classifier('졸작 쓰레기 망작 돈이 아깝다')
                self.naive_bayes_classifier('망작 쓰레기 다신 안볼것 같다')
                self.naive_bayes_classifier('어느정도 볼만은 했다')
                self.naive_bayes_classifier('너무 좋아요. 내 인생의 최고의 명작 영화')
                self.naive_bayes_classifier('형편없는 영화였다. 보다가 졸았다.')

            elif menu == '0':
                break

    def crawling(self):
        f = open('./save/movie_reviews.txt', 'w', encoding='UTF-8')

        # -- 500페이지까지 크롤링
        for no in range(1, 501):
            url = 'https://movie.naver.com/movie/point/af/list.naver?&page=%d' % no
            html = urllib.request.urlopen(url)
            soup = BeautifulSoup(html, 'html.parser')

            reviews = soup.select('tbody > tr > td.title')
            for rev in reviews:
                title = rev.select_one('a.movie').text.strip()
                score = rev.select_one('div.list_netizen_score > em').text.strip()
                comment = rev.select_one('br').next_sibling.strip()

                # -- 긍정/부정 리뷰 레이블 설정
                if int(score) >= 8:
                    label = 1  # -- 긍정 리뷰 (8~10점)
                elif int(score) <= 4:
                    label = 0  # -- 부정 리뷰 (0~4점)
                else:
                    label = 2

                f.write(f'{title}\t{score}\t{comment}\t{label}\n')
        f.close()

    def stereotype(self):
        file = self.file
        file.fname = 'movie_reviews.txt'
        data = pd.read_csv(self.new_file(file), delimiter='\t', names=['title', 'score', 'comment', 'label'])
        df_data = pd.DataFrame(data)

        # 코멘트가 없는 리뷰 데이터(NaN) 제거
        df_reviews = df_data.dropna()
        # 중복 리뷰 제거
        df_reviews = df_reviews.drop_duplicates(['comment'])

        return df_reviews

    def reviews_info(self):
        df_reviews = self.stereotype()

        print(df_reviews.head(10))
        print(df_reviews.info())
        '''
                                 title  ...  label
        0  마녀(魔女) Part2. The Other One  ...      1
        1  마녀(魔女) Part2. The Other One  ...      1
        2                     버즈 라이트이어  ...      0
        3                           실종  ...      1
        4  마녀(魔女) Part2. The Other One  ...      0
        5                     버즈 라이트이어  ...      1
        6                        범죄도시2  ...      1
        7                       그대가 조국  ...      0
        8                          브로커  ...      0
        9  마녀(魔女) Part2. The Other One  ...      0

        [10 rows x 4 columns]
        <class 'pandas.core.frame.DataFrame'>
        Int64Index: 4649 entries, 0 to 4998
        Data columns (total 4 columns):
         #   Column   Non-Null Count  Dtype 
        ---  ------   --------------  ----- 
         0   title    4649 non-null   object
         1   score    4649 non-null   int64 
         2   comment  4649 non-null   object
         3   label    4649 non-null   int64 
        dtypes: int64(2), object(2)
        memory usage: 181.6+ KB
        '''

        # 영화 리스트 확인
        movie_lst = df_reviews.title.unique()
        print('전체 영화 편수 =', len(movie_lst))
        print(movie_lst[:10])
        '''
        전체 영화 편수 = 805
        ['마녀(魔女) Part2. The Other One' '버즈 라이트이어' '실종' '범죄도시2' '그대가 조국' '브로커'
         '십개월의 미래' '탑건' '기적' '쥬라기 월드: 도미니언']

        '''

        # 각 영화 리뷰 수 계산
        cnt_movie = df_reviews.title.value_counts()
        print(cnt_movie[:20])
        '''
        브로커                               1345
        범죄도시2                              688
        마녀(魔女) Part2. The Other One        478
        쥬라기 월드: 도미니언                       264
        그대가 조국                             151
        버즈 라이트이어                            88
        인터셉터                                65
        닥터 스트레인지: 대혼돈의 멀티버스                 50
        피는 물보다 진하다                          44
        애프터 양                               38
        미드나이트                               37
        이공삼칠                                32
        카시오페아                               25
        실종                                  19
        뜨거운 피                               18
        극장판 포켓몬스터DP: 기라티나와 하늘의 꽃다발 쉐이미      17
        허슬                                  17
        니 부모 얼굴이 보고 싶다                      17
        윤시내가 사라졌다                           14
        연애 빠진 로맨스                           13
        '''

        # 각 영화 평점 분석
        # info_movie = df.groupby('title')['score'].describe() lambda 로 변환
        # ic((lambda a, b: df.groupby(a)[b].describe())('title', 'score').sort_values(by=['count'], axis=0,
        #                                                                             ascending=False))
        info_movie = df_reviews.groupby('title')['score'].describe()
        print(info_movie.sort_values(by=['count'], axis=0, ascending=False))
        '''
                                      count       mean       std  ...   50%   75%   max
        title                                                     ...                  
        브로커                          1345.0   4.823792  3.614953  ...   4.0   8.0  10.0
        범죄도시2                         688.0   9.122093  1.889889  ...  10.0  10.0  10.0
        마녀(魔女) Part2. The Other One   478.0   8.064854  3.074542  ...  10.0  10.0  10.0
        쥬라기 월드: 도미니언                  264.0   6.382576  2.742678  ...   6.0   9.0  10.0
        그대가 조국                        151.0   5.556291  4.373611  ...   4.0  10.0  10.0
        ...                             ...        ...       ...  ...   ...   ...   ...
        미인도                             1.0  10.000000       NaN  ...  10.0  10.0  10.0
        민스미트 작전                         1.0   6.000000       NaN  ...   6.0   6.0   6.0
        바닷마을 다이어리                       1.0   8.000000       NaN  ...   8.0   8.0   8.0
        바람                              1.0  10.000000       NaN  ...  10.0  10.0  10.0
        히든 피겨스                          1.0   5.000000       NaN  ...   5.0   5.0   5.0
        '''
        # 긍정, 부정 리뷰 수
        print(df_reviews.label.value_counts())
        '''
        1    2638
        0    1351
        2     660
        '''

    def visualization(self):
        df_reviews = self.stereotype()
        top10 = df_reviews.title.value_counts().sort_values(ascending=False)[:10]
        top10_title = top10.index.tolist()
        self.top10_title = top10_title
        top10_reviews = df_reviews[df_reviews['title'].isin(top10_title)]
        self.top10_reviews = top10_reviews

        # print(top10_title)
        # print(top10_reviews.info())
        '''
        ['브로커', '범죄도시2', '마녀(魔女) Part2. The Other One', '쥬라기 월드: 도미니언', '그대가 조국', 
        '버즈 라이트이어', '인터셉터', '닥터 스트레인지: 대혼돈의 멀티버스', '피는 물보다 진하다', '애프터 양']
        <class 'pandas.core.frame.DataFrame'>
        Int64Index: 3211 entries, 0 to 4997
        Data columns (total 4 columns):
         #   Column   Non-Null Count  Dtype 
        ---  ------   --------------  ----- 
         0   title    3211 non-null   object
         1   score    3211 non-null   int64 
         2   comment  3211 non-null   object
         3   label    3211 non-null   int64 
        dtypes: int64(2), object(2)
        memory usage: 125.4+ KB

        '''
        self.average_rating()
        self.rating_distribution()
        self.circular_chart()

    def average_rating(self):
        top10_reviews = self.top10_reviews

        movie_title = top10_reviews.title.unique().tolist()  # -- 영화 제목 추출
        avg_score = {}  # -- {제목 : 평균} 저장
        for t in movie_title:
            avg = top10_reviews[top10_reviews['title'] == t]['score'].mean()
            avg_score[t] = avg

        plt.figure(figsize=(10, 5))
        plt.title('영화 평균 평점 (top 10: 리뷰 수)\n', fontsize=17)
        plt.xlabel('영화 제목')
        plt.ylabel('평균 평점')
        plt.xticks(rotation=20)

        for x, y in avg_score.items():
            color = np.array_str(np.where(y == max(avg_score.values()), 'orange', 'lightgrey'))
            plt.bar(x, y, color=color)
            plt.text(x, y, '%.2f' % y,
                     horizontalalignment='center',
                     verticalalignment='bottom')
        plt.show()
        self.avg_score = avg_score

    def rating_distribution(self):
        fig, axs = plt.subplots(5, 2, figsize=(15, 25))
        axs = axs.flatten()

        top10_reviews = self.top10_reviews
        avg_score = self.avg_score

        for title, avg, ax in zip(avg_score.keys(), avg_score.values(), axs):
            num_reviews = len(top10_reviews[top10_reviews['title'] == title])
            x = np.arange(num_reviews)
            y = top10_reviews[top10_reviews['title'] == title]['score']
            ax.set_title('\n%s (%d명)' % (title, num_reviews), fontsize=15)
            ax.set_ylim(0, 10.5, 2)
            ax.plot(x, y, 'o')
            ax.axhline(avg, color='red', linestyle='--')  # -- 평균 점선 나타내기
        plt.show()

    def circular_chart(self):
        fig, axs = plt.subplots(5, 2, figsize=(15, 25))
        axs = axs.flatten()
        colors = ['pink', 'gold', 'whitesmoke']

        top10_reviews = self.top10_reviews
        avg_score = self.avg_score

        for title, ax in zip(avg_score.keys(), axs):
            num_reviews = len(top10_reviews[top10_reviews['title'] == title])
            values = top10_reviews[top10_reviews['title'] == title]['label'].value_counts()
            ax.set_title('\n%s (%d명)' % (title, num_reviews), fontsize=15)
            ax.pie(values,
                   autopct='%1.1f%%',
                   colors=colors,
                   shadow=True,
                   startangle=90)
            ax.axis('equal')
        plt.show()

    def embedding(self):
        df_reviews = self.stereotype()
        pos_reviews = df_reviews[df_reviews['label'] == 1]
        neg_reviews = df_reviews[df_reviews['label'] == 0]

        # -- 긍정 리뷰
        pos_reviews['comment'] = pos_reviews['comment'].apply(lambda x: re.sub(r'[^ㄱ-ㅣ가-힝+]', ' ', x))
        # -- 부정 리뷰
        neg_reviews['comment'] = neg_reviews['comment'].apply(lambda x: re.sub(r'[^ㄱ-ㅣ가-힝+]', ' ', x))

        okt = Okt()
        pos_comment_nouns = []
        for cmt in pos_reviews['comment']:
            pos_comment_nouns.extend(okt.nouns(cmt))  # -- 명사만 추출
        # -- 추출된 명사 중에서 길이가 1보다 큰 단어만 추출
        pos_comment_nouns2 = []
        word = [w for w in pos_comment_nouns if len(w) > 1]
        pos_comment_nouns2.extend(word)
        return pos_comment_nouns2

    def draw_frequency(self):
        pos_comment_nouns2 = self.embedding()
        pos_word_count = Counter(pos_comment_nouns2)

        pos_top_20 = {}
        for word, counts in pos_word_count.most_common(20):
            pos_top_20[word] = counts
            # print(f'{word} : {counts}')
        '''
        영화 : 1220
        연기 : 362
        배우 : 298
        액션 : 262
        생각 : 232
        '''
        plt.figure(figsize=(10, 5))
        plt.title('긍정 리뷰의 단어 상위 (%d개)' % 20, fontsize=17)
        plt.ylabel('단어의 빈도수')
        plt.xticks(rotation=70)
        for key, value in pos_top_20.items():
            if key == '영화': continue
            plt.bar(key, value, color='lightgrey')
        plt.show()

    def draw_wordcloud(self):
        pos_word_count = Counter(self.embedding())
        wc = WordCloud('./data/D2Coding.ttf', background_color='ivory', width=800, height=600)
        cloud = wc.generate_from_frequencies(pos_word_count)
        plt.figure(figsize=(8, 8))
        plt.imshow(cloud)
        plt.axis('off')
        plt.show()

    def naive_bayes_classifier(self, doc):
        training_set = self.load_corpus()
        self.count_words(training_set)
        self.train(training_set)
        self.classify(doc)

    def load_corpus(self):
        file = self.file
        file.fname = 'movie_reviews.txt'
        corpus = pd.read_csv(self.new_file(file), delimiter='\t', names=['title', 'point', 'doc', 'label'])
        corpus.drop(['title', 'label'], axis=1, inplace=True)
        corpus = corpus[['doc', 'point']]
        corpus = np.array(corpus)
        # ic(corpus)
        return corpus

    def count_words(self, training_set):
        counts = defaultdict(lambda: [0, 0])
        for doc, point in training_set:
            # 영화리뷰가 text 일때만 카운드
            if self.is_number(doc) is False:
                # 리뷰를 띄어쓰기 단위로 토크나이징
                words = doc.split()
                for word in words:
                    counts[word][0 if point > 8 else 1] += 1
        # ic(counts)
        return counts

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def word_probabilities(self, counts, total_class0, total_class1, k):
        # 단어의 빈도수를 [단어, p(w|긍정), p(w|부정)] 형태로 변환
        return [(w, (class0 + k) / (total_class0 + 2 * k),(class1 + k) / (total_class1 + 2 * k)) for w, (class0, class1) in counts.items()]

    def class0_probabilities(self, word_probs, doc):
        # 별도 토크나이즈 하지 않고 띄어쓰기만
        docwords = doc.split()
        # 초기값은 모두 0으로 처리
        log_prob_if_class0 = log_prob_if_class1 = 0.0
        # 모든 단어에 대해 반복
        for word, prob_if_class0, prob_if_class1 in word_probs:
            # 만약 리뷰에 word 가 나타나면 해당 단어가 나올 log 에 확률을 더 해줌
            if word in docwords:
                log_prob_if_class0 += math.log(prob_if_class0)
                log_prob_if_class1 += math.log(prob_if_class1)
            # 만약 리뷰에 word 가 나타나지 않는다면
            # 해당 단어가 나오지 않을 log 에 확률을 더해줌
            # 나오지 않을 확률은 log(1 - 나올 확률) 로 계산
            else:
                log_prob_if_class0 += math.log(1.0 - prob_if_class0)
                log_prob_if_class1 += math.log(1.0 - prob_if_class1)
        prob_if_class0 = math.exp(log_prob_if_class0)
        prob_if_class1 = math.exp(log_prob_if_class1)
        return prob_if_class0 / (prob_if_class0 + prob_if_class1)

    def train(self, training_set):
        # 범주0 (긍정) 과 범주1(부정) 문서의 수를 세어줌
        num_class0 = len([1 for _, point in training_set if point > 8])
        num_class1 = len(training_set) - num_class0
        # train
        word_counts = self.count_words(training_set)
        # print(word_counts)
        self.word_probs = self.word_probabilities(word_counts, num_class0, num_class1, self.k)
        # ic(self.word_probs)

    def classify(self, doc):
        print(f'댓글: "{doc}", 긍정점수: {round(self.class0_probabilities(self.word_probs, doc)*100, 2)}점')


if __name__ == '__main__':
    Solution().hook()