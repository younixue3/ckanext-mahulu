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
    # Provide user_traffic_data for the home page
    daily_visits = [random.randint(200, 1000) for _ in range(30)]
    user_traffic_data = {
        'daily_visits': daily_visits,
        'total_visits': sum(daily_visits),
        'growth': '+8.3%'
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
