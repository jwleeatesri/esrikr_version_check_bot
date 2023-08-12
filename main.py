import os
import requests
import json

import pandas as pd

from smtplib import SMTP
from dotenv import load_dotenv
from pathlib import Path
from pprint import pprint # debugging

GEOCODING_URL = "https://geocodekr.arcgis.com/arcgis/monitor/version.json"
ROUTING_URL = "https://routekr.arcgis.com/arcgis/monitor/version.json"

BASE_PATH = Path(__file__).resolve().parent

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
        return version
    raise ValueError("")

def load_version_history(file_name: Path):
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
def store_version_history(file_name:Path, version_history: list)->None:
    

def compare():
    pass

def send_email():
    pass

if __name__ == "__main__":
    pprint(get_current_version("ROUTING"))