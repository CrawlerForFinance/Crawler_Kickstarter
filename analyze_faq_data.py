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