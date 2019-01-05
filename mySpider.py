#!/usr/bin/python
#coding=utf-8
import urllib
from urllib import parse
from urllib import request
import requests
from bs4 import BeautifulSoup
import re
import time
from translate import baidu_translate
import pandas as pd
import numpy as np

global rank
global num

url = 'http://www.medsci.cn/sci/index.do?action=search'

headers = {
    'POST':url,
    'Host':'www.medsci.cn',
    'Origin':'http://www.medsci.cn',
    "Referer":"http://www.medsci.cn/sci",
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36",
}
value = {
    "fullname": "0920-5691",
    "bigclass": "null",
    "smallclass": 'null',
    "impact_factor_b": "",
    "impact_factor_s": "",
    "rank": "number_rank_b",
    "Submit": "我要查询"
}

"""
根据ISSN号码进行查询
参数:ISSN字符串,形如"0920-5691"
返回值:html,已经编译成UTF8
"""
def getData(ISSN):
    value["fullname"] = ISSN
    data = urllib.parse.urlencode(value).encode(encoding='UTF8')
    req = request.Request(url, data)
    for key in headers:
        req.add_header(key, headers[key])
    response = request.urlopen(req)
    html = response.read()
    data2 = html.decode('utf-8')
    return data2

"""
获取重定向之后的真实地址
url:原地址
返回:重定向之后的URL
"""
def get_real_url(url,try_count = 1):
    http_headers = { 'Accept': '*/*','Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'}
    if try_count > 3:
        return url
    try:
        rs = requests.get(url,headers=http_headers,timeout=10)
        if rs.status_code > 400:
            return get_real_url(url,try_count+1)
        return rs.url
    except:
        return get_real_url(url, try_count + 1)

"""
获取期刊的主页
输入:url,从查询页读取得到,形如:journal.do?id=f7ff1846
输出:字符串,期刊主页链接
"""
def getHomePage(jid):
    medscihome="http://www.medsci.cn/sci/"
    #           http://www.medsci.cn/sci/url.do?id=f7ff1846&q=w
    queryurl=medscihome+"url.do?"+jid+"&q=w"
    
    realurl=get_real_url(queryurl)

    return realurl

"""
数据分检
输入:字符串形式的html
输出:全名,年文章数,投稿难易,一审周期,主页链接
"""
def parseHtml(HtmlStr):
    FullName="空"
    NumOfPapers="空"
    EasyOrHard="空"
    ReviewTime="空"
    HomePage="空"
    try:
        html =BeautifulSoup(HtmlStr,"html5lib")
        FullName    = html.findAll('p',{'class':{'f_c_999 tac_l'}})[0].string.replace("space","").replace("\n","").replace("\t","")  # 全名
        NumOfPapers = html.findAll('td',{'data-title':{'年文章'}})[0].string.replace("space","").replace("\n","").replace("\t","")  # 年文章数
        EasyOrHard  = html.findAll('td',{'data-title':{'投稿难易'}})[0].string.replace("space","").replace("\n","").replace("\t","")  # 投稿难易
        ReviewTime  = html.findAll('td',{'data-title':{'一审周期'}})[0].string.replace("space","").replace("\n","").replace("\t","") # 一审周期
        # 找主页链接http://www.medsci.cn/sci/journal.do?id=f7ff1846
        #          http://www.medsci.cn/sci/url.do?id=f7ff1846&q=w
        home="http://www.medsci.cn/sci/"
        zzr=html.find('td',{'data-title':{'主页'}}).children # 主页url
        href1=""
        for child in zzr:
            href1=child.get("href") #journal.do?id=f7ff1846
        begin=href1.find('id=')
        jid=href1[begin:]
        HomePage=getHomePage(jid)
    except Exception as e:
        print(e)
        print("出错")
    return FullName,NumOfPapers,EasyOrHard,ReviewTime,HomePage

"""
测试函数
"""
def test(issn):
    HtmlStr=getData(str(issn))
    enFullName,NumOfPapers,EasyOrHard,ReviewTime,HomePage=parseHtml(HtmlStr)
    zhFullName=baidu_translate(enFullName)
    print(enFullName,zhFullName,NumOfPapers,EasyOrHard,ReviewTime,HomePage)

"""
工作函数
"""
def job():
    ISSNs = pd.read_csv('./issn.csv')
    dataList=[]
    index=0
    files=0
    names=['ISSN','全名','中文全名','年文章量','投稿难易度','初审周期','主页']
    resFile=pd.DataFrame(columns=names,data=dataList)
    resFile.to_csv("./res.csv",mode='a+',index=False)
    for issn in ISSNs['issn']:
        HtmlStr=getData(issn)
        enFullName,NumOfPapers,EasyOrHard,ReviewTime,HomePage=parseHtml(HtmlStr)
        zhFullName=baidu_translate(enFullName)
        #print(issn,enFullName,zhFullName,NumOfPapers,EasyOrHard,ReviewTime,HomePage)
        dataList.append([issn,enFullName,zhFullName,NumOfPapers,EasyOrHard,ReviewTime,HomePage])
        print('第{}条处理完毕,ISSN={}'.format(index,issn))
        index=index+1
        if index % 30 == 0:
            resFile=pd.DataFrame(data=dataList)
            resFile.to_csv("./res.csv",mode='a+',header=False, index=False)
            dataList=[]
            print("第{}次保存".format(files))
            files=files+1
    if len(dataList)!=0:
        resFile=pd.DataFrame(data=dataList)
        resFile.to_csv("./res.csv",mode='a+',header=False, index=False)
        print("剩余数据保存完毕")
    print("全部处理完毕")

"""
入口
"""  
if __name__ == "__main__":
    #job()  # 工作
    test("2168-7161")  # 测试