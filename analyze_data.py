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

from tools_kickstarter import *

from analyze_newlyend_data import analyzeNewlyEndData
from analyze_newlyend_user_data import analyzeNewlyEndUsersData
from analyze_comments_data import analyzeCommentsData
from analyze_backers_data import analyzeBackersData
from analyze_creator import analyzeCreatorBackProjectsData, analyzeCreatorCreateProjectsData
from analyze_faq_data import analyzeFaqData
from analyze_reward_data import analyzeRewardData
from analyze_update_data import analyzeUpdatesData

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

    tag_location = soup.find_all('a', {'class':'grey-dark mr3 nowrap'})
    if tag_location:
        tag_location = tag_location[0]
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
        traceback.print_exc()

    comment_modal_url_split = url.split('?')
    comment_modal_url = comment_modal_url_split[0] + '/comments'
    try:
        analyzeCommentsData(comment_modal_url, writers[2], basicInfo)
    except Exception,e:
        traceback.print_exc()

    tempBuff = [urltrip]
    tempBuff.extend(basicInfo)
    try:
        analyzeRewardData(soup, writers[3], tempBuff)
    except Exception,e:
        traceback.print_exc()
    try:
        analyzeFaqData(soup, writers[4], tempBuff)
    except Exception,e:
        traceback.print_exc()
    # try:
    #     analyzeCreatorBackProjectsData(basicInfo[3], basicInfo[1], writers[5])
    # except Exception,e:
    #     pass
    # try:
    #     analyzeCreatorCreateProjectsData(basicInfo[3], basicInfo[1], writers[6])
    # except Exception,e:
    #     pass
#end analyzeData()

#--------------------------------------------------------
