import base64
import os
import requests
import json
import logging

import pandas as pd

from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
from email.message import EmailMessage
from smtplib import SMTP
from dotenv import load_dotenv
from pathlib import Path
from pprint import pprint # debugging

GEOCODING_URL = "https://geocodekr.arcgis.com/arcgis/monitor/version.json"
ROUTING_URL = "https://routekr.arcgis.com/arcgis/monitor/version.json"

BASE_PATH = Path(__file__).resolve().parent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("esrikr_bot.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# def send_gmail(service, body, to):
#     # creds, _ = google.auth.default()
#     with open("service_key.json", "r") as f:
#         service_account_credentials = json.load(f)
#     credentials = service_account.Credentials.from_service_account_info(service_account_credentials)
#     gmail_service = build('gmail', 'v1', credentials=credentials)

#     message = {
#         'to': to,
#         'subject': f'{service} test, {body}',
#         'body': 'this is a test'
#     }
#     logger.info(f"Sending emails for {service}")
#     gmail_service.users().messages().send(userId='me', body=message).execute()

def send_naver_mail(service, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = f"[서비스 업데이트] {service}"
    msg["From"] = "esrikr_bot@naver.com"
    msg["To"] = ",".join(to) if len(to) > 1 else to[0]

    server = SMTP('smtp.naver.com', 587)
    server.starttls()
    server.login("esrikr_bot@naver.com", "gksrladl2023")
    server.send_message(msg)
    logger.info("message sent")
    server.quit()

def get_current_version(_type: str) -> dict:
    """
    주어진 서비스 타입의 현 버젼을 확인한다.
    """
    if _type == "GEOCODING":
        url = GEOCODING_URL
    elif _type == "ROUTING":
        url = ROUTING_URL
    else:
        raise ValueError("코드를 도대체 어떻게 짠게야")
    
    resp = requests.get(
        url=url
    ).json()

    version = resp.get("version")
    if version:
        logger.info(f"Successfully retrieved the response for {_type}")
        return version
    raise ValueError("")

def load_version_history(file_name: Path):
    try:
        with open(file_name, "r") as f:
            logger.info(f"Loading version history for {str(file_name)}")
            return json.loads(f.read())
    except FileNotFoundError:
        logger.error(f"{file_name} not found")
        return []
    
def store_version_history(file_name:Path, version_history: list)->None:
    logger.info(f"Dumping version history to {file_name}")
    with open(file_name, "w") as f:
        json.dump(version_history, f)

def check_and_update_version(service_name, new_version_data):
    file_name = f"{service_name}_version_history.json"
    version_history = load_version_history(file_name)

    if not version_history or version_history[-1]['data'] != new_version_data:
        logger.debug("If not section running")
        timestamped_version = {
            'data': new_version_data,
            'timestamp': f"{datetime.now():%y%m%d %H:%M}"
        }
        version_history.append(timestamped_version)
        # send_gmail(service_name, 'hello', ['jwlee@esrikr.com', 'ljin0906@gmail.com'])
        send_naver_mail(service=service_name, body="서비스가 업데이트 되었습니다. (테스트)", to=["jwlee@esrikr.com", "syhan@esrikr.com", "dhkim@esrikr.com"])
        store_version_history(file_name, version_history)
    else:
        logger.info("No changes")

if __name__ == "__main__":
    geocoding_resp = get_current_version("GEOCODING")
    routing_resp = get_current_version("ROUTING")

    check_and_update_version("GEOCODING", geocoding_resp)
    check_and_update_version("ROUTING", routing_resp)