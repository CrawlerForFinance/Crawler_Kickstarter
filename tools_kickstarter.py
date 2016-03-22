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

configfileName = 'config'
# filedirectory = u'D:\\datas\\pythondatas\\kickstarter\\'
filedirectory = u'/Users/shawn/Documents/project/kick/newversion/'
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
def analyzeNewlyEndData(url, writer, categoryName):
    global filedirectory
    webcontent = readFromUrl(url.split("?")[0]+"/description")
    print "$$$$$$"+url.split("?")[0]+"/description"
    category = subcategory = title = backers = location_City = location_State = isSuccessful = PlgAmt = ''
    Goal = ""
    beginDate = endDate = PlgAmt = spanDays = Goal = backers = Unit = ""
    #Creator
    creatorName = creatorAdd = ''
    FB_state = FB_name = FB_friends = 'NA'
    num_websites = ''
    #print webcontent
    soup = BeautifulSoup(webcontent)
    purged_tag = soup.find('div', {'id' : 'purged_project'})
    if not purged_tag:
        #******************************
        #页面上栏部分
        currentDate = getTime('%Y-%m-%d %H:%M:%S')
        #decide whether  over

        tag_time = soup.find('div', {'class':'NS_projects__funding_period'})
        #统一beginDate, endDate
        if tag_time:
            tag_time_begin = tag_time.find_all('time')[0]
            tag_time_end = tag_time.find_all('time')[1]
            if tag_time_begin and tag_time_end:
                beginDate = tag_time_begin['datetime']
                endDate = tag_time_end['datetime']
                spanDays = re.split('[()]', tag_time.find('p').text)[1]
                spanDays = spanDays.split(' ')[0]
                print "beginDate: " + beginDate
                print "endDate: " + endDate
                print "spanDays: " + spanDays

        tag_duration = soup.find('span', {'id':'project_duration_data'})
        #没有结束的和没有成功的时有这个标签的，成功的是没有这个标签的
        if tag_duration:
            #spanDays = re.match('(\d+).\d?', tag_duration['data-duration']).group(1)
            remaining = tag_duration['data-hours-remaining']
            isSuccessful = "0"
            # print "not successful"
            # spanDays = tag_duration['data-duration']
            # endData = tag_duration['data-end_time']
            # beginDate = (parse(endData) - datetime.timedelta(days=float(spanDays))).strftime("%Y%m%d")
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
                # beginDate = DatesList[0]['datetime']
                # endData = DatesList[1]['datetime']
                # spanDays = (parse(endData) - parse(beginDate)).days
        print "isSuccessful:" + str(isSuccessful)
        print "spanDays:" + str(spanDays)
        print "endDate:" + endDate
        print "beginDate:" + beginDate
        print "backers:" + str(backers)
        print "plgAmt:" + PlgAmt
        print "Goal:" + str(Goal)
        print "Unit:" + str(Unit)
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
        attrs1 = [urltrip, currentDate, category, subcategory, title, location_City, location_State, Goal, Unit, isSuccessful, backers, PlgAmt]
        # print attrs1
        #******************************
        #页面右栏最下端
        attrs4 = [beginDate,endDate, spanDays]
        # print attrs4
        #******************************
        
        
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
            if lastLoginDate == '':
                lastLoginDate = joinedDate
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
                    attrs6.append('0')
                #print '-'
            # print attrs6
        #******************************
        
        #******************************
        buffer1 = []
        buffer1.extend(attrs1)
        buffer1.extend(attrs4)
        buffer1.extend(attrs5)
        buffer1.extend(attrs6)
        writer.writerow(buffer1)
    else:
        print 'project has been purged'
#--------------------------------------------------
def analyzeData(url, writers, attr):
    global filedirectory
    webcontent = readFromUrl(url)
    #print webcontent
    soup = BeautifulSoup(webcontent)
    buffer1 = []
    #******************************
    #页面上栏部分
    currentDate = getTime('%Y-%m-%d %H:%M:%S')
    #currentDate = getTime('%Y-%m-%d')
    #currentClock = getTime('%H:%M:%S')

    category = subcategory = title = backers = comments = location_City = location_State = ''
    updatesContent = commentsContent = ''
    '''creator name
    creators = soup.find('meta', {'name' : 'title'})
    creatorstr = creators['content']
    creatorstrspliter = creatorstr.split("by")
    creator = creatorstrspliter[1].lstrip().rstrip()
    '''
    tag_category = soup.find('li', class_='category')
    if tag_category:
        category = tag_category.a.get_text()
        category = category.strip()
        #print category
    category = attr
    tag_title = soup.find('meta', {'property':'og:title'})
    if tag_title:
        title = tag_title['content']
        title = title.replace(';', '.')
    
    tag_backers = soup.find('div', {'id':'backers_count'})
    if tag_backers:
        backers_sum = tag_backers.find('data')
        if backers_sum:
            backers = backers_sum['data-value']
    tag_comments = soup.find('a', {'class':'js-load-project-comments'})
    if tag_comments:
        comments = tag_comments['data-comments-count']
        print "comments   ", comments

    tag_location = soup.find_all('a', {'class':'grey-dark mr3 nowrap'})[0]
    location_City = ''
    location_State = ''
    if tag_location:
        location_str = tag_location.text
        if ',' in location_str:
            location_City = location_str.split(",")[0].strip()
            location_State = location_str.split(",")[1].strip()
            print "location_City:",location_City, "  location_State",location_State 
    
    tag_subcategory = soup.find_all('a', {'class':'grey-dark mr3 nowrap'})
    if tag_subcategory:
        for singleItem in tag_subcategory:
            ref = singleItem['href'].split('?ref=')
            if ref[1] == 'category':
                hrefspliter = ref[0].split('/')
                subcategory = hrefspliter[-1]
                subcategory = subcategory.replace('%20', ' ')
    #attrs1 = [url, currentDate, currentClock, category, title, updates, backers, comments, location]
    urltrip = url.split('?')[0]
    attrs1 = [urltrip, currentDate, category, subcategory, title, backers, comments, location_City, location_State]
    #******************************
    #页面左侧部分
    video = video_length = desLength = desPics = riskLength = FAQQ = FAQA = '0'
    desContent = riskContent = ''
    tag_video = soup.find('div', {'id':'video-section'})
    if tag_video and tag_video['data-has-video']=='true':
        video = '1'
        video_length_tag = soup.find('time', {'class':'time total_time left mr1 video-time--total'})
        if video_length_tag:
            video_length = video_length_tag.text
            print video_length
    #get video length
    #creator_content = readFromUrl(creator_modal_url)
    #soup_creator = BeautifulSoup(creator_content)
    tag_description = soup.find('div', {'class':'full-description'})
    if tag_description:
        desContent = cleanString(tag_description.get_text())
        desLength = getWordNumber(desContent)
        desPics = str(len(tag_description.find_all('img')))
    #******************************
    #desciprtion部分
    description_modal_url_split = url.split('?')
    description_modal_url = description_modal_url_split[0] + '/description'
    description_content = readFromUrl(description_modal_url)
    soup_description = BeautifulSoup(description_content)
    tag_risk = soup_description.find('div', {'class':'mb6 mb2'})
    if tag_risk:
        #print tag_risk.get_text()
        riskContent = tag_risk.find('p').string
        if riskContent:
            riskContent = riskContent.lstrip().rstrip()
            riskLength = getWordNumber(riskContent)
        #print 'riskLength: ', riskLength
    FAQQ = str(len(soup_description.find_all('div', {'class':'faq-question'})))
    FAQA = str(len(soup_description.find_all('div', {'class':'faq-answer'})))
    #print 'FAQQ: ', FAQQ
    #print 'FAQA: ', FAQA
    attrs2 = [video, video_length, desLength, desPics, desContent, riskLength, riskContent, FAQQ, FAQA]

    #******************************
    #页面右栏上方
    moneyUnit = backers = pledgedAmount = goal = daysToGo = '0'
    tag_pledged = soup.find('div', {'id':'pledged'})
    if tag_pledged:
        goal = tag_pledged['data-goal']
        goal = goal.replace(',', '')
        pledgedAmount = tag_pledged['data-pledged']
        pledgedAmount = pledgedAmount.replace(',', '')
        tag_amount = tag_pledged.find('data')
        if tag_amount:
            moneyUnit = tag_amount['data-currency']
    # tag_backers = soup.find('meta', {'property':'twitter:text:backers'})
    # if tag_backers:
    #     backers = tag_backers['content']

    
    attrs3 = [moneyUnit, pledgedAmount, goal]
    #******************************
    #页面右栏最下端
    beginDate = endDate = spanDays = deltaDays = ''
    tag_period = soup.find('div', {'id':'meta'})
    if tag_period:
        # time1 = tag_period.find('time')
        # beginDate = re.match('(\d+-\d+-\d+)T.*', time1['datetime']).group(1)
        time2 = time1.find_next_sibling('time')
        endDate = re.match('(\d+-\d+-\d+)T.*', time2['datetime']).group(1)
    tag_duration = soup.find('span', {'id':'project_duration_data'})
    # if tag_duration:
    #     spanDays = re.match('(\d+).\d?', tag_duration['data-duration']).group(1)
    if tag_duration:
        #spanDays = re.match('(\d+).\d?', tag_duration['data-duration']).group(1)
        spanDays = tag_duration['data-duration']
        #print spanDays
        endDate = tag_duration['data-end_time']
        curDateUTC = datetime.datetime.now(tz=pytz.timezone('UTC'))
        end = parse(endDate)
        deltaDays = (end - curDateUTC).days
        #print 'end;:', end
        #print 'days to go:', deltaDays
        if(deltaDays == 0):
            recordNewlyEnd(category,url)
            #print "newly end project:   " + title
            deltaDays = float((end - curDateUTC).seconds) / 24 / 3600
        #print 'days to go:', deltaDays
        #print endDate
    attrs4 = [deltaDays,endDate, spanDays]
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
    soup_creator = BeautifulSoup(creator_content)
    tag_creator_name = soup_creator.find('h1', {'class':'h2 normal mb1'})
    if tag_creator_name:
        creatorName = tag_creator_name.find('a').text
    '''creator location'''
    tag_creator_location = soup_creator.find('p', {'class':'h5 bold mb0'})
    if tag_creator_location:
        creatorAdd_str = tag_creator_location.text
        if ',' in creatorAdd_str:
            creatorAdd_City =  creatorAdd_str.split(',')[0]
            creatorAdd_State = creatorAdd_str.split(',')[1]
        else:
            creatorAdd_City = creatorAdd_State = creatorAdd_str
        print "city:",creatorAdd_City,"  state,",creatorAdd_State
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
        list_websites = tag_website.find('a', {'rel':'nofollow'})
        num_websites = len(list_websites)
    attrs5 = [creatorName, creatorAdd_City, creatorAdd_State, FB_state, FB_name, str(FB_friends), str(num_websites)]
    
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
        #to get number of projects of each category
        tag_circle = soup2.find('div', {'id':'small_circle'})
        if tag_circle:
            # review problem
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
        
    
    #******************************
    buffer1.extend(attrs1)
    buffer1.extend(attrs2)
    buffer1.extend(attrs3)
    buffer1.extend(attrs4)
    buffer1.extend(attrs5)
    buffer1.extend(attrs6)

    writers[0].writerow(buffer1)
    #-------------------------------------
    #basicInfo = [currentDate, currentClock, category, title, creatorID, creator]
    basicInfo = [currentDate, category, title, creatorID, creatorName]
    # backersUrl = url+'/backers'
    # try:
    #     analyzeBackersData(backersUrl, writers[1], basicInfo)
    # except:
    #     pass

    update_modal_url_split = url.split('?')
    update_modal_url = update_modal_url_split[0] + '/updates'
    try:
        analyzeUpdatesData(update_modal_url, writers[1], basicInfo)
    except Exception,e:
        pass

    comment_modal_url_split = url.split('?')
    comment_modal_url = comment_modal_url_split[0] + '/comments'
    try:
        analyzeCommentsData(comment_modal_url, writers[2], basicInfo)
    except Exception,e:
        pass

    tempBuff = [urltrip]
    tempBuff.extend(basicInfo)
    try:
        analyzeRewardData(soup, writers[3], tempBuff)
    except Exception,e:
        traceback.print_exc()
    try:
        analyzeFaqData(soup, writers[4], tempBuff)
    except Exception,e:
        pass
    # try:
    #     analyzeCreatorBackProjectsData(basicInfo[3], basicInfo[1], writers[5])
    # except Exception,e:
    #     pass
    # try:
    #     analyzeCreatorCreateProjectsData(basicInfo[3], basicInfo[1], writers[6])
    # except Exception,e:
    #     pass
#end analyzeData()
#-----------------------------------------------------
def analyzeBackersData(url, writer, attrs):
    backersContent = readFromUrl(url)
    soup_backers = BeautifulSoup(backersContent)
    tag_backerPage = soup_backers.find('li', class_='page')
    if tag_backerPage:
        backerList = tag_backerPage.find_all('div', class_='NS_backers__backing_row')
        for backerItem in backerList:
            buffer2 = [url+'/backers']
            buffer2.extend(attrs)
            tag_backer = backerItem.div
            backerName = tag_backer.h5.get_text().strip()
            #print backerName
            backerID = re.match('/profile/(\S+)', backerItem.a['href']).group(1)
            backerLocation = ''
            tag_backerLocation = tag_backer.find('p', class_='location')
            if tag_backerLocation:
                backerLocation = (tag_backerLocation.get_text()).strip()
            i_backingNumber = 1
            tag_backing = tag_backer.find('p', class_='backings')
            if tag_backing:
                backingNumber = re.search('\d+', tag_backing.get_text()).group(0)
                i_backingNumber = (int)(str(backingNumber))+1
            buffer2.extend([backerName, backerID, backerLocation, i_backingNumber])
            writer.writerow(buffer2)

#-----------------------------------------------------
# review problem: too many find without validate
def analyzeUpdatesData(url, writer, attrs):
    #print 'UPDATING: ', url
    update_content = readFromUrl(url)
    soup_update = BeautifulSoup(update_content)
    # review problem
    tag_updates_div = soup_update.find('div', {'class':'NS_projects__updates_section'})
    tag_timeline = tag_updates_div.find('div', {'class':'timeline'})
    tag_update_items_right = tag_timeline.find('div', {'class':'timeline__item timeline__item--right'})
    tag_update_items_left = tag_timeline.find('div', {'class':'timeline__item timeline__item--left'})
    tmp_div = 'timeline__divider timeline__divider--launched timeline__divider--launched--' + attrs[1].lower()
    #print 'tmp_div: ', tmp_div
    #tag_update_items_lauched = tag_timeline.find('div', {'class':'timeline__divider timeline__divider--launched timeline__divider--launched--dance'})
    #tag_update_items_lauched = tag_timeline.find('div', {'class': ''})
    tag_update_items_lauched = tag_timeline.find(True, {'class': re.compile(r'\btimeline__divider--launched\b')})
    #print 'tag_timeline: ',tag_timeline
    #print 'tag_update_items_right: ',tag_update_items_right
    #print 'tag_update_items_left: ',tag_update_items_left
    #print 'tag_update_items_lauched: ',tag_update_items_lauched
    u_date = u_title = u_content = ''
    like_num = comment_num = 'NA'
    buffer3 = [url]
    buffer3.extend(attrs)
    if tag_update_items_left == None:
        if tag_update_items_right == None:
            if tag_update_items_lauched:
                #print 'tag_update_items_lauched: ', tag_update_items_lauched
                #lauched 
                u_title = tag_update_items_lauched.find('div', {'class':'h2'}).string
                #<time class="js-adjust-time" data-format="LL" datetime="2015-04-02T14:21:01-04:00">
                u_date_div = tag_update_items_lauched.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                
                buffer3.extend([u_title, u_date, like_num, comment_num, u_content])
                #print 'buffer3: ',buffer3
                writer.writerow(buffer3)
                #print 'buffer3: ',buffer3
        else:
            #right list
            #print 'tag_update_items_right: ', tag_update_items_right
            for singleItemRight in tag_update_items_right:
                # review problen: double underline?
                u_title = singleItemRight.find('h2', {'class':'grid-post__title'}).string
                u_date_div = singleItemRight.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                u_content_div = singleItemRight.find('div', {'class':'grid-post__content'})
                u_content_p = u_content_div.find('p')
                for pItem in u_content_p:
                    u_content += pItem.string
                u_metadata = singleItemRight.find('div', {'class':'grid-post__metadata'})
                for spanItem in u_metadata:
                    span_content = spanItem.string
                    span_content_spliter = span_content.split(' ')
                    if (span_content_spliter[1] == 'like') or (span_content_spliter[1] == 'likes'):
                        #df
                        like_num = span_content_spliter[0]
                    elif (span_content_spliter[1] == 'comment') or (span_content_spliter[1] == 'comments'):
                        #fd
                        comment_num = span_content_spliter[0]

                buffer3.extend([u_title, u_date, like_num, comment_num, u_content])
                #print 'buffer3: ',buffer3
                writer.writerow(buffer3)
                #print 'buffer3: ',buffer3
            if tag_update_items_lauched:
                #print 'tag_update_items_lauched: ', tag_update_items_lauched
                #lauched 
                u_title = tag_update_items_lauched.find('div', {'class':'h2'}).string
                #<time class="js-adjust-time" data-format="LL" datetime="2015-04-02T14:21:01-04:00">
                u_date_div = tag_update_items_lauched.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                
                buffer3.extend([u_title, u_date, like_num, comment_num, u_content])
                #print 'buffer3: ',buffer3
                writer.writerow(buffer3)
                #print 'buffer3: ',buffer3
    else:
        #left list
        #print 'tag_update_items_left: ', tag_update_items_left
        for singleItemleft in tag_update_items_left:
                u_title = singleItemleft.find('h2', {'class':'grid-post__title'}).string
                u_date_div = singleItemleft.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                u_content_div = singleItemleft.find('div', {'class':'grid-post__content'})
                u_content_p = u_content_div.find('p')
                for pItem in u_content_p:
                    u_content += pItem.string
                u_metadata = singleItemleft.find('div', {'class':'grid-post__metadata'})
                for spanItem in u_metadata:
                    span_content = spanItem.string
                    span_content_spliter = span_content.split(' ')
                    if (span_content_spliter[1] == 'like') or (span_content_spliter[1] == 'likes'):
                        #df
                        like_num = span_content_spliter[0]
                    elif (span_content_spliter[1] == 'comment') or (span_content_spliter[1] == 'comments'):
                        #fd
                        comment_num = span_content_spliter[0]
                buffer3.extend([u_title, u_date, like_num, comment_num, u_content])
                #print 'buffer3: ',buffer3
                writer.writerow(buffer3)
                #print 'buffer3: ',buffer3
        if tag_update_items_right == None:
            if tag_update_items_lauched:
                #print 'tag_update_items_lauched: ', tag_update_items_lauched
                #lauched
                u_date = tag_update_items_lauched.find('div', {'class':'h2'}).string
                #<time class="js-adjust-time" data-format="LL" datetime="2015-04-02T14:21:01-04:00">
                u_date_div = tag_update_items_lauched.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                #buffer3 = [url]
                #buffer3.extend(attrs)
                buffer3.extend([u_title, u_date, like_num, comment_num, u_content])
                writer.writerow(buffer3)
                #print 'buffer3: ',buffer3
        else:
            #right list
            #print 'tag_update_items_right: ', tag_update_items_right
            for singleItemRight in tag_update_items_right:
                u_title = singleItemRight.find('h2', {'class':'grid-post__title'}).string
                u_date_div = singleItemRight.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                u_content_div = singleItemRight.find('div', {'class':'grid-post__content'})
                u_content_p = u_content_div.find('p')
                for pItem in u_content_p:
                    u_content += pItem.string
                u_metadata = singleItemRight.find('div', {'class':'grid-post__metadata'})
                for spanItem in u_metadata:
                    span_content = spanItem.string
                    span_content_spliter = span_content.split(' ')
                    if (span_content_spliter[1] == 'like') or (span_content_spliter[1] == 'likes'):
                        like_num = span_content_spliter[0]
                    elif (span_content_spliter[1] == 'comment') or (span_content_spliter[1] == 'comments'):
                        comment_num = span_content_spliter[0]
                buffer3.extend([u_title, u_date, like_num, comment_num, u_content])
                #print 'buffer3: ',buffer3
                writer.writerow(buffer3)
                #print 'buffer3: ',buffer3
            if tag_update_items_lauched:
                #print 'tag_update_items_lauched: ', tag_update_items_lauched
                #lauched
                u_date = tag_update_items_lauched.find('div', {'class':'h2'}).string
                #<time class="js-adjust-time" data-format="LL" datetime="2015-04-02T14:21:01-04:00">
                u_date_div = tag_update_items_lauched.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                #buffer3 = [url]
                #buffer3.extend(attrs)
                buffer3.extend([u_title, u_date, like_num, comment_num, u_content])
                writer.writerow(buffer3)
                #print 'buffer3: ',buffer3
#end analyzeUpdatesData()

#---------------------------------------------------
def analyzeCommentsData(url, writer, attrs):
    #print 'COMMENTING'
    commentsContent = readFromUrl(url)
    soup_comments = BeautifulSoup(commentsContent)
    tag_comments = soup_comments.find('ol', class_='comments')
    if tag_comments:
        list_comments = tag_comments.find_all('li', class_='comment')
    else:
        return
    for comment in list_comments:
        #print 'COMMENT : ', comment
        buffer4 = [url.split('/comments')[0]]
        buffer4.extend(attrs)
        commentator = commentatorID = date = content = ''
        tag_commentator = comment.find('a', class_='author')
        if tag_commentator:
            commentator = tag_commentator.string
            commentatorID = re.match('/profile/(\S+)', tag_commentator['href']).group(1)
        tag_date = comment.find('data', {'data-format': 'distance_date'})
        if tag_date:
            date = re.search('(\d+-\d+-\d+)T', tag_date['data-value']).group(1)
        tag_content = comment.find_all('p')
        for p in tag_content:
            #print p
            if p.get_text():
                content += p.get_text()
        content = cleanString(content)
        buffer4.extend([commentator, commentatorID, date, content])
        #print 'buffer4: ', buffer4
        writer.writerow(buffer4)
        #print 'BUFFER : ', buffer4
#end analyzeCommentData

#-----------------------------------------------------
def analyzeRewardData(soup, writer, attrs):
    #******************************
    #Reward
    tag_reward = soup.find('div', {'class':'NS_projects__rewards_list js-project-rewards'})
    print tag_reward
    if tag_reward:
        print 'CRAWLING REWARD'
        reward_list = tag_reward.find('ol').find_all('li', {'class':'hover-group js-reward-available pledge--available pledge-selectable-sidebar'})
        # print reward_list
        for reward_item in reward_list:
            #print 'gaga', rcount
            buffer5 = []
            buffer5.extend(attrs)
            RID = RAmt = RBkr = RDes = Rdel = Rshipto = Unit = ''
            RleftPart = RleftWhole = ""
            RID = reward_item['data-reward-id']
            print "RID:" + RID
            tag_RAmt = reward_item.find('h2', {'class':'reward__pledge-amount'})
            if tag_RAmt:
                AmgString = tag_RAmt.getText().split('\n')[1]
                print AmgString
                RAmt = AmgString.split(' ')[1]
                RAmt = RAmt.replace(' ', "")
                Unit = re.search('(\D+)?', RAmt).group(1)
                RAmt = re.search('\D+(\d+[,.]*\d*)?', RAmt).group(1)
            tag_RBkr = reward_item.find('p', {'class':'reward__backer-count'})
            if tag_RBkr:
                RBkr = re.search('\D(\d+(\.\d+)?)', tag_RBkr.getText()).group(0)
                RBkr = RBkr.strip()
                print 'RBkr :' + RBkr
                tag_left = tag_RBkr.find('span', {'class':'reward__limit'})
                if tag_left:
                    print tag_left.string
                    Rleft = re.search('\D+\((\d+(.*)\d+)?\)', tag_left.string).group(1)
                    RleftPart = Rleft.split(' ')[0]
                    RleftWhole = Rleft.split(' ')[3]
                    print "RleftPart:" + RleftPart
                    print "RleftWhole:" + RleftWhole
            tag_RDes = reward_item.find('div', {'class':'reward__description reward__description--expanded'})
            if tag_RDes:
                RDes = tag_RDes.p.string
                if RDes == None:
                    RDes = ""
                RDes = RDes.strip()
                #RDes = cleanString(RDes)
                print 'RDes :'+ RDes
            tag_Extra = reward_item.find('div',{'class':'reward__extra-info'})
            if tag_Extra:
                tag_Extra = tag_Extra.find('div', {'class':'reward__detail'})
                if tag_Extra:
                    tag_ExtraDel = tag_Extra.find('span',{'class':'reward__detail-info'})
                    if tag_ExtraDel:
                        RdelTime = tag_ExtraDel.find('time')
                        Rdel = RdelTime['datetime']
                        print 'RDel :' + Rdel
                RshiptoTag = tag_Extra.find_next('div',{'class':'reward__detail'})
                if RshiptoTag and RshiptoTag.find('span', {'class':'reward__detail-label'}).string == "Ships to:":
                    Rshipto = RshiptoTag.find('span',{'class':'reward__detail-info'}).string
                    if Rshipto == None:
                        Rshipto = ""
                print 'Rshipto: ' + Rshipto

            buffer5.extend([RID, Unit, RAmt, RBkr, RDes, Rdel, Rshipto, RleftPart, RleftWhole])
            #print 'buffer5:', buffer5
            writer.writerow(buffer5)
#end analyzeRewardData()

#-----------------------------------------------------
def analyzeFaqData(soup, writer, attrs):
    tag_faq = soup.find('ul', class_='faqs')
    if tag_faq:
        faq_list = tag_faq.find_all('li', class_='faq')
        for faq in faq_list:
            buffer6 = []
            buffer6.extend(attrs)
            question = answer = updateDate = updateClock = ''
            tag_question = faq.find('span', class_='question')
            if tag_question:
                question = tag_question.get_text()
            tag_answer = faq.find('div', class_='faq-answer')
            if tag_answer:
                answer = tag_answer.get_text()
                answer = cleanString(answer)
            tag_time = faq.find('time', class_='js-adjust')
            if tag_time:
                updateDate = re.search('(\d+-\d+-\d+)T', tag_time['datetime']).group(1)
                updateClock = re.search('T(\d+:\d+:\d+)-', tag_time['datetime']).group(1)
            buffer6.extend([question, answer, updateDate, updateClock])
            writer.writerow(buffer6)
#end analyzeFaqData

#--------------------------------------------------------
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

def analyzeNewlyEndUsersData(url, writerCreate, writeBack, categoryName):
    global filedirectory
    webcontent = readFromUrl(url.split("?")[0]+"/description")
    print url+"/description"
    #print webcontent
    soup = BeautifulSoup(webcontent)
    #about creator
    creatorID = ''
    bioContent = readFromUrl(url+'/creator_bio.js')
    soup_bio = BeautifulSoup(bioContent)

    tag_creatorUrl = soup.find('meta', {'property':'kickstarter:creator'})
    if tag_creatorUrl:
        creatorUrl = tag_creatorUrl['content']
        creatorID = re.match('https://www\.kickstarter\.com/profile/(\S+)', creatorUrl).group(1)

    '''Get the remote modal'''
    creator_modal_url_split = url.split('?')
    creator_modal_url = creator_modal_url_split[0] + '/creator_bio'
    creator_content = readFromUrl(creator_modal_url)
    soup_creator = BeautifulSoup(creator_content)
    creatorName = ''
    tag_creatorName = soup_creator.find('div',{'class':'table-cell full-width px2 border-box'})
    if tag_creatorName:
        creatorName = tag_creatorName.find('a').text
    print '============TTTTTTTTT=============='
    print str(creatorID)
    print creatorName

    analyzeCreatorCreateProjectsData(str(creatorID), creatorName, categoryName, writerCreate);
    analyzeCreatorBackProjectsData(str(creatorID), creatorName, categoryName, writeBack);

#---------------------------------------------------
def analyzeCreatorBackProjectsData(creatorID, createName, catogryNM, writer):
    print 'analysing creator back info...'
    #basicInfo = [currentDate, category, title, creatorID, creator]
    creatorHomePageUrl = 'https://www.kickstarter.com/profile/' + creatorID
    creatorHomePage = readFromUrl(creatorHomePageUrl)
    soup_chp = BeautifulSoup(creatorHomePage)
    backProjectListContent = soup_chp.find('div', {'id':'profile_projects_list'})
    print 'before inside'
    print creatorHomePageUrl
    if (backProjectListContent):
        print 'here'
        ulBackPrjContent = backProjectListContent.find('ul', {'class':'mobius'})
        liBackPrjContent = ulBackPrjContent.find('li')
        setBackPrjContent = liBackPrjContent.find_all('div', {'class':'project-card-mini-wrap'})
        for div in setBackPrjContent:
            print 'for'
            aHref = div.find('a')
            backPrjUrl = 'https://www.kickstarter.com' + aHref['href'] + '?ref=category_ending_soon'
            #analyzeNewlyEndData('https://www.kickstarter.com/projects/wheretheheckismatt/where-the-heck-is-matt?ref=category_recommended', writer, catogryNM)
            # print backPrjUrl
            getBackProjectsData(backPrjUrl, creatorID, createName, writer, catogryNM)
#end analyzeCreatorProjectsData

#---------------------------------------------------
def analyzeCreatorCreateProjectsData(creatorID, creatorName, catogryNM, writer):
    print 'analysing creator create info...'
    #basicInfo = [currentDate, category, title, creatorID, creator]
    creatorHomePageUrl = 'https://www.kickstarter.com/profile/' + creatorID + '/created'
    creatorHomePage = readFromUrl(creatorHomePageUrl)
    soup_chp = BeautifulSoup(creatorHomePage)
    createProjectListContent = soup_chp.find('div', {'id':'main'})
    liCreatePrjContent = createProjectListContent.find_all('li', {'class':'mb2'})
    for li in liCreatePrjContent:
        aSetOfCreatePrjContent = li.find_all('a')
        aHref = ''
        for aItem in aSetOfCreatePrjContent:
            partIOfA = aItem['href'].split('/')[1]
            partIIOfA = partIOfA.split('/')[0]
            if partIIOfA == 'projects':
                aHref = aItem['href']
                break
        if aHref:
            # print '### start to get create project...'
            createPrjUrl = 'https://www.kickstarter.com' + aHref
            # print 'href: ' + createPrjUrl
            getBackProjectsData(createPrjUrl, creatorID, creatorName, writer, catogryNM)
#end analyzeCreatorProjectsData

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
