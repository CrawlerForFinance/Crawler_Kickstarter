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

def analyzeNewlyEndUsersData(url, writerCreate, writeBack, categoryName):
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
        #******************************
        buffer1 = [creatorUserID, creatorUserName]
        buffer1.extend(attrs1)
        buffer1.extend(attrs4)
        # buffer1.extend(attrs5)
        # buffer1.extend(attrs6)
        writer.writerow(buffer1)
    else:
        print 'project has been purged'
#--------------------------------------------------
#--------------------------------------------------