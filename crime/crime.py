import numpy as np
import pandas as pd
from sklearn import preprocessing

from context.domains import Reader, File, Printer
import folium


class Solution(Reader):
    def __init__(self):
        self.file = File()
        self.printer = Printer()
        self.crime_rate_columns = ['살인검거율', '강도검거율', '강간검거율', '절도검거율', '폭력검거율']
        self.crime_columns = ['살인', '강도', '강간', '절도', '폭력']
        self.file.context = './data/'

    def hook(self):
        def print_menu():
            print('0. Exit')
            print('1. crime_in_seoul.csv, 구글맵 API 를 이용해서 서울시내 경찰서 주소목록파일(police_pos.csv)을 작성하시오.')
            print('2. us-states.json, us_unemployment.csv 를 이용해서 미국 실업률 지도(folium_test.html)를 작성하시오.')
            print('3. cctv_in_seoul.csv, pop_in_seoul.csv 를 이용해서 서울시내 경찰서 주소목록파일(cctv_pop.csv)을 작성하시오.')
            print('4. police_pos.csv를 이용하여 경찰서 범죄검거율 정규화파일(police_norm.csv)을 작성하시오')
            print('5. 주어진 데이터를 활용하여 서울시내 경찰서 범죄발생과 검거율 현황지도(폴리움)를 작성하시오')
            return input('메뉴 선택 \n')

        while 1:
            menu = print_menu()
            if menu == '1':
                self.save_police_pos()

            elif menu == '2':
                self.folium_test()

            elif menu == '3':
                self.save_cctv_pos()

            elif menu == '4':
                self.save_police_norm()

            elif menu == '5':
                self.draw_crime_map()

            elif menu == '0':
                break

    def save_police_pos(self):
        file = self.file
        file.fname = 'crime_in_seoul'
        crime = self.csv(file)
        station_names = []
        for name in crime['관서명']:
            station_names.append(f'서울{str(name[:-1])}경찰서')
        # print(f'station_names range: {len(station_names)}')  #서울시내 경찰서는 총 31개
        # for i, name in enumerate(station_names):
        #     print(f'name {i} = {name}')
        gmaps = self.gmaps()
        # a = gmaps.geocode('서울종암경찰서', language='ko')
        # print(a)
        '''
        [{'address_components': 
            [{'long_name': '３２９', 'short_name': '３２９', 'types': ['premise']}, 
            {'long_name': '백범로', 'short_name': '백범로', 'types': ['political', 'sublocality', 'sublocality_level_4']}, 
            {'long_name': '용산구', 'short_name': '용산구', 'types': ['political', 'sublocality', 'sublocality_level_1']}, 
            {'long_name': '서울특별시', 'short_name': '서울특별시', 'types': ['administrative_area_level_1', 'political']}, 
            {'long_name': '대한민국', 'short_name': 'KR', 'types': ['country', 'political']}, 
            {'long_name': '140-111', 'short_name': '140-111', 'types': ['postal_code']}], 
            'formatted_address': '대한민국 서울특별시 용산구 백범로 329', 
            'geometry': {'location': 
                {'lat': 37.5387099, 'lng': 126.9659183}, 
                'location_type': 'ROOFTOP', 
                'viewport': {'northeast': {'lat': 37.5400588802915, 'lng': 126.9672672802915}, 
                'southwest': {'lat': 37.5373609197085, 'lng': 126.9645693197085}}}, 
                'partial_match': True, 'place_id': 'ChIJhbgEHxKifDURLOHanwAKdJI', 
                'plus_code': {'compound_code': 'GXQ8+F9 대한민국 서울특별시', 'global_code': '8Q98GXQ8+F9'}, 
                'types': ['establishment', 'point_of_interest', 'police']}]
        
        서울종암경찰서는 2021.12.20에 이전해 구글맵에 등록이 되어있지 않다. 
        '''
        station_addrs = []
        station_lats = []
        station_lngs = []
        # print(station_names[21])
        for i, name in enumerate(station_names):
            if name != '서울종암경찰서':
                temp = gmaps.geocode(name, language='ko')
            else:
                temp = self.jongam_police_info()
            # print(f'name {i} = {temp[0].get("formatted_address")}')
            station_addrs.append(temp[0].get('formatted_address'))
            t_loc = temp[0].get('geometry')
            station_lats.append(t_loc['location']['lat'])
            station_lngs.append(t_loc['location']['lng'])

        gu_names = []
        for name in station_addrs:
            temp = name.split()
            gu_name = [gu for gu in temp if gu[-1] == '구'][0]
            gu_names.append(gu_name)
        crime['구별'] = gu_names
        # [print(i) for i in crime['구별']]
        crime.to_csv('./save/police_pos.csv', index=False) # index=False는 인덱스 무작위생성 방지

    def save_cctv_pos(self):
        file = self.file
        file.fname = 'cctv_in_seoul'
        cctv = self.csv(file)
        file.fname = 'pop_in_seoul'
        pop = self.xls(file=file, header=1, cols='B,D,G,J,N', skiprows=[2])
        # print(pop)
        '''
                 자치구          합계        한국인     등록외국인   65세이상고령자
        0     합계  10197604.0  9926968.0  270636.0  1321458.0
        1    종로구    162820.0   153589.0    9231.0    25425.0
        2     중구    133240.0   124312.0    8928.0    20764.0
        3    용산구    244203.0   229456.0   14747.0    36231.0
        '''
        # print(cctv)
        '''
                     기관명    소계  2013년도 이전  2014년  2015년  2016년
        0    강남구  2780       1292    430    584    932
        1    강동구   773        379     99    155    377
        2    강북구   748        369    120    138    204
        3    강서구   884        388    258    184     81
        '''
        # pop.rename(columns={'자치구': '구별', '합계': '인구수', '등록외국인': '외국인', '65세이상고령자': '고령자'}, inplace=True)
        pop.columns = ['구별', '인구수', '한국인', '외국인', '고령자']
        # pop.dropna(inplace=True) # NaN 하나라도 있는 rows drop
        # pop.dropna(how='all')    # 모든 값이 NaN일 경우에만 drop
        # pop.drop(index=26, inplace=True)
        pop.drop([26], inplace=True)
        pop['외국인비율'] = pop['외국인'] / pop['인구수'] * 100
        pop['고령자비율'] = pop['고령자'] / pop['인구수'] * 100

        cctv.rename(columns={'기관명': '구별'}, inplace=True)
        cctv.drop(['2013년도 이전', '2014년', '2015년', '2016년'], axis=1, inplace=True)
        # print(pop)
        # print(cctv)
        cctv_pop = pd.merge(cctv, pop, on='구별')
        print(cctv_pop)

        cor1 = np.corrcoef(cctv_pop['고령자비율'], cctv_pop['소계'])
        cor2 = np.corrcoef(cctv_pop['외국인비율'], cctv_pop['소계'])
        print(f'고령자비율과 CCTV의 상관계수 {str(cor1)} \n'
              f'외국인비율과 CCTV의 상관계수 {str(cor2)} ')
        """
         고령자비율과 CCTV 의 상관계수 [[ 1.         -0.28078554]
                                     [-0.28078554  1.        ]] 
         외국인비율과 CCTV 의 상관계수 [[ 1.         -0.13607433]
                                     [-0.13607433  1.        ]]
        r이 -1.0과 -0.7 사이이면, 강한 음적 선형관계,
        r이 -0.7과 -0.3 사이이면, 뚜렷한 음적 선형관계,
        r이 -0.3과 -0.1 사이이면, 약한 음적 선형관계,
        r이 -0.1과 +0.1 사이이면, 거의 무시될 수 있는 선형관계,
        r이 +0.1과 +0.3 사이이면, 약한 양적 선형관계,
        r이 +0.3과 +0.7 사이이면, 뚜렷한 양적 선형관계,
        r이 +0.7과 +1.0 사이이면, 강한 양적 선형관계
        고령자비율 과 CCTV 상관계수 [[ 1.         -0.28078554] 약한 음적 선형관계
                                    [-0.28078554  1.        ]]
        외국인비율 과 CCTV 상관계수 [[ 1.         -0.13607433] 거의 무시될 수 있는
                                    [-0.13607433  1.        ]]                        
         """

        cctv_pop.to_csv('./save/cctv_pop.csv')

    def save_police_norm(self):
        file = self.file
        file.context = './save/'
        file.fname = 'police_pos'
        police_pos = self.csv(file)
        police = pd.pivot_table(police_pos, index='구별', aggfunc=np.sum)
        police['살인검거율'] = police['살인 검거'].astype(int) / police['살인 발생'].astype(int) * 100
        police['강도검거율'] = police['강도 검거'].astype(int) / police['강도 발생'].astype(int) * 100
        police['강간검거율'] = police['강간 검거'].astype(int) / police['강간 발생'].astype(int) * 100
        police['절도검거율'] = police['절도 검거'].astype(int) / police['절도 발생'].astype(int) * 100
        police['폭력검거율'] = police['폭력 검거'].astype(int) / police['폭력 발생'].astype(int) * 100
        police.drop(columns={'살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거'}, axis=1, inplace=True)

        for i in self.crime_rate_columns:
            police[i].loc[police[i] > 100] = 100  # loc()는 데이터프레임의 행이나 컬럼에 index로 접근한다.
        police.rename(columns={
            '살인 발생': '살인',
            '강도 발생': '강도',
            '강간 발생': '강간',
            '절도 발생': '절도',
            '폭력 발생': '폭력'
        }, inplace=True)
        police.to_csv('./save/police.csv', sep=',', encoding='UTF-8')
        print(police)
        x = police[self.crime_rate_columns].values
        min_max_scalar = preprocessing.MinMaxScaler()
        """    
        피쳐 스케일링(Feature scalining)은 해당 피쳐들의 값을 일정한 수준으로 맞춰주는 것이다.
        이때 적용되는 스케일링 방법이 표준화(standardization) 와 정규화(normalization)다.
        
        1단계: 표준화(공통 척도)를 진행한다.
            표준화는 정규분포를 데이터의 평균을 0, 분산이 1인 표준정규분포로 만드는 것이다.
            x = (x - mu) / sigma
            scale = (x - np.mean(x, axis=0)) / np.std(x, axis=0)
        2단계: 이상치 발견 및 제거
        3단계: 정규화(공통 간격)를 진행한다.
            정규화에는 평균 정규화, 최소-최대 정규화, 분위수 정규화가 있다.
             * 최소최대 정규화는 모든 데이터를 최대값을 1, 최솟값을 0으로 만드는 것이다.
            도메인은 데이터의 범위이다.
            스케일은 데이터의 분포이다.
            목적은 도메인을 일치시키거나 스케일을 유사하게 만든다.     
        """
        x_scaled = min_max_scalar.fit_transform(x.astype(float))
        police_norm = pd.DataFrame(x_scaled, columns=self.crime_columns, index=police.index)
        police_norm[self.crime_rate_columns] = police[self.crime_rate_columns]
        police_norm['범죄'] = np.sum(police_norm[self.crime_rate_columns], axis=1)
        police_norm['검거'] = np.sum(police_norm[self.crime_columns], axis=1)
        police_norm.to_csv('./save/police_norm.csv', sep=',', encoding='UTF-8')

    def folium_test(self):
        file = self.file
        file.fname = 'us-states.json'
        states = self.new_file(file)

        file.fname = 'us_unemployment'
        unemployment = self.csv(file)

        bins = list(unemployment["Unemployment"].quantile([0, 0.25, 0.5, 0.75, 1]))
        m = folium.Map(location=[39, -97], zoom_start=5)
        folium.Choropleth(
            geo_data=states, # dataframe 타입이 아닌 json
            name="choropleth",
            data=unemployment,
            columns=["State", "Unemployment"],
            key_on="feature.id",
            fill_color="YlGn",
            fill_opacity=0.7,
            line_opacity=0.5,
            legend_name="Unemployment Rate (%)",
            bins=bins,
            reset=True
        ).add_to(m)
        m.save("./save/folium_test.html")

    def draw_crime_map(self):
        # 서울시 지도 geo_simple.json
        file = self.file
        file.fname = 'geo_simple'
        seoul_map = self.map_json(file)

        # 검거율 정규화 데이터 police_norm.csv
        file.fname = 'police_norm'
        file.context = './save/'
        police_norm = self.csv(file)

        # 범죄현황 데이터 crime_in_seoul.csv
        file.fname = 'crime_in_seoul'
        file.context = './data/'
        crime = self.csv(file)

        # 경찰서위치 police_pos.csv
        file.fname = 'police_pos'
        file.context = './save/'
        police_pos = self.csv(file)

        station_names = []
        for name in crime['관서명']:
            station_names.append(f'서울{str(name[:-1])}경찰서')

        gmaps = self.gmaps()
        station_addrs = []
        station_lats = []
        station_lngs = []

        for i, name in enumerate(station_names):
            if name != '서울종암경찰서':
                temp = gmaps.geocode(name, language='ko')
            else:
                temp = self.jongam_police_info()
            station_addrs.append(temp[0].get('formatted_address'))
            t_loc = temp[0].get('geometry')
            station_lats.append(t_loc['location']['lat'])
            station_lngs.append(t_loc['location']['lng'])

        police_pos['lat'] = station_lats
        police_pos['lng'] = station_lngs
        col = ['살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거']
        tmp = police_pos[col] / police_pos[col].max()
        police_pos['검거'] = np.sum(tmp, axis=1)

        folium_map = folium.Map(location=[37.5502, 126.982], zoom_start=12, title='Stamen Toner')
        folium.Choropleth(
            geo_data=seoul_map,
            data=tuple(zip(police_norm['구별'], police_norm['범죄'])),
            columns=["State", "Crime Rate"],
            key_on="feature.id",
            fill_color="PuRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Crime Rate (%)",
            reset=True,
        ).add_to(folium_map)
        for i in police_pos.index:
            folium.CircleMarker([police_pos['lat'][i], police_pos['lng'][i]],
                                radius=police_pos['검거'][i] * 10,
                                fill_color='#0a0a32').add_to(folium_map)

        folium_map.save('./save/crime_map.html')

    def jongam_police_info(self):
        return [{'address_components':
                     [{'long_name': '３２', 'short_name': '３２', 'types': ['premise']},
                      {'long_name': '화랑로7길', 'short_name': '화랑로7길',
                       'types': ['political', 'sublocality', 'sublocality_level_4']},
                      {'long_name': '성북구', 'short_name': '성북구',
                       'types': ['political', 'sublocality', 'sublocality_level_1']},
                      {'long_name': '서울특별시', 'short_name': '서울특별시',
                       'types': ['administrative_area_level_1', 'political']},
                      {'long_name': '대한민국', 'short_name': 'KR', 'types': ['country', 'political']},
                      {'long_name': '140-111', 'short_name': '140-111', 'types': ['postal_code']}],
                 'formatted_address': '대한민국 서울특별시 성북구 화랑로7길 32',
                 'geometry': {'location':
                                  {'lat': 37.6038816, 'lng': 127.0400157},
                              'location_type': 'ROOFTOP',
                              'viewport': {'northeast': {'lat': 37.60388169879458, 'lng': 127.04001571848704},
                                           'southwest': {'lat': 37.60388169879458, 'lng': 127.04001571848704}}},
                 'partial_match': True, 'place_id': 'ChIJhbgEHxKifDURLOHanwAKdJI',
                 'plus_code': {'compound_code': 'GXQ8+F9 대한민국 서울특별시', 'global_code': '8Q98GXQ8+F9'},
                 'types': ['establishment', 'point_of_interest', 'police']}]


if __name__ == '__main__':
    Solution().hook()

