#!/usr/bin/python
# coding:utf-8

import cfscrape
import requests
import re
import random
import chardet
from time import sleep
import subprocess
# from selenium import webdriver

class YifileSite:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        # urls
        self.urlLogin = "https://www.yifile.com/account.php?action=login"
        self.urlAccount = "https://www.yifile.com/account.php"
        self.urlCode = "https://www.yifile.com/loginid.php?id=3"

        # set session
        self.session = requests.session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        self.scraper = cfscrape.create_scraper(delay=10, sess=self.session)
        self.referer = "https://www.yifile.com/"

    def _decode(self,content):
        encode_type = chardet.detect(content)  
        return content.decode(encode_type['encoding'])

    def _checkLogin(self, content):
        pattern = re.compile(r'您已登录')
        regResult = pattern.findall(self._decode(content))
        if len(regResult) > 0:
            return True
        else:
            return False

    def _curl(self, url, referer):
        user_agent = self._choieUa()
        if len(referer) == 0 :
            referer = self.referer

        cookie_arg, a = cfscrape.get_cookie_string(url)
        cmd = "curl --referer '{referer}' --cookie '{cookie_arg}' -A '{user_agent}' '{url}'"

        loginContent = None
        try:
            loginContent = subprocess.check_output(cmd.format(referer = referer, cookie_arg=cookie_arg, user_agent=user_agent, url=url), shell=True)
        except subprocess.CalledProcessError as e:
            loginContent = None
            
        return loginContent, cookie_arg


    def login(self):
        # browser = webdriver.PhantomJS()
        # browser.get(self.urlLogin)
        # sleep(7)    #这里注意需要睡眠5s以上，因为检测页面需要5s左右的时间通过，通过后才能获得真正的网页。
        # print(browser.page_source)

        homePage, cookie_arg = self._curl("https://www.yifile.com/", "")
        
        cookies = dict(cookie=cookie_arg)
        #self.scraper.cookies = cookies

        loginContent = self.scraper.get(self.urlLogin, cookies=cookies).content
        
        #print(loginContent)

        # 检查是否登录
        if self._checkLogin(loginContent):
            return True

        # 登录前获取 formhash
        pattern = re.compile(r'name="formhash" value="(\w+)"')
        getformhash = pattern.findall(self._decode(loginContent))

        if len(getformhash) > 0:
            formhash = getformhash[0]
        else:
            formhash = ""
            print ('get formhash faild')

        print("get formhash", formhash)

        # 开始 login
        loginData = {
            'action': 'login',
            'task': 'login',
            'ref': 'https://www.yifile.com/',
            'formhash': formhash,
            'username': self.username,
            'password': self.password,
            'remember': '1'
        }

        account = self.scraper.post(self.urlAccount, loginData)

        #print(account.content)

        # 检查是否登录成功
        # check login status
        pattern = re.compile(r'登录成功')
        acontent = pattern.findall(self._decode(account.content))

        print("登录[post]", acontent)

        if len(acontent) > 0:
            loginStatus = acontent[0]
        else :
            loginStatus = "登录失败"

        if loginStatus == '登录成功':
            return True
        else:
            return False

    # 获取验证码
    def getCode(self):
        headers = {'referer': 'https://www.yifile.com/file/XIfxdXPGmw7Vih8T6mq4.html'}
        content = self.scraper.get("https://www.yifile.com/includes/imgcode.inc.php?verycode_type=2", headers=headers).content
        return content

    # 获取下载地址
    def _getDownloadUrl(self, url):
        downloadPage = self.scraper.get(url)
        pattern = re.compile(r'<a onclick="setCookie\(\);" href="(.*)" id')

        content = downloadPage.content

        print(content)

        reResult = pattern.findall(self._decode(content))

        pattern2 = re.compile(r'解冻')
        reResult2 = pattern2.findall(self._decode(content))
        if len(reResult2) > 0:
             print ('down:需要解冻!!!!!!')

        return reResult
    
    # need解冻
    def checkJedong(self):
        downloadPage = self.scraper.get("https://www.yifile.com/mydisk.php?item=profile&&menu=cp")
        pattern = re.compile(r'解冻')
        reResult = pattern.findall(self._decode(downloadPage.content))

        if len(reResult) > 0:
            auth = ""              
            for i in range(0,4):
                current_code = random.randint(0,9)
                auth += str(current_code)

            requests.get('https://sc.ftqq.com/SCU9426Tf8c93224ef853531d39171ed2ee44dda594b812d41eff.send?text=网盘下载助手&desp=需要解冻, 主人需要解冻~ ' + auth )
            print ('check:需要解冻!')
            self.scraper.get("https://www.yifile.com/loginid.php?id=1")
            return True
        else:
            return False

    # send解冻
    def sendJedong(self):
        self.scraper.get("https://www.yifile.com/loginid.php?id=1")
        print ('发送解冻邮件')
        return "发送解冻邮件成功"

    # 解冻
    def doJedong(self, url):
        headers = {'referer': 'https://www.yifile.com/loginid.php'}
        self.scraper.get(url, headers=headers)
        print ('解冻')


    def download(self, url, code):
        referer = url
        print("请求下载信息", url, code)
        
        urls = self._getDownloadUrl(url)

        if len(urls) > 0:
            # 获取地址
            print ('step:获取地址成功', urls)
            return self._makeurls(referer, urls)
        else:
            # 校验验证码
            postData = {
                'id': '1061937',
                'verycode': code
            }
            codePage = self.scraper.post(self.urlCode, postData)

            if "true" not in self._decode(codePage.content):
                urls = self._getDownloadUrl(url)
                if len(urls) > 0:
                     # 获取地址
                    
                    print ('再次获取地址成功', urls)
                    return self._makeurls(referer, urls)
            else:
                print ('验证码错误')
                return []

    def _makeurls(self, referer, urls):
        urlssss = []
        if len(urls) > 0:
            for url in urls:
                urlssss.append({
                    "url" : url,
                    "referer" : referer,
                })
        return urlssss   


    def _choieUa(self):
        user_agent_list = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
            "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        ]
        return random.choice(user_agent_list)

        