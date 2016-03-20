# -*- coding: utf-8 -*-
#分析整理实际抓取的类和本来的类的个数
import openpyxl
import datetime,time,string

prePath = 'data/AliveNumber_'
realPath = 'data/'
resultPath = 'datasummary.xlsx'

starttime = datetime.datetime(2015,8,10)
endtime = datetime.datetime(2015,8,24)
#daynum = (endtime-starttime).days

#获取处理的时间范围
while True:
    try:
        startinput = input('input start time:' )
        starttime = datetime.datetime.strptime(startinput,"%Y-%m-%d").date()
        #starttime = datetime.datetime(startinput)
        break
    except:
        print('Start time illegal! Please input again!')
        continue
while True:
    try:
        endinput = input('input end time:')
        endtime = datetime.datetime.strptime(endinput,"%Y-%m-%d").date()
        #endtime = datetime.datetime(endinput)
        break
    except:
        print('end time illegal! Please input again!')
        continue  
daynum = (endtime-starttime).days
#处理理论上应该的数据
work_book = openpyxl.load_workbook(resultPath)
work_sheet1 = work_book.get_sheet_by_name("DailyAlive")

#读取csv文件
currentindex = 49
for dateindex in range(0,daynum+1):
    date = starttime+datetime.timedelta(dateindex)
    fopen = open(prePath+date.strftime('%Y%m%d')+'.csv','r')
    alive = []
    try:
        for line in fopen.readlines():
            alive.append(int(line.split(',')[1]))
    finally:
        fopen.close()
    #写入到xlxs文件中
    work_sheet1.append({'A':date.strftime('%Y/%m/%d'),'B':alive[0],'C':alive[1],'D':alive[2],'E':alive[3],'F':alive[4],'G':alive[5],'H':alive[6],'I':alive[7],'J':alive[8],'K':alive[9],'L':alive[10],'M':alive[11],'N':alive[12],'O':alive[13],'P':alive[14]})
#work_book.save('test.xlsx')

#读取实际抓取的数据
title=['Art','Comics','Crafts','Dance','Design','Fashion','Film&Video','Food','Games','Journalism','Music','Photography','Publishing','Technology','Theater']
work_sheet2 = work_book.get_sheet_by_name("RealGet")
for dateindex in range(0,daynum+1):
    date = starttime+datetime.timedelta(dateindex)
    realget = []
    for index in range(0,len(title)):
        #依次处理每一个类
        classname = title[index]
        #projects_Art_20150623
        fopen = open(realPath+classname+'/projects_'+classname+'_'+date.strftime('%Y%m%d')+'.csv','r',encoding= 'utf-8')
        count = 0
        try:
            for line in fopen.readlines():
                if("https" in line):
                    count +=1
            
            realget.append(count)
        finally:
            fopen.close()
    #将结果写入带走xlxs文件中
    work_sheet2.append({'A':date.strftime('%Y/%m/%d'),'B':realget[0],'C':realget[1],'D':realget[2],'E':realget[3],'F':realget[4],'G':realget[5],'H':realget[6],'I':realget[7],'J':realget[8],'K':realget[9],'L':realget[10],'M':realget[11],'N':realget[12],'O':realget[13],'P':realget[14]})
    
newfilename = 'datasummary'+str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))+'.xlsx'
work_book.save(newfilename)
