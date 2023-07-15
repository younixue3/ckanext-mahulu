import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config



# import ckanext.testing.cli as cli
# import ckanext.testing.helpers as helpers
import ckanext.mahulu.views as views
# from ckanext.testing.logic import (
#     action, auth, validators
# )

def showing_dataset(id):
    context = {}
    data_dict: dict[str, Any] = {u'id': id, u'include_tracking': True}
    value = toolkit.get_action('package_show')(context, data_dict)
    # value = toolkit.asbool(value)
    return value

def newest_dataset():
    '''Return a sorted list of the groups with the most datasets.'''

    # Get a list of all the site's groups from CKAN, sorted by number of
    # datasets.
    groups = toolkit.get_action('package_list')(
        data_dict={'all_fields': True})

    # Truncate the list to the 10 most popular groups only.
    groups = groups[:10]

    return groups


class MahuluPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    
    # plugins.implements(plugins.IAuthFunctions)
    # plugins.implements(plugins.IActions)
    # plugins.implements(plugins.IBlueprint)
    # plugins.implements(plugins.IClick)
    plugins.implements(plugins.ITemplateHelpers)
    # plugins.implements(plugins.IValidators)
    

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "mahulu")

    
    # IAuthFunctions

    # def get_auth_functions(self):
    #     return auth.get_auth_functions()

    # IActions

    # def get_actions(self):
    #     return action.get_actions()

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints(self)

    # IClick

    # def get_commands(self):
    #     return cli.get_commands()

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'mahulu_newset_dataset': newest_dataset,
            'mahulu_showing_dataset': showing_dataset
            }

    # IValidators

    # def get_validators(self):
    #     return validators.get_validators()
    
