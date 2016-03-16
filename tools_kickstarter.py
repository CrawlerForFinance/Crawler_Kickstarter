#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib
import sys, string, time, os, re, json
import csv
import unicodecsv
from bs4 import BeautifulSoup
import socket
from random import randint
import datetime
from dateutil.parser import parse
import pytz
import traceback
import re

# from analyze_newlyend_data import analyzeNewlyEndData
# from analyze_newlyend_user_data import analyzeNewlyEndUsersData
# from analyze_comments_data import analyzeCommentsData
# from analyze_backers_data import analyzeBackersData
# from analyze_creator import analyzeCreatorBackProjectsData, analyzeCreatorCreateProjectsData
# from analyze_faq_data import analyzeFaqData
# from analyze_reward_data import analyzeRewardData
# from analyze_update_data import analyzeUpdatesData

configfileName = 'config'
filedirectory = u'D:\\datas\\pythondatas\\kickstarter\\'
enable_proxy = True

#For login
urlHost = u'https://www.kickstarter.com'
urlLogin = u'https://www.kickstarter.com/user_sessions'
urlIndex = u'https://www.kickstarter.com/'
urlCategory = u'https://www.kickstarter.com/discover/advanced?'
urlStartPage = u'https://www.kickstarter.com/discover/categories/'

#for excel
username = u'victor1991@126.com'
password = u'wmf123456'
#'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
ipAddress = ['191.234.5.2', '178.98.246.45, 231.67.9.23']
host = 'www.kickstarter.com'
userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']
#headers=[{'User-Agent': userAgent[0], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}, {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'User-Agent': userAgent[1], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}, {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'User-Agent': userAgent[2], 'Host': 'www.kickstarter.com', 'X-Forwarded-For':ipAddress}]
HEADERS_NUMBER = 3

TRY_LOGIN_TIMES = 5 #尝试登录次数
CATEGORY_COUNT = 15

#--------------------------------------------------
#读取配置文件，返回目标文件夹地址
def getConfig():
    global filedirectory, username, password, threadCount
    try:
        configfile = open(os.getcwd()+'/'+configfileName, 'r')
        #line = configfile.readline()
        pattern = re.compile(u'\s*(\w+)\s*=\s*(\S+)\s*')
        for line in configfile:
            #print line
            m = pattern.match(line)
            if m:
                if m.group(1) == u'filedirectory':
                    filedirectory =  m.group(2)+'/'
                elif m.group(1) == u'username':
                    username = m.group(2)
                elif m.group(1) == u'password':
                    password = m.group(2)
                elif m.group(1) == u'threadCount':
                    threadCount = m.group(2)
                #print filedirectory
        configfile.close()
    except:
        configfile = open(os.getcwd()+'/'+configfileName, 'wb')
        configfile.write('filedirectory = '+filedirectory+'\n')
        configfile.write('username = '+username+'\n')
        configfile.write('password = '+password+'\n')
        configfile.write('threadCount = '+threadCount+'\n')
        configfile.close()
        print('Create new config file!')
    
    createFolder(filedirectory)
    
    print('[CONFIG]')
    print('filedirectory = '+filedirectory)
    print('username = '+username)
    print('password = '+password)
    return filedirectory
#end def getConfig()  
#--------------------------------------------------
#登录函数
def login():
    print('Logging in...')
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    #md5pwd = hashlib.md5(password).hexdigest();
    #print 'md5 password = '+md5pwd
    #md5pwd = '73f7d9af739c494a455418da7a2efcce'
    data = {'utf8':'%E2%9C%93', 'user_session[email]':username, 'user_session[password]':password, 'commit':'Log me in!', 'user_session[remember_me]':'0', 'user_session[remember_me]':'1'};
    postdata = urllib.urlencode(data)
    for i in range(TRY_LOGIN_TIMES):
        try:
            #print headers[randint(0, HEADERS_NUMBER-1)]
            req = urllib2.Request(urlLogin, postdata, getRandomHeaders())
            result = urllib2.urlopen(req)
            if urlIndex != result.geturl(): #通过返回url判断是否登录成功
                print result.geturl()
                print(u'[FAIL]Wrong USERNAME or PASSWORD. Please try again!')
                return False
            result.close()
    
            req2 = urllib2.Request(urlIndex, headers=getRandomHeaders())
            result2 = urllib2.urlopen(req2)
            #print result2.read()
            print("LOGIN SUCCESS!")
            return True #登录成功
        except:
            print(u'[FAIL]Login failed. Retrying...')
            #return False
    #end for
    print(u'[FAIL]login failed after retrying')
#end def login()
#--------------------------------------------------
#查看文件夹是否存在：若不存在，则创建
def createFolder(filedirectory):
    if os.path.isdir(filedirectory):
        pass
    else:
        os.makedirs(filedirectory) #可以创建多级目录
    return
#--------------------------------------------------
#从url读取response
def responseFromUrl(url, formdata = None, headers = None):
    response = None
    #here in kickstarter are all HTTPS
    '''
    proxy_handler = urllib2.ProxyHandler({"http": '186.238.51.149:8080'})
    if enable_proxy:
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
    '''
    if formdata != None:
        formdata = urllib.urlencode(formdata)
    if headers == None:
        headers = getRandomHeaders()
    loopCount = 0
    while True:
        loopCount += 1
        if loopCount > 5:
            print('\nFailed when trying responseFromUrl():')
            print('  URL = '+url+'\n')
            break
        try:
            req = urllib2.Request(url, formdata, headers)
            response = urllib2.urlopen(req)
            curUrl = response.geturl()
            break
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print('ERROR:'+str(e.code)+' '+str(e.reason))
                if(e.code == 429):
                    time.sleep(2)
                    continue
        except:
            print 'error: ' + url
            pass
        if(response == None):
            print('responseFromUrl get a None')
            time.sleep(1)
            login()
            continue
    #end while
    
    return response
#--------------------------------------------------
#生成一个随机的headers
def getRandomHeaders():
    ipNumber = len(ipAddress)
    agentNumber = len(userAgent)
    headers = {'User-Agent': userAgent[randint(0, agentNumber-1)], 'Host': host, 'X-Forwarded-For': ipAddress[randint(0, ipNumber-1)]}
    return headers    
#--------------------------------------------------
#从url读取页面内容
def readFromUrl(url, formdata = None, headers = None):
    response = responseFromUrl(url, formdata, headers)
    if response:
        m = response.read()
        response.close()
        return m
    else:
        return None
#end def readFromUrl
#--------------------------------------------------
def getTime(format = None):
    if format:
        strtime = str(time.strftime(format, time.localtime(time.time())))
    else:
        strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    return strtime
#--------------------------------------------------
def getWordNumber(str):
    list_word = str.split()
    return len(list_word)    
#--------------------------------------------------
def cleanString(str):
    str = str.replace('\r\n', ' ')
    str = str.replace('\n', ' ')
    return str.strip()
#--------------------------------------------------

#--------------------------------------------------
def recordNewlyEnd(category, url):
    startTime = str(time.strftime('%Y%m', time.localtime(time.time())))
    name_sheet = filedirectory+"NewlyEnd_"+ category + "_" +startTime+'.txt'
    writer = open(name_sheet, 'a')
    # file_sheet.write('\xEF\xBB\xBF') #防止windows下excel打开显示乱码
    #print name_sheet + "  " + url
    # writer = csv.writer(file_sheet)
    try:
        #urlsList = writer.readlines()
        buffer_newlyEnd = url
        writer.write(buffer_newlyEnd.strip() + "\n")
        writer.close()
    except socket.error as e:
        #print('[ERROR] Socket error: '+str(e.errno))
        writer.close()
#end recordNewlyEnd

def getBackProjectsData(url, creatorUserID, creatorUserName, writer, categoryName):
    webcontent = readFromUrl(url.split("?")[0]+"/description")
    print "$$$$$$"+url.split("?")[0]+"/description"
    #print webcontent
    soup = BeautifulSoup(webcontent)
    # buffer1 = []
    #******************************
    #页面上栏部分
    currentDate = getTime('%Y-%m-%d %H:%M:%S')
    
    category = subcategory = title = backers = location_City = location_State = isSuccessful = PlgAmt = ''
    Goal = ""
    beginDate = endData = PlgAmt = spanDays = Goal = backers = Unit = ""
    #decide whether  over

    tag_duration = soup.find('span', {'id':'project_duration_data'})
    #没有结束的和没有成功的时有这个标签的，成功的是没有这个标签的
    if tag_duration:
        print '1111111111111111112'
        #spanDays = re.match('(\d+).\d?', tag_duration['data-duration']).group(1)
        remaining = tag_duration['data-hours-remaining']
        isSuccessful = "0"
        # print "not successful"
        spanDays = tag_duration['data-duration']
        endData = tag_duration['data-end_time']
        beginDate = (parse(endData) - datetime.timedelta(days=float(spanDays))).strftime("%Y%m%d")
        tag_creator = soup.find('a', {'class':'remote_modal_dialog green-dark'})
        if tag_creator:
            creatorstr = tag_creator.text
            creatorUrl = url.split('?')[0] + "/creator_bio"
        tag_backersCount = soup.find('div', {'id':'backers_count'})
        if tag_backersCount:
            backers = tag_backersCount['data-backers-count']
        tag_PlgAmg = soup.find('div', {'id':'pledged'})
        if tag_PlgAmg:
            PlgAmt = re.search('\D+(\d+[,.]*\d*)?', tag_PlgAmg.find('data').string).group(1)
            PlgAmt = PlgAmt.replace(',', '')
        tag_Goal = soup.find('div',{'class':'num h1 bold nowrap'})
        if tag_Goal:
            Goal = tag_Goal['data-goal']
            Goal = Goal.replace(',', '')
            Unit = tag_Goal.find('data')['data-currency']
    else:
        print '22222222222222222'
        isSuccessful = "1"
        tag_creator = soup.find('a', {'class':'hero__link remote_modal_dialog js-update-text-color'})
        #print tag_creator
        if tag_creator:
            creatorstr = tag_creator.text
            creatorUrl = url.split('?')[0] + "/creator_bio"
        tag_Successful = soup.find('div', {'class':'NS_projects__spotlight_stats'})
        #print tag_Successful
        if tag_Successful:
            backersstr = tag_Successful.find('b').text
            backers = backersstr.split(' ')[0]
            PlgAmt = re.search('\D+(\d+[,.]*\d*)?',tag_Successful.find('span').text).group(1)
            PlgAmt = PlgAmt.replace(',', '')
        tag_Goal = soup.find('div',{'class':'col-right col-4 py2 border-left'})
        if tag_Goal:
            tag_GoalInner = tag_Goal.find('div',{'class':'h5'})
            if tag_GoalInner:
                tag_Unit = tag_GoalInner.find('span')
                #print tag_Unit['class'], type(tag_Unit['class'])
                Unit = tag_Unit['class'][1]
                Goal = re.search('\D+(\d+[,.]*\d*)?',tag_Unit.string.strip()).group(1)
                Goal = Goal.replace(',', '')
        tag_timePirod = soup.find('div',{'class':'NS_projects__funding_period'})
        #print tag_timePirod
        if tag_timePirod:
            tag_timePirod = tag_timePirod.find('p')
            DatesList = tag_timePirod.findAll('time')
            beginDate = DatesList[0]['datetime']
            endData = DatesList[1]['datetime']
            spanDays = (parse(endData) - parse(beginDate)).days
    # print "isSuccessful:" + str(isSuccessful)
    # print "spanDays:" + str(spanDays)
    # print "endData:" + endData
    # print "beginDate:" + beginDate
    # print "backers:" + str(backers)
    # print "plgAmt:" + PlgAmt
    # print "Goal:" + str(Goal)
    # print "Unit:" + str(Unit)
    category = categoryName
    tag_title = soup.find('meta', {'property':'og:title'})
    if tag_title:
        title = tag_title['content']
        title = title.replace(';', '.')
        # print "title:" + title
    tag_location = soup.find('meta', {'property':'twitter:text:location'})
    if tag_location:
        location = tag_location['content']
        # print "location:" + location
    tag_location = soup.find_all('a', {'class':'grey-dark mr3 nowrap'})[0]
    location_City = ''
    location_State = ''
    if tag_location:
        location_str = tag_location.text
        if ',' in location_str:
            location_City = location_str.split(",")[0].strip()
            location_State = location_str.split(",")[1].strip()
            print "location_City:",location_City, "  location_State",location_State 
    # print location_City + ", " + location_State
    tag_subcategory = soup.find_all('a', {'class':'grey-dark mr3 nowrap'})
    if tag_subcategory:
        for singleItem in tag_subcategory:
            ref = singleItem['href'].split('?ref=')
            if ref[1] == 'category':
                hrefspliter = ref[0].split('/')
                subcategory = hrefspliter[-1]
                subcategory = subcategory.replace('%20', ' ')

    urltrip = url.split('?')[0]
    attrs1 = [urltrip, currentDate, category, subcategory, title, location_City, location_State, Goal, PlgAmt, Unit, isSuccessful, backers]
    # print attrs1
    #******************************
    #页面右栏最下端
    attrs4 = [beginDate,endData, spanDays]
    # print attrs4
    #******************************
    #Creator
    creatorName = creatorAdd = ''
    FB_state = FB_name = FB_friends = 'NA'
    num_websites = ''
    
    #TODO: is there any difference?
    '''Get the remote modal'''
    creator_modal_url_split = url.split('?')
    creator_modal_url = creator_modal_url_split[0] + '/creator_bio'
    creator_content = readFromUrl(creator_modal_url)
    creatorAdd_City = location_City
    creatorAdd_State = location_State
    soup_creator = BeautifulSoup(creator_content)
    tag_creatorName = soup_creator.find('div',{'class':'table-cell full-width px2 border-box'})
    if tag_creatorName:
        creatorName = tag_creatorName.find('a').text
    tag_creatorFB = soup_creator.find('div', {'class':'facebook py1 border-bottom h5'})
    if tag_creatorFB:
        #FB_friends = re.match('(\s|\n)*(\d+).*', tag_creatorFB.find('span', class_='number').string).group(2)
        tag_FB_state = tag_creatorFB.find('span', {'class':'ss-icon ss-facebook facebook color-facebook margin-right'})
        if tag_FB_state:
            FB_state = 'attached'
            tag_FB_name = tag_creatorFB.find('a', {'class':'popup'})
            if tag_FB_name:
                FB_name = tag_FB_name.string
            tag_FB_friends = tag_creatorFB.find('span', {'class':'number h6 nowrap'})
            if tag_FB_friends:
                FB_friends_spliter = tag_FB_friends.string.split(' ')
                FB_friends = FB_friends_spliter[0]
    tag_website = soup_creator.find('div', {'class':'pt4 mobile-hide'})
    if tag_website:
        # review problem: find returns a list?
        list_websites = tag_website.find('a', {'rel':'nofollow'})
        num_websites = len(list_websites)
    attrs5 = [creatorName, creatorAdd_City, creatorAdd_State, FB_state, FB_name, str(FB_friends.strip()), str(num_websites)]
    # print attrs5
    #******************************
    #about creator
    creatorID = lastLoginDate = joinedDate = ''
    bioLength = NBacked = NCreated = '0'
    bioContent = readFromUrl(url+'/creator_bio.js')
    soup_bio = BeautifulSoup(bioContent)
    
    tag_lastLogin_div = soup_creator.find('div', {'class':'last-login py1 border-bottom h5'})
    if tag_lastLogin_div:
        tag_lastLogin = tag_lastLogin_div.find('time', {'class':'js-adjust-time'})
        if tag_lastLogin:
            lastLoginDate = re.match('(\d+-\d+-\d+)T.*', tag_lastLogin['datetime']).group(1)

    tag_creatorUrl = soup.find('meta', {'property':'kickstarter:creator'})
    attrs6 = []
    if tag_creatorUrl:
        creatorUrl = tag_creatorUrl['content']
        creatorID = re.match('https://www\.kickstarter\.com/profile/(\S+)', creatorUrl).group(1)
        creater_verified = ''

        tag_cv_span = soup_creator.find('span', {'class':'ss-icon ss-check green margin-right'})
        if tag_cv_span:
            creater_verified = 'yes'
        else:
            creater_verified = 'no'
        creatorContent = readFromUrl(creatorUrl)
        soup2 = BeautifulSoup(creatorContent)
        tag_joined = soup2.find('meta', {'property':'kickstarter:joined'})
        if tag_joined:
            joinedDate = re.match('(\d+-\d+-\d+) .*', tag_joined['content']).group(1)
        tag_bio = soup2.find('meta', {'property':'og:description'})
        if tag_bio:
            bioLength = getWordNumber(tag_bio['content'])
        tag_NBacked = soup2.find('a', {'id':'list_title'})
        if tag_NBacked:
            NBacked = re.search('\d+', tag_NBacked.get_text()).group(0)
            tag_NCreated = tag_NBacked.parent.find_next_sibling('li')
            if tag_NCreated:
                NCreated = re.search('\d+', tag_NCreated.get_text()).group(0)
        attrs6 = [str(creatorID), creater_verified, bioLength, lastLoginDate, joinedDate, str(NBacked), str(NCreated)]
        #print attrs6
        #to get number of projects of each category
        tag_circle = soup2.find('div', {'id':'small_circle'})
        if tag_circle:
            scriptPart = tag_circle.find_next('script').string
            scriptData = re.search('circle_data = (\[.*\]);', scriptPart).group(1)
            script = json.loads(scriptData)
            for item in script:
                #print item['projects_backed'],
                attrs6.append(item['projects_backed'])
        else:
            #for deleted user
            for i in range(CATEGORY_COUNT):
                attrs6.append('')
            #print '-'
        # print attrs6
    
    #******************************
    print 'attrs1'
    print attrs1
    print 'attrs4'
    print attrs4
    buffer1 = [creatorUserID, creatorUserName]
    buffer1.extend(attrs1)
    buffer1.extend(attrs4)
    # print 'ID: ' + buffer1[0]
    writer.writerow(buffer1)
#--------------------------------------------------
