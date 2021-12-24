import requests
from bs4 import BeautifulSoup
from myProject03.settings import STATIC_DIR,TEMPLATE_DIR
from matplotlib import font_manager,rc
import matplotlib.pyplot as plt
import os, pandas as pd
import folium

# wordcloud
from konlpy.tag import Okt
import matplotlib as mpl
from wordcloud import STOPWORDS, WordCloud
import re


def movie_crawling(data):
    for i in range(10):
        base_url='https://movie.naver.com/movie/point/af/list.nhn?&page='
        url = base_url+str(i+1)
        req=requests.get(url)

        if req.ok:
            html=req.text
            soup=BeautifulSoup(html, 'html.parser')
            titles=soup.select('td.title > a.movie')
            # print(titles)
            points=soup.select('td.title em')
            contents=soup.select('td.title')

            for i in range(len(titles)):
                title=titles[i].get_text()
                point = points[i].get_text()
                content_arr = contents[i].get_text().replace('신고','').split("\n\n")
                content = content_arr[2].replace("\t",'').replace("\n",'')
                data.append([title, point, content])
            print(data)

def weather_make_chart(result, wfs, dcounts):
    font_location="C:/Windows/fonts/malgun.ttf"
    font_name=font_manager.FontProperties(fname=font_location).get_name()
    rc('font',family=font_name)

    high = []
    low = []
    xdata = []

    for row in result.values_list():
        high.append(row[5])
        low.append(row[4])
        xdata.append(row[2].split('-')[2])
    print(xdata)
    plt.cla()
    plt.figure(figsize=(10,6)) #그래프 크기
    plt.plot(xdata,low, label='최저기온')
    plt.plot(xdata,high, label='최고기온')
    plt.legend()
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_busan.png'),dpi=300)

    plt.cla()
    plt.bar(wfs, dcounts)
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_bar.png'),dpi=300)

    plt.cla()
    plt.pie(dcounts, labels=wfs, autopct='%.1f%%')
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_pie.png'),dpi=300)
    image_dic = {'plot' : 'weather_busan.png', 'bar' : 'weather_bar.png', 'pie':'weather_pie.png'}
    return image_dic

def map():
    ex = {'경도' : [127.061026,127.047883,127.899220,128.980455,127.104071,127.102490,127.088387,126.809957,127.010861,126.836078
                ,127.014217,126.886859,127.031702,126.880898,127.028726,126.897710,126.910288,127.043189,127.071184,127.076812
                ,127.045022,126.982419,126.840285,127.115873,126.885320,127.078464,127.057100,127.020945,129.068324,129.059574
                ,126.927655,127.034302,129.106330,126.980242,126.945099,129.034599,127.054649,127.019556,127.053198,127.031005
                ,127.058560,127.078519,127.056141,129.034605,126.888485,129.070117,127.057746,126.929288,127.054163,129.060972],
     '위도' : [37.493922,37.505675,37.471711,35.159774,37.500249,37.515149,37.549245,37.562013,37.552153,37.538927,37.492388
              ,37.480390,37.588485,37.504067,37.608392,37.503693,37.579029,37.580073,37.552103,37.545461,37.580196,37.562274
              ,37.535419,37.527477,37.526139,37.648247,37.512939,37.517574,35.202902,35.144776,37.499229,35.150069,35.141176
              ,37.479403,37.512569,35.123196,37.546718,37.553668,37.488742,37.493653,37.498462,37.556602,37.544180,35.111532
              ,37.508058,35.085777,37.546103,37.483899,37.489299,35.143421],
     '구분' : ['음식','음식','음식','음식','생활서비스','음식','음식','음식','음식','음식','음식','음식','음식','음식','음식'
             ,'음식','음식','소매','음식','음식','음식','음식','소매','음식','소매','음식','음식','음식','음식','음식','음식'
             ,'음식','음식','음식','음식','소매','음식','음식','의료','음식','음식','음식','소매','음식','음식','음식','음식'
             ,'음식','음식','음식']}
    ex = pd.DataFrame(ex)
    print(ex)

    # 지도의 중심을 지정하기 위해 위도와 경도의 평균 구하기
    lat = ex['위도'].mean()
    long = ex['경도'].mean()
    
    # 지도 띄우기
    m = folium.Map([lat,long],zoom_start=9)

    for i in ex.index:
        sub_lat = ex.loc[i, '위도']
        sub_long = ex.loc[i, '경도']

        title = ex.loc[i, '구분']

        # 지도에 데이터 찍어서 보여주기
        folium.Marker([sub_lat, sub_long], tooltip=title).add_to(m)
        m.save(os.path.join(TEMPLATE_DIR,'bigdata/maptest.html'))


def weather_crawling(last_date, weather):
    req = requests.get('http://www.weather.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=108')
    html = req.text
    soup = BeautifulSoup(html,'lxml')

    for i in soup.find_all('location'):
        weather[i.find('city').text]=[]
        for j in i.find_all('data'):
            temp = []
            if(len(last_date)==0) or (j.find('tmef').text >str(last_date)):
                temp.append(j.find('tmef').text)
                temp.append(j.find('wf').text)
                temp.append(j.find('tmn').text)
                temp.append(j.find('tmx').text)
                print('temp : ', temp)
                weather[i.find('city').string].append(temp)        



def make_chart(titles, points):
    font_location="C:/Windows/fonts/malgun.ttf"
    font_name=font_manager.FontProperties(fname=font_location).get_name()
    rc('font',family=font_name)
    plt.cla()
    plt.ylabel('영화평점평균')
    plt.xlabel('영화제목')
    plt.bar(range(len(titles)),points, align='center')
    plt.xticks(range(len(titles)),list(titles),rotation=70)
    plt.savefig(os.path.join(STATIC_DIR,'images\\movie_fig.png'))


def make_wordCloud(data):
    message=''
    for item in data:
        # item에 있는 key가 message라면
        if 'message' in item.keys() :
            message = message+ re.sub(r'[^\w]',' ', item['message'])+''

    message
    # !pip install Okt
    # from konlpy.tag import Okt

    nlp = Okt()
    message_N = nlp.nouns(message)
    message_N

    # 단어 빈도 구하기 리스트형태로 전처리 돼있어야함
    from collections import Counter
    count = Counter(message_N)
    count

    # 상위 50개 단어 딕셔너리에 저장
    word_count = dict()
    for tag, counts in count.most_common(50):
        if(len(str(tag))>1):
            word_count[tag] = counts
    word_count


    font_name = mpl.font_manager.FontProperties(fname='c:/Windows/fonts/Hancom Gothic Bold.ttf').get_name()
    mpl.rc('font', family=font_name)
    plt.figure(figsize=(12,5))
    plt.xlabel('키워드')
    plt.ylabel('빈도수')
    plt.grid('true')

    # 워드 클라우드 그리기

    font_path = 'c:/Windows/fonts/Hancom Gothic Bold.ttf'
    font_name = font_manager.FontProperties(fname=font_path).get_name()


    stopwords = set(STOPWORDS)
    wc = WordCloud(font_path, background_color='ivory', width=800, height=600,)
    cloud = wc.generate_from_frequencies(word_count)
    plt.figure(figsize=(8,8))
    plt.imshow(cloud)
    plt.axis('off')
    plt.savefig(os.path.join(STATIC_DIR,'images\\k_wordcloud.png'))
    cloud.tofile('./static/images/k_wordCloud.png')

def spi_check(data):
    url = 'http://vip.mk.co.kr/newSt/price/minprice.php?&stCode=153270&type=10'
    
    req = requests.get(url, headers={ "User-Agent": "Mozilla/5.0" })
    if req.ok:
        html=req.content.decode('euc-kr','replace')
        soup=BeautifulSoup(html, 'html.parser')
        tbodys = soup.select('table.table_3')
        # body > div:nth-child(11) > div > table > tbody > tr > td:nth-child(1) > table.table_3 > tbody
        
        trs = tbodys[0].select('tr')
        
        print(trs)

        for i in trs[1:]:
            time = i.select_one('td.center').get_text()
            print(time)

            spi = i.select('td')[1].get_text().replace(',','')
            print(spi)
            data.append([time,spi])
            # body > div:nth-child(11) > div > table > tbody > tr > td:nth-child(1) > table.table_3 > tbody > tr:nth-child(2)
        print(data)

                # tr:nth-child(1) > td.center
                # tr:nth-child(1) > td:nth-child(2)
# body > div:nth-child(11) > div > table > tbody > tr > td:nth-child(1) > table.table_3 > tbody > tr:nth-child(1) > td:nth-child(2)
def spi_make_chart(time, spi):
    font_location="C:/Windows/fonts/malgun.ttf"
    font_name=font_manager.FontProperties(fname=font_location).get_name()
    rc('font',family=font_name)

    plt.cla()
    plt.ylabel('코스피 지수')
    plt.xlabel('시간')
    plt.bar(range(len(spi)),spi, align='center')
    plt.xticks(range(len(time)),list(time),rotation=70)
    plt.ylim([min(spi)-50, max(spi)+50])
    
    plt.savefig(os.path.join(STATIC_DIR,'images\\spi_fig.png'))
    

##################################
#      갑자기 모듈을 못찾을때      #
##################################

# 아나콘다3 제대로 실행되고 있는지 확인