#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import os
import zipfile
import datetime
import argparse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import ui
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


def parse_command_line_args():
    parser = argparse.ArgumentParser(prog="iij.py", description="""
        get IIJ Service Online graph download as csv and png
        """)
    parser.add_argument('--start_date', type=str, required=True, default=datetime.datetime.today().strftime("%Y/%m/%d"), nargs='?',
                        help="""
        specify a start date of data.
        Style: YYYY/MM/DD
    """)
    parser.add_argument('--end_date', type=str, required=True, default=datetime.datetime.today().strftime("%Y/%m/%d"), nargs='?',
                        help="""
        specify a end date of data.
        Style: YYYY/MM/DD
    """)
    parser.add_argument('--proxy', action='store_true',
                        help="""
        Enable proxy option.
        Attention: you must set proxy.json as proxy infomation
    """)
    return vars(parser.parse_args())


def set_inputfield(inputfield, options):
    inputfield.clear()
    inputfield.send_keys(options)
    time.sleep(0.3)

def set_selectfield(inputfield, options):
    selectfield = Select(inputfield)
    selectfield.select_by_value(options)
    time.sleep(0.3)

def click_btn(inputbtn):
    inputbtn.click()
    time.sleep(1)

def get_manifest_json():
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    return manifest_json

def get_background_js(proxyinfo):
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };
    
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxyinfo['PROXY_HOST'], proxyinfo['PROXY_PORT'], proxyinfo['PROXY_USER'], proxyinfo['PROXY_PASS'])
    
    return background_js

class ChromeBrowswer:
    def __init__(self, proxyinfo):
        # Chromeオプション
        options = Options()
        #options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1024,768')

        self.proxyenable = proxyinfo['PROXY_ENABLE']
        if self.proxyenable:
            self.proxyhost = proxyinfo['PROXY_HOST']
            self.proxyport = proxyinfo['PROXY_PORT']
            self.proxyuser = proxyinfo['PROXY_USER']
            self.proxypass = proxyinfo['PROXY_PASS']

            # Chrome用のproxyプロファイルの作成
            self.proxyprofile = 'proxy_auth_plugin.zip'
            with zipfile.ZipFile(self.proxyprofile, 'w') as zp:
                zp.writestr( "manifest.json", get_manifest_json() )
                zp.writestr( "background.js", get_background_js(proxyinfo) )
                options.add_extension(self.proxyprofile)

        self.driver = webdriver.Chrome(options=options)
 
    def login(self, logininfo):
        self.baseurl = logininfo['baseurl']
        self.username = logininfo['username']
        self.userpass = logininfo['userpass']

        self.driver.get(self.baseurl)
        # ユーザ入力
        set_inputfield(self.driver.find_element_by_xpath( '/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table[3]/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr[1]/td[2]/input' ), self.username)
        # パスワード入力
        set_inputfield(self.driver.find_element_by_xpath( '/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table[3]/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr[2]/td[2]/input' ), self.userpass)
        # ログインボタンクリック
        click_btn(self.driver.find_element_by_xpath( '/html/body/table/tbody/tr/td/table/tbody/tr[2]/td/table[3]/tbody/tr/td[2]/table/tbody/tr/td/input[1]' ))
        time.sleep(3)

    def drow_graph(self, servicecode, customercode):
        # [設定と管理 > サービスの設定と管理 > インターネット接続サービス]
        self.driver.get( self.baseurl + "admin/service/setting/ip/index.cfm?serviceIdList=IIJ.IP" )
        time.sleep(1)

        # [各サービス画面]
        self.driver.get( self.baseurl + "admin/service/setting/ip/index.cfm?mode=jump_menu&serviceIdList=IIJ.IP&serviceId=IIJ%2EIP&serviceCode=" + servicecode + "&customerCode=" + customercode )
        time.sleep(1)

        # [トラフィックグラフ]
        self.driver.get( self.driver.find_element_by_xpath( "/html/body/div[2]/table[1]/tbody/tr[1]/td/table/tbody/tr/td[2]/a" ).get_attribute("href") )
        time.sleep(1)
        
    def change_graph_options(self, startdate, enddate):
        graphoptions = {}
        graphoptions['fromYear'] = startdate.split("/")[0]
        graphoptions['fromMonth'] = str(int(startdate.split("/")[1]))
        graphoptions['fromDay'] = str(int(startdate.split("/")[2]))                
        graphoptions['toYear'] = enddate.split("/")[0]
        graphoptions['toMonth'] = str(int(enddate.split("/")[1]))
        graphoptions['toDay'] = str(int(enddate.split("/")[2]))

        # 開始年
        set_selectfield(self.driver.find_element_by_xpath( "/html/body/form/div/table[4]/tbody/tr/td/select[1]" ), graphoptions['fromYear'])
        # 開始月
        set_selectfield(self.driver.find_element_by_xpath( "/html/body/form/div/table[4]/tbody/tr/td/select[2]" ), graphoptions['fromMonth'])
        # 開始日
        set_selectfield(self.driver.find_element_by_xpath( '/html/body/form/div/table[4]/tbody/tr/td/select[3]' ), graphoptions['fromDay'])
        # 開始年
        set_selectfield(self.driver.find_element_by_xpath( '/html/body/form/div/table[4]/tbody/tr/td/select[4]' ), graphoptions['toYear'])
        # 開始月
        set_selectfield(self.driver.find_element_by_xpath( '/html/body/form/div/table[4]/tbody/tr/td/select[5]' ), graphoptions['toMonth'])
        # 開始日
        set_selectfield(self.driver.find_element_by_xpath( '/html/body/form/div/table[4]/tbody/tr/td/select[6]' ), graphoptions['toDay'])
        # 更新
        click_btn(self.driver.find_element_by_xpath( "/html/body/form/div/table[4]/tbody/tr/td/input[2]" ))

    def download_graph(self, filename):
        url = self.driver.find_element_by_xpath( "/html/body/form/div/img" ).get_attribute("src")

        # セッションCookieのコピー
        # Chrome WebDriverでグラフにアクセスし、help-igate.iij.ad.jpにアクセスする際に必要なセッションCookieをrequestsに設定
        self.driver.get(url)
        session = requests.session()        
        jar = requests.cookies.RequestsCookieJar()
        for cookie in self.driver.get_cookies():
            jar.set(cookie["name"], cookie["value"], domain=cookie["domain"], path=cookie["path"], secure=cookie["secure"])
        
        # グラフのダウンロード
        # requestsでアクセスし、responseのデータをバイナリ形式で保存
        if self.proxyenable:
            proxy_dict = {
                "http": "http://%s:%s@%s:%s/" % (self.proxyuser, self.proxypass, self.proxyhost, self.proxyport),
                "https": "http://%s:%s@%s:%s/" % (self.proxyuser, self.proxypass, self.proxyhost, self.proxyport)
            }
            response = session.get(url, cookies=jar, proxies=proxy_dict)
        else:
            response = session.get(url, cookies=jar)

        file_path = os.path.dirname(filename)
        if not os.path.exists(file_path):
          os.makedirs(file_path)

        # PNGダウンロード
        with open(filename, 'wb') as f:
           f.write(bytes(response.content))

        self.driver.back()

    def download_csv(self, filename):
        url = self.driver.find_element_by_xpath( "/html/body/form/div/img" ).get_attribute("src")
        self.driver.get(url)

        url = url + "&csv=1"

        js = """
        var getBinaryResourceText = function(url) {
            var req = new XMLHttpRequest();
            req.open('GET', url, false);
            req.overrideMimeType('text/plain; charset=x-user-defined');
            req.send(null);
            if (req.status != 200) return '';

            var filestream = req.responseText;
            var bytes = [];
            for (var i = 0; i < filestream.length; i++){
                bytes[i] = filestream.charCodeAt(i) & 0xff;
            }

            return bytes;
        }
        """
        js += "return getBinaryResourceText(\"{url}\");".format(url=url)
        data_bytes = self.driver.execute_script( js )

        file_path = os.path.dirname(filename)
        if not os.path.exists(file_path):
          os.makedirs(file_path)

        # PNGダウンロード
        with open(filename, 'wb') as f:
           f.write(bytes(data_bytes))
        
        compFile = zipfile.ZipFile( filename.replace(".csv", ".zip"), 'w', zipfile.ZIP_DEFLATED )
        compFile.write( filename )
        compFile.close()
        os.remove( filename )

        self.driver.back()

    def close(self):
        self.driver.quit()
        if self.proxyenable:
            os.remove( self.proxyprofile )


if __name__ == "__main__":
    # 変数定義
    parse_args = parse_command_line_args()
    start_date = parse_args['start_date']
    end_date = parse_args['end_date']

    # システム情報/ユーザ情報読み込み
    logininfo = json.load(open("settings/login.json", "r", encoding='utf-8'))
    nodeinfo  = json.load(open("settings/node.json", "r", encoding='utf-8'))
 
    # proxy情報読み込み
    proxyinfo = {}
    proxyinfo['PROXY_ENABLE'] = False
    if parse_args['proxy']:
        proxyinfo = json.load(open("settings/proxy.json", "r"))
        proxyinfo['PROXY_ENABLE'] = True

    # ブラウザ開始
    cb = ChromeBrowswer( proxyinfo )

    # サイトログイン
    cb.login( logininfo )

    for nodeinfo in nodeinfo["nodelist"]:
        if start_date == end_date:
            pngfile = start_date.replace("/", "") + "_" + nodeinfo["servicecode"] + ".png"
            csvfile = start_date.replace("/", "") + "_" + nodeinfo["servicecode"] + ".csv"
        else:
            pngfile = start_date.replace("/", "") + "-" + end_date.replace("/", "") + "_" + nodeinfo["servicecode"] + ".png"
            csvfile = start_date.replace("/", "") + "-" + end_date.replace("/", "") + "_" + nodeinfo["servicecode"] + ".csv"

        # グラフを表示
        cb.drow_graph( nodeinfo["servicecode"], nodeinfo["customercode"] )
        # グラフ条件の変更
        cb.change_graph_options( start_date, end_date )
        # グラフ保存
        cb.download_graph( "./outputs/" + pngfile )
        # グラフ元データ保存
        cb.download_csv( "./outputs/CSV/" + csvfile ) 

    # ブラウザ終了
    cb.close()
