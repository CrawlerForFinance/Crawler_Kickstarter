#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei, Wang Yuqi, Xiao Yongbo, Feng Letong"

import urllib, urllib2, cookielib, threading
import sys, string, time, os, re, json, Queue
import csv, argparse, unicodecsv
# import csv, argparse
from bs4 import BeautifulSoup
import socket
from tools_kickstarter import *
import logging

#global constant
DEBUG = False
SORT_TYPE = 'end_date'
#SORT_TYPE = 'most_funded'

#for crawl
urlHost = u'https://www.kickstarter.com'
urlStart = u'http://www.my089.com/Loan/default.aspx'
urlNav = u'https://www.kickstarter.com/discover?ref=nav'
#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'Accept':'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Host':'www.kickstarter.com', 'X-Requested-With':'XMLHttpRequest'}

#titles = ([u"link",u"dataDate",u"dataClock",u"Category",u"Title",u"Updates", u"Backers",u"Comments", u"PAdd",u"Video",u"DesLength",u'DesPics', u'DescriptionContent', u"RiskLength", u'RiskContent', u"FAQQ",u"FAQA",u"货币单位",u"Bkrs",u"PlgAmt",u"Goal",u"DaysToGo",u"BgnDate",u"EndDate",u"SpanDays",u"CreatorNM",u"CAdd",u"FB",u"CreatorID",u"BioLength",u"LastLoginDate",u"JoinedDate",u"NBacked",u"NCreated",u"Art",u"Comics",u"Dance",u"Design",u"Fashion",u"Film&Video",u"Food",u"Games",u"Music",u"Photograph",u"Publishing",u"Technology",u"Theater"], ['link', u"dataDate",u"dataClock",u"Category",u"Title",u"CreatorID",u"BackerNM",u"BackerID",u"BackerLocation", u"NBP"], ['link', u"dataDate",u"dataClock", u'Category', u'Title', u'CreatorID', 'updateTitle', 'updateDate', 'likeNumber','updateContent'], ['link', u"dataDate",u"dataClock", u'Category', u'Title', u'CreatorID', u'commentator', u'commentatorID', u'commentDate', u'commentContent'], ['link', u"dataDate",u"dataClock", 'Category', 'Title', 'CreatorID', 'Amount', 'backersNumber', 'Description', 'DeliveryDate'], ['link', u"dataDate",u"dataClock", 'Category', 'Title', 'CreatorID', 'Question', 'Answer'])
titles = ([u"link",u"dataDate",u"Category",u"SubCategory",u"Title", u"Backers",u"Comments", u"PAdd_City", u"PAdd_State", u"Video",u"Video_Time", u"DesLength",u'DesPics', u'DescriptionContent', u"RiskLength", u'RiskContent', u"FAQQ",u"FAQA",u"货币单位", u"PlgAmt",u"Goal",u"DaysToGo", u"EndDate",u"SpanDays",u"CreatorNM",u"CAdd_City", u"CAdd_State", u"FBState",u"FBNm",u"NFBFriends",u"NWebsites",u"CreatorID",u"CreaterVerified",u"BioLength",u"LastLoginDate",u"JoinedDate",u"NBacked",u"NCreated",u"Art",u"Comics",u"Crafts",u"Dance",u"Design",u"Fashion",u"Film&Video",u"Food",u"Games",u"Journalism",u"Music",u"Photograph",u"Publishing",u"Technology",u"Theater"], [u'link', u"dataDate", u'Category', u'Title', u'CreatorID', u'Creatoror', u'updateTitle', u'updateDate', u'likeNumber',u'CommentNumber',u'updateContent'], ['link', u"dataDate", u'Category', u'Title', u'CreatorID', u'CreatorName', u'commentator', u'commentatorID', u'commentDate', u'commentContent'], ['link', u"dataDate", 'Category', 'Title', 'CreatorID', u'Creatoror','rewardID','Unit', 'Amount', 'backersNumber', 'Description', 'DeliveryDate', 'shipto', 'leftPart', 'leftWhole'], ['link', u"dataDate", 'Category', 'Title', 'CreatorID',u'Creatoror',  'Question', 'Answer'], ["UserID", u"UserName", u"link",u"dataDate",u"Category",u"SubCategory",u"Title", u"Location_City",u"Location_State", u"Goal", u"PlgAmt", u"Unit", u"isSuccessful", u"backers", u"BeginDate", u"EndDate",u"SpanDays"], ["UserID", u"UserName", u"link",u"dataDate",u"Category",u"SubCategory",u"Title", u"Location_City",u"Location_State", u"Goal", u"PlgAmt", u"Unit", u"isSuccessful", u"backers", u"BeginDate", u"EndDate",u"SpanDays"])

orderCount = 0
allCount = 0
categoryIdList = [1, 3, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 26]
categoryNameList = ['Art','Comics','Dance','Design','Fashion','Food','Film&Video','Games','Journalism','Music','Photography','Technology','Theater', 'Publishing','Crafts']
sheetName = ['projects', 'updates', 'comments', 'rewards', 'FAQs', 'userBackProjects', 'userCreateProjects']
newlyend_title = [u"link",u"dataDate",u"Category",u"SubCategory",u"Title",u"PAdd_City",u"PAdd_State",u"Goal",u"Unit",u"Successful",u"Backers",u"PlgAmt",u"BeginDate",u"EndDate",u"SpanDays",u"CreatorName",u"CAdd_City",u"CAdd_State", u"FBState",u"FBNm",u"NFBFriends",u"NWebsites",u"CreatorID",u"CreaterVerified",u"BioLength",u"LastLoginDate",u"JoinedDate",u"NBacked",u"NCreated",u"Art",u"Comics",u"Crafts",u"Dance",u"Design",u"Fashion",u"Film&Video",u"Food",u"Games",u"Journalism",u"Music",u"Photograph",u"Publishing",u"Technology",u"Theater"]

#logging
logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.DEBUG)  
#logging.debug('this is a message')  
# add active project number dictionary
ActiveDict = {}

#----------------------------------------------
def createWriters(filedirectory, prefix=""):
    writers = [] #csv writer list
    startTime = str(time.strftime('%Y%m%d', time.localtime(time.time())))
    for i in range(1, len(titles)-1):
        name_sheet = filedirectory+sheetName[i-1]+'_'+prefix+'_'+startTime+'.csv'
        #flag_newfile = True
        if os.path.isfile(name_sheet):
            flag_newfile = False
        file_sheet = open(name_sheet, 'wb')
        file_sheet.write('\xEF\xBB\xBF') #防止windows下excel打开显示乱码
        
        writer = unicodecsv.writer(file_sheet)
        writers.append(writer)
        #if flag_newfile:
        writer.writerow(titles[i-1])
    return writers
#----------------------------------------------
class getDataThread(threading.Thread):
    global writers, categoryName
    def __init__(self, tId, urlQueue):
        threading.Thread.__init__(self)
        self.tId = tId
        self.q = urlQueue
    def run(self):
        while not exitFlag:
            queueLock.acquire()
            url = self.q.get()
            queueLock.release()
            print("thread "+ str(self.tId) + ": "+url)
            analyzeData(url, writers, categoryName)
        #end while
#end class getDataThread
#----------------------------------------------
class getUrlQueueThread(threading.Thread):
    def __init__(self, tId, urlQueue, categoryId):
        threading.Thread.__init__(self)
        self.tId = tId
        self.q = urlQueue
        self.categoryId = categoryId
    def run(self):
        global pageCount
        # get only active projects, need to be filterd
        global urlNum
        categoryFinish = False
        categoryName = categoryNameList[categoryIdList.index(self.categoryId)]
        aliveNum = int(ActiveDict[categoryName])
        if urlNum >= aliveNum:
            categoryFinish = True
        #end #
        while True:
            # get only active projects, need to be filterd
            if categoryFinish:
                print 'no alive' + str(urlNum)
                break
            # end
            pageLock.acquire()
            pageCount += 1
            if DEBUG:
                if(pageCount == 2):
                    break
            if pageCount%20 == 0:
                print('  get page '+str(pageCount)+'...')
            #pageUrl = urlCategory+'page='+str(pageCount)+'&category_id='+str(self.categoryId)+'&woe_id=0&sort='+SORT_TYPE
            #pageUrl = urlCategory+'page='+str(pageCount)+ '&sort='+SORT_TYPE
            if "&" in categoryName:
                pageUrl = urlStartPage + "film%20&%20video" + "?page=" + str(pageCount) + "&sort=" + SORT_TYPE
            else:
                pageUrl = urlStartPage+categoryName + '?page='+str(pageCount)+ '&sort='+SORT_TYPE
            # print 'pageUrl:', pageUrl
            print pageUrl
            pageLock.release()
            m = readFromUrl(pageUrl, headers = headers)#需要特定的headers
            try:
                #response = urllib2.urlopen(req)
                scriptData = json.loads(m)
                projList = scriptData['projects']
                if(len(projList) == 0):
                    break
                queueLock.acquire()
                for proj in projList:
                    url = proj['urls']['web']['project']
                    print url
                    urlQueue.put(url)
                    # get only active projects, need to be filterd
                    urlNum += 1
                    if urlNum >= aliveNum:
                        categoryFinish = True
                        if urlNum != aliveNum:
                            urlQueue.get(url)
                        break
                    #end #
                queueLock.release()
            except socket.error as e:
                print('[ERROR] Socket error: '+str(e.errno))
                continue
            # except Exception, e:
            #     # logging.exception(e)
            #     continue
            
        #end while
#end class getUrlQueueThread(threading.Thread):            
#----------------------------------------------
def getUrlQueue(categoryNo):
    global urlQueue, categoryName
    global urlNum
    urlNum = 0
    categoryId = categoryIdList[categoryNo-1]
    categoryName = categoryNameList[categoryNo-1]
    print("Start: get projects list in category "+categoryName+"...")
    startTime = time.clock()
    threads = []
    '''
    for i in xrange(threadCount):
        thread = getUrlQueueThread(i, urlQueue, categoryId)
        threads.append(thread)
    '''    
    for i in xrange(1):
        thread = getUrlQueueThread(i, urlQueue, categoryId)
        threads.append(thread)
    
    print urlQueue.qsize()
    print "over"
    # return
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    endTime = time.clock()
    print("Finish: get projects list in category "+categoryName)
    print("Projects count: "+str(urlQueue.qsize()))
    print(u'time: '+str(endTime-startTime)+'s\n')
    #end while
#end getUrlQueue()
#----------------------------------------------
def getCategory(filedirectory, categoryNo, startPage, endPage):
    starttime = time.clock()
    #lastpage = begin_page #记录抓取的最后一个有效页面
    
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    
    categoryId = categoryIdList[categoryNo-1]
    categoryName = categoryNameList[categoryNo-1]
    subFolder = filedirectory+categoryName+'/'
    createFolder(subFolder)
    writers = createWriters(subFolder, categoryName+'_'+str(startPage)+'-'+str(endPage))
    
    i = categoryId
    pageCount = startPage-1
    while True:
        pageCount += 1
        if pageCount > endPage:
            break
        print('************************************************************')
        print('* CATEGORY ID='+str(i)+';  '+'CATEGORY NAME='+categoryName+'; PAGE='+str(pageCount)+' ')
        print('************************************************************')
        req = urllib2.Request(urlCategory+'page='+str(pageCount)+'&category_id='+str(i)+'&woe_id=0&sort='+SORT_TYPE, headers=headers)
        try:
            response = urllib2.urlopen(req)
            m = response.read()
            #print m
            scriptData = json.loads(m)
            projList = scriptData['projects']
            if(len(projList) == 0):
                break
            for proj in projList:
                url = proj['urls']['web']['project']
                #print url
                analyzeData(url, writers)
            response.close()
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print('[ERROR]'+str(e.code)+' '+str(e.reason))
            print(str(e.reason))
            print('url = ')
        except socket.error as e:
            print('[ERROR] Socket error: '+str(e.errno))
            continue
        #endwhile
    #end for
    
    endtime = time.clock()
    print(u'[execute time]:'+str(endtime-starttime)+'s') #50:47.9s
    return
#----------------------------------------------
def getAllCategory(filedirectory):
    starttime = time.clock()
    #lastpage = begin_page #记录抓取的最后一个有效页面
    
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    
    writers = createWriters(filedirectory)
    
    for i in categoryIdList:
        pageCount = 0
        while True:
            pageCount += 1
            print('CATEGORY ID: '+str(i)+';  PAGE: '+str(pageCount))
            req = urllib2.Request(urlCategory+'page='+str(pageCount)+'&category_id='+str(i)+'&woe_id=0&sort='+SORT_TYPE, headers=headers)
            try:
                response = urllib2.urlopen(req)
                m = response.read()
                scriptData = json.loads(m)
                projList = scriptData['projects']
                if(len(projList) == 0):
                    break
                for proj in projList:
                    url = proj['urls']['web']['project']
                    print url
                    analyzeData(url, writers)
                response.close()
            except (urllib2.URLError) as e:
                if hasattr(e, 'code'):
                    print('[ERROR]'+str(e.code)+' '+str(e.reason))
                print(str(e.reason))
                print('url = ')
            except socket.error as e:
                print('[ERROR] Socket error: '+str(e.errno))
                continue
        #endwhile
    #end for
    
    endtime = time.clock()
    print(u'[execute time]:'+str(endtime-starttime)+'s') #50:47.9s
    return
#end def getData()
#---------------------------
def getInput():
    global categoryNo, startPage, endPage, getUsers, getAllData, monthNo, categoryStart, categoryEnd, monthStart, monthEnd
    getUsers = False
    getAllData = False
    length = len(categoryIdList)
#     while True:
# # getAllData
#         try:
#             raw_getAllData = raw_input(u'Get All Data (y) or set a certain category and a certain month (n)?:\n')
#             if (raw_getAllData == 'y' or raw_getAllData == 'Y'):
#                 getAllData = True
#             elif (raw_getAllData == 'n' or raw_getAllData == 'N'):
#                 getAllData = False
#             else:
#                 print('Please input y or n!')
#                 continue
#             break
#         except:
#             if(raw_categoryNo == ''):
#                 categoryNo = 1
#                 break
#             print('Not a number. Please input again!')
#             continue
    while True:
        try:
            raw_categoryNoSection = raw_input(u'Input category section, ("1,5" means "[1, 5)"):\n')
            categoryNoSectionStr = raw_categoryNoSection.split(",")
            categoryStart = int(categoryNoSectionStr[0])
            categoryEnd = int(categoryNoSectionStr[1])
            if (categoryStart > categoryEnd):
                print('first number should be smaller then the last number!')
                continue
            break
        except:
            if(raw_categoryNoSection == '' or raw_categoryNoSection.find(',') == -1):
                break
            print('Not a section. Please input again!')
            continue
    while True:
        try:
            raw_monthSection = raw_input('Input month section, ("10,2" means "[10,2)")\n')
            monthSectionStr = raw_monthSection.split(",")
            monthStart = int(monthSectionStr[0])
            monthEnd = int(monthSectionStr[1])
            break
        except:
            if(raw_monthSection == '' or raw_monthSection.find(',') == -1):
                break
            print('Not a section. Please input again!')
            continue
    # while not getAllData:
    #     try:
    #         raw_categoryNo = raw_input(u'Input category number(1-'+str(length)+', default=1):\n')
    #         categoryNo = int(raw_categoryNo)
    #         if categoryNo < 1 or categoryNo > length:
    #             print('Category number illegal! Please input again!')
    #             continue
    #         break
    #     except:
    #         if(raw_categoryNo == ''):
    #             categoryNo = 1
    #             break
    #         print('Not a number. Please input again!')
    #         continue
    # while not getAllData:
    #     try:
    #         raw_categoryGetUsers = raw_input('Input nth Month(6,7,8,9,10,11,12,1):\n')
    #         if ((int(raw_categoryGetUsers) == 1) or (int(raw_categoryGetUsers) >= 6 and int(raw_categoryGetUsers) <= 12)):
    #             monthNo = int(raw_categoryGetUsers)
    #         else:
    #             print('Please input right month')
    #             continue
    #         break
    #     except:
    #         if(raw_categoryGetUsers == ''):
    #             # getUsers = False
    #             break
    #         print('1Command input illegal! Please type with 1 or 0!')
    #         continue
    '''
    while True:
        try:
            raw_endPage = raw_input('Input end page(default=100000):\n')
            endPage = int(raw_endPage)
            if endPage < 1:
                print('End page illegal! Please input again!')
                continue
            break
        except:
            if(raw_endPage == ''):
                endPage = 100000
                break
            print('Not a number. Please input again!')
            continue
            '''
#----------------------------
def CreateNewlyEndPrjUsersCreateWriter(categoryName):
    startTime = str(time.strftime('%Y%m', time.localtime(time.time())))
    name_sheet = filedirectory + categoryName +'/' + categoryName + "_users_create" + startTime + ".csv"
    # if os.path.isfile(name_sheet):
    #     flag_newfile = False
    file_sheet = open(name_sheet, 'wb')
    file_sheet.write('\xEF\xBB\xBF')
    writer = unicodecsv.writer(file_sheet)
    writer.writerow(titles[6])
    return writer
#----------------------------
def CreateNewlyEndPrjUsersBackWriter(categoryName):
    startTime = str(time.strftime('%Y%m', time.localtime(time.time())))
    name_sheet = filedirectory + categoryName +'/' + categoryName + "_users_back_" + startTime + ".csv"
    # if os.path.isfile(name_sheet):
    #     flag_newfile = False
    file_sheet = open(name_sheet, 'wb')
    file_sheet.write('\xEF\xBB\xBF')
    writer = unicodecsv.writer(file_sheet)
    writer.writerow(titles[5])
    return writer
#----------------------------
def CreateNewlyEndWriter(categoryName):

    startTime = str(time.strftime('%Y%m', time.localtime(time.time())))
    name_sheet = filedirectory+categoryName+'/'+"NewlyEndProject_"+categoryName + "_" + startTime + ".csv"
    if not os.path.isfile(name_sheet):
        file_sheet = open(name_sheet, 'ab')
        file_sheet.write('\xEF\xBB\xBF')
        writer = unicodecsv.writer(file_sheet)
        writer.writerow(newlyend_title)
    else:
        file_sheet = open(name_sheet, 'ab')
        file_sheet.write('\xEF\xBB\xBF')
        writer = unicodecsv.writer(file_sheet)
    return writer
    # analyzeNewlyEndData(writer, )
#-----------------------------
def getActiveNum():
    activeUrl = urlNav
    startTime = str(time.strftime('%Y%m%d', time.localtime(time.time())))
    name_sheet = filedirectory+"AliveNumber"+'_'+startTime+'.csv'
    flag_newfile = True
    if os.path.isfile(name_sheet):
        flag_newfile = False
    file_sheet = open(name_sheet, 'ab')
    file_sheet.write('\xEF\xBB\xBF') #防止windows下excel打开显示乱码
        
    writer = unicodecsv.writer(file_sheet)
    if flag_newfile:
        writer.writerow(['category', 'AliveNumber'])
    try:
        m = readFromUrl(activeUrl, headers = headers)#需要特定的headers
        soup = BeautifulSoup(m)
        active = soup.findAll('div',class_='h4 bold')
        category = soup.findAll('div', class_='h3')
        for cat, act in zip(category, active):
            ActiveDict[cat.string.strip().replace(' ', '')] = act.string.split(' ')[0]
            buffer_livenum = [cat.string.strip().replace(' ', ''), act.string.split(' ')[0]]
            writer.writerow(buffer_livenum)
        print ActiveDict
    except socket.error as e:
        print('[ERROR] Socket error: '+str(e.errno))
#----------------------------
#global variable
categoryName = ''
categoryNo = 1
startPage = 1
endPage = 100000
urlQueue = Queue.Queue()
writers = []
exitFlag = 0
pageCount = 0 #翻页计数器
threadCount = 8 #并发线程数
urlNum = 0
#----------------------------
#main
if __name__=='__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
    sys.setrecursionlimit(1000000)#设置递归调用深度
    
    #参数解析器
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-c', '--categoryno', action='store', dest='categoryNo', help='Set category NO.(1-15)')
    parser.add_argument('-t', '--threadcount', action='store', dest='threadCount', help='Set thread number', default=8)

    args = parser.parse_args()
    if(args.categoryNo == None):
        getInput()
    else:
        categoryNo = int(args.categoryNo)
    threadCount = int(args.threadCount)
    
    filedirectory = getConfig()
    print 'get active num'
    
    # getActiveNum()
    
    if login():
        print '------------INPUT INFORMATION---------------------'
        print '- CategoryNumber='+str(categoryNo)
        print '- StartPage='+str(startPage)
        print '- EndPage='+str(endPage)
        print '- ThreadCount='+str(threadCount)
        print '------------INPUT INFORMATION---------------------'
        
        # queueLock = threading.Lock()
        # pageLock = threading.Lock()
        # pageCount = 0
        # getUrlQueue(categoryNo)
        
        # if getAllData:
        for index in range(categoryStart, categoryEnd):
            categoryName = categoryNameList[index-1]
            subFolder = filedirectory+categoryName+'/'
            createFolder(subFolder)
        # else:
        #     categoryId = categoryIdList[categoryNo-1]
        #     categoryName = categoryNameList[categoryNo-1]
        #     subFolder = filedirectory+categoryName+'/'
        #     createFolder(subFolder)
        # writers = createWriters(subFolder, categoryName)

        # startTime = time.clock()
        # threads = []

        
        # for i in xrange(threadCount):
        #     thread = getDataThread(i+1, urlQueue)
        #     threads.append(thread)
            
        # for t in threads:
        #     t.start()
        
        # while not urlQueue.empty():
        #     pass
        
        # exitFlag = 1
        
        # for t in threads:
        #     t.join()
        # print("Exiting Main Thread")
        # endTime = time.clock()
        # print(u'[Total execute time]:'+str(endTime-startTime)+'s')
        #10 thread: 637s: 400 projects
        


        #writers = createWriters(filedirectory)
        #analyzeData(urlTest, writers)
        
        #getAllCategory(filedirectory)
        #getCategory(filedirectory, categoryNo, startPage, endPage)
        
        # get all end project url creator info
        if (getUsers):
            endPrjfileList = []
            # 返回一个列表，其中包含在目录条目的名称(google翻译)
            allFiles = os.listdir(filedirectory)
            # 先添加目录级别
            for f in allFiles:
                if(os.path.isfile(filedirectory + '/' + f) and (f.startswith('NewlyEnd'))):
                    endPrjfileList.append(filedirectory + '/' + f)
            newly_end_users_create_writer = CreateNewlyEndPrjUsersCreateWriter()
            newly_end_users_back_writer = CreateNewlyEndPrjUsersBackWriter()
            for f in endPrjfileList:
                try:
                    urlFile = open(f)
                    categoryName = f.split('_')[1].split('_')[0].lower()
                    if urlFile:
                        print 'getFile'
                        urllist = urlFile.readlines()
                        print len(urllist)
                        unniurllist = list(set(urllist))
                        print len(unniurllist)
                        for url in urllist:
                            analyzeNewlyEndUsersData(url.strip(), newly_end_users_create_writer, newly_end_users_back_writer, categoryName)
                            print 'heiheihei'
                except Exception, e:
                    print e
                    raise e

        
        import datetime
        for index in range(categoryStart, categoryEnd):
            categoryName = categoryNameList[index-1]
            #for cat in categoryNameList:
            # if datetime.date.today().day == 1:
            # newly_end_writer = CreateNewlyEndWriter(categoryName)
            newly_end_users_create_writer = CreateNewlyEndPrjUsersCreateWriter(categoryName)
            newly_end_users_back_writer = CreateNewlyEndPrjUsersBackWriter(categoryName)
            yesterday = datetime.date.today()-datetime.timedelta(days=1)
            lastMonth = yesterday.strftime("%Y%m")
            #name_sheet = filedirectory+"NewlyEnd_"+categoryName+"_"+lastMonth+".txt"
            if monthEnd == 1:
                for indexMonth in range(monthStart, 13):
                    if indexMonth < 10:
                        monthNoStr = "20150" + str(indexMonth)
                    else:
                        monthNoStr = "2015" + str(indexMonth)
                    name_sheet = filedirectory+"/NewlyEnd_" + categoryName+"_"+ monthNoStr + ".txt"
                    print 'file name ' + name_sheet
                    try:
                        urlFile = open(name_sheet)
                        if urlFile:
                            print 'getFile'
                            urllist = urlFile.readlines()
                            print len(urllist)
                            unniurllist = list(set(urllist))
                            print len(unniurllist)
                            for url in unniurllist:
                                # analyzeNewlyEndData(url.strip(), newly_end_writer, categoryName)
                                analyzeNewlyEndUsersData(url.strip(), newly_end_users_create_writer, newly_end_users_back_writer, categoryName)
                                print 'heiheihei'
                    except Exception, e:
                        print e
                        raise e
            elif monthEnd == 2:
                for indexMonth in range(monthStart, 13):
                    if indexMonth < 10:
                        monthNoStr = "20150" + str(indexMonth)
                    else:
                        monthNoStr = "2015" + str(indexMonth)
                    name_sheet = filedirectory+"/NewlyEnd_" + categoryName+"_"+ monthNoStr + ".txt"
                    print 'file name ' + name_sheet
                    try:
                        urlFile = open(name_sheet)
                        if urlFile:
                            print 'getFile'
                            urllist = urlFile.readlines()
                            print len(urllist)
                            unniurllist = list(set(urllist))
                            print len(unniurllist)
                            for url in unniurllist:
                                # analyzeNewlyEndData(url.strip(), newly_end_writer, categoryName)
                                analyzeNewlyEndUsersData(url.strip(), newly_end_users_create_writer, newly_end_users_back_writer, categoryName)
                                print 'heiheihei'
                    except Exception, e:
                        print e
                        raise e
                name_sheet = filedirectory+"/NewlyEnd_" + categoryName+"_201601.txt"
                print 'file name ' + name_sheet
                try:
                    urlFile = open(name_sheet)
                    if urlFile:
                        print 'getFile'
                        urllist = urlFile.readlines()
                        print len(urllist)
                        unniurllist = list(set(urllist))
                        print len(unniurllist)
                        for url in unniurllist:
                            # analyzeNewlyEndData(url.strip(), newly_end_writer, categoryName)
                            analyzeNewlyEndUsersData(url.strip(), newly_end_users_create_writer, newly_end_users_back_writer, categoryName)
                            print 'heiheihei'
                except Exception, e:
                    print e
                    raise e
            else:
                for indexMonth in range(monthStart, monthEnd):
                    if indexMonth < 10:
                        monthNoStr = "20150" + str(indexMonth)
                    else:
                        monthNoStr = "2015" + str(indexMonth)
                    name_sheet = filedirectory+"/NewlyEnd_" + categoryName+"_"+ monthNoStr + ".txt"
                    print 'file name ' + name_sheet
                    try:
                        urlFile = open(name_sheet)
                        if urlFile:
                            print 'getFile'
                            urllist = urlFile.readlines()
                            print len(urllist)
                            unniurllist = list(set(urllist))
                            print len(unniurllist)
                            for url in unniurllist:
                                # analyzeNewlyEndData(url.strip(), newly_end_writer, categoryName)
                                analyzeNewlyEndUsersData(url.strip(), newly_end_users_create_writer, newly_end_users_back_writer, categoryName)
                                print 'heiheihei'
                    except Exception, e:
                        print e
                        raise e
