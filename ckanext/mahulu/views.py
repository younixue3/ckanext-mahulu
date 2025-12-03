from flask import Blueprint, render_template
import random

# Define a Mahulu blueprint and routes
mahulu_blueprint = Blueprint('mahulu', __name__)


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


def get_blueprints(self):
    # Return the blueprint; routes are declared via decorators
    return mahulu_blueprint
