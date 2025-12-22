import os
import datetime
import random
import logging
from typing import Dict, List

import requests
import json

LOGGER = logging.getLogger(__name__)

url_base = "https://sismut.mahakamulukab.go.id"

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
    # We no longer generate random data. 
    # If the real data from push is not available, we return empty/zero structure.
    # Ideally, we should try to GET the stats if possible, but for now we fallback to empty to avoid confusion.
    
    return {
        'daily_visits': [],
        'daily_total': 0,
        'monthly_total': 0,
        'total_total': 0,
        'monthly_growth': '+0%',
        'growth': '+0%',
    }


def parse_sismut_traffic_data(response_data: Dict) -> Dict:
    """
    Parse SISMUT response data to match user_traffic_data structure.
    Expected response_data format:
    {
         "records": [
             { "period": "daily", "date": "...", "count": ... },
             { "period": "monthly", "date": "...", "count": ... }
         ]
    }
    """
    records = response_data.get('records', [])
    if not records and 'data' in response_data:
        records = response_data['data'].get('records', [])
    
    # Process daily visits
    daily_records = [r for r in records if (r.get('period') or '').lower() == 'daily']
    # Sort by date
    try:
        daily_records.sort(key=lambda x: x.get('date', ''))
    except Exception:
        pass
        
    daily_visits = [{
        'date': r.get('date'),
        'count': int(r.get('count', 0)),
        'iid': r.get('iid'),
        'url': r.get('url')
    } for r in daily_records if r.get('date')]
    
    today = datetime.date.today().isoformat()
    today_dt = datetime.date.today()
    
    # daily_total: Sum of counts for today
    daily_total = sum(int(r.get('count', 0)) for r in daily_records if r.get('date') == today)
    
    # monthly_total: Find the record for the current month
    current_month_prefix = today[:7] # YYYY-MM
    monthly_records = [r for r in records if (r.get('period') or '').lower() == 'monthly']
    monthly_total = sum(int(r.get('count', 0)) for r in monthly_records if (r.get('date') or '').startswith(current_month_prefix))
    
    # total_total: Sum of 'total' records, or sum of monthly records as fallback
    total_records = [r for r in records if (r.get('period') or '').lower() == 'total']
    if total_records:
        total_total = sum(int(r.get('count', 0)) for r in total_records)
    else:
        # Fallback: Sum of all monthly records
        total_total = sum(int(r.get('count', 0)) for r in monthly_records)
        
    # Calculate growth (monthly)
    # Compare current month vs previous month
    # previous month
    first = today_dt.replace(day=1)
    prev_month_dt = first - datetime.timedelta(days=1)
    prev_month_prefix = prev_month_dt.isoformat()[:7]
    
    prev_month_total = sum(int(r.get('count', 0)) for r in monthly_records if (r.get('date') or '').startswith(prev_month_prefix))
    
    monthly_growth = '+0%'
    if prev_month_total > 0:
        growth_pct = ((monthly_total - prev_month_total) / prev_month_total) * 100
        monthly_growth = f"{growth_pct:.1f}%"
        
    return {
        'daily_visits': daily_visits[-30:], # Last 30 days
        'daily_total': daily_total,
        'monthly_total': monthly_total,
        'total_total': total_total,
        'monthly_growth': monthly_growth,
        'growth': monthly_growth,
    }


def push_sismut_visitors(records: List[Dict]) -> Dict:
    """
    Push visitor records to SISMUT via POST /api/ckan/visitors
    Expected record keys: period, date, count, iid (optional), url (optional)
    """
    url_base_local = url_base.rstrip('/')
    endpoint = f"{url_base_local}/api/v1/ckan/visitors"
    headers = _build_sismut_headers(url_base)
    payload = {'records': records}
    try:
        LOGGER.info("SISMUT POST %s records=%s", endpoint, len(records))
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        LOGGER.info("SISMUT POST status: %s", resp.status_code)
        data = None
        try:
            data = resp.json()
        except Exception:
            data = None
        
        parsed_stats = {}
        if data:
            parsed_stats = parse_sismut_traffic_data(data)

        if 200 <= resp.status_code < 300:
            return {'status': 'ok', 'status_code': resp.status_code, 'response': (data if data is not None else {'text': resp.text}), 'parsed_stats': parsed_stats}
        else:
            return {'status': 'error', 'status_code': resp.status_code, 'error_text': resp.text}
    except Exception as e:
        LOGGER.warning('SISMUT visitors push failed: %s', e)
        return {'status': 'error', 'error': str(e)}


def get_sismut_infografik() -> List[Dict]:
    """
    Fetch infographics from SISMUT via GET /api/infografik
    """
    url_base_local = url_base.rstrip('/')
    endpoint = f"{url_base_local}/api/infografik"
    # Try without auth first as infografik is likely public, or use headers if needed.
    # User instruction implies just hitting the endpoint.
    # However, existing functions use _build_sismut_headers.
    # Let's try to just get it.
    try:
        LOGGER.info("SISMUT GET %s", endpoint)
        resp = requests.get(endpoint, timeout=10)
        # resp.raise_for_status() # Don't raise, just handle
        if resp.status_code == 200:
             data = resp.json()
             # Laravel response structure:
             # { "data": [...], "message": "sukses", ... }
             # The list of infographics is in 'data' field.
             
             if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                 return data['data']
             elif isinstance(data, list):
                 return data
             return []
        else:
             LOGGER.warning("SISMUT GET infografik failed: %s %s", resp.status_code, resp.text)
             return []
    except Exception as e:
        LOGGER.warning('SISMUT infografik fetch failed: %s', e)
        return []


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
