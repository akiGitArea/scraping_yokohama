# ID、PASS、施設（プルダウン（三ツ沢：150、新横浜：570））、日付(idbtn_N)、時間（プルダウン）、コート番号（プルダウン（新横浜57--,新横浜15--））
# 固有番号（施設、コート番号）はソースで保持

# TODO スクショ（メニュー＞抽選申込確認）（グーグルドライブ上に配置）
# TODO スクショをラインに送る

import gspread
import time
import datetime

# import requests
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By

# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
from googleapiclient.discovery import build

# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.chrome.options import Options  # オプションを使うために必要
from apiclient.http import MediaFileUpload

places = {"三ツ沢公園": "150", "新横浜公園": "570"}
today = datetime.date.today()
dayAfter2Month = today + relativedelta(months=2)
dayAfter2MonthYyyyMm = dayAfter2Month.strftime("%Y%m")  # yyyymm
folderName = dayAfter2MonthYyyyMm + "_横浜"
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


def uploadFileToGoogleDrive(service, fileName, local_path, mimetype, folder_id):
    """
    filename:   アップロード先でのファイル名
    local_path: アップロードするファイルのローカルのパス
    mimetype:   http通信の規格(csv→text/csv 参照:https://qiita.com/AkihiroTakamura/items/b93fbe511465f52bffaa)
    """

    # "parents": ["****"]この部分はGoogle Driveに作成したフォルダのURLの後ろ側の文字列に置き換えてください。
    file_metadata = {"name": fileName, "mimeType": mimetype, "parents": [folder_id]}
    media = MediaFileUpload(
        local_path, mimetype=mimetype, chunksize=1024 * 1024, resumable=True
    )
    # media = MediaFileUpload(local_path, mimetype=mimetype,resumable=True ) #csvなどの場合はこちらでも可(チャンクサイズは不要)
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    print(f"{fileName}のアップロード完了！")


def applicationYokohama():
    # ユニークなnameのリストを作成（抽選データ保有ユーザーのみ）
    targetUsers = {}
    # スクショ保存用のディレクトリ作成
    SHARE_FOLDER_ID = "1hckWWf_S64gB7oQ8MUaYM9QKjzNVPdwY"
    drive_service = build("drive", "v3", credentials=credentials)
    dirInfos = []
    # ドライブのフォルダ名取得
    response = (
        drive_service.files()
        .list(
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            q=f"parents in '{SHARE_FOLDER_ID}' and trashed = false",
            fields="nextPageToken, files(id, name)",
        )
        .execute()
    )
    for file in response.get("files", []):
        print(f"Found file: {file.get('name')} ({file.get('id')})")
        dirInfos.append({"name":file.get("name"),"id":file.get("id")})
    # ドライブに当月フォルダない場合は作成
    print(dirInfos)
    dir = ""
    dirId = ""
    for dirInfo in dirInfos:
        if folderName not in dirInfo["name"]:
            file_metadata = {
                "name": folderName,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [SHARE_FOLDER_ID],
            }
            dir = drive_service.files().create(body=file_metadata, fields="id").execute()
            # fieldに指定したidをfileから取得できる
            # print("Folder ID: %s" % dir.get("id"))
            dirId = dir.get("id")
            break
        else:
            dirId = dirInfo["id"]
            break

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
        userInfos = list(filter(lambda user: user["name"] == key, lottoryData))
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
        
        for userInfo in userInfos:
            # # 新規抽選を申し込む
            driver.find_element(By.XPATH, '//*[@id="RSGK001_01"]').click()
            time.sleep(1)
            # スポーツ選択
            driver.find_element(
                By.XPATH, '//*[@id="FRM_RSGK402"]/div[3]/div/div/a[1]'
            ).click()
            time.sleep(0.2)
            # テニスコート選択
            driver.find_element(
                By.XPATH, '//*[@id="FRM_RSGK403"]/div[3]/div/div/a[4]'
            ).click()
            time.sleep(0.2)
            # 施設指定
            driver.find_element(
                By.XPATH, f'//option[@value="{places[userInfo["place"]]}"]'
            ).click()
            time.sleep(0.2)
            # テニスコート番号選択
            driver.find_element(
                By.XPATH,
                f'//*[@id="FRM_RSGK404"]/div[7]/div/div/a[{str(int(userInfo["court_no"])+1)}]',
            ).click()
            time.sleep(0.2)
            # 日付選択
            driver.find_element(By.ID, f'idbtn_{userInfo["day"]}').click()
            time.sleep(1)
            # 時間とコート選択
            driver.find_element(
                By.ID,
                f'idinput_{places[userInfo["place"]].rstrip("0")}{str(int(userInfo["court_no"])-1).zfill(2)}_{userInfo["date"]}_{userInfo["time"]}',
            ).click()
            time.sleep(0.2)
            # 「申し込む」選択
            driver.find_element(
                By.XPATH,
                '//*[@id="FRM_RSGK407"]/div[3]/div/div/div/button//*[@id="idbtn_modoru"]',
            ).click()
            time.sleep(0.2)
            # 「次へ」選択
            driver.find_element(
                By.XPATH, '//*[@id="footer"]/div/button[2]//*[@id="idbtn_calview"]'
            ).click()
            time.sleep(0.2)
            # 「確定」選択
            driver.find_element(By.XPATH, '//*[@id="idbtn_calview"]').click()
            time.sleep(0.2)
            # # 「申込を続ける」選択
            # driver.find_element(By.XPATH, '//*[@id="idbtn_modoru"]').click()
            # time.sleep(1)
            # 「メニューへ」選択
            driver.find_element(By.XPATH, '//*[@id="home_btn"]/a/img').click()
            time.sleep(1)
        # 「抽選申込・確認」選択
        driver.find_element(By.XPATH, '//*[@id="RSGK001_02"]').click()
        time.sleep(1)
        # スクショ
        driver.execute_script("document.body.style.zoom='80%'")  # スクショ用に画面を縮小
        # scleenShot = driver.get_screenshot_as_png()
        driver.save_screenshot(f"{key}.png")
        driver.execute_script("document.body.style.zoom='100%'")
        uploadFileToGoogleDrive(
            drive_service, f"{key}.png", f"./{key}.png", "image/png", dirId
        )
        # folder_id = dirId
        # file_metadata = {"name": f"{key}.png", "parents": [folder_id]}
        # media = MediaFileUpload(f"{key}.png", mimetype="text/plain", resumable=True)
        # file = (
        #     drive_service.files()
        #     .create(body=file_metadata, media_body=media, fields="id")
        #     .execute()
        # )

        # ログアウト
        driver.find_element(By.XPATH, '//*[@id="header"]/div[3]/a/img').click()
        time.sleep(1)
        # # TODO LINEにスクショ送信
        # # LineNotify 連携用トークン・キー準備
        # line_notify_token = "rC4NpRtelGBGi9I1A7wTvq47lz0qGQ32jh2giIyi8Po"
        # line_notify_api = "https://notify-api.line.me/api/notify"
        # # httpヘッダー設定
        # headers = {"Authorization": f"Bearer {line_notify_token}"}
        # # トーク送信メッセージ設定
        # payload = {"message": "抽選"}
        # # 送信画像設定
        # files = {"imageFile": open(f"{key}.png", "rb")}  # バイナリファイルオープン
        # # post実行
        # requests.post(line_notify_api, data=payload, headers=headers, files=files)


applicationYokohama()
