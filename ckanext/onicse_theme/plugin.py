import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.onicse_theme.helpers as helpers
from ckan.lib.plugins import DefaultTranslation


class OnicseThemePlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.ITranslation)

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
            'is_internal_login_enabled':
                helpers.is_internal_login_enabled,
            'groups_available': 
                helpers.groups_available,
        }
    

    def update_config_schema(self, schema):

        ignore_missing = toolkit.get_validator('ignore_missing')
        validators = [ignore_missing]
        schema.update({
            'about_text_en': validators,
            'about_text_fr': validators,
            'site_description_en': validators,
            'site_description_fr': validators,
        })

        return schema
