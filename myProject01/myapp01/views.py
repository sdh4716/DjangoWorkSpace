from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from myapp01.models import Board, Comment
import urllib.parse
from django.http.response import HttpResponse, JsonResponse
import math , os

# Create your views here.

UPLOAD_DIR = "C:/DjangoWorkSpace/UploadedFiles/"

# write_from
def write_form(request):
    return render(request, 'board/write.html')

#insert
@csrf_exempt
def insert(request):
    fname=''
    fsize=0
    # 파일이 선택되면
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        # %s 문자열
        fp = open('%s%s' %(UPLOAD_DIR,fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto = Board(writer = request.POST['writer'],
                title = request.POST['title'],
                content = request.POST['content'],
                filename=fname,
                filesize=fsize
    )
    dto.save()
    return redirect("/list/")

# download_count
def download_count(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    dto.down_up()
    dto.save()
    count = dto.down

    return JsonResponse({'idx' : id, 'count':count})

#list
def list(request):

    page = request.GET.get('page','1')
    word = request.GET.get('word','')
    field = request.GET.get('field','title')

    print('word :',word)
    print('field :', field)

    if field == 'all':
        boardCount = Board.objects.filter(Q(writer__contains=word)
                                         |Q(title__contains=word)
                                         |Q(content__contains=word)).count()
        # where like와 같음
    elif field == 'writer':
        boardCount = Board.objects.filter(Q(writer__contains=word)).count()

    elif field == 'title':
        boardCount = Board.objects.filter(Q(title__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(Q(content__contains=word)).count()
    else:
         boardCount = Board.objects.all().count()

    pageSize = 5
    blockPage = 3
    currentPage = int(page)
    start = (currentPage -1) * pageSize

    totPage= math.ceil(boardCount/pageSize)
    startPage = math.floor((currentPage-1)/blockPage)*blockPage +1
    endPage = startPage + blockPage-1

    if endPage > totPage:
        endPage = totPage

    if field == 'all':
        boardList = Board.objects.filter(Q(writer__contains=word)
                                         |Q(title__contains=word)
                                         |Q(content__contains=word)).order_by('-idx')[start:start+pageSize]
        # where like와 같음
    elif field == 'writer':
        boardList = Board.objects.filter(Q(writer__contains=word)).order_by('-idx')[start:start+pageSize]

    elif field == 'title':
        boardList = Board.objects.filter(Q(title__contains=word)).order_by('-idx')[start:start+pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(Q(content__contains=word)).order_by('-idx')[start:start+pageSize]
    else:
        # 오름차순 = idx , 내림차순 = -idx
         boardList = Board.objects.all().order_by('-idx')[start:start+pageSize]

    print('boardCount', boardCount)

    context = {'boardList' : boardList, 'boardCount' :boardCount, 'currentPage' : currentPage,
    'word' : word, 'blockPage' : blockPage, 'startPage' : startPage, 
    'endPage' : endPage, 'totPage' : totPage, 'field' : field,
    # range는 시작부터 끝 값까지만 출력되기 때문에 +1
    'range' : range(startPage, endPage+1)}
    return render(request, 'board/list.html', context)


#상세보기(query)
def detail_idx(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()

    return render(request, 'board/detail.html',{'dto' : dto})

#상세보기(restful)
def detail(request, board_idx):
    print("board_idx",board_idx)
    dto = Board.objects.get(idx=board_idx)
    dto.hit_up()
    dto.save()
    commentList = Comment.objects.filter(board_idx=board_idx).order_by('-idx')

    return render(request, 'board/detail.html',
    {'dto' : dto, 'commentList' : commentList})

#삭제
def delete(request, board_idx):
    dto = Board.objects.get(idx=board_idx)
    dto.delete()

    return redirect("/list/")

#수정 폼
def update_form(request, board_idx):
    dto = Board.objects.get(idx=board_idx)
    return render(request, 'board/update.html',{'dto' : dto})

#수정
@csrf_exempt #csrf를 쓰지 않는다고 선언
def update(request):
    id = request.POST['idx']

    dto = Board.objects.get(idx=id)
    fname = dto.filename
    filesize = dto.filesize

    # 파일이 선택되면
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        # %s 문자열
        fp = open('%s%s' %(UPLOAD_DIR,fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto_update = Board(id,
                writer = request.POST['writer'],
                title = request.POST['title'],
                content = request.POST['content'],
                filename=fname,
                filesize=fsize)

    dto_update.save()
    return redirect('/list/')

# 댓글 입력
@csrf_exempt
def comment_insert(request):
    id = request.POST['idx']
    dto = Comment(board_idx=id, writer = 'aa', content=request.POST['content'])
    dto.save()
    # return redirect("/detail_idx?idx="+id)
    return redirect("/detail/"+id)

# 다운로드
def download(request):
    id = request.GET['idx']
    print('id',id)

    dto = Board.objects.get(idx=id)
    path = UPLOAD_DIR + dto.filename

    # filename = urlquote(path) # 장고 3.0에서 됨
    filename = urllib.parse.quote(dto.filename) # 장고 4.0에서 됨
   
    with open(path, 'rb') as file:
        response = HttpResponse(file.read(),
        content_type = 'application/octet-stream')
        response['Content-Disposition'] = "attachment; filename*=UTF-8''{0}".format(filename)
    
    # dto.down_up()
    # dto.save()
    return response

