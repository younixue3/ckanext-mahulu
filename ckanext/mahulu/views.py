from flask import Blueprint, render_template, url_for
import ckan.lib.base as base
import requests

mahulu = Blueprint(
    "mahulu", __name__)

def page():
    user_traffic_data = {
        'daily_visits': 10,
        'total_visits': 100,
        'growth': '+2.3%'
    }

    return render_template('home/index.html', user_traffic_data=user_traffic_data)

def get_blueprints(self):

    route = [
        (u'/', u'', page),
    ]

    blueprint = Blueprint(self.name, self.__module__)
    blueprint.template_folder = u'templates/home/index.html'
    blueprint.add_url_rule('/hello_plugin', '/hello_plugin', page)
    return blueprint
