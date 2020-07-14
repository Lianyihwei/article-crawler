from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os
from datetime import date
import pymysql.cursors
import urllib.request
from datetime import date
today = str(date.today())

connection = pymysql.connect(host='localhost',
                             user='user',
                             password='password',
                             db="new_media",
                             cursorclass=pymysql.cursors.DictCursor)

options = Options()
options.add_argument('--headless')
options.experimental_options["prefs"] = {"profile.default_content_settings": {"images": 2},
                                        "profile.managed_default_content_settings": {"images":2}}

driver = webdriver.Chrome("/Users/lianyihwei/Applications/webDrive/chromedriver", chrome_options=options)

try:
    with connection.cursor() as cursor:
        for i in range(1,2):
# --------Inside--------
#             time.sleep(2)
            driver.get('https://www.inside.com.tw/?page='+str(i))
            soup = BeautifulSoup(driver.page_source)
            article_box = soup.select("div.post_list-list_style")[0]
            articles = article_box.select("div.post_list_item")
            for article in articles:
                title = article.select("h3.post_title")[0].text
                date = article.select("li.post_date")[0].text.strip().replace("/","-")
                tags = article.select("a.hero_slide_tag")
                tags_string = ""
                for tag in tags:
                    tags_string += "#"+tag.text+" "
                if today == date: 
                    print(title)
                    print(date)
                    print(tags_string)
                    
                    sql = '''
                    INSERT INTO `new_media`.`articles`(`title`,`date`,`tags`,`brand`)
                    VALUE("{}","{}","{}","{}")
                    '''.format(title,date,tags_string,"inside")
                    cursor.execute(sql)
                    connection.commit()
# --------TechNews--------
#             time.sleep(2)
            driver.get('https://technews.tw/page/'+ str(i)+ '/')
            soup = BeautifulSoup(driver.page_source)
            article_box = soup.select("div#content")[0]
            articles = article_box.select("header.entry-header")
            for article in articles:
                title = article.select("h1.entry-title")[0].text
                date = article.select("span.body")[1].text.strip().replace(" 年 ","-").replace(" 月 ","-").replace(" 日 ","-")
                tags = article.select("span.body")[2].select("a")
                iframe = article.select("iframe")[1]
                response = urllib.request.urlopen(iframe.attrs["src"])
                iframe_soup = BeautifulSoup(response)
                share = iframe_soup.select("span#u_0_2")[0].text
                tags_string = ""
                for tag in tags:
                    tags_string += "#"+tag.text+" "
                if today == date[0:10]:
                    print(title)
                    print(date)
                    print(tags_string)
                    print(share)
                    

                    sql = '''
                    INSERT INTO `new_media`.`articles`(`title`,`date`,`tags`,`share`,`brand`)
                    VALUE("{}","{}","{}","{}","{}")
                    '''.format(title,date,tags_string,share,"technews")
                    cursor.execute(sql)
                    connection.commit()            
# --------TechOrange--------
        driver.get("https://buzzorange.com/techorange/")
        for i in range(1,2):
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(2)
        soup = BeautifulSoup(driver.page_source)
        article_box = soup.select("main#main")[0]
        articles = article_box.select("article")
        for article in articles:
            title = article.select("h4.entry-title")[0].text
            date = article.select("time.entry-date")[0].text.strip().replace("/","-")
            share = article.select("span.shareCount")[0].text.split(" ")[0]
            if share.find("K") != -1:
                share = float(share) * 1000
            else:
                share = article.select("span.shareCount")[0].text.split(" ")[0]
            if today == date:
                print(title)
                print(date)
                print(share)

                sql = '''
                INSERT INTO `new_media`.`articles`(`title`,`date`,`share`,`brand`)
                VALUE("{}","{}","{}","{}")
                '''.format(title,date,share,"techorange")
                cursor.execute(sql)
                connection.commit()


    connection.close()
    driver.close()
except Exception as e:
    print(e)
    driver.close()