from ckan.plugins import toolkit
from ckan.lib import search
from datetime import datetime
from logging import getLogger
import ckan.logic as logic
from ckan.logic import NotFound

log = getLogger(__name__)


def _get_action(action, context_dict, data_dict):
    """Helper to get an action from toolkit."""
    return toolkit.get_action(action)(context_dict, data_dict)


def get_recently_updated_datasets(limit=3):
    '''
     Returns recently created or updated datasets, including creation date.
    :param limit: Limit of the datasets to be returned. Default is 3.
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
                created_date = package.get('created')
                package['created_at'] = created_date
                modified = datetime.strptime(
                    package['metadata_modified'].split('T')[0], '%Y-%m-%d')
                package['days_ago_modified'] = (datetime.now() - modified).days
                pkgs.append(package)
            except NotFound:
                log.warning(f"Dataset with ID {pkg['id']} not found, skipping.") # noqa
                continue
        return pkgs
    return pkgs


def get_date_by_id(package_id):
    try:
        # Fetch the package details using the 'package_show' action
        package = logic.get_action('package_show')(
            {'ignore_auth': True}, {'id': package_id}
        )
        # Get the creation date
        created_at = package.get('metadata_created')

        if created_at:
            # Convert string to datetime object
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)

        return created_at
    except Exception as e:
        log.error(f"Error fetching creation date for package {package_id}: {str(e)}") # noqa
        return None


def get_groups_by_id(package_id):
    try:
        package = logic.get_action('package_show')(
            {'ignore_auth': True}, {'id': package_id}
        )
        groups = package.get('groups', [])

        if not groups:
            return None

        group_titles = [group.get('title') for group in groups]

        return group_titles

    except Exception as e:
        log.error(f"Error fetching groups for package {package_id}: {str(e)}")
        return None
