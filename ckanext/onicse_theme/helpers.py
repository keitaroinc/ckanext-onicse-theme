from ckan.plugins import toolkit
from ckan.lib import search
from datetime import datetime
from logging import getLogger
from ckan import model
from ckanext.stats.stats import Stats
from ckan.logic import NotFound

from sqlalchemy import func
from ckan.model import Package

log = getLogger(__name__)

def _get_action(action, context_dict, data_dict):
    return toolkit.get_action(action)(context_dict, data_dict)

def get_recently_updated_datasets(limit=5):
    '''
     Returns recent created or updated datasets.
    :param limit: Limit of the datasets to be returned. Default is 5.
    :type limit: integer
    :returns: a list of recently created or updated datasets
    :rtype: list
    '''
    try:
        pkg_search_results = toolkit.get_action('package_search')(data_dict={
            'sort': 'metadata_modified desc',
            'rows': limit,
        })['results']

    except (toolkit.ValidationError, search.SearchError):
        return []
    else:
        pkgs = []
        for pkg in pkg_search_results:
            try:
                package = toolkit.get_action('package_show')(
                    data_dict={'id': pkg['id']})
                modified = datetime.strptime(
                    package['metadata_modified'].split('T')[0], '%Y-%m-%d')
                package['days_ago_modified'] = (datetime.now() - modified).days
                pkgs.append(package)
            except NotFound:
                log.warning(f"Dataset with ID {pkg['id']} not found, skipping.")
                continue
        return pkgs
