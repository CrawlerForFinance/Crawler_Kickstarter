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