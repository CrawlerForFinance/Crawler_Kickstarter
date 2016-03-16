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

def analyzeNewlyEndData(url, writer, categoryName):
    global filedirectory
    webcontent = readFromUrl(url.split("?")[0]+"/description")
    print url+"/description"
    #print webcontent
    soup = BeautifulSoup(webcontent)
    buffer1 = []
    #******************************
    #页面上栏部分
    currentDate = getTime('%Y-%m-%d %H:%M:%S')

    category = subcategory = title = backers = location_City = location_State = isSuccessful = PlgAmt = ''
    Goal = ""
    beginDate = endData = PlgAmt = spanDays = Goal = backers = Unit = ""
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
            print spanDays
    
    #没有结束的和没有成功的时有这个标签的，成功的是没有这个标签的
    tag_success = soup.find('div',{'calss':'NS_projects__spotlight_stats'})
    if not tag_success:
        #spanDays = re.match('(\d+).\d?', tag_duration['data-duration']).group(1)
        remaining = tag_duration['data-hours-remaining']
        if int(remaining) == 0:
            isSuccessful = "0"
            print "not successful"
            tag_creator = soup.find('a', {'class':'remote_modal_dialog green-dark'})[0]
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
            return
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
    print "isSuccessful:" + str(isSuccessful)
    print "spanDays:" + str(spanDays)
    print "endData:" + endData
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
        print "title:" + title
    tag_location = soup.find('meta', {'property':'twitter:text:location'})
    if tag_location:
        location = tag_location['content']
        print "location:" + location
    tag_location = soup.find_all('a', {'class':'grey-dark mr3 nowrap'})[0]
    location_City = ''
    location_State = ''
    if tag_location:
        location_str = tag_location.text
        if ',' in location_str:
            location_City = location_str.split(",")[0].strip()
            location_State = location_str.split(",")[1].strip()
    print location_City + ", " + location_State
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
    attrs1 = [urltrip, currentDate, category, subcategory, title, location_City, location_State, Goal, Unit, isSuccessful, backers, PlgAmt]
    print attrs1
    #******************************
    attrs4 = [beginDate,endData, spanDays]
    print attrs4
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
    print attrs5
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
        print attrs6
    
    #******************************
    buffer1.extend(attrs1)
    buffer1.extend(attrs4)
    buffer1.extend(attrs5)
    buffer1.extend(attrs6)
    writer.writerow(buffer1)