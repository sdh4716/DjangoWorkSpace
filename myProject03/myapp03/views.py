from django.shortcuts import render, redirect,get_object_or_404
from myapp03.models import Board, Comment, Movie, Forecast, Spi
from .form import UserForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import urllib.parse
from django.http.response import HttpResponse, JsonResponse

from django.core.paginator import Paginator
# 검색 시 and, or 대신에 쓸 수 있는 컴포넌트
from django.db.models import Q

#####
from myapp03 import bigdataProcess
from django.db.models.aggregates import Avg,Count
import os, pandas as pd

import json

UPLOAD_DIR= 'C:/DjangoWorkSpace/UploadedFiles/'

def movie(request):
    data=[]
    bigdataProcess.movie_crawling(data)
    # title, point, content 순서대로 data 들어있음
    for r in data :
        dto = Movie(title=r[0],
                    point=r[1],
                    content=r[2])
        dto.save()
    return redirect('/')

def spi(request):
    data=[]
    bigdataProcess.spi_check(data)
    # time, spi
    # for r in data:
    #     dto = Spi(time=r[0], spi=r[1])
    #     dto.save()
    data = Spi.objects.values('time','spi')[0:10] # 하나의 컬럼을 가져올때 values
    df = pd.DataFrame(data)
    print(df)
    bigdataProcess.spi_make_chart(df.time, df.spi)
    return render(request, "bigdata/chart.html",{"data":data, "img_data":'spi_fig.png'})

def movie_chart(request):
    data = Movie.objects.values('title').annotate(point_avg = Avg('point'))[0:10] # 하나의 컬럼을 가져올때 values
    df = pd.DataFrame(data)
    # print(df)
    bigdataProcess.make_chart(df.title, df.point_avg)
    return render(request, "bigdata/chart.html",{"data":data, "img_data":'movie_fig.png'})

def weather(request):
    last_date = Forecast.objects.values('tmef').order_by('-tmef')[:1]
    print('last_date :', len(last_date))
    weather = {}
    bigdataProcess.weather_crawling(last_date, weather)

    # 크롤링된 데이터를 db로 저장
    for i in weather : 
        for j in weather[i]:
            dto = Forecast(city=i, tmef=j[0], wf=j[1], tmn=j[2], tmx=j[3])
            dto.save()

    result = Forecast.objects.filter(city='부산')
    result1 = Forecast.objects.filter(city='부산').values('wf').annotate(dcount=Count('wf')).values("dcount","wf")
    print("result1 query :", str(result1.query)) # sql문 보여주기

    df = pd.DataFrame(result1)
    print(df)


    image_dic = bigdataProcess.weather_make_chart(result, df.wf, df.dcount)
    print("imagedic:" , image_dic)
    return render(request,"bigdata/chart1.html",{"img_data":image_dic})
    

def map(request):
    bigdataProcess.map()
    return render(request, "bigdata/map.html")

def wordcloud(request):
    a_path="C:/DjangoWorkSpace/myProject03/data/"
    data = json.loads(open(a_path+'4차 산업혁명.json','r',encoding='utf-8').read())
    bigdataProcess.make_wordCloud(data)
    return render(request, 'bigdata/chart.html',{"img_data":'k_wordCloud.png'})

############################

#write_form
@login_required(login_url='/login/')
def write_form(request):
    return render(request, 'board/write.html',
                )


#insert
@csrf_exempt
def insert(request):
    fname=''
    fsize=0
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR, fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()    

    dto = Board(writer=request.user,
            title=request.POST['title'],
            content=request.POST['content'],
            filename=fname,
            filesize=fsize
    )
    dto.save()
    return redirect("/list/")

#list
def list(request):

    page = request.GET.get('page','1')
    word = request.GET.get('word','')
    boardCount = Board.objects.filter(Q(writer__username__icontains=word)
                                |Q(title__contains=word)
                                |Q(content__contains=word)).count()
    boardList = Board.objects.filter(Q(writer__username__icontains=word)
                        |Q(title__contains=word)
                        |Q(content__contains=word)).order_by('-id')

    pageSize = 5
   
    #페이징처리
    paginator = Paginator(boardList,pageSize)  #import
    print('paginator :' , paginator)
    page_obj = paginator.get_page(page)
    print('page_obj :' , page_obj)
     
    rowNo = boardCount-(int(page)-1)*pageSize

    context ={'page_list':page_obj, 'page' : page ,
               'word':word, 'boardCount':boardCount,'rowNo':rowNo }
    return render(request, 'board/list.html',context)     



# download_count
def download_count(request):
    id = request.GET['id']
    dto = Board.objects.get(id =id)
    dto.down_up()
    dto.save()
    count = dto.down

    return JsonResponse({'id' : id , 'count':count})


            
#다운로드
def download(request):
    id = request.GET['id']
 
    dto = Board.objects.get(id =id)
    path = UPLOAD_DIR + dto.filename
    #filename = urlquote(path)  # 장고 3
    filename = urllib.parse.quote(dto.filename)  # 장고 4.0
    print("filename :", filename)
    with open(path,'rb') as file:
        response=HttpResponse(file.read(), 
                             content_type='application/octet-stream')  # import 필요함
        response['Content-Disposition']="attachment;filename*=UTF-8''{0}".format(filename)
 
        return response      


#상세보기
def detail(request, board_id):
    dto = Board.objects.get(id=board_id)
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail.html',
        {'dto' : dto}) 


#comment_insert
@login_required(login_url='/login/')
@csrf_exempt
def comment_insert(request):  
    board_id = request.POST['id']
    board = get_object_or_404(Board, pk=board_id) 
    dto = Comment(
                 writer=request.user,
                 content= request.POST['content'],board=board)
    dto.save()
    #return redirect("/detail_idx?idx="+id)  
    return redirect("/detail/"+board_id)  


#삭제
def delete(request, board_id):
    Board.objects.get(id=board_id).delete() 
    return redirect("/list/")   

#수정 폼
def update_form(request,board_id) : 
    dto = Board.objects.get(id=board_id)
    return render(request, 'board/update.html',{'dto' : dto})

#수정
@csrf_exempt
def update(request):
    id = request.POST['id']

    dto = Board.objects.get(id=id)
    fname = dto.filename
    fsize = dto.filesize

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR, fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()  


    dto_update  = Board(id,
            # user이 String이 아닌 객체이기 때문에,
            writer=request.user,
            title=request.POST['title'],
            content=request.POST['content'],
            filename=fname,
            filesize=fsize)
    dto_update.save()

    return redirect('/list/') 



#################
# sign up 
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)  #import
        if form.is_valid():
            print('signup POST is_valid')
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password) #import
            login(request,user)
            return redirect('/') #import 
        else:
            print('signup POST un_valid')
    else:
        form = UserForm()

    return render(request, 'common/signup.html',{'form':form})