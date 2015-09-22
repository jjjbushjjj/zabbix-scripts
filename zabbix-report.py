#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import MySQLdb
import time
import datetime
import calendar
import os
import os.path
from tempfile import TemporaryFile
from xlwt import Workbook,easyxf
from xlrd import open_workbook

today = datetime.date.today()

report_dir="/work/opt/zabbix-reports"

host='127.0.0.1'
port=3306
user = 'report_user'
password = 'report_passwd'
database = 'zabbix'

keys = ("cpuload","disk_usage","network_in","network_out")
thre_dic = {"cpuload":15,"disk_usage":85,"network_in":409600}


def custom_report(startTime,endTime):
    sheetName = time.strftime('%m%d_%H%M',startTime) + "_TO_" +time.strftime('%m%d_%H%M',endTime)
    customStart = time.mktime(startTime)
    customEnd = time.mktime(endTime)
    generate_excel(customStart,customEnd,0,sheetName)

def daily_report():

    dayStart = time.mktime(today.timetuple())
    dayEnd = time.time() 
    sheetName = time.strftime('%Y%m%d',time.localtime(dayEnd))
    generate_excel(dayStart,dayEnd,1,sheetName)

def weekly_report():
    lastMonday = today

    while lastMonday.weekday() != calendar.MONDAY:
        lastMonday -= datetime.date.resolution
    weekStart = time.mktime(lastMonday.timetuple())
    weekEnd = time.time()

    sheetName = "weekly_" + time.strftime('%Y%m',time.localtime(weekEnd)) + "_" + str(weekofmonth)
    generate_excel(weekStart,weekEnd,2,sheetName)



def monthly_repport():

    firstDay = today 

    while firstDay.day != 1:
        firstDay -= datetime.date.resolution
    monthStart = time.mktime(firstDay.timetuple()) 
    monthEnd = time.time()
    sheetName = "monthly_" + time.strftime('%Y%m',time.localtime(monthEnd))
    generate_excel(monthStart,monthEnd,3,sheetName)



def getConnection():

    try:
        connection=MySQLdb.connect(host=host,port=port,user=user,passwd=password,db=database,connect_timeout=1);
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    return connection



def getHosts():
    conn=getConnection()
    cursor = conn.cursor()
    command = cursor.execute("""select ip,hostid,Role from hosts where ip<>'127.0.0.1' and ip<>'' and status=0 order by ip;""");
    hosts = cursor.fetchall()
    cursor.close()
    conn.close()
    return hosts



def getItemid(hostid):
    keys_str = "','".join(keys)
    conn=getConnection()
    cursor = conn.cursor()
    command = cursor.execute("""select itemid from items where hostid=%s and key_ in ('%s')""" %(hostid,keys_str));
    itemids = cursor.fetchall()
    cursor.close()
    conn.close()
    return itemids



def getReportById_1(hostid,start,end):
    keys_str = "','".join(keys)
    conn=getConnection()
    cursor = conn.cursor()
    command = cursor.execute("""select items.itemid , key_ as key_value ,units, max(history.value) as max,avg(history.value) as average ,min(history.value) as min from history, items where items.hostid=%s and items.key_ in ('%s')and items.value_type=0 and history.itemid=items.itemid and (clock>%s and clock<%s) group by itemid, key_value;""" %(hostid,keys_str,start,end));
    values = cursor.fetchall()
    cursor.close()
    conn.close();
    return values



def getReportById_2(hostid,start,end):
    keys_str = "','".join(keys)
    conn=getConnection()
    cursor = conn.cursor()
    command = cursor.execute("""select items.itemid , key_ as key_value ,units, max(history_uint.value) as max,avg(history_uint.value) as average ,min(history_uint.value) as min from history_uint, items where items.hostid=%s and items.key_ in ('%s')and items.value_type=3 and history_uint.itemid=items.itemid and (clock>%s and clock<%s) group by itemid, key_value;""" %(hostid,keys_str,start,end));
    values = cursor.fetchall()
    cursor.close()
    conn.close();
    return values





def generate_excel(start,end,reportType,sheetName):
    book = Workbook(encoding='utf-8')
    sheet1 = book.add_sheet(sheetName)
    merge_col = 1
    merge_col_step = 2
    title_col = 1
    title_col_step = 2
    hosts = getHosts()
    isFirstLoop=1
    host_row = 2 
    max_col = 1
    avg_col = 2

    normal_style = easyxf(
'borders: right thin,top thin,left thin, bottom thin;'
'align: vertical center, horizontal center;'
)
    abnormal_style = easyxf(
'borders: right thin, bottom thin,top thin,left thin;'
'pattern: pattern solid, fore_colour red;'
'align: vertical center, horizontal center;'
)
    sheet1.write_merge(0,1,0,0,"HOSTS")
    for ip,hostid,role in hosts:
        sheet1.row(host_row).set_style(normal_style)
        max_col = 1
        avg_col = 2
        reports = getReportById_1(hostid,start,end) + getReportById_2(hostid,start,end)
        if(isFirstLoop==1):
            sheet1.write(host_row,0,ip,normal_style)
            for report in reports:
                title = report[1] + " " + report[2]
                sheet1.write_merge(0,0,merge_col,merge_col+1,title,normal_style)
                merge_col += merge_col_step
                sheet1.write(1,title_col,"MAX",normal_style)
                sheet1.write(1,title_col+1,"Average",normal_style)
                title_col += title_col_step


                if(report[3] >= thre_dic[report[1]]):
                    sheet1.write(host_row,max_col,report[3],abnormal_style)
                    sheet1.write(host_row,avg_col,report[4],normal_style)
                else:
                    sheet1.write(host_row,max_col,report[3],normal_style)
                    sheet1.write(host_row,avg_col,report[4],normal_style)
                max_col = max_col + 2
                avg_col =avg_col+ 2
                isFirstLoop=0   
        else:
            sheet1.write(host_row,0,ip,normal_style)
            for report in reports:

                if(report[3] >= thre_dic[report[1]]):
                    sheet1.write(host_row,max_col,report[3],abnormal_style)
                    sheet1.write(host_row,avg_col,report[4],normal_style)
                else:
                    sheet1.write(host_row,max_col,report[3],normal_style)
                    sheet1.write(host_row,avg_col,report[4],normal_style)
            max_col = max_col + 2
            avg_col =avg_col+ 2
        host_row = host_row +1
    saveReport(reportType,book)





def saveReport(reportType,workBook):

    if(not (os.path.exists(report_dir))):
        os.makedirs(report_dir)

    os.chdir(report_dir)

    month_dir=time.strftime('%Y-%m',time.localtime(time.time()))
    if(not (os.path.exists(month_dir))):
        os.mkdir(month_dir)
    os.chdir(month_dir)

    if(reportType == 0):
        excelName = "custom_report_"+ time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time())) + ".xls"       

    elif(reportType == 1):
        excelName = "daily_report_" + time.strftime('%Y%m%d',time.localtime(time.time())) + ".xls"

    elif(reportType == 2):

        weekofmonth = (today.day+7-1)/7 
        excelName = "weekly_report_" + time.strftime('%Y%m',time.localtime(time.time())) +"_" + str(weekofmonth) + ".xls"

    else:
        monthName = time.strftime('%Y%m',time.localtime(time.time()))
        excelName = "monthly_report_" + monthName + ".xls"

    print excelName
    workBook.save(excelName)



def main():

    argvCount = len(sys.argv)
    dateFormat = "%Y-%m-%d %H:%M:%S"
    today = datetime.date.today()
    if(argvCount == 2):


        startTime = today.timetuple()
        dateFormat = "%Y-%m-%d %H:%M:%S"
        endTime = time.strptime(sys.argv[1],dateFormat)
        custom_report(startTime,endTime)
    elif(argvCount == 3):

        startTime = time.strptime(sys.argv[1],dateFormat)
        endTime = time.strptime(sys.argv[2],dateFormat)
        custom_report(startTime,endTime)
    elif(argvCount ==1):

        today = datetime.date.today()
        dayOfMonth = today.day

        year = int(time.strftime('%Y',time.localtime(time.time())))

        month = int(time.strftime('%m',time.localtime(time.time())))

        lastDayOfMonth = calendar.monthrange(year,month)[1]

        daily_report()

    if(today.weekday()==6):
        weekly_report()

    if(dayOfMonth == lastDayOfMonth):
        monthly_repport()
    else:

        usage()
def usage():
    print """zabbix-report.py ['2012-09-01 01:12:00'] ['2012-09-01 01:12:00']"""

main()
