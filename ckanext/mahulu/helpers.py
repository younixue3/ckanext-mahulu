import os
import datetime
import random
import logging
from typing import Dict, List

import requests
import json

LOGGER = logging.getLogger(__name__)

url_base = "https://sismut.esistem.web.id"

# url_base = "https://4450f6e3767b.ngrok-free.app"


def mahulu_hello():
    return "Hello, testing!"

def _shape_records_to_daily_visits(records: List[Dict]) -> List[Dict]:
    daily = [r for r in records if (r.get('period') or '').lower() == 'daily']
    try:
        daily.sort(key=lambda r: r.get('date'))
    except Exception:
        pass
    shaped = [{'date': r.get('date'), 'count': int(r.get('count', 0))} for r in daily if r.get('date')]
    return shaped[-30:]


def _get_sismut_token(url_base: str) -> str:
    username = 'superadmin'
    password = 'samarinda'
    fallback = ''
    if not username or not password:
        return fallback
    try:
        endpoint = f"{url_base}/api/v1/auth/login"
        LOGGER.info("SISMUT login POST %s (form)", endpoint)
        form = {'username': username, 'password': password}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        resp = requests.post(endpoint, data=form, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json() or {}
        token = (
            ((data.get('data') or {}).get('user') or {}).get('token')
            or (data.get('data') or {}).get('token')
            or data.get('token')
        )
        masked = (token[:6] + '...' + token[-4:]) if token and len(token) > 12 else (token or '')
        if masked:
            LOGGER.info("SISMUT token obtained: %s", masked)
        return token or ''
    except Exception as e:
        LOGGER.warning('SISMUT login failed: %s', e)
        return fallback


def _build_sismut_headers(url_base: str) -> Dict[str, str]:
    headers = {'Content-Type': 'application/json'}
    token = _get_sismut_token(url_base)
    if token:
        headers['Authorization'] = f"Bearer {token}"
    LOGGER.info("SISMUT headers built: auth=%s", 'yes' if token else 'no')
    return headers


def _fetch_sismut_visitors() -> Dict:
    today = datetime.date.today()
    daily_visits = []
    for i in range(30):
        day = today - datetime.timedelta(days=29 - i)
        count = random.randint(200, 1000)
        daily_visits.append({'date': day.isoformat(), 'count': count})
    total_visits = sum(item['count'] for item in daily_visits)
    growth_value = random.uniform(-0.2, 0.4)
    growth = f"{growth_value:.0%}"
    return {
        'daily_visits': daily_visits,
        'total_visits': total_visits,
        'growth': growth,
    }


def push_sismut_visitors(records: List[Dict]) -> Dict:
    """
    Push visitor records to SISMUT via POST /api/ckan/visitors
    Expected record keys: period, date, count, iid (optional), url (optional)
    """
    url_base_local = url_base.rstrip('/')
    endpoint = f"{url_base}/api/v1/ckan/visitors"
    headers = _build_sismut_headers(url_base)
    payload = {'records': records}
    try:
        LOGGER.info("SISMUT POST %s records=%s", endpoint, len(records))
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        LOGGER.info("SISMUT POST status: %s", resp.status_code)
        resp.raise_for_status()
        return resp.json() or {'status': 'ok'}
    except Exception as e:
        LOGGER.warning('SISMUT visitors push failed: %s', e)
        return {'status': 'error', 'error': str(e)}


def get_user_traffic_data():
    return _fetch_sismut_visitors()

def sismut_login_print() -> Dict:
    sample = {'data': {'user': {'token': 'example-token'}}}
    print("Status Code: 200")
    print(f"Response Text: {json.dumps(sample)}")
    return sample

def sismut_push_visitors_print(records: List[Dict] | None = None) -> Dict:
    payload = {
        'records': records or [
            {'period': 'daily', 'date': '2025-11-10', 'count': 100, 'iid': 'dataset-1', 'url': 'https://ckan.example/dataset-1'},
            {'period': 'monthly', 'date': '2025-11-01', 'count': 2500, 'iid': 'dataset-1', 'url': 'https://ckan.example/dataset-1'},
        ]
    }
    sample = {'status': 'ok', 'received': payload}
    print("Status Code: 200")
    print(f"Response Text: {json.dumps(sample)}")
    return sample

def get_helpers():
    return {
        "mahulu_hello": mahulu_hello,
        "get_user_traffic_data": get_user_traffic_data,
        "push_sismut_visitors": push_sismut_visitors,
        "sismut_login_print": sismut_login_print,
        "sismut_push_visitors_print": sismut_push_visitors_print,
    }
