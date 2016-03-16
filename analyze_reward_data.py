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
def analyzeRewardData(soup, writer, attrs):
    #******************************
    #Reward
    tag_reward = soup.find('div', {'class':'NS_projects__rewards_list js-project-rewards'})
    #print tag_reward
    if tag_reward:
        #print 'CRAWLING REWARD'
        reward_list = tag_reward.find('ol').find_all('li', {'class':'hover-group js-reward-available pledge--available pledge-selectable-sidebar'})
        # #print reward_list
        for reward_item in reward_list:
            ##print 'gaga', rcount
            buffer5 = []
            buffer5.extend(attrs)
            RID = RAmt = RBkr = RDes = Rdel = Rshipto = Unit = ''
            RleftPart = RleftWhole = ""
            RID = reward_item['data-reward-id']
            #print "RID:" + RID
            tag_RAmt = reward_item.find('h2', {'class':'pledge__amount'})
            if tag_RAmt:
                AmgString = tag_RAmt.getText().split('\n')[1]
                #print AmgString
                RAmt = AmgString.split(' ')[1]
                RAmt = RAmt.replace(' ', "")
                Unit = re.search('(\D+)?', RAmt).group(1)
                RAmt = re.search('\D+(\d+[,.]*\d*)?', RAmt).group(1)
            tag_RBkr = reward_item.find('p', {'class':'pledge__backer-count'})
            if tag_RBkr:
                RBkr = re.search('\D(\d+(\.\d+)?)', tag_RBkr.getText()).group(0)
                RBkr = RBkr.strip()
                #print 'RBkr :' + RBkr
                tag_left = tag_RBkr.find('span', {'class':'pledge__limit'})
                if tag_left:
                    #print tag_left.string
                    Rleft = re.search('\D+\((\d+(.*)\d+)?\)', tag_left.string).group(1)
                    RleftPart = Rleft.split(' ')[0]
                    RleftWhole = Rleft.split(' ')[3]
                    #print "RleftPart:" + RleftPart
                    #print "RleftWhole:" + RleftWhole
            tag_RDes = reward_item.find('div', {'class':'pledge__reward-description pledge__reward-description--expanded'})
            if tag_RDes:
                RDes = tag_RDes.p.string
                if RDes == None:
                    RDes = ""
                RDes = RDes.strip()
                #RDes = cleanString(RDes)
                #print 'RDes :'+ RDes
            tag_Extra = reward_item.find('div',{'class':'pledge__extra-info'})
            if tag_Extra:
                tag_Extra = tag_Extra.find('div', {'class':'pledge__detail'})
                if tag_Extra:
                    tag_ExtraDel = tag_Extra.find('span',{'class':'pledge__detail-info'})
                    if tag_ExtraDel:
                        RdelTime = tag_ExtraDel.find('time')
                        Rdel = RdelTime['datetime']
                        #print 'RDel :' + Rdel
                RshiptoTag = tag_Extra.find_next('div',{'class':'pledge__detail'})
                if RshiptoTag and RshiptoTag.find('span', {'class':'pledge__detail-label'}).string == "Ships to:":
                    Rshipto = RshiptoTag.find('span',{'class':'pledge__detail-info'}).string
                    if Rshipto == None:
                        Rshipto = ""
                #print 'Rshipto: ' + Rshipto

            buffer5.extend([RID, Unit, RAmt, RBkr, RDes, Rdel, Rshipto, RleftPart, RleftWhole])
            ##print 'buffer5:', buffer5
            writer.writerow(buffer5)
#end analyzeRewardData()
