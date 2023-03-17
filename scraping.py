# ID、PASS、施設（プルダウン（三ツ沢：150、新横浜：570））、日付(idbtn_N)、時間（プルダウン）、コート番号（プルダウン（新横浜57--,新横浜15--））
# 固有番号（施設、コート番号）はソースで保持

import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
load_dotenv()
# 環境変数を参照
USERS = os.getenv('USERS')
usersJson = json.loads(USERS)
driver = webdriver.Chrome()
driver.get('https://yoyaku.city.yokohama.lg.jp/')

places={
    "三ツ沢公園":"150",
    "新横浜公園":"570"
    }

# TODO スプシから取得した配列をjsonに変換
# users =
users = [{"name":"堀澤貴行","place":"新横浜公園","date":"27","time":"19002100","courtNum":"8","yyyymmdd":"20230527","priority":"1"},{"name":"堀澤貴行","place":"新横浜公園","date":"27","time":"19002100","courtNum":"9","yyyymmdd":"20230527","priority":"1"}]

for key, value in usersJson.items():
    texts = driver.find_element(By.XPATH,'//*[@id="main001"]/div[1]/div/div/div/div[1]/input')
    texts.send_keys(value['id'])
    texts = driver.find_element(By.XPATH,'//*[@id="main001"]/div[1]/div/div/div/div[2]/input')
    texts.send_keys(value['pass'])
    # ログイン
    driver.find_element(By.XPATH,'//*[@id="navi_login_r"]/img').click()
    time.sleep(1)
    # 新規抽選を申し込む
    driver.find_element(By.XPATH,'//*[@id="RSGK001_01"]').click()
    time.sleep(1)
    # スポーツ選択
    driver.find_element(By.XPATH,'//*[@id="FRM_RSGK402"]/div[3]/div/div/a[1]').click()
    time.sleep(1)
    # テニスコート選択
    driver.find_element(By.XPATH,'//*[@id="FRM_RSGK403"]/div[3]/div/div/a[4]').click()
    time.sleep(1)
    userInfos = list(filter(lambda user : user['name'] == key, users))
    # print(userInfos)
    for userInfo in userInfos:
        # 施設指定
        driver.find_element(By.XPATH,f'//option[@value="{places[userInfo["place"]]}"]').click()
        time.sleep(1)
        # テニスコート番号選択
        driver.find_element(By.XPATH,f'//*[@id="FRM_RSGK404"]/div[7]/div/div/a[{str(int(userInfo["courtNum"])+1)}]').click()
        time.sleep(1)
        # 日付選択
        driver.find_element(By.ID,f'idbtn_{userInfo["date"]}').click()
        time.sleep(1)
        # 時間とコート選択
        driver.find_element(By.ID,f'idinput_{places[userInfo["place"]].rstrip("0")}{str(int(userInfo["courtNum"])-1).zfill(2)}_{userInfo["yyyymmdd"]}_{userInfo["time"]}').click()
        time.sleep(1)
        # 「申し込む」選択
        driver.find_element(By.XPATH,'//*[@id="FRM_RSGK407"]/div[3]/div/div/div/button//*[@id="idbtn_modoru"]').click()
        time.sleep(1)
        # 「次へ」選択
        driver.find_element(By.XPATH,'//*[@id="footer"]/div/button[2]//*[@id="idbtn_calview"]').click()
        time.sleep(1)
        # 「確定」選択
        driver.find_element(By.XPATH,'//*[@id="idbtn_calview"]').click()
        time.sleep(1)
        # 「申込を続ける」選択
        driver.find_element(By.XPATH,'//*[@id="idbtn_modoru"]').click()
        time.sleep(1)
    # ログアウト
    driver.find_element(By.XPATH,'//*[@id="header"]/div[3]/a/img').click()
    time.sleep(5)
