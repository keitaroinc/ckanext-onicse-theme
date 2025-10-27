from ckan.plugins import toolkit
from ckan.lib import search
from datetime import datetime
from logging import getLogger
import json
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
    

def is_internal_login_enabled():
    """
    Check if internal login (SSO) is enabled in CKAN configuration.
    Returns:
        bool: True if internal login is explicitly enabled in CKAN config, otherwise False.
    """
    value = toolkit.config.get('ckanext.saml2auth.enable_ckan_internal_login', 'False')
    if value is None:
        return False
    return str(value).strip().lower() == 'true'

def groups_available():
    """
    Returns the configured featured groups or all public groups
    Compatible with anonymous users
    """
    from ckan.logic import get_action
    from ckan.plugins import toolkit
    import json

    def _parse_featured_group_names(raw_value):
        if not raw_value:
            return []

        candidate_values = None
        if isinstance(raw_value, str):
            stripped = raw_value.strip()
            if not stripped:
                return []
            try:
                parsed = json.loads(stripped)
            except ValueError:
                # Fallback: treat as space/comma separated string
                candidate_values = toolkit.aslist(stripped)
            else:
                if isinstance(parsed, list):
                    candidate_values = parsed
                else:
                    candidate_values = toolkit.aslist(parsed)
        else:
            candidate_values = toolkit.aslist(raw_value)

        if candidate_values is None:
            candidate_values = []

        cleaned_names = []
        for value in candidate_values:
            if value is None:
                continue
            if isinstance(value, str):
                cleaned_value = value.strip().strip(",")
                cleaned_value = cleaned_value.strip("'\"'")
            else:
                cleaned_value = str(value)
            if cleaned_value:
                cleaned_names.append(cleaned_value)
        return cleaned_names

    # First attempt using the featured groups
    featured_groups = toolkit.config.get("onicse.featured_groups", "")
    group_names = _parse_featured_group_names(featured_groups)

    if group_names:
        try:
            groups = []
            for group_name in group_names:
                try:
                    group = get_action("group_show")(
                        {"ignore_auth": True},
                        {"id": group_name}
                    )
                    groups.append(group)
                except Exception as exc:
                    log.warning(
                        "Featured group '%s' could not be loaded and will be ignored: %s",
                        group_name,
                        exc,
                    )
                    continue
            if groups:
                return groups
        except Exception as e:
            log.warning(f"Error getting featured groups: {e}")

    # Fallback: use all public groups
    try:
        return get_action("group_list")(
            {"ignore_auth": True},
            {"all_fields": True}
        )
    except Exception as e:
        log.warning(f"Error getting all groups: {e}")
        return []