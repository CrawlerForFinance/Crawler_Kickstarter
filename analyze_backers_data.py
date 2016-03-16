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

