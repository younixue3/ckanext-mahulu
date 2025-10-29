from flask import Blueprint, render_template
import ckan.plugins.toolkit as toolkit
import ckan.model as model

infographic_blueprint = Blueprint('infographic', __name__)

@infographic_blueprint.route('/infographic-data', endpoint='infographic_data')
def infographic_data():
    # Get all packages
    context = {'model': model}
    
    # Search for packages with infographic tag or infographic in the title/description
    search_params = {
        'q': 'infographic',
        'rows': 100
    }
    
    # Get the search results
    result = toolkit.get_action('package_search')(context, search_params)
    
    # Extract the packages from the search results
    packages = result.get('results', [])
    
    # Get facets for filtering
    facets = [
        {'name': 'tags', 'title': 'Tags'},
        {'name': 'organization', 'title': 'Organizations'}
    ]
    
    # Render the template with the packages and facets
    return render_template('infographic_data.html', packages=packages, facets=facets)