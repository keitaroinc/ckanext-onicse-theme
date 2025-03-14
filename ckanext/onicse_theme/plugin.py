import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.onicse_theme.helpers as helpers

class OnicseThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "onicse_theme")

    def get_helpers(self):
        return {
            'get_recently_updated_datasets':
                helpers.get_recently_updated_datasets,
            'get_date_by_id':
                helpers.get_date_by_id,
        }
