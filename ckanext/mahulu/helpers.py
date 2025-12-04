import os
import datetime
import random
import logging
from typing import Dict, List

import requests


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


def _fetch_sismut_visitors() -> Dict:
    url_base = os.environ.get('SISMUT_URL', '').rstrip('/')
    token = os.environ.get('SISMUT_TOKEN')
    secret = os.environ.get('SISMUT_SECRET')
    if not url_base or not token:
        raise RuntimeError('SISMUT env not configured')

    endpoint = f"{url_base}/api/ckan/visitors"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {token}",
    }
    if secret:
        headers['X-CKAN-SECRET'] = secret

    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json() or {}
        records = data.get('records') or data.get('data') or []
        daily_visits = _shape_records_to_daily_visits(records)
        total_visits = sum(item['count'] for item in daily_visits)
        growth = '0%'
        return {
            'daily_visits': daily_visits,
            'total_visits': total_visits,
            'growth': growth,
        }
    except Exception as e:
        logging.getLogger(__name__).warning('SISMUT visitors fetch failed: %s', e)
        raise


def get_user_traffic_data():
    try:
        return _fetch_sismut_visitors()
    except Exception:
        # Fallback: generate synthetic last-30-days data with dates
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

def get_helpers():
    return {
        "mahulu_hello": mahulu_hello,
        "get_user_traffic_data": get_user_traffic_data,
    }
