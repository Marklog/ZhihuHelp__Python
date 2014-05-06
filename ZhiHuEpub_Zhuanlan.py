# -*- coding: utf-8 -*-
import  os
import  json

import  sys#修改默认编码
reload( sys )
sys.setdefaultencoding('utf-8')

import  sqlite3#使用数据库管理数据
import  urllib2
import  zipfile
import  pickle
import  threading#使用线程下载图片，直接默认20线程#知乎图片是用CDN分发的，不必担心
import  time#睡眠
import re
def DownloadPicWithThread(ImgList=[]):#添加图片池功能#当图片下载完成时在ImgList中删除之
    Time=0
    MaxThread   =   50
    while   Time<10:
        MaxPage     =   len(ImgList)
        Buf_ImgList =   []
        Time+=1
        ThreadList  =   []
        for t   in  ImgList:#因为已下载过的文件不会重新下载，所以直接重复执行十遍，不必检测错误#待下载的文件可能会突破万这一量计，所以还是需要一些优化
            ThreadList.append(threading.Thread(target=DownloadImg,args=(t,Buf_ImgList,)))
        for Page in  range(MaxPage):
            if  threading.activeCount()-1 <   MaxThread:#实际上是总线程数
                ThreadList[Page].start()#有种走钢丝的感觉。。。
            else    :
                print   u'第({}/10)轮下载图片，线程库中还有{}条线程等待运行'.format(Time,MaxPage-Page)
                time.sleep(1)

        Thread_LiveFlag =   True
        while   Thread_LiveFlag:#等待线程执行完毕
            Thread_LiveFlag =   False
            ThreadRunning   =   0
            for t   in  ThreadList:
                if  t.isAlive():
                    Thread_LiveFlag=True
                    ThreadRunning+=1
            print   u"第({}/10)轮下载图片，目前还有{}条线程正在运行,等待所有线程执行完毕".format(Time,ThreadRunning)
            if  ThreadRunning>0:
                time.sleep(1)
        ImgList =   Buf_ImgList
def returnCursor():
    if  os.path.isfile('./ZhihuDateBase.db'):
        conn    =   sqlite3.connect("./ZhihuDateBase.db")
        conn.text_factory = str
        cursor  =   conn.cursor()
        return  cursor
    else:
        print   u'抱歉，没有找到数据库，请先运行知乎助手'
        return  None
def Mkdir(DirName=u''):
    if  DirName=='':
        return
    else:
        try :                        
            os.mkdir(DirName)
        except  OSError:
            pass#已存在
    return
def CreateMimeType():
    f   =   open('mimetype','w')
    f.write('application/epub+zip')
    f.close()
def CreateContainer_XML():
    f   =   open('META-INF/container.xml','w')      
    f.write('''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf"
     media-type="application/oebps-package+xml" />
  </rootfiles>
</container>''')
    f.close()
def returnTagContent(text='',tagname=''):
    TagBeginStr     =   re.search(r"<"+tagname+r'.*?>',text).group(0)#如果没有这个标签会报AttributeError
    BeginPos        =   text.index(TagBeginStr)+len(TagBeginStr)
    rowEndPos       =   text.index('</'+tagname+'>')
    newText         =   text[BeginPos:rowEndPos]#初始字符位置
    #开始检测是否有重复标签
    completeTime    =   len(re.findall(r"<"+tagname+r'.*?>',newText)) 
    while   completeTime:
        bufPos  =   rowEndPos
        for i   in  range(completeTime):
            bufPos  =   text.index('</'+tagname+'>',bufPos+1)
        newText         =   text[rowEndPos:bufPos]
        completeTime    =   len(re.findall(r"<"+tagname+r'.*?>',newText)) 
        rowEndPos       =   bufPos
    return  text[BeginPos:rowEndPos]
def removeTag(text='',tagname=[]):
    text    =   text.replace('</'+tagname+'>','')
    text    =   re.sub(r"<"+tagname+r'.*?>','',text)
    return  text
def removeAttibute(text='',AttList=[]):
    for Att in  AttList:
        for t   in  re.findall(Att+'[^\s^>]*',text):
            text    =   text.replace(t,'')
    return text
def closeimg(text='',ImgList=[]):
    for t   in  re.findall(r'<img.*?>',text):
        text    =   text.replace(t,fixPic(removeAttibute(t,['data-rawwidth','data-original']).replace("data-rawheight",'height')[:-1]+u'  alt="知乎图片"/>',ImgList))
    return text
def fixPic(t='',ImgList=[]):
    for k   in  re.findall(r'src="http://p\d\.zhimg\.com[/\w]{7}[\w]{32}_[\d\w\.]{5}',t)  :
        t   =   t.replace(k,'src="../images/'+k[-38:])
        ImgList.append(k[5:])
    for k   in  re.findall('(?<=src=")http://p\d\.zhimg\.com[/\w]{7}[_\w]{11}\.jpg',t):
        t   =   t.replace(k,'src="../images/'+k[-15:])
        ImgList.append(k[5:])
    return  t
def DownloadImg(imghref='',Buf_ImgList=[]):#下载失败时应报错或重试
    try :
        CheckName   =   u'../知乎图片池/'
        try :
            MetaName    =     re.search(r'[^/]*\.jpg',imghref).group(0)
        except  AttributeError:
            print       u'程序出现错误，未能成功提取图片链接'
            print       u'目标网址'+imghref
            print       u'已陷入死循环，请关闭程序'
            raise       IOError('over')
            MetaName    =     ''
        imgfilename =   './OEBPS/images/'+MetaName   
        if  not os.path.isfile(CheckName+MetaName):
            img =   urllib2.urlopen(url=imghref,timeout=10)
            k   =   img.read()
            if  len(k)==0:
                raise   IOError('hello world')
                return 0
            imgfile     =   open(imgfilename,"wb")
            imgpoolfile =   open(CheckName+MetaName,"wb")
            imgfile.write(k)
            imgpoolfile.write(k)
            imgfile.close()
            imgpoolfile.close()
        else    :
            if  not os.path.isfile(imgfilename):
                imgfile     =   open(imgfilename,"wb")
                imgpoolfile =   open(CheckName+MetaName,"rb")
                imgfile.write(imgpoolfile.read())
                imgfile.close()
                imgpoolfile.close()
    except  :
        Buf_ImgList.append(imghref)
    return 0
def CreateOPF(OPFInfoDict={},Mainfest='',Spine=''):#生成文件函数均假定当前目录为电子书根目录
    f   =   open('./OEBPS/content.opf','w')
    XML =   u'''<?xml version='1.0' encoding='utf-8'?>
               <package unique-identifier="%(AuthorAddress)s" version="2.0">
               <metadata xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/"  >
               <dc:title>%(BookTitle)s</dc:title>
               <dc:identifier id="%(AuthorAddress)s">%(AuthorAddress)s</dc:identifier>
               <dc:language>zh-CN</dc:language>
               <dc:creator>%(AuthorName)s</dc:creator>
               <dc:description>%(Description)s</dc:description>
               <dc:rights>本电子书由ZhihuHelper制作生成，仅供个人阅读学习，严禁用于商业用途</dc:rights>
               <meta name="cover" content="cover-image" />
               </metadata>
               <!-- Content Documents -->
               <manifest>
               <item id="main-css" href="stylesheet.css" media-type="text/css"/> <!--均与OPF处同一文件夹内，所以不用写绝对路径-->
               <item id="ncx"   href="toc.ncx"      media-type="application/x-dtbncx+xml"/>
               <item id="cover" href="html/cover.html"   media-type="application/xhtml+xml"/>
               <item id="title" href="html/title.html"   media-type="application/xhtml+xml"/>'''%OPFInfoDict +   Mainfest+                '''
               <item id="cover-image" href="images/cover.jpg" media-type="image/jpg"/>
               <!-- Need to Choose Image Type -->
               </manifest>
               <spine toc="ncx" >
               <itemref idref="cover" linear="yes"/>
               <itemref idref="title" linear="yes"/>
               
               '''+Spine+'''
               </spine>
               <guide>
               <reference type="cover"  title="封面" href="html/cover.html"   />
               <reference type="toc"    title="目录" href="html/title.html" />
               </guide>
               </package>
               '''
    f.write(XML)
    f.close()
def CreateNCX(NCXInfoDict={},Ncx=''):
    f   =   open('./OEBPS/toc.ncx','w')
    XML =   '''<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" 
                 "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="%(AuthorAddress)s"/>
    <meta name="dtb:depth" content="-1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>%(BookTitle)s</text>
  </docTitle>'''%NCXInfoDict+Ncx+'''
</ncx>
    '''
    f.write(XML)
    f.close()
def PrintDict(Dict={}):
    for t   in Dict:
        print t,Dict[t]
ImgList =   []

def ZipToEpub(EpubName='a.epub'):
    epub    =   zipfile.ZipFile(os.path.abspath('../../'+os.curdir+u'/知乎答案集锦/'+EpubName),'w')
    epub.write('mimetype', compress_type=zipfile.ZIP_STORED)
    DictNo  =   0
    for p in os.listdir('.'):
        print   'p=',p,'EpubName=',EpubName
        if  p   ==  EpubName:
            print   'yuanwenjian'
            continue
        if  not os.path.isfile(p):
            for f in os.listdir(p):
                if  not os.path.isfile(os.path.join(p, f)):
                        for k in os.listdir(os.path.join(p, f)):
                            DictNo+=1
                            if  DictNo%10==0:
                                print   u'将文件添加至电子书内k=',os.path.join(p,f,k)#否则用户会被弹幕刷屏至死#宁可刷屏至死，也不能显得慢。。。改成10了，不谢
                            epub.write(os.path.join(p,f,k), compress_type=zipfile.ZIP_STORED)
                else:
                    print   u'将文件添加至电子书内_f=',os.path.join(p, f)
                    epub.write(os.path.join(p,f), compress_type=zipfile.ZIP_STORED)
        else    :
            print   u'将文件添加至电子书内_p=',p
            epub.write(p,compress_type=zipfile.ZIP_STORED)
    epub.close()
##########################################################新开始
def ChooseTarget(url=''):#选择
    try :
        return  re.search(r'(?<=zhuanlan.zhihu.com/)[^/]*',url).group(0)
    except  AttributeError:
        print   u'未能匹配到专栏名'
        return  ''
######新修改
def DealAnswerDict(JsonDict=[],ImgList=[],JsonDictList=[]):#必须是符合规定的Dict，规定附后
    for k in JsonDict:
        t                    =   k
        Dict={}
        Dict['ColumnID']     =   t["column"]["slug"]#专栏ID
        Dict['ColumnName']   =   t["column"]["name"]#专栏名
        Dict['ArticleLink']  =   t['links']['comments']
        Dict['TitleImage']   =   t["titleImage"]
        Dict['ArticleTitle'] =   t["title"]
        Dict['AuthorName']   =   t['author']['name']
        Dict['AuthorIDLink'] =   t['author']['profileUrl']#全地址
        Dict['PublishedTime']=   t["publishedTime"]
        Dict['Commit']       =    t["commentsCount"]
        Dict['Agree']        =   t["likesCount"]
        Dict['Content']      =   closeimg(text=t["content"].replace('<hr>','<hr />').replace('<br>','<br />'),ImgList=ImgList)#需要进一步处理#testTag
        Buf_AuthorID         =   t['author']['avatar']['id']
        Buf_AuthorTemplete   =   t['author']['avatar']['template']
        Dict['AuthorIDLogo'] =   Buf_AuthorTemplete.format(id=Buf_AuthorID,size='s')     
        
        
        
        HtmlStr =u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
            <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="provider" content="www.zhihu.com"/>
        <meta name="builder" content="ZhihuHelpv1.4"/>
        <meta name="right" content="该文档由ZhihuHelp_v1.4生成。ZhihuHelp为姚泽源为知友提供的知乎答案收集工具，仅供个人交流与学习使用。在未获得知乎原答案作者的商业授权前，不得用于任何商业用途。"/>
        <link rel="stylesheet" type="text/css" href="../stylesheet.css"/>
        <title>%(ArticleTitle)s</title>
        </head>
        <body>
        <div    align="center"   class="TitleImage">
        <img    src="%(TitleImage)s"    alt=""/>
        </div>
        <div    align="center"   class="Title">
        <h3 align="left">%(ArticleTitle)s</h3>
        </div>
        <div    class="answer-body">
            <div    class="answer-content">
                <img align="right" src="%(AuthorIDLogo)s" alt=""/><a style="color:black;font:blod" href=%(AuthorIDLink)s>%(AuthorName)s</a>
            <br /><br />
                %(Content)s    
            </div>
            <div    class='zm-item-comment-el'>
                <div  class='update' >
                    赞同：%(Agree)s
                </div>
                <p  class='comment'   align   ="right">           
                    评论：%(Commit)s 
                </p>
            </div>
        </div>
        <div>
        <h2> </h2>
        </div>
        </body></html>
        """%Dict
        Dict['HtmlStr'] =   HtmlStr
        JsonDictList.append(Dict)#按发布顺序排序

def MakeInfoDict(ColumnInfoDict={}):
    Dict    =   {}
    Dict['BookTitle']       =   u'知乎专栏之'+ColumnInfoDict['Name']
    Dict['AuthorAddress']   =   ColumnInfoDict['Href']
    Dict['AuthorName']      =   ColumnInfoDict['Name']
    Dict['Description']     =   ColumnInfoDict['Description']
    return Dict   

def OpenUrl(url=""):
    Time    =   0
    t       =   ''   
    while   Time<10:
        try :
            t   =   urllib2.urlopen(url=url).read()
            if  t!='':
                return t
        except  IOError :
            pass
        Time+=1
        print   u'第({}/10)次尝试打开页面'.format(Time)
    print   u'10次尝试全部失败，目标网址={} ，请检查网络链接或网址是否正确'.format(url)
    
    
    return  t
def ErrorReturn(ErrorInfo=""):#返回错误信息并退出，错误信息要用unicode编码
    print   ErrorInfo
    print   u"点按回车继续"
    raw_input()                                                                       

def ZhihuHelp_Epub():
    FReadList   =   open('ReadList.txt','r')
    Mkdir(u"电子书制作临时资源库")
    Mkdir(u'电子书制作临时资源库/知乎图片池')
    for url in  FReadList:
        ImgList     =   []#清空ImgList
        InfoDict    =   {}
        JsonDict    =   []#初始化
        print   u'待抓取链接:',url
        url =   url.replace("\r",'').replace("\n",'')
        Target      =   ChooseTarget(url)
        if  Target!='':
            TargetUrl   =   'http://zhuanlan.zhihu.com/api/columns/'+Target+'/posts?limit=20000&offset=0'
            InfoTargetUrl   =   'http://zhuanlan.zhihu.com/api/columns/'+Target
        else:
            continue
        #专栏信息
        print   u'开始获取专栏信息'
        t           =   OpenUrl(url=InfoTargetUrl)
        if  t=='':
            ErrorReturn(u'获取专栏信息失败')
            continue
        InfoDict    =   json.loads(t)
        ColumnInfoDict  =   {}
        ColumnInfoDict["FollowersCount"]    =   InfoDict["followersCount"]
        ColumnInfoDict["Description"]       =   InfoDict["description"]
        ColumnInfoDict["Name"]              =   InfoDict["name"]
        ColumnInfoDict["Href"]              =   Target
        InfoDict    =   MakeInfoDict(ColumnInfoDict)
        
        #专栏全文
        print   u'开始获取专栏内容'
        t           =   OpenUrl(url=TargetUrl)
        if  t=="":
            ErrorReturn(u'专栏内容没有抓到')
            continue
        JsonDict    =   json.loads(t)
        JsonDictList=   []
        DealAnswerDict(JsonDict=JsonDict,ImgList=ImgList,JsonDictList=JsonDictList)       
       
       
        os.chdir(u'电子书制作临时资源库')
        BufDir              =   u'%(BookTitle)s(%(AuthorAddress)s)_电子书制作临时文件夹'%InfoDict
        Mkdir(BufDir)
        os.chdir(BufDir)
        f   =   open('mimetype','w')
        f.write(u'application/epub+zip')
        f.close()
        Mkdir('META-INF')
        Mkdir('OEBPS')
        os.chdir(u'./'+'OEBPS')
        Mkdir('html')
        Mkdir('images')
        os.chdir('..')
        print   u'文件目录创建完毕'
        #文件目录创建完毕
        
        #开始输出目录与文件
        print   u'答案处理完成，开始输出文件'
        TitleHtml   =   open("./OEBPS/html/title.html",'w')
        TitleHtml.write(u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
             <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
             <head>
         <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
         <meta name="provider" content="www.zhihu.com"/>
         <meta name="builder" content="ZhihuHelpv1.4"/>
         <meta name="right" content="该文档由ZhihuHelp_v1.4生成。ZhihuHelp为姚泽源为知友提供的知乎答案收集工具，仅供个人交流与学习使用。在未获得知乎原答案作者的商业授权前，不得用于任何商业用途。"/>
         <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
                     <title>目录</title>
                     </head>
                     <body>
                     <center><h1>目录</h1></center><hr/><br />\n''')
        No  =   1
        Ncx=   u'''<navMap><navPoint id="title" playOrder="1">
              <navLabel>
                <text>目录</text>
              </navLabel>
              <content src="html/title.html"/>
            </navPoint>''' 
        Mainfest=''
        Spine=''
        DictNo      =   0
        DictCountNo =   len(JsonDictList)
        for t   in  JsonDictList:
            DictNo      +=   1
            if  DictNo%10==0:
                print   u'正在输出第{}个文件，共{}个'.format(DictNo,DictCountNo)
            No+=1
            TitleStr    =   t['ArticleTitle']
            Ncx     +=u'<navPoint id="chapter{No}" playOrder="{No}"> <navLabel> <text>{title}</text> </navLabel> <content src="html/chapter{No}.html"/> </navPoint> \n'.format(title=TitleStr,No=No)
            Mainfest+=u'<item id="chapter{No}" href="html/chapter{No}.html" media-type="application/xhtml+xml"   />\n'.format(No=No)
            Spine   +=u'<itemref idref="chapter{No}" linear="yes"/>\n'.format(No=No)
        
            TitleHtml.write(u"""<p><a href="chapter{No}.html">{Title}</a></p><br />\n""".format(No=No,Title=TitleStr))
            f   =   open(u'./OEBPS/html/chapter{}.html'.format(No),'w')
            f.write(t['HtmlStr'])
            f.close()
        Ncx +="</navMap>"
        
        
        TitleHtml.write(u"""</body></html>\n""")
        TitleHtml.close()
        
        
        CreateOPF(InfoDict,Mainfest,Spine)
        CreateNCX(InfoDict,Ncx)
        f   =   open('./META-INF/container.xml','w')
        f.write('''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
          <rootfiles>
            <rootfile full-path="OEBPS/content.opf"
             media-type="application/oebps-package+xml" />
          </rootfiles>
        </container>''')#元文件
        f.close()
        #临时创建一个封面文件
        f=  open("OEBPS/html/cover.html","w")
        coverHtmlStr    =   '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
             <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
             <head>
         <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
         <meta name="provider" content="www.zhihu.com"/>
         <meta name="builder" content="ZhihuHelpv1.4"/>
         <meta name="right" content="该文档由ZhihuHelp_v1.4生成。ZhihuHelp为姚泽源为知友提供的知乎答案收集工具，仅供个人交流与学习使用。在未获得知乎原答案作者的商业授权前，不得用于任何商业用途。"/>
         <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
                     <title>%(BookTitle)s</title>
                     </head>
                     <body>
                     <center>
                     <img  class="cover" src="../images/cover.jpg"/>
                     <br />\n
        <h1>%(BookTitle)s</h1>
        <h2>%(AuthorName)s</h2></center>
        <center><a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/cn/">
        <img alt="知识共享许可协议" style="border-width:0" src="../images/88x31.png">
        </a>
        </center>
        <center>本作品采用<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/3.0/cn/">知识共享署名-非商业性使用-禁止演绎 3.0 中国大陆许可协议</a>进行许可。</center>
        </body>
        </html>
        '''%InfoDict
        f.write(coverHtmlStr)
        f.close()
        print   u'答案生成完毕，输出待下载图片链接，若图片下载时间过长可自行用迅雷下载并将下载完成的图片放在文件夹：/电子书制作临时资源库/XXX_电子书制作临时文件夹/OEBPS/images内，程序检测到图片已存在即不会再去下载,减少程序运行时间(咱这毕竟不是迅雷。。。囧)'
        #输出链接，反正最多就三四万个。。。
        f   =   open(u"../%(BookTitle)s待下载图片链接.txt"%InfoDict,'w')
        for t   in  ImgList:
            f.write(t+'\r\n')
        f.close()
        
        #复制CSS与cover两个文件到临时文件夹中
        #print os.path.abspath('../../'+os.curdir+'/电子书制作资源文件夹/cover.jpg')
        f   =   open(os.path.abspath('../../'+os.curdir+u'/电子书制作资源文件夹/cover.jpg'),'rb')#真凶残啊。。。
        k   =   open(u'OEBPS/images/cover.jpg','wb')
        k.write(f.read())
        k.close()
        f.close()
        f   =   open(os.path.abspath('../../'+os.curdir+u'/电子书制作资源文件夹/88x31.png'),'rb')#真凶残啊。。。 
        k   =   open(u'OEBPS/images/88x31.png','wb')  
        k.write(f.read())                           
        k.close()              
        f.close()       
        
        
        
        f   =   open(os.path.abspath('../../'+os.curdir+u'/电子书制作资源文件夹/stylesheet.css'),'r')
        k   =   open(u'OEBPS/stylesheet.css','w')
        k.write(f.read())
        k.close()
        f.close()
        DownloadPicWithThread(ImgList)
        ZipToEpub(InfoDict['BookTitle']+'.epub')
        os.chdir('..')
        os.chdir('..')#回到元目录
        print   u'%(BookTitle)s制作完成'%InfoDict
ZhihuHelp_Epub()
