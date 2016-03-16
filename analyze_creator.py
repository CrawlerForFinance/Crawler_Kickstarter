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