# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 13:24:10 2017

@author: Administrator
"""

from lxml import etree
import pymysql
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header

db = pymysql.connect(
        host = 'localhost',
        user = 'root',
        password = 'henry_2006',
        db = 'hl_sight',
        charset = 'utf8')
cur = db.cursor()

def getfund():  # 读取本地jijin.txt获取网址，爬取数据并保存数据库
    liebiaos = []
    line = open(r'D:\HUILV\Navicat\Python\jijin.txt','r')
    count = len(open(r'D:\HUILV\Navicat\Python\jijin.txt','r').readlines())
    n = 0
    while n < count:
        url = line.readline()
        url = url.strip('\n')
        res = requests.get(url)
        res.encoding = 'utf-8'
        html = etree.HTML(res.text)
            
        names = html.xpath('//div[@class="fundDetail-tit"]/div/text()')[0]
        daima = html.xpath('//div[@class="fundDetail-tit"]/div/span[2]/text()')[0]
        newprice = html.xpath('//*[@id="gz_gsz"]/text()')[0]
        yesterprice = html.xpath('//*[@id="body"]/div[12]/div/div/div[2]/div[1]/div[1]/dl[2]/dd[1]/span[1]/text()')[0]
        updowns = html.xpath('//*[@id="gz_gszze"]/text()')[0]
        fudong = html.xpath('//span[@id="gz_gszzl"]/text()')[0]
        times = html.xpath('//*[@id="gz_gztime"]/text()')[0]
        times = times[1:-1]
        print(names + newprice + yesterprice + updowns + daima + fudong + times)
        
        sql2 = """insert into fund_au9999(name,daima,newprice,yesterprice,updowns,fudong,time)
        values(%s,%s,%s,%s,%s,%s,%s)"""
        t = (names,daima,newprice,yesterprice,updowns,fudong,times)
        try:
            cur.execute(sql2,t)
            db.commit()
        except:
            print('数据库写入失败！')
                
        a = float(fudong.strip('%'))  # 浮动超过0.8%的基金信息添加到列表，并作为返回值
        if a <= -0.8:
            liebiao = names + '(' + daima + '):' + fudong
            liebiaos.append(liebiao)
        n = n + 1
    line.close()
    return liebiaos
    
def getau9999():  # 调用本地浏览器爬取数据，并将数据保存到数据库
    res = requests.get('http://www.dyhjw.com/au9999.html')
    html = etree.HTML(res.text)
    
    names = '上海黄金AU9999'
    daima = html.xpath('/html/body/div[4]/div[2]/div[2]/div[1]/div/h2/text()')[0]
    newprice = html.xpath('/html/body/div[4]/div[2]/div[2]/div[2]/div[1]/span[1]/text()')[0]
    fudong = html.xpath('/html/body/div[4]/div[2]/div[2]/div[2]/div[1]/span[3]/font[2]/text()')[0]
    updowns = html.xpath('/html/body/div[4]/div[2]/div[2]/div[2]/div[1]/span[3]/font[1]/text()')[0]
    
    yesterprice = html.xpath('/html/body/div[4]/div[2]/div[2]/div[2]/ul/li[4]/font/text()')[0]
    times = html.xpath('/html/body/div[4]/div[2]/div[2]/div[1]/div/span[2]/b/text()')[0]
    
    times = times[:(times.index('，')-1)]+' '+times[(times.index('，')+1):]
    print(names + daima + newprice + yesterprice + updowns + fudong + times)
    
    sql2 = """insert into fund_au9999(name,daima,newprice,yesterprice,updowns,fudong,time)
        values(%s,%s,%s,%s,%s,%s,%s)"""
    t = (names,daima,newprice,yesterprice,updowns,fudong,times)
    try:
        cur.execute(sql2,t)
        db.commit()
    except:
        print('数据库写入失败！')
    
    liebiao2s = []
    a = float(fudong.strip('%'))
    if a <= -1:  # 跌涨幅超过1%，将实时价格保存至列表，并作为返回值
        liebiao2 = names + '最新价:' + newprice + ' 涨跌幅:' + fudong
        liebiao2s.append(liebiao2)
    return liebiao2s

def sendmail():  # 合并需要发送邮件的列表，通过stmplib发送邮件
    mailcontent = getfund() + getau9999()
    if len(mailcontent) != 0:
        mailcontent = "\n".join(str(i) for i in mailcontent)
        mail_host="smtp.exmail.qq.com"  #设置服务器
        mail_user="zhangxiaolan@gototw.com.cn"    #邮箱用户名
        mail_pass="Aa18627652885"   #邮箱密码 
         
        sender = 'zhangxiaolan@gototw.com.cn'
        receivers = ['lotusime@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        
        message = MIMEText(mailcontent, 'plain', 'utf-8')
        message['From'] = Header("python", 'utf-8')
        message['To'] =  Header("lotusime", 'utf-8')
         
        subject = 'Remind today:Fund and AU99.99！'
        message['Subject'] = Header(subject, 'utf-8')
         
        try:
            smtpObj = smtplib.SMTP() 
            smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
            smtpObj.login(mail_user,mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
        except smtplib.SMTPException:
            print ("Error: 无法发送邮件")

sendmail()
cur.close()
db.close()

    




