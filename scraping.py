# ID、PASS、施設（プルダウン（三ツ沢：150、新横浜：570））、日付(idbtn_N)、時間（プルダウン）、コート番号（プルダウン（新横浜57--,新横浜15--））
# 固有番号（施設、コート番号）はソースで保持

# TODO スクショ（メニュー＞抽選申込確認）（グーグルドライブ上に配置）
# TODO スクショをラインに送る

import gspread
import time
import datetime
import requests
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.chrome.options import Options  # オプションを使うために必要

places = {"三ツ沢公園": "150", "新横浜公園": "570"}
today = datetime.date.today()
dayAfter2Month = today + relativedelta(months=2)
dayAfter2MonthYyyyMm = dayAfter2Month.strftime("%Y%m")  # yyyymm
# スプレッドシート操作の準備
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "auto-lottery-987e274706c6.json", scope
)
gc = gspread.authorize(credentials)
# IDPASSシート
SPREADSHEET_KEY_IDPASS = "1B736lqLfQXfU6HXVdSgp9Yb7wLREu6nGjzhSxgLvTgA"
SPREADSHEET_KEY_LOTTERY_DETAIL_YOKOHAMA = "1wEXQLe4tBDwzpKBlqtdjIOPvesEo35M0rYqxTrePMu8"
worksheetIdPass = gc.open_by_key(SPREADSHEET_KEY_IDPASS).worksheet("ユーザー")
# 日付可変（抽選_yyyymm + 2ヵ月後）
worksheetLottoryDetailYokohama = gc.open_by_key(
    SPREADSHEET_KEY_LOTTERY_DETAIL_YOKOHAMA
).worksheet(f"抽選_{dayAfter2MonthYyyyMm}")
usersData = worksheetIdPass.get_all_records(empty2zero=False, head=1, default_blank="")
lottoryData = worksheetLottoryDetailYokohama.get_all_records(
    empty2zero=False, head=1, default_blank=""
)
# print(f"usersData---------------------{usersData}")
# print(f"lottoryData---------------------{lottoryData}")

option = Options()  # オプションを用意
option.add_argument("--incognito")  # シークレットモードの設定を付与
driver = webdriver.Chrome(options=option)
driver.get("https://yoyaku.city.yokohama.lg.jp/")


def applicationYokohama():
    # ユニークなnameのリストを作成（抽選データ保有ユーザーのみ）
    targetUsers = {}
    for data in lottoryData:
        if data["name"] not in targetUsers:
            idPass = {}
            tmp = [user for user in usersData if user["name"] == data["name"]]
            idPass["id"] = tmp[0]["id"]
            idPass["pass"] = tmp[0]["pass"]
            # print(f"idPass---------------------{idPass}")
            targetUsers[data["name"]] = idPass
    # print(f"targetUsers---------------------{targetUsers}")

    for key, value in targetUsers.items():
        # print(f"key---------------------{key}")
        # print(f"value---------------------{value}")
        texts = driver.find_element(
            By.XPATH, '//*[@id="main001"]/div[1]/div/div/div/div[1]/input'
        )
        texts.send_keys(value["id"])
        texts = driver.find_element(
            By.XPATH, '//*[@id="main001"]/div[1]/div/div/div/div[2]/input'
        )
        texts.send_keys(value["pass"])
        # ログイン
        driver.find_element(By.XPATH, '//*[@id="navi_login_r"]/img').click()
        time.sleep(1)
        # 新規抽選を申し込む
        driver.find_element(By.XPATH, '//*[@id="RSGK001_01"]').click()
        time.sleep(1)
        # スポーツ選択
        driver.find_element(
            By.XPATH, '//*[@id="FRM_RSGK402"]/div[3]/div/div/a[1]'
        ).click()
        time.sleep(1)
        # テニスコート選択
        driver.find_element(
            By.XPATH, '//*[@id="FRM_RSGK403"]/div[3]/div/div/a[4]'
        ).click()
        time.sleep(1)
        # userInfos = list(filter(lambda user: user["name"] == key, lottoryData))
        # for userInfo in userInfos:
        #     # 施設指定
        #     driver.find_element(
        #         By.XPATH, f'//option[@value="{places[userInfo["place"]]}"]'
        #     ).click()
        #     time.sleep(1)
        #     # テニスコート番号選択
        #     driver.find_element(
        #         By.XPATH,
        #         f'//*[@id="FRM_RSGK404"]/div[7]/div/div/a[{str(int(userInfo["court_no"])+1)}]',
        #     ).click()
        #     time.sleep(1)
        #     # 日付選択
        #     driver.find_element(By.ID, f'idbtn_{userInfo["day"]}').click()
        #     time.sleep(1)
        #     # 時間とコート選択
        #     driver.find_element(
        #         By.ID,
        #         f'idinput_{places[userInfo["place"]].rstrip("0")}{str(int(userInfo["court_no"])-1).zfill(2)}_{userInfo["date"]}_{userInfo["time"]}',
        #     ).click()
        #     time.sleep(1)
        #     # 「申し込む」選択
        #     driver.find_element(
        #         By.XPATH,
        #         '//*[@id="FRM_RSGK407"]/div[3]/div/div/div/button//*[@id="idbtn_modoru"]',
        #     ).click()
        #     time.sleep(1)
        #     # 「次へ」選択
        #     driver.find_element(
        #         By.XPATH, '//*[@id="footer"]/div/button[2]//*[@id="idbtn_calview"]'
        #     ).click()
        #     time.sleep(1)
        #     # 「確定」選択
        #     driver.find_element(By.XPATH, '//*[@id="idbtn_calview"]').click()
        #     time.sleep(1)
        #     # 「申込を続ける」選択
        #     driver.find_element(By.XPATH, '//*[@id="idbtn_modoru"]').click()
        #     time.sleep(1)
        # 「メニューへ」選択
        driver.find_element(By.XPATH, '//*[@id="home_btn"]/a/img').click()
        time.sleep(1)
        # 「抽選申込・確認」選択
        driver.find_element(By.XPATH, '//*[@id="RSGK001_02"]').click()
        time.sleep(1)
        # スクショ
        driver.execute_script("document.body.style.zoom='80%'")  # スクショ用に画面を縮小
        scleenShot = driver.get_screenshot_as_png()
        driver.save_screenshot(f"{key}.png")
        driver.execute_script("document.body.style.zoom='100%'")
        # # スクショ保存用のディレクトリ作成
        # gauth = GoogleAuth()
        # # TODO ドライブアクセスするのに認証情報必要？
        # # https://dev.classmethod.jp/articles/oauth2client-is-deprecated/
        # gauth.LocalWebserverAuth()
        # drive = GoogleDrive(gauth)
        # folder_id = "1hckWWf_S64gB7oQ8MUaYM9QKjzNVPdwY"
        # # TODO ドライブのフォルダ名取得
        # # TODO ドライブに当月フォルダない場合は作成
        # f_folder = drive.CreateFile(
        #     {
        #         "title": dayAfter2MonthYyyyMm,
        #         "mimeType": "application/vnd.google-apps.folder",
        #         "parents": [
        #             {
        #                 "id": folder_id,
        #                 "kind": "drive#fileLink",
        #             }
        #         ],
        #     }
        # )
        # f_folder.Upload()
        # # Googleドライブに保存
        # file_metadata = {
        #     "title": f"{key}.png",
        #     "mimeType": "application/vnd.google-apps.folder",
        #     "parents": [
        #         {
        #             "id": folder_id,
        #             "kind": "drive#fileLink",
        #         }
        #     ],
        # }
        # f = drive.CreateFile(file_metadata)
        # f.SetContentFile(scleenShot)
        # f.Upload(param={"supportsTeamDrives": True})
        # ログアウト
        driver.find_element(By.XPATH, '//*[@id="header"]/div[3]/a/img').click()
        time.sleep(1)
        # TODO LINEにスクショ送信
        # LineNotify 連携用トークン・キー準備
        line_notify_token = "rC4NpRtelGBGi9I1A7wTvq47lz0qGQ32jh2giIyi8Po"
        line_notify_api = "https://notify-api.line.me/api/notify"
        # httpヘッダー設定
        headers = {"Authorization": f"Bearer {line_notify_token}"}
        # トーク送信メッセージ設定
        payload = {"message": "抽選"}
        # 送信画像設定
        files = {"imageFile": open(f"{key}.png", "rb")}  # バイナリファイルオープン
        # post実行
        requests.post(line_notify_api, data=payload, headers=headers, files=files)


applicationYokohama()
