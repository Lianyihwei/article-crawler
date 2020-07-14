from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import traceback
import pymysql.cursors
from dotenv import load_dotenv
load_dotenv()

connection = pymysql.connect(host='localhost',
                             user='user',
                             password='password',
                             db="new_media",
                             cursorclass=pymysql.cursors.DictCursor)

options = Options()
options.add_argument("--disable-notifications")
options.experimental_options["prefs"] = {"profile.default_content_settings": {"images": 2},
                                        "profile.managed_default_content_settings": {"images":2}}

driver = webdriver.Chrome("/Users/lianyihwei/Applications/webDrive/chromedriver", chrome_options=options)

try:
    with connection.cursor() as cursor:
        driver.get('https://www.facebook.com')
        time.sleep(1)
        username = driver.find_elements_by_css_selector("input[name=email]")[0]
        password = driver.find_elements_by_css_selector("input[name=pass]")[0]
        username.send_keys(os.getenv("EMAIL"))
        password.send_keys(os.getenv("PASSWORD"))
        time.sleep(2)
        login_button = driver.find_elements_by_css_selector("input[type=submit]")[0]
        login_button.click()
        time.sleep(2)
        
        driver.get("https://www.facebook.com/ericsteakshop")
        for i in range(1,4):
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(2)
        
        check = True
        while check:
# -------點選打開更多留言-------
            show_more_comments = driver.find_elements_by_css_selector("a._4sxc._42ft")
            for show_more_comment in show_more_comments:
                ActionChains(driver).move_to_element(show_more_comment).perform()
                show_more_comment.click()
# -------點選打開留言中更多內容-------
            show_more_cotents = driver.find_elements_by_css_selector("a._5v47.fss")
            for show_more_cotent in show_more_cotents:
                ActionChains(driver).move_to_element(show_more_cotent).perform()
                show_more_cotent.click()
            
            time.sleep(2)
            print("open reply")
            
            if (len(show_more_comments) == 0 and len(show_more_cotents) == 0):
                check = False

# -------抓取貼文內容-------
        
        soup = BeautifulSoup(driver.page_source)
        article_box = soup.select("div._1xnd")[1]
        articles = article_box.select("div._5pcr.userContentWrapper")
        for article in articles:
            
            date = content = promotion_date = ""
            attach = interactive = promotion_attach = promotion_interactive = replied_count = shared_count = good = 0
            
            utime = article.select("abbr._5ptz")[0]["data-utime"]
            date = datetime.fromtimestamp(int(utime))
            print("date: "+str(date))
            
            content = ""
            if(len(article.select("div.text_exposed_root")) == 0):
                show_contents = article.select("div.userContent > p")
                for show_content in show_contents:
                    content = content + show_contents.text + "。"
            else:
                show_contents = article.select("div.text_exposed_root > p")
                hide_contents = article.select("div.text_exposed_show > p")
                for show_content in show_contents:
                    content = content + show_content.text +"。"
                for hide_content in hide_contents:
                    content = content +hide_content.text +"。"
            print("Content: " + content)
            
# -------抓取廣告數據 attach觸及人數 interactive互動人數 
            if(len(article.select("tr._51mx")) > 0):
                attach = article.select("td._51m-.vMid.hLeft span")[0].text.replace(",","")
                interactive = article.select("td._51mw._51m-.vMid.hLeft span")[0].text.replace(",","")
                print("觸及人數: " + attach)
                print("互動人數: " + interactive)
# -------promotion加強推廣日期、觸及與互動人數-------
                if(len(article.select("div._6r-l div._one.lfloat div")) > 0):
                    promotion_string = article.select("div._6r-l div._one.lfloat div")[0].text
                    promotion_date = promotion_string.split(":")[1]
                    promotion_attach = article.select("div._6r-n")[0].text.replace(",","")
                    promotion_interactive = article.select("div._6r-n")[1].text.replace(",","")
                    print("promotion_date: " + promotion_date)
                    print("promotion_attach: " + promotion_attach)
                    print("promotion_interactive: " + promotion_interactive)
# -------按讚、留言、分享數-------
            good = article.select("span._81hb")[0].text.replace(",","")
            relpied_elements = article.select("span._1whp._4vn2")
            shared_elements = article.select("span._355t._4vn2")
            print("按讚數： "+good)
            if(len(relpied_elements) > 0):
                replied_count = relpied_elements[0].text.split("則")[0].replace(",","")
                print("留言數： "+replied_count)
            if(len(shared_elements) > 0):
                shared_count = shared_elements[0].text.split("次")[0].replace(",","")
                print("分享數： "+shared_count)
            
            sql = '''SELECT * FROM fb_social_data.posts WHERE date = "{}"
                '''.format(date)
            cursor.execute(sql)
            posts = cursor.fetchall()
            
            if(len(posts) > 0):
                sql = '''UPDATE `fb_social_data`.`posts` SET 
                        date = "{}",
                        content = "{}",
                        attach = "{}",
                        interactive = "{}",
                        promotion_date = "{}",
                        promotion_attach = "{}",
                        promotion_interactive = "{}",
                        replied_count = "{}",
                        shared_count = "{}",
                        good = "{}" WHERE (date = "{}")'''.format(
                date,content,attach,interactive,promotion_date,promotion_attach,promotion_interactive,
                replied_count,shared_count,good,date)
                
            else:
                sql = '''INSERT INTO fb_social_data.posts(date,content,attach,interactive,promotion_date,promotion_attach,
                        promotion_interactive,replied_count,shared_count,good) 
                        VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'''.format(
                date,content,attach,interactive,promotion_date,promotion_attach,promotion_interactive,
                replied_count,shared_count,good)

            cursor.execute(sql)
            connection.commit()
                    
    connection.close()
    driver.close()
except Exception:
    print(traceback.format_exc())
    connection.close()
    driver.close()