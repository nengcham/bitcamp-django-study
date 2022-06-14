from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urljoin
import re
import pandas as pd
import folium
import googlemaps
import numpy as np

from context.domains import File, Reader


class Solution(Reader):
    def __init__(self):
        self.url_base = 'http://www.chicagomag.com'
        self.url_sub = '/Chicago-Magazine/November-2012/Best-Sandwiches-Chicago/'
        self.url = self.url_base + self.url_sub
        self.file = File()
        self.file.context = './save/'

    def hook(self):
        def print_menu():
            print('0. Exit')
            print('1. 시카고 매거진에서 데이터 가져오기')
            print('2. 가지고 온 데이터를 전처리하여 best_sandwiches_list_chicago.csv 만들기')
            print('3. best_sandwiches_list_chicago.csv의 홈페이지를 통해 가격 주소 추가한 csv 만들기')
            print('4. 주어진 데이터를 활용하여 시카고 샌드위치 맛집 현황지도(폴리움)를 작성하시오')
            return input('메뉴 선택 \n')

        while 1:
            menu = print_menu()
            if menu == '1':
                self.read_html()

            elif menu == '2':
                self.preprocessing()

            elif menu == '3':
                self.preprocessing2()

            elif menu == '4':
                self.draw_sandwich_map()

            elif menu == '0':
                break

    def read_html(self):
        # headers를 쓰는 이유는 시큐리티 때문에
        req = Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req)
        soup = BeautifulSoup(html, "html.parser")
        # print(soup)
        # print(soup.find_all('div', 'sammy'))
        # print(len(soup.find_all('div', 'sammy')))  # 샌드위치는 총 50개
        # print(soup.find_all('div', 'sammy')[0]) # 1등 샌드위치
        return soup.find_all('div', 'sammy')

    def preprocessing(self):
        rank = []
        main_menu = []
        cafe_name = []
        url_add = []
        list_soup = self.read_html()
        for item in list_soup:
            rank.append(item.find(class_='sammyRank').get_text())

            tmp_string = item.find(class_='sammyListing').get_text()

            main_menu.append(re.split(('\n|\r\n'), tmp_string)[0])
            cafe_name.append(re.split(('\n|\r\n'), tmp_string)[1])

            url_add.append(urljoin(self.url_base, item.find('a')['href']))

        # print(rank[:5])
        # print(main_menu[:5])
        # print(cafe_name[:5])
        # print(url_add[:5])
        # print(len(rank), len(main_menu), len(cafe_name), len(url_add))
        '''
        ['1', '2', '3', '4', '5']
        ['BLT', 'Fried Bologna', 'Woodland Mushroom', 'Roast Beef', 'PB&L']
        ['Old Oak Tap', 'Au Cheval', 'Xoco', 'Al’s Deli', 'Publican Quality Meats']
        ['http://www.chicagomag.com/Chicago-Magazine/November-2012/Best-Sandwiches-in-Chicago-Old-Oak-Tap-BLT/',
         'http://www.chicagomag.com/Chicago-Magazine/November-2012/Best-Sandwiches-in-Chicago-Au-Cheval-Fried-Bologna/',
         'http://www.chicagomag.com/Chicago-Magazine/November-2012/Best-Sandwiches-in-Chicago-Xoco-Woodland-Mushroom/',
         'http://www.chicagomag.com/Chicago-Magazine/November-2012/Best-Sandwiches-in-Chicago-Als-Deli-Roast-Beef/',
         'http://www.chicagomag.com/Chicago-Magazine/November-2012/Best-Sandwiches-in-Chicago-Publican-Quality-Meats-PB-L/']
        (50, 50, 50, 50)
        '''
        data = {'Rank': rank, 'Menu': main_menu, 'Cafe': cafe_name, 'URL': url_add}
        df = pd.DataFrame(data, columns=['Rank', 'Cafe', 'Menu', 'URL'])
        # print(df.head())
        '''
          Rank  ...                                                URL
        0    1  ...  http://www.chicagomag.com/Chicago-Magazine/Nov...
        1    2  ...  http://www.chicagomag.com/Chicago-Magazine/Nov...
        2    3  ...  http://www.chicagomag.com/Chicago-Magazine/Nov...
        3    4  ...  http://www.chicagomag.com/Chicago-Magazine/Nov...
        4    5  ...  http://www.chicagomag.com/Chicago-Magazine/Nov...
        '''
        return df.to_csv('./save/best_sandwiches_list_chicago.csv', sep=',', encoding='UTF-8', index=False)

    def preprocessing2(self):
        file = self.file
        file.fname = 'best_sandwiches_list_chicago'
        df = self.csv(file)

        price = []
        address = []
        for i in df['URL']:
            req = Request(i, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req)
            soup_tmp = BeautifulSoup(html, 'lxml')

            gettings = soup_tmp.find('p', 'addy').get_text()

            price.append(gettings.split()[0][:-1])
            address.append(' '.join(gettings.split()[1:-2]))
        print(price)
        print(address)
        '''
        ['$10', '$9', '$9.50']
        ['2109 W. Chicago Ave.,', '800 W. Randolph St.,', '445 N. Clark St.,']
        '''
        df['Price'] = price
        df['Address'] = address
        df = df.loc[:, ['Rank', 'Cafe', 'Menu', 'Price', 'Address']]
        df.set_index('Rank', inplace=True)
        print(df.head())
        return df.to_csv('./save/best_sandwiches_list_chicago2.csv', sep=',', encoding='UTF-8')

    def draw_sandwich_map(self):
        file = self.file
        file.fname = 'best_sandwiches_list_chicago2'
        df = self.csv(file)
        lat = []
        lng = []
        gmaps = self.gmaps()
        for i in df['Address']:
            if i != 'Multiple':
                target_name = i + ', ' + 'Chicago'
                gmaps_output = gmaps.geocode(target_name)
                location_output = gmaps_output[0].get('geometry')
                lat.append(location_output['location']['lat'])
                lng.append(location_output['location']['lng'])
            else:
                lat.append(np.nan)
                lng.append(np.nan)
        df['lat'] = lat
        df['lng'] = lng
        # print(df.head())

        m = folium.Map(location=[df['lat'].mean(), df['lng'].mean()], zoom_start=11)
        for n in df.index:
            if df['Address'][n] != 'Multiple':
                folium.Marker([df['lat'][n], df['lng'][n]], popup=df['Cafe'][n]).add_to(m)
        return m.save('./save/sandwich_map.html')


if __name__ == '__main__':
    Solution().hook()