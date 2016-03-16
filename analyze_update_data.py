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

#-----------------------------------------------------
# review problem: too many find without validate
def analyzeUpdatesData(url, writer, attrs):
    #print 'UPDATING: ', url
    update_content = readFromUrl(url)
    soup_update = BeautifulSoup(update_content)
    # review problem
    tag_updates_div = soup_update.find('div', {'class':'NS_projects__updates_section'})
    tag_timeline = tag_updates_div.find('div', {'class':'timeline'})
    tag_update_items_right = tag_timeline.find_all('div', {'class':'timeline__item timeline__item--right'})
    tag_update_items_left = tag_timeline.find_all('div', {'class':'timeline__item timeline__item--left'})
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
            # print 'tag_update_items_right: ', tag_update_items_right
            for singleItemRight in tag_update_items_right:
                # review problen: double underline?
                print singleItemRight.find('h2', {'class':'grid-post__title'})
                u_title = singleItemRight.find('h2', {'class':'grid-post__title'}).string
                u_date_div = singleItemRight.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                u_content_div = singleItemRight.find('div', {'class':'grid-post__content'})
                try:
                    u_content_p = u_content_div.find('p')
                    for pItem in u_content_p:
                        u_content += pItem.string
                except:
                    pass
                u_metadata = singleItemRight.find('div', {'class':'grid-post__metadata'})
                for spanItem in u_metadata:
                    if not spanItem:
                        continue
                    span_content = spanItem.string

                    if not span_content:
                        continue

                    span_content_spliter = span_content.split(' ')

                    if len(span_content_spliter) <= 1:
                        continue

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
        # print 'tag_update_items_left: ', tag_update_items_left
        for singleItemleft in tag_update_items_left:
                print singleItemleft.find('h2', {'class':'grid-post__title'})
                u_title = singleItemleft.find('h2', {'class':'grid-post__title'}).string
                u_date_div = singleItemleft.find('time', {'class':'js-adjust-time'})
                u_date = re.match('(\d+-\d+-\d+)T.*', u_date_div['datetime']).group(1)
                u_content_div = singleItemleft.find('div', {'class':'grid-post__content'})
                try:
                    u_content_p = u_content_div.find('p')
                    for pItem in u_content_p:
                        u_content += pItem.string
                except:
                    pass
                u_metadata = singleItemleft.find('div', {'class':'grid-post__metadata'})
                for spanItem in u_metadata:
                    if not spanItem:
                        continue
                    span_content = spanItem.string

                    if not span_content:
                        continue

                    span_content_spliter = span_content.split(' ')

                    if len(span_content_spliter) <= 1:
                        continue

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

                try:
                    u_content_p = u_content_div.find('p')
                    for pItem in u_content_p:
                        u_content += pItem.string
                except:
                    pass

                u_metadata = singleItemRight.find('div', {'class':'grid-post__metadata'})
                for spanItem in u_metadata:
                    if not spanItem:
                        continue
                    span_content = spanItem.string


                    if not span_content:
                        continue
                    
                    span_content_spliter = span_content.split(' ')

                    if len(span_content_spliter) <= 1:
                        continue

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
