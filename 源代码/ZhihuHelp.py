# -*- coding: utf-8 -*-
import  urllib2
import  HTMLParser
import  re
import  zlib
import  threading
import  time
import  datetime

import  json#在returnPostHeader中解析Post返回值
import  os#打开更新页面

import  sys#修改默认编码
reload( sys )
sys.setdefaultencoding('utf-8')




import  socket#捕获TimeOut错误

import sqlite3#数据库！
###########################################################
#数据库部分
import pickle
###########################################################

######TestTool#####
def PrintDict(Dict={}):
    for r   in  Dict:
        print   r.decode("utf-8") ,Dict[r].decode("utf-8")
####TestToolEnd####



def UpdatePostHeader(cursor=None ,UserID='',Password=''):#建一个用于储存PostHeader的变量#如果没输账号密码的话即使选择了模式2也会按读取公共收藏夹模式进行
    if  UserID=='':
        PrivateModeFlag=False
        UserID='mengqingxue2014@qq.com'
        Password='131724qingxue'
    else:
        PrivateModeFlag=True

    rowcount    =cursor.execute('select count(Pickle)  from VarPickle where Var="PostHeader"').fetchone()[0]
    #print   rowcount
    if  rowcount!=0:
        cursor.execute('select Pickle  from VarPickle where Var="PostHeader"') #SQLTag
        ReadHeader       =   cursor.fetchone() #SQLTag
        #print   ReadHeader
        ChangedHeader    =  pickle.loads(ReadHeader[0])
        if  ChangedHeader['UpdateTime']  !=  str(datetime.date.fromtimestamp(time.time())):
            print   u"Cookie非本日，需要更新"
            try:#SAE云豆快用完了，但愿用完之前能通过中级开发者认证。。。
                helpme      =   urllib.urlopen(u'http://zhihuhelpbyyzy.sinaapp.com/404',timeout=1)#加一个页面访问量。。。囧
            except:
                pass
            rowcount=0
    if  rowcount==0  :
        ChangedHeader    =   {}
        ChangedHeader['PostHeader']=    {
        'Host':' www.zhihu.com'
        
        ,'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
        
        ,'Accept':' */*'
        
        ,'Accept-Language':' zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'
        
        ,'Accept-Encoding':' gzip, deflate'
        
        ,'Content-Type':' application/x-www-form-urlencoded; charset=UTF-8'
        ,'X-Requested-With':' XMLHttpRequest'
        ,'Cookie':'q_c1=1be8e7b2a09e435cb54d5c2a163921d8|1395875831000|1395875831000; _xsrf=0bc5f5eab6f94e7d9d04fbb2512a4541; zata=zhihu.com.1be8e7b2a09e435cb54d5c2a163921d8.392145; q_c0="NTc1Mjk3OTkxMmM1NzU1N2MzZGQ5ZTMzMzRmNWVlMDR8MW9xU3hPdDF4U29BQlc4Qg==|1395876156|3a33a46cd3ddfd0920aadce47bc203d146f19bd6"; zatb=zhihu.com; __utma=51854390.1578864184.1395876138.1395876138.1395876138.1; __utmb=51854390.6.9.1395876161862; __utmc=51854390; __utmz=51854390.1395876138.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=51854390.100-1|2=registration_date=20130127=1^3=entry_date=20130127=1'
        ,'Connection':' keep-alive'
        ,'Pragma':' no-cache'
        ,'Cache-Control':' no-cache'
        }
        ChangedHeader["ChangeFlag"] =   False
        ChangedHeader["UpdateTime"] =   '2014-03-29'#Time和datetime模块需要导入
    header  =   {
'Accept'    :'*/*'
,'Accept-Encoding'   :'gzip,deflate,sdch'
,'Accept-Language'    :'zh,zh-CN;q=0.8,en-GB;q=0.6,en;q=0.4'
,'Connection'    :'keep-alive'
,'Content-Type'    :'application/x-www-form-urlencoded; charset=UTF-8'
,'Host'    :'www.zhihu.com'
,'Origin'    :'http://www.zhihu.com'
,'Referer'    :'http://www.zhihu.com/'
,'User-Agent'    :'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36'
,'X-Requested-With'    :'XMLHttpRequest'
}
    try :
        ZhihuFrontPage=urllib2.urlopen(u"http://www.zhihu.com")#这里也可能出错
    except  urllib2.HTTPError   as e    :
        print   u'服务器错误'
        print   u'错误内容',str(e).decode("utf-8")
        print   u'转为使用旧有PostHeader'
        return  ChangedHeader
    except  urllib2.URLError    as e    :
        print   u'网络错误'
        print   u'错误内容',str(e).decode("utf-8")
        print   u'话说网络链接正常不？'
        print   u'转为使用旧有PostHeader'
        return  ChangedHeader
    string  = ZhihuFrontPage.read()
    xsrfPos =string.find('name="_xsrf" value="')+len('name="_xsrf" value="')
    xsrf=string[xsrfPos:string.find('"',xsrfPos+3)]
    header["Cookie"]="_xsrf="+xsrf
    request =   urllib2.Request(url='http://www.zhihu.com/login',data='_xsrf={0}&email={1}&password={2}&rememberme=y'.format(xsrf,UserID,Password),headers=header)
    try :
        buf         =   urllib2.urlopen(request)
    except  urllib2.HTTPError   as e    :
        print   u'服务器错误'
        print   u'错误内容',e
        print   u'话说网络链接正常不？'
        print   u'转为使用旧有PostHeader'
        return  ChangedHeader
    except  urllib2.URLError    as e    :
        print   u'网络错误'
        print   u'错误内容',e
        print   u'话说网络链接正常不？'
        print   u'转为使用旧有PostHeader'
        return  ChangedHeader
    PostInfo    =   json.loads(buf.read())
    if  len(PostInfo)== 2   :
        print   "Login Success!"
    else    :
        try :
            print   u'错误代码:',PostInfo['errcode'],u'\n错误信息如下:'#在这里进行的登陆检测
            PrintDict(PostInfo['msg'])
            if  PrivateModeFlag:
                print   u'请在网页上登陆一次知乎帐号，确认用户名密码正确后再登陆'
                print   u'点击回车退出'
                raw_input()
                os._exit(0)
            else:
                print   u'''登陆失败，请在知乎网页上登陆下方帐号后再运行本程序：\n帐号：mengqingxue2014@qq.com\n密码：131724qingxue'''
                print   u'临时转换为使用内置旧cookie登陆，内置cookie有效期至2014-04-20日，cookie过期后程序将无法运行'#可以考虑使用旧有cookie
                print   u'点击回车继续'
                raw_input()
        except  KeyError:
            print   u"囧，这都能抛KeyError。。。\n检查下帐号密码输对没\n如果你连续三次看见这句话的话...\n肯定是改验证方式了，\n上知乎@姚泽源更新脚本"
        #PrintDict(ChangedHeader)
        return  ChangedHeader
    buf          =   buf.info()["set-cookie"]
    qc1          =   buf[0:buf.find(u';')+1]+"xsrf="+xsrf+';'
    qc0          =   buf[buf.find(u'q_c0'):buf.find(u';',buf.find(u'q_c0'))+1]
    cookie       =   qc1+qc0
    PostHeader={
    'Host':'www.zhihu.com'
    
    ,'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
    
    ,'Accept':' */*'
    
    ,'Accept-Language':' zh-cn,zh;q=0.8,en-GB;q=0.6,en;q=0.4'
    
    ,'Accept-Encoding':' gzip, deflate'
    ,'Content-Type':' application/x-www-form-urlencoded; charset=UTF-8'
    
    ,'X-Requested-With':' XMLHttpRequest'
        
    ,'Connection':' keep-alive'
    
    ,'Pragma':' no-cache'
    
    ,'Cache-Control':' no-cache'
    }
    PostHeader   ["Cookie"]     =   cookie
    ChangedHeader['PostHeader'] =   PostHeader
    ChangedHeader["ChangeFlag"] =   True
    ChangedHeader["UpdateTime"] =   str(datetime.date.fromtimestamp(time.time()))#Time和datetime模块需要导入
    
    rowcount    =   cursor.execute('select count(Pickle)  from VarPickle where Var="PostHeader"').fetchone()[0]
    if  rowcount==0:
        cursor.execute("insert  into VarPickle  (Var,Pickle) values ('PostHeader',?) ",(pickle.dumps(ChangedHeader),))
    else:
        cursor.execute("update VarPickle set Pickle=? where Var='PostHeader'",(pickle.dumps(ChangedHeader),))
    return  ChangedHeader
######################网页内容分析############################
#个人答案页面、收藏夹页面答案连接提取
class   HtmlParser(HTMLParser.HTMLParser):
    AnswerList=[]
    def handle_starttag(self ,tag, attrs):
        if  tag ==  "a":
            for name,value  in attrs    :
                if  value   ==  "answer-date-link meta-item":
                    self.AnswerList.append(attrs[2][1])
    def returnAnswerList(self):
        return  self.AnswerList
#由returnAnswerList返回提取的答案链接列表，格式：['/question/21354/answer/15488',]
#网页答案抓取
##图片重载
def PictureReload(Content=''):
    ContinueFlag    =   True
    ImgPlace        =   0
    RealPlace       =   0
    EndPlace        =   0
    while   ContinueFlag    :
        try :
            ImgPlace    =	Content.index(u'//s1.zhimg.com/misc/whitedot.jpg',ImgPlace)
            RealPlace   =   Content.index(u'data-actualsrc="',ImgPlace)+len(u'data-actualsrc="')
            EndPlace    =   Content.index(u'">',RealPlace)
            Content      =   Content.replace(u'//s1.zhimg.com/misc/whitedot.jpg',Content[RealPlace:EndPlace],1)
        except  ValueError :#所有图片连接都已处理完毕
            ContinueFlag    =   False
    return Content
##Div读取（返回答案真实部分）
def ReturnRealAnswerContent(text=''):#...居然可以这么简单，我的递归啊！我的炫技啊! T_T #哈哈^-^
    DivFirstPlace   =   0
    DivEndPlace     =   0
    DivRepeatTimes  =   0
    DivFirstPlace   =   text.index(u"zm-editable-content clearfix")+len(u"zm-editable-content clearfix")+2
    DivEndPlace     =   text.index(u'<div class="zm-item-meta zm-item-comment-el answer-actions clearfix">')
    DivEndPlace     =   text.rindex(u'</div>',DivFirstPlace,DivEndPlace)
    DivEndPlace     =   text.rindex(u'</div>',DivFirstPlace,DivEndPlace)
    return              PictureReload(text[DivFirstPlace:DivEndPlace])
#个人信息读取（提取回答首页个人信息时用，也可以用来检测知乎是否修改过页面结构）
def ReadPersonInfo(k=""):   
    Buf_Pos     =   k.find(u'<div class="title-section ellipsis">')+40
    Buf_Pos     =   k.find(u'href="/people/',Buf_Pos)+14
    ID_ID       =   k[Buf_Pos:k.find(u'"',Buf_Pos)]
    ID_Name     =   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    try:
        Buf_Pos     =   k.index(u'<span class="bio" title=')+5#找不到会抛错
    except  ValueError:
        ID_Sign     =   ''#签名档为空，要做好答题列表均为空的准备
    else    :
        ID_Sign     =   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    Buf_Pos     =   k.find(u'asks">')+15
    ID_Asks     =   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    Buf_Pos     =   k.find(u'answers">',Buf_Pos)+20
    ID_Answers  =   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    Buf_Pos     =   k.find(u'posts">',Buf_Pos)+20
    ID_Posts    =   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    Buf_Pos     =   k.find(u'collections">',Buf_Pos)+20
    ID_Collections= k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    Buf_Pos     =   k.find(u'logs">',Buf_Pos)+20
    ID_Logs     =   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    Buf_Pos     =   k.find(u'<span class="zg-gray-normal">关注了</span><br />')+50
    ID_Followees=   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    Buf_Pos     =   k.find(u'<span class="zg-gray-normal">关注者</span><br />')+50
    ID_Followers=   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    Buf_Pos     =   k.find(u'<span class="zg-gray-normal">个人主页被 ')+40          
    ID_Visit    =   k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]     
    #数据校验
    Dict    ={}
    print   'begin'
    #PrintDict(Dict)
    #print   k
    try :
        Dict['ID_Asks']	        =int(ID_Asks)
        Dict['ID_Answers']	    =int(ID_Answers)
        Dict['ID_Posts']	    =int(ID_Posts)
        Dict['ID_Collections']	=int(ID_Collections)
        Dict['ID_Logs']	        =int(ID_Logs)
        Dict['ID_Followees']	=int(ID_Followees)
        Dict['ID_Followers']	=int(ID_Followers)
        Dict['ID_Visit']	    =int(ID_Visit)
        Dict['ID_ID']	        = ID_ID
        Dict['ID_Name']	        = ID_Name
        Dict['ID_Sign']	        = ID_Sign
    except ValueError as e :#若有错肯定是致命错误
        print   u"哦漏，知乎更改页面结构了，快去喊@姚泽源 更新"
        print   u"错误信息："
        print   e
        print   u'点按回车键退出'
        raw_input()
        os._exit(0)
    return  Dict	

def ReadCollectionInfo(k=""):
    Dict            =   {}
    Buf_Pos         =   k.find(u"<title>")+7   
    Dict['title']   =   k[Buf_Pos:k.find(u'</title>')-11]
    Buf_Pos         =   k.find(u'<h2 class="zm-list-content-title">')
    Buf_Pos         =   k.find(u'<a href="/people/',Buf_Pos)+17
    Dict['AuthorID']=   k[Buf_Pos:k.find(u'"',Buf_Pos)]
    Dict['AuthorName']= k[k.find(u'>',Buf_Pos)+1:k.find(u'<',Buf_Pos)]
    return  Dict
#获取答题列表页数

def FetchMaxAnswerPageNum(Content=""):
    try:
        Pos         =   Content.index(u'">下一页</a></span>')
        RightPos    =   Content.rfind(u"</a>",0,Pos)
        LeftPos     =   Content.rfind(u">",0,RightPos)
        MaxPage     =   int(Content[LeftPos+1:RightPos])
        print   u"答案列表共计{}页".format(MaxPage)
        return MaxPage
    except:
        print   u"答案列表共计1页"
        return 1
#答案信息读取

def ReadAnswer(k='',url="",ID=""):
    Dict={}
    Dict["ID"]              =   ""#       
    Dict["Sign"]            =   ""
    Dict["AgreeCount"]      =   0#
    Dict["CollectionCount"] =   0#
    Dict["CommitCount"]     =   0#
    Dict["QuestionID"]      =   ""#
    Dict["AnswerID"]        =   ""#
    Dict["UpdateTime"]      =   "1970-01-01"
    Dict["QuestionTitle"]   =   ""#
    Dict["Questionhref"]    =   ""#
    Dict["AnswerContent"]   =   ""#
    Dict["UserName"]        =   "ErrorName"###############原数据库里没有，想办法加上它
    Dict["QuestionTitle"]   =   k[k.find(u'<title>')+len(u'<title>'):k.find(u'</title>')-5]
    Dict["Questionhref"]    =   url
    Dict["AnswerID"]        =   url[url.rfind(u"answer/")+len(u"answer/"):]
    Dict["QuestionID"]      =   url[url.find(u"question/")+len(u"question/"):url.find(u"/answer/")]
    Buffer_AgreePos         =   k.find(u'<span class="count">')+len(u'<span class="count">')
    Dict["AgreeCount"]      =   k[Buffer_AgreePos:k.find(u"<",Buffer_AgreePos)]
    
    Buffer_IDPos    =   k.find(u'<h3 class="zm-item-answer-author-wrap">')+38
    try :
        k[Buffer_IDPos:Buffer_IDPos+20].index(u"匿名用户")
        Dict['ID']      =   '404NotFound!'
        Dict['Sign']    =   ''
        Dict['UserName']=   u'匿名用户'
    except  ValueError:
        Buffer_IDPos    =   k.find('href="/people/',Buffer_IDPos)+14#话说，你用Find的时候就不担心find个-1出来么。。。#出来过，爽翻了T_T
        Dict["ID"]      =   k[Buffer_IDPos:k.find('"',Buffer_IDPos)]
        Buffer_IDPos    =   k.find('<a data-tip',Buffer_IDPos)+7
        Dict["UserName"]=   k[k.find('>',Buffer_IDPos)+1:k.find(u'<',Buffer_IDPos)]
        Buffer_IDPos    =   k.find(u'<',Buffer_IDPos)
        try :
            k[Buffer_IDPos:Buffer_IDPos+60].index(u"</a>，<strong")
            Buffer_SignPos      =   k.index(u'<strong title="', Buffer_IDPos)+len(u'<strong title="')
            Dict["Sign"]        =   k[Buffer_SignPos:k.find(u'" class="zu-question-my-bio"',Buffer_SignPos)]
        except  ValueError:
            Dict["Sign"]    =   ""
    Dict["AnswerContent"]   =   ReturnRealAnswerContent(k)
    Buffer_Date             =   k.find(u'answer-date-link meta-item" target="_blank')
    update                  =   k[k.find(u">",Buffer_Date)+1:k.find(u"<",Buffer_Date)]
    if  len(update)!=10 :
        if  len(update)!=5  :
            update  =   time.strftime(u'%Y-%m-%d',time.localtime(time.time()-86400))#昨天
        else    :
            update  =   time.strftime(u'%Y-%m-%d',time.localtime(time.time()))#今天
    Dict["UpdateTime"]      =   update
    Buffer_Commit   =   k.find(u'z-icon-comment"></i>',   Buffer_AgreePos)+len(u'z-icon-comment"></i>')                
    try :
        Dict["CommitCount"]     =   int(k[Buffer_Commit:k.find(u" 条评论",Buffer_Commit)])
    except  UnicodeEncodeError:
        Dict["CommitCount"] =   0
    Buffer_Commit           =   k.find(u'collections">')+len(u'collections">')
    Dict["CollectionCount"] =   (k[Buffer_Commit:k.find(u"<",Buffer_Commit)]).replace(u'ml>\n','0')
    ##类型验证
    try:
        Dict["AgreeCount"]      =int(Dict["AgreeCount"])
        Dict["CollectionCount"] =int(Dict["CollectionCount"])
        Dict["CommitCount"]     =int(Dict["CommitCount"])
    except ValueError as e :#若有错肯定是致命错误
        print   u"哦漏，知乎更改页面结构了，快去喊@姚泽源 更新"
        print   u"错误信息："
        print   e
        print   u'点按回车键退出'
        raise   NameError("ReadAnswer发生错误")
    return Dict
#WorkForFetchUrl    

def OpenUrl(Request):#打开网页，失败时休眠一秒后再尝试，十次为止，返回网页内容,失败则返回空字符串#需要再调整
    Times=0
    LoopFlag=True
    while   LoopFlag    and Times<5:#修改为5
        try :
            Content =   urllib2.urlopen(Request,timeout=5)
        except  urllib2.HTTPError   as  inst:
            print   inst
            if  int(inst.code/100)   ==   4:
                print   u'您所要找的网页在一片没有知识的荒原上'
                return  ''
            else:
                if  int(inst.code/100)==    5:
                    print   u"知乎服务器正在紧张的撰写答案第{}次，请耐心等待~".format(Times)
                    time.sleep(0.5)
                else    :
                    print   inst.code#待测试，看能找到403或者503错误不
                    print   u'打开网页时出现错误，0.5秒后重试'
            Times   +=  1
            time.sleep(0.5)
        except  urllib2.URLError as inst    :
            print   inst
            print   inst.reason#待测试，看能找到403或者503错误不
            print   u'错误网址：'+Request.get_full_url()
            print   u'打开网页异常#严肃脸：网址对了？#，0.5秒后重试'
            Times   +=  1
            time.sleep(0.5)
        except  socket.timeout  as  e   :
            print   e
            print   u"打开网页超时,0.5秒后重试"
            Times   +=  4
            time.sleep(0.5)

        else:
            LoopFlag    =   False
            if  Content.info().get(u"Content-Encoding")=="gzip":             
                try:    
                    k   =   zlib.decompress(Content.read(), 16+zlib.MAX_WBITS)
                except  zlib.error as   ziperror:
                    print   u'解压缩出错'
                    print   u'错误信息：'
                    print   zliberror
                    k   =   ""
            else    :
                k   =   Content.read()
            k   =   k.decode(u"utf-8",errors="ignore")
            return  k
    print   u'十次尝试全部失败，放弃读取这个答案，减小最大线程数可以减少这种现象的发生。\n附注:未能成功打开的网页链接:',Request.get_full_url()
    return  ''#失败则返回空字符串
def WorkForFetchFrontPageInfo(ID='',Collect='',PostHeader={}):#读取首页信息
    if  Collect ==  ''  and ID  ==  '':
        print   u"大爷您想干啥？ID和Collect都没填啊我去"
        print   u'点按回车键退出'
        raw_input()
        os._exit(0)
        return
    url =   "http://www.zhihu.com/"
    RequestDict={}
    Dict       ={}
    if  Collect ==  '':#抓取个人答题连接
        url +=  'people/'+ID+'/answers'
        Post =   urllib2.Request(url,headers=PostHeader)
        Content =OpenUrl(Post)
        if  Content !='':
            MaxPage =   FetchMaxAnswerPageNum(Content)
            Dict    =   ReadPersonInfo(Content)
            Dict['title']   =   Dict["ID_Name"]+u"的知乎回答集锦"
            url =   'http://www.zhihu.com/people/'+ID+'/answers?order_by=vote_num&page='  
            for t   in  range(MaxPage):
                if  t==0   :
                    RequestDict[t]  =   [urllib2.Request(url[:-6],headers=PostHeader),False]#当答案不足一页时按页排序会返回空网页
                else    :
                    RequestDict[t]  =   [urllib2.Request(url+str(t+1),headers=PostHeader),False]
    else:
        url +=  'collection/'+Collect
        Post =   urllib2.Request(url,headers=PostHeader)                    
        Content =OpenUrl(Post)
        if  Content !='':
            MaxPage =   FetchMaxAnswerPageNum(Content)
            Dict    =   ReadCollectionInfo(Content)
            Dict["CollectionID"]    =   Collect
            url =   'http://www.zhihu.com/collection/'+Collect+'?page='  
            for t   in  range(MaxPage):
                if  t==0   :
                    RequestDict[t]  =   [urllib2.Request(url[:-6],headers=PostHeader),False]#当答案不足一页时按页排序会返回空网页
                else    :
                    RequestDict[t]  =   [urllib2.Request(url+str(t+1),headers=PostHeader),False]
    return  Dict,RequestDict#MaxNum在len（dict）里
def WorkForFetchUrl(RequestDict={},Page=0):#抓取回答链接
    print   u"正在抓取第{}页上的答案链接".format(Page)
    HtmlParser_thread   =   HtmlParser()
    HtmlParser_thread.AnswerList=[]
    HtmlParser_thread.feed(OpenUrl(RequestDict[Page][0]))
    RequestDict[Page][0]=HtmlParser_thread.returnAnswerList()
    if  len(RequestDict[Page][0])!=0:
        RequestDict[Page][1]=True
    return
def WorkForGetAnswer(RequestDict={},Page=0,ID=''):#抓取回答链接,ID置空为读取收藏夹内容 
    if  ID=='':
        print   u"正在抓取第{}个答案，共{}个".format(Page,len(RequestDict))#真别扭，不想改了
    else:
        print   u"正在抓取{}的第{}个答案，共{}个".format(ID,Page,len(RequestDict))#真别扭，不想改了
    k       =   OpenUrl(RequestDict[Page][0])
    if  k   !="" :#若网页打开失败直接返回
        Dict =   ReadAnswer(k,RequestDict[Page][0].get_full_url(),ID)
        if   Dict["UpdateTime"]!=''  and Dict["UpdateTime"]!='1970-01-01':
            RequestDict[Page][0]=Dict
            RequestDict[Page][1]=True
    return

#_________________________________________________________________________________________________________#
def WorkForSuitUrl_ID(cursor=None,ID='',RequestDict={},PostHeader={}):#对抓取的Url进行处理#ID模式#是建立两个模式还是共用同一套机制？#先共用同一套机制试试
    Dict    =   {}
    No      =   0
    IndexList=  []
    OriginListSQL   =   cursor.execute('select  Questionhref    from    AnswerInfoTable where ID=?',(ID,)).fetchall()#SQLTag
    SQLDetectDict   =   {}#快速查询系统
    for QHref   in  OriginListSQL:
        SQLDetectDict[QHref[0]]    =   0
    for keyword in  RequestDict:
        if  RequestDict[keyword][1]==True:
            for url in  RequestDict[keyword][0]: 
                try :
                    SQLDetectDict[u"http://www.zhihu.com"+url]#Hash,n(1)这样就好接受多了
                except  KeyError:
                    Dict[No]    =   [urllib2.Request(u"http://www.zhihu.com"+url,headers=PostHeader),False]
                    No+=1
                IndexList.append(  u"http://www.zhihu.com"+url)
    return  Dict,IndexList
def WorkForSuitUrl_Collection(cursor=None,RequestDict={},PostHeader={}):#对抓取的Url进行处理#收藏夹模式#复杂度nlogn#核心问题：找到数据库中所没有的问题链接，返回所有问题链接
    Dict    =   {}
    No      =   0
    IndexList=  []
    for keyword in  RequestDict:
        if  RequestDict[keyword][1]==True:
            for url in  RequestDict[keyword][0]: 
                rowcount    =    cursor.execute('select  count(Questionhref)    from    AnswerInfoTable where Questionhref=?',(u"http://www.zhihu.com"+url,)).fetchone()[0]#SQLTag
                if  rowcount ==0:
                    Dict[No]    =   [urllib2.Request(u"http://www.zhihu.com"+url,headers=PostHeader),False]
                    No+=1
                IndexList.append(  u"http://www.zhihu.com"+url)

    return  Dict,IndexList
def WorkForSuitUrl_OpenError__or__ReCatchUrl(RequestList=[],PostHeader={}):#对指定UrlList进行包装重读
    Dict    =   {}
    No      =   0
    for url in  RequestList:
        Dict[No]    =   [urllib2.Request(u"http://www.zhihu.com"+url,headers=PostHeader),False]
        No+=1
    return  Dict

#_________________________________________________________________________________________________________#




def ThreadWorker_FetchUrl(MaxThread=200,RequestDict={}):
    MaxPage =   len(RequestDict)
    ThreadList=[]
    for Page in  range(MaxPage):
        ThreadList.append(threading.Thread(target=WorkForFetchUrl,args=(RequestDict,Page,)))

    for Page in  range(MaxPage):
        if  threading.activeCount()-1 <   MaxThread:#实际上是总线程数
            ThreadList[Page].start()
        else    :
            print   u'正在抓取答案链接，线程库中还有{}条线程等待运行'.format(MaxPage-Page)
            time.sleep(1)

    Thread_LiveFlag =   True
    while   Thread_LiveFlag:#等待线程执行完毕
        Thread_LiveFlag =   False
        ThreadRunning   =   0
        for t   in  ThreadList:
            if  t.isAlive():
                Thread_LiveFlag=True
                ThreadRunning+=1
        print   u"目前还有{}条线程正在运行,等待所有线程执行完毕".format(ThreadRunning)
        time.sleep(1)
    return




def ThreadWorker_GetAnswer(MaxThread=200,RequestDict={},ID=""):
    MaxPage =   len(RequestDict)
    ThreadList=[]
    for Page in  range(MaxPage):
        ThreadList.append(threading.Thread(target=WorkForGetAnswer,args=(RequestDict,Page,ID)))
                                                                                             
    for Page in  range(MaxPage):
        if  threading.activeCount()-1 <   MaxThread:
            ThreadList[Page].start()
        else    :
            print   u'正在读取答案，线程库中还有{}条线程等待运行'.format(MaxPage-Page)
            time.sleep(1)

    Thread_LiveFlag =   True
    while   Thread_LiveFlag:#等待线程执行完毕
        Thread_LiveFlag =   False
        ThreadRunning   =   0
        for t   in  ThreadList:
            if  t.isAlive():
                Thread_LiveFlag=True
                ThreadRunning+=1
        print   u"目前正在读取答案的线程数为{},等待所有线程执行完毕".format(ThreadRunning)
        time.sleep(1)
    return  

def AppendRequestDictIntoDataBase(cursor=None,RequestDict={}):#可以放在ReadAnswer里，避免数据库gone away#假定已有数据库
    
    #Contents    =   Answer_Info(ID=Dict["ID"],Sign=Dict["Sign"],AgreeCount=Dict["AgreeCount"],CollectionCount=Dict["CollectionCount"],CommitCount=Dict["CommitCount"],QuestionID=Dict["QuestionID"],AnswerID=Dict["AnswerID"],UpdateTime=Dict["UpdateTime"],QuestionTitle=Dict["QuestionTitle"],Questionhref=Dict["Questionhref"],AnswerContent=Dict["AnswerContent"],UserName=Dict["UserName"])
    
    OpenErrorIndex  =   []
    for  DictIndex   in   range(len(RequestDict)):
        #PrintDict(RequestDict[DictIndex][0])
        NeedToAppendDict    =   RequestDict[DictIndex]
        if  NeedToAppendDict[1] :
            rowcount    =   cursor.execute('select  count(Questionhref)  from    AnswerInfoTable where Questionhref=?',(NeedToAppendDict[0]['Questionhref'],)).fetchone()[0]
            if  rowcount==0:
                cursor.execute('insert  into    AnswerInfoTable (ID,Sign,AgreeCount,CollectionCount,CommitCount,QuestionID,AnswerID,UpdateTime,QuestionTitle,Questionhref,AnswerContent,UserName) values (?,?,?,?,?,?,?,?,?,?,?,?)',(NeedToAppendDict[0]["ID"],NeedToAppendDict[0]["Sign"],NeedToAppendDict[0]["AgreeCount"],NeedToAppendDict[0]["CollectionCount"],NeedToAppendDict[0]["CommitCount"],NeedToAppendDict[0]["QuestionID"],NeedToAppendDict[0]["AnswerID"],NeedToAppendDict[0]["UpdateTime"],NeedToAppendDict[0]["QuestionTitle"],NeedToAppendDict[0]["Questionhref"],NeedToAppendDict[0]["AnswerContent"],NeedToAppendDict[0]["UserName"],))
            else    :
                cursor.execute('update   AnswerInfoTable set ID=?,Sign=?,AgreeCount=?,CollectionCount=?,CommitCount=?,QuestionID=?,AnswerID=?,UpdateTime=?,QuestionTitle=?,AnswerContent=?,UserName=?  where Questionhref=?',(NeedToAppendDict[0]["ID"],NeedToAppendDict[0]["Sign"],NeedToAppendDict[0]["AgreeCount"],NeedToAppendDict[0]["CollectionCount"],NeedToAppendDict[0]["CommitCount"],NeedToAppendDict[0]["QuestionID"],NeedToAppendDict[0]["AnswerID"],NeedToAppendDict[0]["UpdateTime"],NeedToAppendDict[0]["QuestionTitle"],NeedToAppendDict[0]["AnswerContent"],NeedToAppendDict[0]["UserName"],NeedToAppendDict[0]["Questionhref"],))
        else:
            #print   NeedToAppendDict[0].get_full_url()
            OpenErrorIndex.append(NeedToAppendDict[0].get_full_url())
    return  OpenErrorIndex
def CheckUpdate():#检查更新，强制更新吧，可惜没法实现云更新了
    print   u"检查更新。。。"
    try:
        UpdateTime  =   urllib2.urlopen(u"http://zhihuhelpbyyzy-zhihu.stor.sinaapp.com/ZhihuHelpUpdateTime.txt",timeout=10)
    except:
        print   u'网络连接超时，跳过更新'
        return
    Time        =   UpdateTime.readline().replace(u'\n','').replace(u'\r','')
    url         =   UpdateTime.readline().replace(u'\n','').replace(u'\r','') 
    if  Time=="2014-04-10":#上传版本文件的时候不要用utf8编码谢谢。。。有BOM的
        print   u'当前版本已是最新版'
        return
    else:
        print   u"发现新版本，按回车键进入更新页面"
        print   u'新版本下载地址:'+url
        print   u'Mac 和 Linux 用户请手工打网址进入。。。当然，根据原码内的提示自行调整CheckUpdae里的内容也行~'
        raw_input()
        os.system('explorer '+url)#Mac和Linux用户戳过来#Linux用户把explorer改成系统里浏览器的名字，比如按了FireFox的就改成firefox  【firefox小写】，按了Chrome的就。。。再装一个Firefox。。。在我的电脑上输chrome木反应#Mac用户请把『explorer 』改成 『open /Applications/Safari.app 』（有空格）#我才不告诉你我这儿没苹果的测试环境呢口亨
    return
def ClearWindow():
    print   u"""












































  *****************************************************************************
  * ______  _   _   _   _   _   _   _        _   _   _____   _       _____    *
  *|___  / | | | | | | | | | | | | | |      | | | | | ____| | |     |  _  \   *
  *   / /  | |_| | | | | |_| | | | | |      | |_| | | |__   | |     | |_| |   *
  *  / /   |  _  | | | |  _  | | | | |      |  _  | |  __|  | |     |  ___/   *
  * / /__  | | | | | | | | | | | |_| |      | | | | | |___  | |___  | |       *
  */_____| |_| |_| |_| |_| |_| \_____/      |_| |_| |_____| |_____| |_|       *
  *         | |        / / | | |_   _| | | | | /  _  \ | | | | |_   _|        *
  *         | |  __   / /  | |   | |   | |_| | | | | | | | | |   | |          *
  *         | | /  | / /   | |   | |   |  _  | | | | | | | | |   | |          *
  *         | |/   |/ /    | |   | |   | | | | | |_| | | |_| |   | |          *
  *         |___/|___/     |_|   |_|   |_| |_| \_____/ \_____/   |_|          *
  *                            _____   _   _   _                              *
  *                           /  ___| | | | | | |                             *
  *                           | |     | | | | | |                             *
  *                           | |  _  | | | | | |                             *
  *                           | |_| | | |_| | | |                             *
  *                           \_____/ \_____/ |_|                             *
  *****************************************************************************
                请将用户主页地址或收藏夹首页地址预先存入ReadList.txt中
          比如：@yolfilm的主页网址是：http://www.zhihu.com/people/yolfilm
          '精悍名言'收藏夹的网址是：http://www.zhihu.com/collection/19619639
        将这些网址复制粘贴到ReadList.txt文件中，保存完毕后轻点回车即可开始运行"""
    raw_input()
    return




def ChooseTarget(url=''):#选择
    ID  =   re.search(r'(?<=zhihu\.com/people/)(?P<ID>[\w\.-]*)',url)#匹配ID
    Collect=re.search(r'(?<=zhihu\.com/collection/)(?P<collect>\d*)',url)#匹配收藏
    if  ID  ==  None:
        if  Collect==None:
            print   u"没有匹配到任何数据，请检查一下地址是否正确。目前只支持\
识别用户首页地址与收藏夹首页地址"
            print   u'未成功识别的地址：',url
            print   u'点按回车继续'
            raw_input()
            return  (False,"")
        else:
            print   u"成功匹配到收藏夹"
            print   Collect.group(u'collect')
            return  (False,Collect.group(u'collect'))
    else:
        print   u"成功匹配到ID"
        print   ID.group(u'ID')
        return  (True,ID.group(u'ID'))

def WriteHtmlFile(cursor=None,IndexList=[],InfoDict={},IDFlag=True):#u'没有抓取过收藏夹名字，sigh'
    Dict    =   {   'ID':'',
                    'Sign':'',
                    'AgreeCount':'',
                    'CollectionCount':'',
                    'QuestionID':'',
                    'AnswerID':'',
                    'UpdateTime':'',
                    'AnswerContent':'',
                    'CommitCount':'',
                    'QuestionTitle':'',
                    'Questionhref':'',
                    'UserName':''}
    File    =   open(u"./%(title)s.html"%InfoDict,"w")
    File.write(ShaoErBuYi(InfoDict=InfoDict,IDFlag=IDFlag))
    print   u"开始写入数据"
    MaxAnswer =   len(IndexList)
    for t   in  range(MaxAnswer):
        SelectAnswerList   =   cursor.execute("select * from AnswerInfoTable where Questionhref=?",(IndexList[t],)).fetchone()#SQLTag
        if  SelectAnswerList==None:
            continue
        Dict['ID']              =   SelectAnswerList[0]
        Dict['Sign']            =   SelectAnswerList[1]
        Dict['AgreeCount']      =   SelectAnswerList[2]
        Dict['CollectionCount'] =   SelectAnswerList[3]
        Dict['QuestionID']      =   SelectAnswerList[4]
        Dict['AnswerID']        =   SelectAnswerList[5]
        Dict['UpdateTime']      =   SelectAnswerList[6]
        Dict['AnswerContent']   =   SelectAnswerList[7]
        Dict['CommitCount']     =   SelectAnswerList[8]
        Dict['QuestionTitle']   =   SelectAnswerList[9]
        Dict['Questionhref']    =   SelectAnswerList[10]
        Dict['UserName']        =   SelectAnswerList[11]
        if  len(SelectAnswerList)!=0:
            File.write(u"""
    <h2 class="zm-item-title">
        提问：
        <a  href='%(Questionhref)s'>%(QuestionTitle)s</a>
    </h2>
    <div    class="answer-body">
        <div    class="answer-content">
            <a style="color:black;font:blod" href=http://www.zhihu.com/people/%(ID)s>%(UserName)s</a>,<strong>%(Sign)s</strong>
            <br/>
            %(AnswerContent)s    
        </div>
        <div    class='zm-item-comment-el'>
            <div  class='update' >
                回答日期：%(UpdateTime)s
            </div>
            <p  class='comment'   align   ="right">           
                赞同：%(AgreeCount)s
                收藏：%(CollectionCount)s
                评论：%(CommitCount)s 
            </p>
        </div>
    </div>
    <hr/>
            """%Dict)
    File.close()
    return
def ShaoErBuYi(InfoDict={},IDFlag=True):
    Head    ="""
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="zh-CN">
    <head>
        <title>
            %(title)s
        </title>
    
        """%InfoDict
    if  IDFlag:
        Body="""
    </head>
    <body>
        
<center><h1>%(title)s</h1></center>
        <hr/>

        <h2><center>版权声明</center></h2>
        <center><p>本网页所有答案由<a href="http://www.zhihu.com/people/%(ID_ID)s">@%(ID_Name)s</a>先生原创或整理并发表在知乎，所有版权归<a href="http://www.zhihu.com/people/%(ID_ID)s">@%(ID_Name)s</a>先生所有。</p></center>
        <center><a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/cn/">
                <img alt="知识共享许可协议" style="border-width:0" src="http://i.creativecommons.org/l/by-nc-nd/3.0/cn/88x31.png" />
            </a>
        </center>
        <br />
        <center>本作品采用<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/cn/">知识共享署名-非商业性使用-禁止演绎 3.0 中国大陆许可协议</a>进行许可。</center>
        <p>附注：</p>
        <p>先生的知乎主页：<a href="http://www.zhihu.com/people/%(ID_ID)s">http://www.zhihu.com/people/%(ID_ID)s</a></p>

        <p>先生的全部答案地址：<a href="http://www.zhihu.com/people/%(ID_ID)s/answers">http://www.zhihu.com/people/%(ID_ID)s/answers</a></p>
        <p>知乎用户协议：<a href="http://www.zhihu.com/terms#sec-licence">http://www.zhihu.com/terms#sec-licence</a></p>
        """%InfoDict
    else:
        Body='''
    </head>
    <body>
        
<center><h1>%(title)s</h1></center>
        <hr/>

        <h2><center>版权声明</center></h2>
        <center><p>本网页所有答案由<a href="http://www.zhihu.com/people/%(AuthorID)s">@%(AuthorName)s</a>在知乎收集与整理，所有版权归原作者所有。</p></center>
        <center><a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/cn/">
                <img alt="知识共享许可协议" style="border-width:0" src="http://i.creativecommons.org/l/by-nc-nd/3.0/cn/88x31.png" />
            </a>
        </center>
        <br />
        <center>本作品采用<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/cn/">知识共享署名-非商业性使用-禁止演绎 3.0 中国大陆许可协议</a>进行许可。</center>
        <p>附注：</p>
        <p><a   href="http://www.zhihu.com/people/%(AuthorID)s">@%(AuthorName)s</a>的知乎主页：<a href="http://www.zhihu.com/people/%(AuthorID)s">http://www.zhihu.com/people/%(AuthorID)s</a></p>
        <p>收藏夹地址：<a href="http://www.zhihu.com/collection/%(CollectionID)s">http://www.zhihu.com/collection/%(CollectionID)s</a></p>
        <p>知乎用户协议：<a href="http://www.zhihu.com/terms#sec-licence">http://www.zhihu.com/terms#sec-licence</a></p>
    '''%InfoDict
    MarkDown='''
<meta http-equiv="Content-Type" content="text/html" charset="utf-8" />
    <style type="text/css">
    /* GitHub stylesheet for MarkdownPad (http://markdownpad.com) */
    /* Author: Nicolas Hery - http://nicolashery.com */
    /* Version: b13fe65ca28d2e568c6ed5d7f06581183df8f2ff */
    /* Source: https://github.com/nicolahery/markdownpad-github */
    
    /* RESET
    =============================================================================*/
    /********/
    个人测试
    .zh-fav-head-title{
        font-size:18px;/*收藏夹标题大小*/;
    }
.zm-item-title{
        color:#259/*知乎问题标题颜色*/; 
        font-size:18px;
}

.zh-list-title .zm-editable-editor-input{font-size:18px;font-weight:700}/*设定列表名、编辑框的宽*/

.zg-bull{   
            padding:0 3px;
            color:#BBB;
            display:inline-block;
            font-family:Arial
        }/*添加评论 修改记录 中间的点*/
h3.zm-tiem-answer-author-info/*答主用户名与签名*/
            {
            color:#222
            font-family: 'Helvetica Neue',Helvetica,Arial,Sans-serif;
            font-size:13px;
            }
strong  {
    font-weight: bold;

}
a:link      {text-decoration:none;      color:#259 }
a:visited   {text-decoration:none;      color:#259 }
a:hover     {text-decoration:underline; color:#259 }
a:active    {text-decoration:underline; color:#259 }
.zm-item-rich-text
{
        font-size: 13px;
        color:#222;
}

.zm-item-comment-el{
        color:#999/*添加品论、关注问题等的颜色*/;
        font-size:13px;
}
.answer-content
{
    postion:relative;
    top:-25px;
}
.update{
    float:left;
}
    /************/
    html, body, div, span, applet, object, iframe, h1, h2, h3, h4, h5, h6, p, blockquote, pre, a, abbr, acronym, address, big, cite, code, del, dfn, em, img, ins, kbd, q, s, samp, small, strike, strong, sub, sup, tt, var, b, u, i, center, dl, dt, dd, ol, ul, li, fieldset, form, label, legend, table, caption, tbody, tfoot, thead, tr, th, td, article, aside, canvas, details, embed, figure, figcaption, footer, header, hgroup, menu, nav, output, ruby, section, summary, time, mark, audio, video {
      margin: 0;
      padding: 0;
      border: 0;
    }
    
    /* BODY
    =============================================================================*/
    
    body {
      font-family: Helvetica, arial, freesans, clean, sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #333;
      background-color: #fff;
      padding: 20px;
      max-width: 960px;
      margin: 0 auto;
    }
    
    body>*:first-child {
      margin-top: 0 !important;
    }
    
    body>*:last-child {
      margin-bottom: 0 !important;
    }
    
    /* BLOCKS
    =============================================================================*/
    
    p, blockquote, ul, ol, dl, table, pre {
      margin: 15px 0;
    }
    
    /* HEADERS
    =============================================================================*/
    
    h1, h2, h3, h4, h5, h6 {
      margin: 20px 0 10px;
      padding: 0;
      font-weight: bold;
      -webkit-font-smoothing: antialiased;
    }
    
    h1 tt, h1 code, h2 tt, h2 code, h3 tt, h3 code, h4 tt, h4 code, h5 tt, h5 code, h6 tt, h6 code {
      font-size: inherit;
    }
    
    h1 {
      font-size: 28px;
      color: #000;
    }
    
    h2 {
      font-size: 24px;
      border-bottom: 1px solid #ccc;
      color: #000;
    }
    
    h3 {
      font-size: 18px;
    }
    
    h4 {
      font-size: 16px;
    }
    
    h5 {
      font-size: 14px;
    }
    
    h6 {
      color: #777;
      font-size: 14px;
    }
    
    body>h2:first-child, body>h1:first-child, body>h1:first-child+h2, body>h3:first-child, body>h4:first-child, body>h5:first-child, body>h6:first-child {
      margin-top: 0;
      padding-top: 0;
    }
    
    a:first-child h1, a:first-child h2, a:first-child h3, a:first-child h4, a:first-child h5, a:first-child h6 {
      margin-top: 0;
      padding-top: 0;
    }
    
    h1+p, h2+p, h3+p, h4+p, h5+p, h6+p {
      margin-top: 10px;
    }
    
    /* LINKS
    =============================================================================*/
    
    a {
      color: #4183C4;
      text-decoration: none;
    }
    
    a:hover {
      text-decoration: underline;
    }
    
    /* LISTS
    =============================================================================*/
    
    ul, ol {
      padding-left: 30px;
    }
    
    ul li > :first-child, 
    ol li > :first-child, 
    ul li ul:first-of-type, 
    ol li ol:first-of-type, 
    ul li ol:first-of-type, 
    ol li ul:first-of-type {
      margin-top: 0px;
    }
    
    ul ul, ul ol, ol ol, ol ul {
      margin-bottom: 0;
    }
    
    dl {
      padding: 0;
    }
    
    dl dt {
      font-size: 14px;
      font-weight: bold;
      font-style: italic;
      padding: 0;
      margin: 15px 0 5px;
    }
    
    dl dt:first-child {
      padding: 0;
    }
    
    dl dt>:first-child {
      margin-top: 0px;
    }
    
    dl dt>:last-child {
      margin-bottom: 0px;
    }
    
    dl dd {
      margin: 0 0 15px;
      padding: 0 15px;
    }
    
    dl dd>:first-child {
      margin-top: 0px;
    }
    
    dl dd>:last-child {
      margin-bottom: 0px;
    }
    
    /* CODE
    =============================================================================*/
    
    pre, code, tt {
      font-size: 12px;
      font-family: Consolas, "Liberation Mono", Courier, monospace;
    }
    
    code, tt {
      margin: 0 0px;
      padding: 0px 0px;
      white-space: nowrap;
      border: 1px solid #eaeaea;
      background-color: #f8f8f8;
      border-radius: 3px;
    }
    
    pre>code {
      margin: 0;
      padding: 0;
      white-space: pre;
      border: none;
      background: transparent;
    }
    
    pre {
      background-color: #f8f8f8;
      border: 1px solid #ccc;
      font-size: 13px;
      line-height: 19px;
      overflow: auto;
      padding: 6px 10px;
      border-radius: 3px;
    }
    
    pre code, pre tt {
      background-color: transparent;
      border: none;
    }
    
    kbd {
        -moz-border-bottom-colors: none;
        -moz-border-left-colors: none;
        -moz-border-right-colors: none;
        -moz-border-top-colors: none;
        background-color: #DDDDDD;
        background-image: linear-gradient(#F1F1F1, #DDDDDD);
        background-repeat: repeat-x;
        border-color: #DDDDDD #CCCCCC #CCCCCC #DDDDDD;
        border-image: none;
        border-radius: 2px 2px 2px 2px;
        border-style: solid;
        border-width: 1px;
        font-family: "Helvetica Neue",Helvetica,Arial,sans-serif;
        line-height: 10px;
        padding: 1px 4px;
    }
    
    /* QUOTES
    =============================================================================*/
    
    blockquote {
      border-left: 4px solid #DDD;
      padding: 0 15px;
      color: #777;
    }
    
    blockquote>:first-child {
      margin-top: 0px;
    }
    
    blockquote>:last-child {
      margin-bottom: 0px;
    }
    
    /* HORIZONTAL RULES
    =============================================================================*/
    
    hr {
      clear: both;
      margin: 15px 0;
      height: 0px;
      overflow: hidden;
      border: none;
      background: transparent;
      border-bottom: 4px solid #ddd;
      padding: 0;
    }
    
    /* TABLES
    =============================================================================*/
    
    table th {
      font-weight: bold;
    }
    
    table th, table td {
      border: 1px solid #ccc;
      padding: 6px 13px;
    }
    
    table tr {
      border-top: 1px solid #ccc;
      background-color: #fff;
    }
    
    table tr:nth-child(2n) {
      background-color: #f8f8f8;
    }
    
    /* IMAGES
    =============================================================================*/
    
    img {
      max-width: 100%
    }
    </style>'''
    return  Head+MarkDown+Body

def CatchUrl(cursor=None,MaxThread=20,IDFlag=True,Target='',PostHeader={}):
    InfoDict    =   {}
    IndexList   =   []
    ErrorIndexList= []
    if  Target=="":
        return  404,InfoDict,IndexList,IDFlag #返回格式：代码(200成功、404未找到对应网页、503服务器错误),InfoDict,IndexList,IDFlag
    if  IDFlag  :
        #ID
        InfoDict    ,   RequestDict =   WorkForFetchFrontPageInfo(ID=Target,Collect='',PostHeader=PostHeader)   #此处应有一个网页打开失败返回404或503的检测
        if  len(RequestDict)==0:
            return  404,InfoDict,IndexList,IDFlag,ErrorIndexList #返回格式：代码(200成功、404未找到对应网页、503服务器错误),InfoDict,IndexList,IDFlag,ErrorIndexList
        ThreadWorker_FetchUrl(MaxThread=MaxThread,RequestDict=RequestDict) #除以8意味在9个周期内要完成指定任务 
        RequestDict ,IndexList      =   WorkForSuitUrl_ID(cursor=cursor,ID=Target,RequestDict=RequestDict,PostHeader=PostHeader)#返回待查询字典
        ThreadWorker_GetAnswer(MaxThread=MaxThread,RequestDict=RequestDict,ID=Target)
        ErrorIndexList  =   AppendRequestDictIntoDataBase(cursor=cursor,RequestDict=RequestDict)
        return  200,InfoDict,IndexList,IDFlag,ErrorIndexList 
    else:
        InfoDict    ,   RequestDict =   WorkForFetchFrontPageInfo(ID="",Collect=Target,PostHeader=PostHeader)   #此处应有一个网页打开失败返回404或503的检测
        if  len(RequestDict)==0:
            return  404,InfoDict,IndexList,IDFlag,ErrorIndexList #返回格式：代码(200成功、404未找到对应网页、503服务器错误),InfoDict,IndexList,IDFlag
        ThreadWorker_FetchUrl(MaxThread=MaxThread,RequestDict=RequestDict) #除以8意味在9个周期内要完成指定任务 
        RequestDict ,IndexList      =   WorkForSuitUrl_Collection(cursor=cursor,RequestDict=RequestDict,PostHeader=PostHeader)#返回待查询字典
        ThreadWorker_GetAnswer(MaxThread=MaxThread,RequestDict=RequestDict,ID=Target)
        ErrorIndexList  =   AppendRequestDictIntoDataBase(cursor=cursor,RequestDict=RequestDict)
        return  200,InfoDict,IndexList,IDFlag,ErrorIndexList 

def ReCatchUrl(MaxThread=20,RequestList=[],PostHeader={}):#设立一个单独的页面
    RequestDict =   WorkForSuitUrl_OpenError__or__ReCatchUrl(RequestList=RequestList,PostHeader=PostHeader)
    ThreadWorker_GetAnswer(MaxThread=MaxThread,RequestDict=RequestDict,ID=Target)
    ErrorIndexList  =   AppendRequestDictIntoDataBase(cursor=cursor,RequestDict=RequestDict)
    return  200,InfoDict,IndexList,IDFlag,ErrorIndexList 

    
    
    
    
    


def ZhihuHelp():#主函数
    CheckUpdate()
    #获取cookie
    if  os.path.isfile('./ZhihuDateBase.db'):
        conn    =   sqlite3.connect("./ZhihuDateBase.db")
        cursor  =   conn.cursor()
    else:
        conn    =   sqlite3.connect("./ZhihuDateBase.db")
        cursor  =   conn.cursor()
        cursor.execute("create table VarPickle (Var varchar(255),Pickle varchar\
(50000),primary key (Var))")
        cursor.execute("create table AnswerInfoTable    ( ID              varchar(255) not Null , Sign            varchar(9000)not Null , AgreeCount      int(11)      not Null , CollectionCount int(11)      not Null , QuestionID      varchar(100) not Null , AnswerID        varchar(100) not Null , UpdateTime      date         not Null , AnswerContent   longtext     not Null , CommitCount     int(11)      not Null , QuestionTitle   varchar(1000)not Null , Questionhref    varchar(255) not Null , UserName        varchar(255) not Null , primary key(Questionhref))")#没有数据库就新建一个
    print   u"请选择模式，输入模式序号后（1或2）回车确认"
    print   u"模式1：抓取用户回答集锦与公共收藏夹\t模式2：抓取私人收藏夹"
    if  raw_input()=='2':
        UserHeader={'UpdateTime':"2014-03-29"}
        while   UserHeader['UpdateTime']=='2014-03-29':
            print   u'请输入您的知乎帐号，回车确认：'
            ZhihuUserID=raw_input()
            print   u'请输入您的知乎密码，回车确认：'
            ZhihuUserPassword=raw_input()
            if len(ZhihuUserID)<6 or    len(ZhihuUserPassword)<8:#用户名最短应该就是a@b.cn了
                print   u'请输入正确的用户名和密码，点按回车退出'
                raw_input()
                os._exit(0)
            UserHeader  =   UpdatePostHeader(cursor=cursor,UserID=ZhihuUserID,\
Password=ZhihuUserPassword)
        PostHeader  =   UserHeader['PostHeader']
    else:
        PostHeader  =   UpdatePostHeader(cursor=cursor)['PostHeader']
    conn.commit()
    MaxThread=20
    print   u'ZhihuHelp热身中。。。\n开始设定最大允许并发线程数\n线程越多速度越快，但线程过多会导致知乎服务器故障无法打开网页读取答案失败，默认最大线程数为20\n请输入一个数字（1~50），回车确认'
    try:
        MaxThread=int(raw_input())
    except  ValueError as e  :
        print   e
        print   u'貌似输入的不是数...最大线程数重置为20，点击回车继续运行'
        MaxThread=20
        raw_input()
    if  MaxThread>200   or  MaxThread<1:
        if  MaxThread>200:
            print   u"线程不要太大好伐\n你线程开的这么凶残你考虑过知乎服务器的感受嘛"
        else:
            print   u"不要输负数啊我去"
        print u"最大线程数重置为20"
        print u'猛击回车继续~'
        raw_input()
    try:
        ReadList    =   open("./ReadList.txt","r")
    except  IOError as e:
        print   e
        print   u'貌似程序所在的目录里好像没有ReadList.txt这个文件，手工新建一个吧'
        print   u'点按回车退出'
        raw_input()
        os._exit(0)
    ClearWindow()#清屏
    Code    =   0
    InfoDict=   {}
    IndexList=  []
    IDFlag  =   False
    ErrorIndexList=False

    for url in  ReadList:
        IDFlag,Target =   ChooseTarget(url)
        if  Target=='':
            continue
        Code,InfoDict,IndexList,IDFlag,ErrorIndexList =CatchUrl(cursor=cursor,MaxThread=MaxThread,IDFlag=IDFlag,Target=Target,PostHeader=PostHeader)     
        conn.commit()                           
        WriteHtmlFile(cursor=cursor,IndexList=IndexList,InfoDict=InfoDict,IDFlag=IDFlag)                                                                               
        File    =   open(u"./未成功读取的页面列表.txt",'a')              
        File.write(u"-------------------------%(title)s:begin---------------------------\n"%InfoDict)
        if len(ErrorIndexList)!=0:
            print   u'开始输出未成功读取的答案列表至『未成功读取的页面列表.txt』中'     
            for t   in  ErrorIndexList:                                                               
                File.write(t+'\n')
                print t     
        File.write(u"-------------------------%(title)s:end---------------------------\n"%InfoDict)
        File.close()                         
        print   u'程序运行完毕，成功抓取{}条答案，{}条答案抓取失败'.format(\
(len(IndexList)-len(ErrorIndexList)),len(ErrorIndexList))
        print   u'若待抓取失败的答案过多可重复运行该程序。抓取成功的答案均已\
存入数据库『ZhihuDateBase.db』中，再次运行时将只会对不在库中的答案进行读取\
。当抓取失败的答案条数为0时，表示所有答案均已成功录入库中'
        print   u'『说人话！』'
        print   u'『重新运行将补抓未成功抓取的网页，如有漏抓请多\
运行几遍程序~。』\n\n\n'     
        try:
            print   u"%(title)s读取完毕~久等了~"%InfoDict
            print   u"%(title)s.html已经保存在程序所在的文件夹里，去看看吧~"%InfoDict
        except: 
            pass
    print   u"所有页面读取完毕~"
    print   u'点按回车键退出'
    raw_input()
    return
ZhihuHelp()
 

