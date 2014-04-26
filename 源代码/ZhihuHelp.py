# -*- coding: utf-8 -*-
import  urllib2
import  HTMLParser
import  re
import  zlib
import  threading
import  time
import  datetime
import  HTMLParser#HTML解码&lt;
import  json#在returnPostHeader中解析Post返回值
import  os#打开更新页面

import  urllib


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
        print   str(r).decode("utf-8") ,'\t\t',str(Dict[r]).decode("utf-8")
####TestToolEnd####

######################网页内容分析############################
#个人答案页面、收藏夹页面答案连接提取
#由returnAnswerList返回提取的答案链接列表，格式：['/question/21354/answer/15488',]
#网页答案抓取
def FetchMaxAnswerPageNum(Content=""):#简单搜索比正则更快
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

def OpenUrl(Request):#打开网页,只尝试一次，失败时返回空字符串，错误信息中包含未打开网址。话说字符串分割对空列表还有效否？
    try :
        Content =   urllib2.urlopen(Request,timeout=5)
    except  urllib2.HTTPError   as  inst:
        print   inst
        if  int(inst.code/100)   ==   4:
            print   u'您所要找的网页在一片没有知识的荒原上'#不报错
            raise   IOError(u"404 Not Found"+u"错误页面\t：\t"+Request.get_full_url())#此失败不可修复，通过报错直接跳过读取该页面
            return  ''
        else:
            if  int(inst.code/100)==    5:
                print   u"知乎正在紧张的撰写答案,服务器繁忙ing，稍后重试"
            else    :
                print   inst.code#未知错误
                print   u'打开网页时出现未知错误'
    except  urllib2.URLError as inst    :
        print   inst
        print   inst.reason#原因不详
        print   u'错误网址：'+Request.get_full_url()
        print   u'打开网页异常#稍后重试'
    except  socket.timeout  as  e   :
        print   e
        print   u"打开网页超时"
    else:
        if  Content.info().get(u"Content-Encoding")=="gzip":             
            try:    
                k   =   zlib.decompress(Content.read(), 16+zlib.MAX_WBITS)
            except  zlib.error as   ziperror:
                print   u'解压缩出错'
                print   u'错误信息：'
                print   zliberror
                k   =   ""
                raise   IOError(u"解压缩错误"+u"错误页面\t：\t"+Request.get_full_url())#此失败不可修复，通过报错直接跳过读取该页面
        else    :
            k   =   Content.read()
        k   =   k.decode(u"utf-8",errors="ignore")
        return  k
    return  ''#失败则返回空字符串
def ThreadWorker(cursor=None,ErrorTextDict={},MaxThread=200,RequestDict={},Flag=1):
    MaxPage =   len(RequestDict)
    ReDict  =   returnReDict()
    AnswerDictList=[]#储存Dict，一并执行SQL
    html_parser=HTMLParser.HTMLParser()
    ThreadList=[]
    for Page in  range(MaxPage):
        ThreadList.append(threading.Thread(target=WorkForFetchUrl,args=(ErrorTextDict,ReDict,html_parser,RequestDict,Page,AnswerDictList,Flag)))
    Times   =   0
    ErrorCount= 0
    LoopFlag=   True
    while   Times<10 and LoopFlag:
        print   u'第{}遍抓取，目前打开失败的页面数={}，稍后会重新打开失败的页面,共尝试10遍'.format(Times+1,ErrorCount)
        for Page in  range(MaxPage):
            if  threading.activeCount()-1 <   MaxThread:#实际上是总线程数
                ThreadList[Page].start()#有种走钢丝的感觉。。。
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
        LoopFlag    =   False
        ErrorCount  =   0
        NewThreadList   =   []
        for t   in  RequestDict:
            if  RequestDict[t][1]==False:
                NewThreadList.append(threading.Thread(target=WorkForFetchUrl,args=(ErrorTextDict,ReDict,html_parser,RequestDict,t,AnswerDictList,Flag)))
                ErrorCount  +=  1
                LoopFlag    =   True
        MaxPage =   ErrorCount
        ThreadList  =   NewThreadList
        Times   +=  1
        if  LoopFlag:
            print   u'第{}遍答案抓取执行完毕，尚存错误页面数{},3秒后进行下一遍抓取'.format(Times+1,ErrorCount)
            time.sleep(3)
    for Dict    in  AnswerDictList:
        AppendDictIntoDataBase(cursor,Dict)
    return
def SaveCollectionIndexIntoDB(RequestDict={},CollectionID=0,cursor=None):
    AnswerList  =   []
    for t   in  RequestDict:
        try:
            RequestDict[t][0].get_full_url()
        except  AttributeError:
            for i   in   RequestDict[t][0]:
                AnswerList.append(i)
    for i   in  AnswerList:
        rowcount    =   cursor.execute('select  count(CollectionID) from    CollectionIndex where CollectionID=?    and Questionhref=?',(CollectionID,i)).fetchone()[0]
        if  rowcount    ==  0:
            cursor.execute('insert  into CollectionIndex   (CollectionID,Questionhref)  values  (?,?) ',(CollectionID,i))
        else    :
            pass
    return
def AppendDictIntoDataBase(cursor=None,Dict={}) :   #假定已有数据库
    rowcount    =   cursor.execute('select  count(Questionhref)  from    AnswerInfoTable where Questionhref=?',(Dict['Questionhref'],)).fetchone()[0]
    if  rowcount==0 :
        cursor.execute('insert  into    AnswerInfoTable (ID,Sign,AgreeCount,CommitCount,QuestionID,AnswerID,UpdateTime,QuestionTitle,Questionhref,UserName) values (?,?,?,?,?,?,?,?,?,?)',(Dict["ID"],Dict["Sign"],Dict["AgreeCount"],Dict["CommitCount"],Dict["QuestionID"],Dict["AnswerID"],Dict["UpdateTime"],Dict["QuestionTitle"],Dict["Questionhref"],Dict["UserName"],))
        cursor.execute('insert  into    AnswerContentTable (Questionhref,AnswerContent) values (?,?)',(Dict["Questionhref"],Dict["AnswerContent"]))
    else    :
        cursor.execute('update   AnswerInfoTable set ID=?,Sign=?,AgreeCount=?,CommitCount=?,QuestionID=?,AnswerID=?,UpdateTime=?,QuestionTitle=?,UserName=?  where Questionhref=?',(Dict["ID"],Dict["Sign"],Dict["AgreeCount"],Dict["CommitCount"],Dict["QuestionID"],Dict["AnswerID"],Dict["UpdateTime"],Dict["QuestionTitle"],Dict["UserName"],Dict["Questionhref"],))
        cursor.execute('update  AnswerContentTable set AnswerContent=? where Questionhref=?',(Dict["AnswerContent"],Dict["Questionhref"],))
    return 
def CheckUpdate():#检查更新，强制更新
    print   u"检查更新。。。"
    try:
        UpdateTime  =   urllib2.urlopen(u"http://zhihuhelpbyyzy-zhihu.stor.sinaapp.com/ZhihuHelpUpdateTime.txt",timeout=10)
    except:
        return
    Time        =   UpdateTime.readline().replace(u'\n','').replace(u'\r','')
    url         =   UpdateTime.readline().replace(u'\n','').replace(u'\r','') 
    if  Time=="2014-03-31":
        return
    else:
        print   u"发现新版本，按回车键进入更新页面"
        print   u'新版本下载地址:'+url
        print   u'Mac 和 Linux 用户请手工打网址进入。。。当然，根据原码内的提示自行调整CheckUpdae里的内容也行~'
        raw_input()
        import  webbrowser
        webbrowser.open_new_tab(url)
    return
def ChooseTarget(url=''):#选择
    try :
        ID      =   re.search(r'(?<=zhihu\.com/people/)(?P<ID>[\w\.-]*)',url).group(0)#匹配ID
    except  AttributeError:
        pass
    else:
        print   u'成功匹配到知乎ID，ID=',ID
        return  1,ID
    try :
        Collect =   re.search(r'(?<=zhihu\.com/collection/)(?P<collect>\d*)',url).group(0)#匹配收藏
    except  AttributeError:
        pass
    else:
        print   u'成功匹配到收藏夹，收藏夹代码=',Collect
        return  2,Collect
    try :
        Roundtable= re.search(r'(?<=zhihu\.com/roundtable/)[^/]*',url).group(0)#知乎圆桌
    except  AttributeError:
        pass
    else:
        print   u'成功匹配到知乎圆桌，圆桌名=',Roundtable
        return  3,Roundtable
    try :
        Topic   =   re.search(r'(?<=zhihu\.com/topic/)[^/]*',url).group(0)#知乎话题
    except  AttributeError:
        pass
    else:
        print   u'成功匹配到话题，话题代码=',Topic
        return  4,Topic
    return  0,""

def WriteHtmlFile(cursor=None,IndexList=[],InfoDict={},TargetFlag=0):#u'没有抓取过收藏夹名字，sigh'
    TitleDict    =   returnHtml_FrontPage(Flag=TargetFlag,InfoDict=InfoDict)
    Dict    =   {   'ID':'',
                    'Sign':'',
                    'AgreeCount':'',
                    'AnswerContent':'',
                    'QuestionID':'',
                    'AnswerID':'',
                    'UpdateTime':'',
                    'AnswerContent':'',
                    'CommitCount':'',
                    'QuestionTitle':'',
                    'Questionhref':'',
                    'UserName':''}
    File    =   open(u"./知乎答案集锦/%(title)s.html"%TitleDict,"w")
    File.write(TitleDict['FrontPageString'])
    print   u"开始生成网页集锦"
    MaxAnswer =   len(IndexList)
    for t   in  range(MaxAnswer):
        SelectAnswerList    =   cursor.execute("select * from AnswerInfoTable where Questionhref=?",(IndexList[t],)).fetchone()#SQLTag
        cursor.execute('select  AnswerContent   from    AnswerContentTable  where   Questionhref=?',(IndexList[t],))
        AnswerContent       =   cursor.fetchone()[0]
        if  SelectAnswerList==None:
            continue
        Dict['ID']              =   SelectAnswerList[0]
        Dict['Sign']            =   SelectAnswerList[1]
        Dict['AgreeCount']      =   SelectAnswerList[2]
        Dict['AnswerContent']   =   AnswerContent
        Dict['QuestionID']      =   SelectAnswerList[3]
        Dict['AnswerID']        =   SelectAnswerList[4]
        Dict['UpdateTime']      =   SelectAnswerList[5]
        Dict['CommitCount']     =   SelectAnswerList[6]
        Dict['QuestionTitle']   =   SelectAnswerList[7]
        Dict['Questionhref']    =   SelectAnswerList[8]
        Dict['UserName']        =   SelectAnswerList[9]
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
                评论：%(CommitCount)s 
            </p>
        </div>
    </div>
    <hr/>
            """%Dict)
    File.close()
    print   u'%(title)s制作完毕'%TitleDict
    return
def returnHtml_FrontPage(Flag=0,InfoDict={}):
    Dict={}
    string=''
    if  Flag==1:
        Dict['title']   =   InfoDict['Name']+'(%(ID)s)'%InfoDict+u'先生的知乎答案集锦'
        Dict['ID_ID']      =   InfoDict['ID']
        Dict['ID_Name']    =   InfoDict['Name']
        string    =    """<center><h1>%(title)s</h1></center>
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
            """%Dict
    if  Flag==2:
        Dict['title']       =   u'知乎收藏之'+InfoDict['Title']
        Dict['Description'] =   InfoDict['Description']
        Dict['AuthorID']    =   InfoDict['AuthorID']
        Dict['AuthorName']  =   InfoDict['AuthorName']
        Dict['CollectionID']=   InfoDict['TargetID']
        

        string    = """<center><h1>%(title)s</h1></center>
                <hr/>
                <p>%(Description)s</p>
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
                <p>知乎用户协议：<a href="http://www.zhihu.com/terms#sec-licence">http://www.zhihu.com/terms#sec-licence</a></p>"""%Dict
    if  Flag==4:#Topic
        Dict['title']       =   u'知乎话题之'+InfoDict['Title']
        Dict['Description'] =   InfoDict['Description']
        Dict['Adress']      =   InfoDict['Adress']
        string    = """<center><h1>%(title)s</h1></center>
                <hr/>
                <p>%(Description)s</p>
                <h2><center>版权声明</center></h2>
                <center><p>本网页所有答案来自于<a href="http://www.zhihu.com">知乎</a>，所有版权归原作者所有。</p></center>
                <center><a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/cn/">
                        <img alt="知识共享许可协议" style="border-width:0" src="http://i.creativecommons.org/l/by-nc-nd/3.0/cn/88x31.png" />
                    </a>
                </center>
                <br />
                <center>本作品采用<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/cn/">知识共享署名-非商业性使用-禁止演绎 3.0 中国大陆许可协议</a>进行许可。</center>
                <p>附注：</p>
                <p>话题地址：<a href="http://www.zhihu.com%(Adress)s">http://www.zhihu.com%(Adress)s</a></p>
                <p>知乎用户协议：<a href="http://www.zhihu.com/terms#sec-licence">http://www.zhihu.com/terms#sec-licence</a></p>"""%Dict

    Head    =\
"""
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="zh-CN">
    <head>
        <title>
            %(title)s
        </title>
    </head>
    <body>

        """%Dict
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

    Dict["FrontPageString"]=Head    +  MarkDown + string  
    return  Dict
def returnReDict():#返回编译好的正则字典
    Dict    =   {}
    Dict['_Collection_QusetionTitle']  =   re.compile(r'(?<=href="/question/\d{8}">).*?(?=</a></h2>)')
    Dict['_QusetionTitle']  =   re.compile(r'(?<=href="/question/\d{8}/answer/\d{8}">).*?(?=</a></h2>)')
    Dict['_AnswerContent']  =   re.compile(r'(?<=<textarea class="content hidden">).*(?=<span class="answer-date-link-wrap"><a class="answer-date-link meta-item" target="_blank" href="/question/\d{8}/answer/\d{8}">[^<]*</a></span></textarea>)')
    Dict['_AgreeCount']  =   re.compile(r'(?<=data-votecount=")\d*(?=">)')
    Dict['_QuestionID']  =   re.compile(r'(?<=<a class="answer-date-link meta-item" target="_blank" href="/question/)\d{8}(?=/answer/\d{8})')#数字位数可能有误#不过对11年的数据也有效，貌似多虑了——除非知乎问题能突破5千万条，否则没必要更新
    Dict['_AnswerID']  =   re.compile(r'(?<=<a class="answer-date-link meta-item" target="_blank" href="/question/\d{8}/answer/)\d{8}(?=">)')
    Dict['_Questionhref']  =   re.compile(r'(?<=<a class="answer-date-link meta-item" target="_blank" href=")[/question\danswer]{34}(?=">)')
    Dict['_UpdateTime']  =   re.compile(r'(?<=<a class="answer-date-link meta-item" target="_blank" href="/question/\d{8}/answer/\d{8}">).*(?=</a></span></textarea>)')#分为13：25、昨天 00:26、2013-05-07三种情况，需进一步处理
    Dict['_CommitCount']  =   re.compile(r'(?<=<i class="z-icon-comment"></i>).*?(?= )')#若转化为int失败则是添加评论#即为0条
    Dict['_ID']  =   re.compile(r'(?<=<a data-tip="p\$t\$)[^"]*(?=" href="/people/)')
    Dict['_UnSuccessName']  =   re.compile(r'(?<=<h3 class="zm-item-answer-author-wrap">).*(?=</h3></div>)')
    Dict['_Sign']  =   re.compile(r'(?<=<strong title=").*(?=" class="zu-question-my-bio">)')
    Dict['_NoRecord']  =   re.compile(r'<span class="copyright zu-autohide"><span class="zg-bull">&bull;</span> 禁止转载</span>')#怎么用？   
    return  Dict


def ErrorReturn(ErrorInfo=""):#返回错误信息并退出，错误信息要用unicode编码
    print   ErrorInfo
    print   u"点按回车退出"
    input()                                                                       
    os._exit(0)                                                                     
    
def SaveAnswerDictIntoDB(AnswerDict={},cursor=None):
    #1.将答案链接存入作者列表中
    #2.检查答案链接里的更新日期是否与数据库中的日期相同，相异则更新数据库# 好麻烦。。。算了吧，不在乎这点CPU使用量
    #3.没有办法记录答案在收藏夹里的位置，只能全部抓取，重新排序后输出
    if  AnswerDict=={}  or  AnswerDict['UpdateTime']=='1970-01-01':
        return
    rowcount    =   cursor.execute('select count(ID)  from AnswerInfoTable where Questionhref=?',(AnswerDict['Questionhref'],)).fetchone()[0]
    if  rowcount==0:
        cursor.execute("insert  into AnswerInfoTable  (ID,Sign,AgreeCount,QuestionID,AnswerID,UpdateTime,CommitCount,QuestionTitle,Questionhref,UserName) values (?,?,?,?,?,?,?,?,?,?)",(Dict["ID"],Dict["Sign"],Dict["AgreeCount"],Dict["QuestionID"],Dict["AnswerID"],Dict["UpdateTime"],Dict["CommitCount"],Dict["QuestionTitle"],Dict["Questionhref"],Dict["UserName"]))
    else:
        cursor.execute("update AnswerInfoTable set ID=?,Sign=?,AgreeCount=?,QuestionID=?,AnswerID=?,UpdateTime=?,CommitCount=?,QuestionTitle=?,UserName=?   where   Questionhref=?",(Dict["ID"],Dict["Sign"],Dict["AgreeCount"],Dict["QuestionID"],Dict["AnswerID"],Dict["UpdateTime"],Dict["CommitCount"],Dict["QuestionTitle"],Dict["UserName"],Dict["Questionhref"]) )
    
    rowcount    =   cursor.execute('select count(Questionhref)  from AnswerContentTable where Questionhref=?',(AnswerDict['Questionhref'],)).fetchone()[0]
    if  rowcount==0:
        cursor.execute("insert  into AnswerContentTable  (AnswerContent,Questionhref) values (?,?)",(Dict['AnswerContent'],Dict["Questionhref"]))
    else:
        cursor.execute("update  AnswerContentTable  set    AnswerContent=? where   Questionhref    =   ?",(Dict['AnswerContent'],Dict["Questionhref"]))
    return  
    
        
def ReadAnswer(ReDict,html_parser,LastDict,text="",Flag=1):
    Dict={}    
    Dict["ID"]              =   ""#       
    Dict["Sign"]            =   ""#
    Dict["AgreeCount"]      =   0#
    Dict["CommitCount"]     =   0#
    Dict["QuestionID"]      =   ""#
    Dict["AnswerID"]        =   ""
    Dict["UpdateTime"]      =   "1970-01-01"#
    Dict["QuestionTitle"]   =   ""#
    Dict["Questionhref"]    =   ""#
    Dict["AnswerContent"]   =   ""#
    Dict["UserName"]        =   "ErrorName"#
    if  text=='':
        return  Dict
    try :#检测禁止转载
        ReDict['_NoRecord'].search(text).group(0)
        return Dict
    except  :
        pass
    try:
        Dict["AgreeCount"]      =   ReDict['_AgreeCount'].search(text).group(0)
    except  AttributeError:
        print   u"赞同数没有收集到"
        return  Dict#ErrorReturn(u" 知乎页面结构已变动，程序无法正常运行，快上知乎@姚泽源喊他更新脚本" )#所有在工作线程里让人敲回车的设计都是耍流氓
    try:
        Dict["QuestionID"]      =   ReDict['_QuestionID'].search(text).group(0)
    except  AttributeError:
        print   u"问题ID没有收集到"
        return  Dict#ErrorReturn(u" 知乎页面结构已变动，程序无法正常运行，快上知乎@姚泽源喊他更新脚本" )
   
    try:                                                                        
        Dict["AnswerID"]        =   ReDict['_AnswerID'].search(text).group(0)
    except  AttributeError:
        print   u"回答ID没有收集到"
        return  Dict#ErrorReturn(u" 知乎页面结构已变动，程序无法正常运行，快上知乎@姚泽源喊他更新脚本" )
    try:                                                                        
        Dict["Questionhref"]    =   'http://www.zhihu.com'+ReDict['_Questionhref'].search(text).group(0)
    except  AttributeError:
        print   u"问题链接没有收集到"
        return  Dict#ErrorReturn(u" 知乎页面结构已变动，程序无法正常运行，快上知乎@姚泽源喊他更新脚本" )
    try:
        Dict["AnswerContent"]   =   html_parser.unescape(ReDict['_AnswerContent'].search(text).group(0)).encode("utf-8")
    except  AttributeError:
        print   u"答案内容没有收集到"
        return  Dict#ErrorReturn(u" 知乎页面结构已变动，程序无法正常运行，快上知乎@姚泽源喊他更新脚本" )
    
    update                  =   ReDict['_UpdateTime'].search(text).group(0)
    if  len(update)!=10 :        
        if  len(update)!=5  :
            update  =   time.strftime(u'%Y-%m-%d',time.localtime(time.time()-86400))#昨天
        else    :
            update  =   time.strftime(u'%Y-%m-%d',time.localtime(time.time()))#今天
    Dict["UpdateTime"]      =   update
    try:
        Dict["CommitCount"] =   int(ReDict['_CommitCount'].search(text).group(0))
    except  ValueError:
        Dict["CommitCount"] =   0
    if  Flag==1:
        try :
            Dict["QuestionTitle"]   =   ReDict['_QusetionTitle'].search(text).group(0)
        except  AttributeError:
            Dict["QuestionTitle"]   =   LastDict["QuestionTitle"]
    else    :
        try :                                                                             
            Dict["QuestionTitle"]   =   ReDict['_Collection_QusetionTitle'].search(text).group(0)
        except  AttributeError:
            Dict["QuestionTitle"]   =   LastDict["QuestionTitle"]
    try :                               
        ID                  =   ReDict['_ID'].search(text).group(0)
        _UserName    	    =	re.compile(r'(?<=<a data-tip="p\$t\$'+ID+r'" href="/people/'+ID+r'">).*?(?=</a>)')#   这里必须要用到已经捕获的ID，否则没法获得用户名
        Dict["UserName"]    =   _UserName.search(text).group(0)
    except  AttributeError  :
        try :#对应于知乎用户与匿名用户两种情况
            Dict["UserName"]    =   ReDict['_UnSuccessName'].search(text).group(0)
            ID                  =   '404NotFound!'
        except  AttributeError:
            Dict["UserName"]    =   u"知乎用户"
            ID                  =   'ZhihuUser!'

    Dict["ID"]              =   ID
    try :
        Dict["Sign"]        =   ReDict['_Sign'].search(text).group(0)
    except  AttributeError  :
        Dict["Sign"]        =   ""
    # 类型验证
    try:
        Dict["AgreeCount"]      =int(Dict["AgreeCount"])           
        Dict["CommitCount"]     =int(Dict["CommitCount"])          
    except ValueError as e :#若有错肯定是致命错误    
        print   u"错误信息："                            
        print   e                                                  
        print   u'点按回车键退出'                    
        return  Dict#ErrorReturn(u"哦漏，知乎更改页面结构了，快去喊@姚泽源 更新")
    return Dict

def WorkForFetchUrl(ErrorTextDict={},ReDict={},html_parser=None,RequestDict={},Page=0,AnswerDictList=[],Flag=1):#抓取回答链接#注意，Page是字符串
    print   u"正在抓取第{}页上的答案".format(Page+1)
    AnswerList  =   []
    try :
        k   =   OpenUrl(RequestDict[Page][0])
    except  IOError as  e:
        ErrorTextDict[Page] = str(e)  
        RequestDict[Page][1]=True
        return
    if  k=='':
        return
    if  Flag==4:
        k       =   k.split('<div class="content"')#话题应使用新的ReadAnswer
    else:
        k       =   k.split('<div class="zm-item"')#话题应使用新的ReadAnswer
    Dict    =   {}
    for t   in  range(1,len(k)):# 为0则何如
        Dict    =   ReadAnswer(ReDict,html_parser,Dict,k[t].replace('\r',"").replace('\n',"").encode("utf-8"),Flag)#使用的是单行模式，所以要去掉\r\n避免匹配失败
        if  Dict['UpdateTime']!='1970-01-01':
            AnswerDictList.append(Dict)
            AnswerList.append(Dict['Questionhref'])
    print   u'第{}页答案抓取成功'.format(Page+1)
    if  RequestDict[Page][1]==False:#答案列表储存于RequesDict中
        RequestDict[Page][0]=AnswerList
        RequestDict[Page][1]=True
    return  

def Login(cursor=None,UserID='mengqingxue2014@qq.com',UserPassword='131724qingxue'):
    qc_1    =   ''#初始化
    print   u'开始验证网页能否打开，验证完毕后将开始登陆流程，请稍等。。。'
    header  =   {
'Accept'    :   '*/*'                                                                                 
,'Accept-Encoding'   :'gzip,deflate,sdch'
,'Accept-Language'    :'zh,zh-CN;q=0.8,en-GB;q=0.6,en;q=0.4'
,'Connection'    :'keep-alive'
,'Host'    :'www.zhihu.com'
,'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
,'DNT':'1'
,'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'
,'X-Requested-With':'XMLHttpRequest'
}
    try :
        ZhihuFrontPage=urllib2.urlopen(u"http://www.zhihu.com")#这里也可能出错#初次打开zhihu.com,获取xsrf信息
    except  urllib2.HTTPError   as e    :
        print   u'服务器错误'
        print   u'错误内容',str(e).decode("utf-8")
        print   u'转为使用旧有PostHeader'
        return  OldPostHeader(cursor=cursor)
    except  urllib2.URLError    as e    :
        print   u'网络错误'
        print   u'错误内容',str(e).decode("utf-8")
        print   u'话说网络链接正常不？'
        print   u'转为使用旧有PostHeader'
        return  OldPostHeader(cursor=cursor)
    try :
        xsrf    =   '_xsrf=' + re.search(r'(?<=name="_xsrf" value=")[^"]*(?="/>)',ZhihuFrontPage.read()).group(0)
        print   xsrf
    except  AttributeError:
        ErrorReturn(u'xsrf读取失败，程序出现致命故障，无法继续运行。\n错误信息：知乎的登陆验证方式可能已更改，无法在返回的cookie中正则匹配到xsrf，请知乎@姚泽源更新脚本')
    except  KeyError:
        print   u' 知乎没有设置xsrf'
    header['Cookie']    =   xsrf+';l_c=1'
    header['Origin']    =   'http://www.zhihu.com'#妈蛋知乎改登陆方式了这个坑坑了我整整两天！！！   
    header['Referer']   =   'http://www.zhihu.com/'                                                

    print   u'网页验证完毕，开始登陆流程'
   
    UserID,UserPassword =   InputUserNameandPassword()
    MaxTryTime  =   0#最多重复三次，三次后自动切换为使用旧有cookie进行登录
    try:
        while   MaxTryTime<10:
            LoginData   =   urllib.quote('{0}&email={1}&password={2}&rememberme=y'.format(xsrf,UserID,UserPassword),safe='=&')
            
            request =   urllib2.Request(url='http://www.zhihu.com/login',data=LoginData,headers=header)
            try :
                buf         =   urllib2.urlopen(request)
            except  urllib2.HTTPError   as e    :
                print   u'服务器错误'
                print   u'错误内容',e
                print   u'话说网络链接正常不？'
                print   u'转为使用旧有Header'
                return  OldPostHeader(cursor=cursor)
            except  urllib2.URLError    as e    :
                print   u'网络错误'
                print   u'错误内容',e
                print   u'话说网络链接正常不？'
                print   u'转为使用旧有PostHeader'
                return  OldPostHeader(cursor=cursor)
            if  qc_1    ==  '':
                try :#如果是初次打开网页的话，登陆成功之后会一并返回qc_1与qc_0,都有用
                    qc_1    =   re.search(r'(q_c1=[^;]*)',buf.info()['set-cookie']).group(0)
                except  AttributeError:
                    ErrorReturn(u'qc_1读取失败，程序出现致命故障，无法继续运行。\n错误信息：知乎登陆流程可能已更改，无法在返回的cookie中正则匹配到qc_1，请知乎@姚泽源更新脚本')         
                    qc_1    =   ''
            try:
                qc_0    =   re.search(r'(q_c0=[^;]*)',buf.info()['set-cookie']).group(0)
            except  AttributeError:
                qc_0    =   ''

            header['Cookie']        =  qc_1 +';'  +xsrf+'; l_c=1'+';'+qc_0
            buf_read    = buf.read()#为什么只能读取一次？？？#info可以读取多次
            PostInfo    =   json.loads(buf_read)
            if  PostInfo['errcode']==269:#提示输入验证码#验证码错误是270#登陆成功不返回任何信息，所以会报错，测试一下#也可能是该用户尚未注册
                print   u'抱歉，错误代码269\n知乎返回的错误信息如下:\n-----------------begin---------------------'
                PrintDict(PostInfo['msg'])
                print   '------------------end----------------------'
                ErrorReturn(u'表示无法处理这样的错误\n如果是需要输入验证码的话请用网页登陆一次知乎之后再来吧~（注：私人账号在网页上成功登陆一次之后就不会再出现验证码了）')
            else    :
                if  PostInfo['errcode']==270:
                    try     :
                        print   PostInfo['msg']['captcha'].encode('gbk')#win下要编码成gbk，
                        print   u'验证码错误？什么情况。。。'
                        ErrorReturn(u'好了现在需要输入验证码了。。。命令行界面表示显示图片不能。。。\n请用网页登陆一次知乎之后再来吧~（注：私人账号在网页上成功登陆一次之后就不会再出现验证码了）')
                    except  KeyError:
                        print   u'用户名或密码不正确，请重新输入用户名与密码\n附注:知乎返回的错误信息见下'
                        PrintDict(PostInfo['msg'])
                        UserID,UserPassword =   InputUserNameandPassword()
                        print   u'再次尝试登陆。。。'
                        MaxTryTime  +=1
                else    :
                    if  MaxTryTime>=3:
                        print   '三次尝试失败，使用已有cookie进行登录'
                        return  OldPostHeader(cursor=cursor)
                    print   u'未知错误，尝试重新登陆，请重新输入用户名与密码\nPS:知乎返回的错误信息:'
                    PrintDict(PostInfo['msg'])
                    UserID,UserPassword =   InputUserNameandPassword()
                    print   u'再次尝试登陆。。。'
                    MaxTryTime  +=1
    except  KeyError:
        print   u'登陆成功！'
        print   u'登陆账号:',UserID
        
        NewHeader   =   (str(datetime.date.fromtimestamp(time.time()).strftime('%Y-%m-%d')),header['Cookie'])#Time和datetime模块需要导入        
        
        rowcount    =   cursor.execute('select count(Pickle)  from VarPickle where Var="PostHeader"').fetchone()[0]
        if  rowcount==0:
            cursor.execute("insert  into VarPickle  (Var,Pickle) values ('PostHeader',?) ",(pickle.dumps(NewHeader),))
        else:
            cursor.execute("update VarPickle set Pickle=? where Var='PostHeader'",(pickle.dumps(NewHeader),))
        return  header
        #提取qc_0,储存之
def OldPostHeader(cursor=None):#可以加一个网络更新cookie的功能
    header  =   {
'Accept'    :   '*/*'                                                                                 
,'Accept-Encoding'   :'gzip,deflate,sdch'
,'Accept-Language'    :'zh,zh-CN;q=0.8,en-GB;q=0.6,en;q=0.4'
,'Connection'    :'keep-alive'
,'Host'    :'www.zhihu.com'
,'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'
}
    
    #print   u'请输入'#少年不要秀技术，这个你真没有。。。
    #    List    =   pickle.loads(t[0])
    #    CookieDict[str(No)] =   List[1]
    #    print   str(No)+':\t\t'+List[0]
    rowcount    =   cursor.execute('select count(Pickle)  from VarPickle where Var="PostHeader"').fetchone()[0]    
    if  rowcount==0:
        List    =   ('2014-04-26','q_c1=d55d91ee99a1484ea45c523d43ad3cc4|1396527477000|1396527477000;_xsrf=304b4ee7168e40b7aefeab4f006935e4;c_c=42bed592cd2011e3a1495254291c3363;q_c0="OTE4NGNlMDI4YWIwODRiMjU2NWZiODliYWU0M2U5Yjd8Z2NXRG1COUxKWm83YjNRRA==|1398502422|30a12ee827e3431fdb2145234bc3b77d071c88fa";')




    else:
        List    =   pickle.loads(cursor.execute("select PostHeader   from VarPickle  where Var='PostHeader'").fetchone()[0])
    recordtime  =   datetime.datetime.strptime(List[0],'%Y-%m-%d').date()
    today       =   datetime.date.today()
    diff        =   30- (today - recordtime).days
    if  diff    >   0:
        print   u'转为使用'+List[0]+u'的登陆记录进行登陆，可能无法读取私人收藏夹。距离该记录过期还有'+str(diff)+u'天，过期后程序将无法继续运行，成功使用账号密码登陆可将记录刷新'
        header['Cookie']    =   List[1]
    else    :
        ErrorReturn(u'账号密码登录&登陆记录已过期\n程序继续无法运行\n请重新运行程序，尝试使用账号密码进行登录。\n倘若一直无法登陆的话请上知乎私信@姚泽源反馈bug,不胜感激')
    return header
def InputUserNameandPassword():
    print   u'请输入您的登陆用户名(知乎注册邮箱)，回车确认'    
    print   u'示例:\n用户名:mengqingxue2014@qq.com\n密码：131724qingxue\nPS:别用这个示例账号。。。登不上。。。囧'
    print   u'请输入用户名,回车确认'
    LoopFlag    =   True
    while   LoopFlag:
        UserID  =   raw_input()
        try :
            re.search(r'\w+@[\w\.]{3,}',UserID).group(0)
        except  AttributeError:
            print   u'话说，输入的账号不规范啊'
            print   u'账号规范：1.必须是正确格式的邮箱\n2.邮箱用户名只能由数字、字母和下划线_构成\n3.@后面必须要有.而且长度至少为3位'
            print   u'范例：mengqingxue2014@qq.com\n5719asd@sina.cn'
            print   u'请重新输入账号，回车确认'
        else:
            LoopFlag    =   False
    print   u'OK,请输入密码，回车确认'
    LoopFlag    =   True
    while   LoopFlag:
        UserPassword  =   raw_input()
        try :
            re.search(r'\w{8,}',UserPassword).group(0)
        except  AttributeError:
            print   u'话说，输入的密码不规范啊'
            print   u'密码规范：1.只能由数字和字母构成2.至少8位'
            print   u'范例：caoyanyanyounaocanfen27149,qing2xue3nv3shen2ni2hao3a0'
            print   u'请重新输入密码，回车确认'
        else:
            LoopFlag    =   False
    print   u'Ok，开始发送登陆请求'
    return  UserID,UserPassword
    
    
    
    
def returnConnCursor():
    if  os.path.isfile('./ZhihuDateBase.db'):
        conn    =   sqlite3.connect("./ZhihuDateBase.db")
        conn.text_factory = str
        cursor  =   conn.cursor()
    else:
        conn    =   sqlite3.connect("./ZhihuDateBase.db")
        conn.text_factory = str
        cursor  =   conn.cursor()
        cursor.execute("create table VarPickle (Var varchar(255),Pickle varchar(50000),primary key (Var))")
        cursor.execute("create table AnswerInfoTable    ( ID              varchar(255) not Null , Sign            varchar(9000) not Null , AgreeCount      int(11)      not Null ,  QuestionID      varchar(20) not Null , AnswerID        varchar(20) not Null , UpdateTime      date         not Null , CommitCount     int(11)      not Null , QuestionTitle   varchar(1000)not Null , Questionhref    varchar(255) not Null , UserName        varchar(255) not Null , primary key(Questionhref))")#没有数据库就新建一个
        cursor.execute("create  table AnswerContentTable    (AnswerContent   longtext     not Null ,  Questionhref    varchar(255) not Null , primary key(Questionhref))")#没有数据库就新建一个
        cursor.execute("create  table   CollectionIndex (CollectionID   int not Null,Questionhref   varchar(255)    not Null, primary key(CollectionID,Questionhref))")#负责永久保存收藏夹链接，防止丢收藏
        conn.commit()
    return  conn,cursor
def CatchFrontInfo(ContentText='',Flag=0):
    if  ContentText=='':
        return# 应该raise个错误出去
    print   u'开始读取答案首页信息。。。'
    InfoDict={}
    if  Flag    ==0:
        return  InfoDict
    if  Flag    ==1:#1,ID;2,Collect;3,RoundTable;4,Topic
        ID_Name_Sign                =   re.search(r'(?<=<div class="title-section ellipsis">).*?(?=<div class="body clearfix">)',ContentText).group(0)


        InfoDict['ID']              =   re.search(r'(?<=href="/people/)[^"]*',ID_Name_Sign).group(0)            
        try:
            InfoDict['Sign']            =   re.search(r'(?<=<span class="bio" title=").*?(?=">)',ID_Name_Sign).group(0)            
        except  AttributeError:
             InfoDict['Sign']           =   ''
        InfoDict['Name']            =   re.search(r'(?<=">).*?(?=</a>)',ID_Name_Sign).group(0)
        ##################################
        Ask_Answer_Pst_CoE          =   re.findall(r'(?<=<span class="num">).*?(?=</span></a>)',ContentText)
        InfoDict['Ask']             =   Ask_Answer_Pst_CoE[0]
        InfoDict['Answer']          =   Ask_Answer_Pst_CoE[1]
        InfoDict['Post']            =   Ask_Answer_Pst_CoE[2]
        InfoDict['Collect']         =   Ask_Answer_Pst_CoE[3]
        InfoDict['Edit']            =   Ask_Answer_Pst_CoE[4]
        ##################################
        
        InfoDict['Agree']           =   re.search(r'(?<=<span class="zm-profile-header-user-agree"><span class="zm-profile-header-icon"></span><strong>).*?(?=</strong>)',ContentText).group(0)
        InfoDict['Thanks']          =   re.search(r'(?<=<span class="zm-profile-header-user-thanks"><span class="zm-profile-header-icon"></span><strong>).*?(?=</strong>)',ContentText).group(0)
        ##################################
        Followee_er                 =   re.findall(r'(?<=</span><br /><strong>).*?(?=</strong><label>)',ContentText)
        InfoDict['Followee']        =   Followee_er[0]
        InfoDict['Follower']        =   Followee_er[1]
        ##################################
        
        InfoDict['Watched']         =   re.search(r'(?<=[^>]{1}<strong>).*?(?=</strong>)',ContentText).group(0)
    if  Flag==2:#收藏夹
        InfoDict['Title']           =   re.search(r'(?<=<h2 class="zm-item-title zm-editable-content" id="zh-fav-head-title">).*?(?=</h2>)',ContentText).group(0)           
        InfoDict['Description']     =   re.search(r'(?<=<div class="zm-editable-content" id="zh-fav-head-description">).*?(?=</div>)',ContentText).group(0)              
        AuthorInfoStr               =   re.search('(?<=<h2 class="zm-list-content-title">).*?(?=</div>)',ContentText).group(0)
        InfoDict['AuthorName']      =   re.search(r'(?<=">).*?(?=</a></h2>)',AuthorInfoStr).group(0)                
        InfoDict['AuthorID']        =   re.search(r'(?<=<a href="/people/)[^"]*(?=">)',AuthorInfoStr).group(0)              
        try :
            InfoDict['AuthorSign']  =   re.search(r'(?<=<div class="zg-gray-normal">).*',AuthorInfoStr).group(0)
        except  AttributeError:
            InfoDict['AuthorSign']  =   ''    
        InfoDict['FollowerCount']   =   re.search(r'(?<=<div class="zg-gray-normal"><a href="/collection/\d{8}/followers">)\d*?(?=</a>)',ContentText).group(0)                   
    if  Flag==3:#圆桌               
        Title_LogoAddress           =   re.search(r'(?<=<h1 class="title">).*?(?=</h1>)',ContentText).group(0)

        InfoDict['Title']           =   re.search(r'(?<=<strong>).*(?=</strong>)',Title_LogoAddress).group(0)
        InfoDict['Adress']          =   re.search(r'(?<=<a href=")[^"]*',Title_LogoAddress).group(0) #/roundtable/copyright2014
        InfoDict['LogoAddress']     =   re.search(r'(?<=<img src=").*(?=" alt=")',Title_LogoAddress).group(0)                 
        InfoDict['Description']     =   re.search(r'(?<=<div class="description">).*?(?=</div>)',ContentText).group(0)                 
    if  Flag==4:#Topic
        InfoDict['Title']           =   re.search(r'(?<=<title>).*?(?=</title>)',ContentText).group(0)[:-12]           
        
        InfoDict['Adress']          =   re.search(r'(?<=http://www.zhihu.com).*?(?=">)',ContentText).group(0)#/topic/19793502
        Buf                         =   re.search(r'(?<=<img alt).*?(?=<)',ContentText).group(0)
        InfoDict['LogoAddress']     =   re.search(r'(?<=src=").*?(?=" class="zm-avatar-editor-preview">)',Buf).group(0)                 
        try :
            InfoDict['Description']     =   re.search(r'(?<=<div class="zm-editable-content" data-editable-maxlength="130" >).*?(?=</div>)',ContentText).group(0)                #正常模式
        except  AttributeError:
            InfoDict['Description']     =   re.search(r'(?<=<div class="zm-editable-content" data-editable-maxlength="130" data-disabled="1">).*?(?=</div>)',ContentText).group(0)                #话题描述不可编辑 

    print   u'首页信息读取成功'
    return  InfoDict

def CreateWorkListDict(PostHeader,TargetFlag,Target):#输入http头、目标代码，目标名，返回首页信息字典与待抓取Request字典
    if  TargetFlag==1:
        url =   'http://www.zhihu.com/people/'+Target+'/answers?page='          
    else:
        if  TargetFlag==2:
            url =   'http://www.zhihu.com/collection/'+Target+'?page='
        else:
            if  TargetFlag==3:#特殊处理
                #url =   'http://www.zhihu.com/roundtable/'+Target+'/answers'
                #InfoDict    =   CatchFrontInfo(k,TargetFlag)
                #算了不做知乎圆桌了，麻烦
                return
            else:
                if  TargetFlag==4:
                    url =   'http://www.zhihu.com/topic/'+Target+'/top-answers?page='#话题功能尚未测试
                else:
                    ErrorReturn(u'输入内容有误，创建待读取列表失败，在输入中提取到的内容为：\n{}\n,错误代码:{}\n'.format(Target,TargetFlag))
    Request =   urllib2.Request(headers=PostHeader,url=url)
    k       =  ''
    Times    =   0
    while   k==''   and Times<10:
        print   u'正在打开答案首页',url
        k   =   OpenUrl(Request)
        if  k=='':
            print   u'第{}/10次尝试打开答案首页失败，1秒后再次打开'.format(Times+1)
            time.sleep(1)
        Times+=1
    if  k   ==  '':
        ErrorReturn(u'打开答案首页失败，请检查网络连接\n打开失败的网址为'+url)
    k   =   k.replace('\n','').replace('\r','')
    InfoDict    =   CatchFrontInfo(k,TargetFlag)
    InfoDict['TargetID']=Target#用于记录收藏夹ID、圆桌名、话题ID
    MaxPage     =   FetchMaxAnswerPageNum(k)
    print   MaxPage
    RequestDict =   {}
    for No  in  range(MaxPage):#从0开始，不要干从1开始这种反直觉的事
        RequestDict[No]    =   [urllib2.Request(url=url+str(No+1),headers=PostHeader),False]
    return  InfoDict,RequestDict

def returnIndexList(cursor=None,Target='',Flag=0,RequestDict={}):
    print   u'读取答案成功，正在生成答案索引'
    Index   =   []
    if  Flag==1:
        for t   in  cursor.execute('select Questionhref  from    AnswerInfoTable where ID=? order   by  AgreeCount  desc',(Target,)):
            Index.append(t[0])
    else:
        if  Flag==2:
            for t   in  cursor.execute('select CollectionIndex.Questionhref  from    CollectionIndex,AnswerInfoTable    where CollectionIndex.CollectionID=?    and CollectionIndex.Questionhref=AnswerInfoTable.Questionhref   order   by  AnswerInfoTable.AgreeCount  desc',(Target,)):
                Index.append(t[0])
        else:
            for t   in  RequestDict:
                try:
                    RequestDict[t][1].get_full_url()
                except  AttributeError:
                    for i   in   RequestDict[t][0]:
                        Index.append(i)
    print   u'答案索引生成完毕，共有{}条答案链接'.format(len(Index))
    return  Index
            
                                                                                                                              


def ZhihuHelp():
    CheckUpdate()
    conn,cursor =   returnConnCursor()
    PostHeader  =   OldPostHeader(cursor)#Login(cursor)
    if  os.path.exists(u'./知乎答案集锦')==False:
        os.makedirs(u'./知乎答案集锦')
    try:
        ReadList    =   open("./ReadList.txt","r")
    except  IOError as e:
        print   e
        ErrorReturn(u'貌似程序所在的目录里好像没有ReadList.txt这个文件，手工新建一个吧')
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
    for TargetUrl in    ReadList:
        print   u'开始识别目标网址'
        TargetFlag,Target   =   ChooseTarget(TargetUrl.replace('\n','').replace('\r',''))
        if  TargetFlag==0:
            print   u'识别目标网址失败，原网址:',TargetUrl,u'识别结果：',Target
            print   u'点按回车继续'
            raw_input()
            continue
        try :
            InfoDict,RequestDict=   CreateWorkListDict(PostHeader=PostHeader,TargetFlag=TargetFlag,Target=Target)
        except  IOError as e:
            print   e
            print   u'抱歉，该网页无法打开，请检查网络链接\nPS:话说那个链接是私人收藏夹么？下载私人收藏夹需要用自己的帐号登陆知乎助手才行。点按回车继续读取下一项内容'
            raw_input()
            continue
        ErrorTextDict       =   {}
        print   u'开始抓取答案'
        ThreadWorker(cursor=cursor,ErrorTextDict=ErrorTextDict,MaxThread=MaxThread,RequestDict=RequestDict,Flag=TargetFlag)
        PrintDict(ErrorTextDict)
        if  TargetFlag==2:
            SaveCollectionIndexIntoDB(RequestDict=RequestDict,CollectionID=Target,cursor=cursor)
        conn.commit()
        IndexList   =   returnIndexList(cursor=cursor,Target=Target,Flag=TargetFlag,RequestDict=RequestDict)
        WriteHtmlFile(cursor=cursor,IndexList=IndexList,InfoDict=InfoDict,TargetFlag=TargetFlag)
    print   '所有链接抓取完毕，久等了~'
ZhihuHelp()
