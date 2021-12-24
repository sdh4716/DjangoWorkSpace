from django.shortcuts import render,redirect
from myapp02.models import Board, Comment
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator


from django.utils.http import urlquote
from django.http.response import HttpResponse, JsonResponse
import urllib.parse
import math , os
# Create your views here.

UPLOAD_DIR= 'd:/JUNG/DjangoWorkSpace/upload/'

#write_form
def write_form(request):
    return render(request, 'board/write.html')

#list
def list(request):

    page = request.GET.get('page','1')
    word = request.GET.get('word','')
    boardCount = Board.objects.filter(Q(writer__contains=word)
                                |Q(title__contains=word)
                                |Q(content__contains=word)).count()
    boardList = Board.objects.filter(Q(writer__contains=word)
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

#list22222
def list2(request):

    page = request.GET.get('page','1')
    word = request.GET.get('word','')
    field = request.GET.get('field','title')

    print('word :', word)
    print('field :', field)

    if field =='all':
        boardCount = Board.objects.filter(Q(writer__contains=word)
                                |Q(title__contains=word)
                                |Q(content__contains=word)).count()
    elif field =='writer':
        boardCount = Board.objects.filter(Q(writer__contains=word)).count()

    elif field == 'title':
        boardCount = Board.objects.filter(Q(title__contains=word)).count()

    elif field =='content':
        boardCount = Board.objects.filter(Q(content__contains=word)).count()

    else:
        boardCount = Board.objects.all().count()

    pageSize = 5
    blockPage =3
    currentPage = int(page)
    start = (currentPage-1) * pageSize

    totPage= math.ceil(boardCount/pageSize)   
    startPage = math.floor((currentPage-1)/blockPage)*blockPage+1  
    endPage = startPage+blockPage-1

    if endPage > totPage:
        endPage = totPage

    if field =='all':
        boardList = Board.objects.filter(Q(writer__contains=word)
                                |Q(title__contains=word)
                                |Q(content__contains=word)).order_by('-id')[start:start+pageSize]
    elif field =='writer':
        boardList = Board.objects.filter(Q(writer__contains=word)).order_by('-id')[start:start+pageSize]

    elif field == 'title':
        boardList = Board.objects.filter(Q(title__contains=word)).order_by('-id')[start:start+pageSize]

    elif field =='content':
        boardList = Board.objects.filter(Q(content__contains=word)).order_by('-id')[start:start+pageSize]

    else:
        boardList = Board.objects.all().order_by('-id')[start:start+pageSize]


   
    print('boardCount',boardCount)

    context ={'boardList' : boardList, 'boardCount':boardCount, 'currentPage' : currentPage,
         'word' : word , 'blockPage' : blockPage, 'startPage':startPage,
         'endPage' : endPage, 'totPage': totPage, 'field' : field,
         'range' : range(startPage, endPage+1)}
    return render(request, 'board/list2.html',context) 


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

    dto = Board(writer=request.POST['writer'],
            title=request.POST['title'],
            content=request.POST['content'],
            filename=fname,
            filesize=fsize
    )
    dto.save()
    return redirect("/list/")   



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
            writer=request.POST['writer'],
            title=request.POST['title'],
            content=request.POST['content'],
            filename=fname,
            filesize=fsize)
    dto_update.save()

    return redirect('/list/') 

#comment_insert
@csrf_exempt
def comment_insert(request):  
    id= request.POST['id']
    dto = Comment(board_id=id,
                 writer='aa',
                 content= request.POST['content'])
    dto.save()
    #return redirect("/detail_idx?idx="+id)  
    return redirect("/detail/"+id)           