from flask import Blueprint, render_template, request
import logging
import datetime
import random

# Define a Mahulu blueprint and routes
mahulu_blueprint = Blueprint('mahulu', __name__)
LOGGER = logging.getLogger(__name__)


@mahulu_blueprint.route('/hello_plugin', endpoint='hello_plugin')
@mahulu_blueprint.route('/', endpoint='mahulu_home')
def page():
    # Provide user_traffic_data with daily, monthly, and total
    today = datetime.date.today()
    days = []
    for i in range(60):
        d = today - datetime.timedelta(days=(59 - i))
        days.append({'date': d, 'count': random.randint(200, 1000)})

    daily_total = next((x['count'] for x in days if x['date'] == today), 0)
    monthly_total = sum(x['count'] for x in days if x['date'].year == today.year and x['date'].month == today.month)
    prev_month_date = (today.replace(day=1) - datetime.timedelta(days=1))
    prev_month_total = sum(x['count'] for x in days if x['date'].year == prev_month_date.year and x['date'].month == prev_month_date.month)
    total_total = sum(x['count'] for x in days)

    monthly_growth = (
        f"{((monthly_total - prev_month_total) / prev_month_total * 100):.1f}%" if prev_month_total > 0 else '+0%'
    )

    daily_visits = [{'date': x['date'].isoformat(), 'count': x['count']} for x in days[-30:]]
    user_traffic_data = {
        'daily_visits': daily_visits,
        'daily_total': daily_total,
        'monthly_total': monthly_total,
        'total_total': total_total,
        'monthly_growth': monthly_growth,
        'growth': monthly_growth,
    }

    return render_template('home/index.html', user_traffic_data=user_traffic_data)


@mahulu_blueprint.before_app_request
def _push_visit_event():
    try:
        if request.method != 'GET':
            return
        p = request.path or '/'
        if (
            p.startswith('/assets') or p.startswith('/static') or p.startswith('/images') or p.startswith('/favicon') or p.startswith('/public') or
            p.startswith('/webassets') or p.startswith('/uploads') or p.startswith('/base') or p.startswith('/api')
        ):
            return
        last = (p.split('/')[-1] or '').lower()
        if any(last.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.svg', '.css', '.js', '.ico', '.woff', '.woff2', '.ttf')):
            return
        today = datetime.date.today().isoformat()
        iid = 'site'
        segments = [seg for seg in p.split('/') if seg]
        if len(segments) >= 2 and segments[0] in ('dataset', 'resource'):
            iid = segments[1]
        LOGGER.info("VISIT push iid=%s path=%s url=%s", iid, p, request.url)
        record = {
            'period': 'daily',
            'date': today,
            'count': 1,
            'iid': iid,
            'url': request.url,
        }
        from ckanext.mahulu import helpers as mahulu_helpers
        mahulu_helpers.push_sismut_visitors([record])
    except Exception:
        LOGGER.warning("VISIT push failed", exc_info=True)


def get_blueprints(self):
    # Return the blueprint; routes are declared via decorators
    return mahulu_blueprint
