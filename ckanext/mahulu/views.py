from flask import Blueprint, render_template, url_for
import ckan.lib.base as base


mahulu = Blueprint(
    "mahulu", __name__)

def page():
    return render_template('home/index.html')

def get_blueprints(self):

    route = [
        (u'/', u'', page),
    ]

    blueprint = Blueprint(self.name, self.__module__)
    blueprint.template_folder = u'templates/home/index.html'
    blueprint.add_url_rule('/hello_plugin', '/hello_plugin', page)
    return blueprint
