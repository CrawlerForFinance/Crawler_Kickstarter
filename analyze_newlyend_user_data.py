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