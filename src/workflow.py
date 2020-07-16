# encoding: utf-8
import sys
import argparse
from workflow import Workflow3, ICON_WEB, ICON_WARNING, ICON_INFO, web, PasswordNotFound
from workflow.background import run_in_background, is_running

__version__ = '0.2.0'

log = None

def search_for_item(project):
    """Generate a string search key for a project"""
    elements = []
    elements.append(project['name'])
    return u' '.join(elements)

def check_for_limit(limit, limiter):
    if limiter is None or limiter == limit:
        return True

    return False

def main(wf):
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    parser.add_argument('--seturl', dest='apiurl', nargs='?', default=None)
    parser.add_argument('--setshard', dest='shard', nargs='?', default=None)
    parser.add_argument('--setauth', dest='auth', nargs='?', default=None)
    parser.add_argument('--search', dest='search', nargs='?', default=None)
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # Save the provided API key or URL
    ####################################################################

    if args.apiurl:
        log.info("Setting API URL to {url}".format(url=args.apiurl))
        wf.settings['api_url'] = args.apiurl
        return 0

    if args.shard:
        log.info("Setting DataDog Shard to {shard}".format(shard=args.shard))
        wf.settings['dd_shard'] = args.shard
        return 0

    if args.auth:
        log.info("Setting DataDog Auth to {auth}".format(auth=args.auth))
        wf.settings['dd_auth'] = args.auth
        return 0

    ####################################################################
    # Check that we have an API url saved
    ####################################################################

    try:
        wf.settings['api_url']
    except KeyError:  # API key has not yet been set
        wf.add_item('No Datadog URL set.',
                    'Please use logseturl to set your Datadog API url.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    try:
        wf.settings['dd_shard']
    except KeyError:  # API key has not yet been set
        wf.add_item('No Datadog Shard set.',
                    'Please use ddlogsetshard to set your Datadog Shard.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    try:
        wf.settings['dd_auth']
    except KeyError:  # API key has not yet been set
        wf.add_item('No Datadog Auth Cookie set.',
                    'Please use ddlogsetauth to set your Datadog Auth Cookie.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    ####################################################################
    # Ensure we have data
    ####################################################################

    query = args.query

    saved_searches = wf.cached_data('saved_searches', None, max_age=0)
    traces = wf.cached_data('traces', None, max_age=0)
    apm = wf.cached_data('apm', None, max_age=0)

    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version available',
                    'Action this item to install the update',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    # Notify the user if the cache is being updated
    if is_running('update') and not saved_searches:
        wf.rerun = 0.5
        wf.add_item('Updating saved view list via DataDog...',
                    subtitle=u'This can take some time if you have a large number of objects.',
                    valid=False,
                    icon=ICON_INFO)

    # Start update script if cached data is too old (or doesn't exist)
    if not wf.cached_data_fresh('saved_searches', max_age=3600) and not is_running('update'):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)
        wf.rerun = 0.5

    # Start update script if cached data is too old (or doesn't exist)
    if not wf.cached_data_fresh('traces', max_age=3600) and not is_running('update'):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)
        wf.rerun = 0.5

    # Start update script if cached data is too old (or doesn't exist)
    if not wf.cached_data_fresh('apm', max_age=3600) and not is_running('update'):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)
        wf.rerun = 0.5

    ####################################################################
    # View/filter DataDog Saved Discovery Pages
    ####################################################################

    # If script was passed a query, use it to filter projects
    if query and traces and check_for_limit('logs', args.search):
        saved_searches = wf.filter(query, saved_searches, key=search_for_item, min_score=20)

    # If script was passed a query, use it to filter projects
    if query and traces and check_for_limit('traces', args.search):
        traces = wf.filter(query, traces, key=search_for_item, min_score=20)

    # If script was passed a query, use it to filter projects
    if query and apm and check_for_limit('apm', args.search):
        apm = wf.filter(query, apm, key=search_for_item, min_score=20)

    if not traces and not saved_searches:
        wf.add_item('No saved log views or traces found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    if check_for_limit('logs', args.search):
        for search in saved_searches:
            wf.add_item(title=search['name'],
                        subtitle=search['search'],
                        # subtitle=project['path_with_namespace'],
                        arg="https://{api_url}/logs?saved_view={view_id}".format(api_url=wf.settings['api_url'], view_id=search['id']),
                        valid=True,
                        icon=None,
                        uid=search['id'])

    # Loop through the returned traces and add an item for each to
    # the list of results for Alfred
    if check_for_limit('traces', args.search):
        for trace in traces:
            wf.add_item(title=trace['name'],
                        subtitle=trace['search'],
                        # subtitle=project['path_with_namespace'],
                        arg="https://{api_url}/apm/traces?saved_view={view_id}".format(api_url=wf.settings['api_url'], view_id=trace['id']),
                        valid=True,
                        icon=None,
                        uid=trace['id'])

    # Loop through the returned traces and add an item for each to
    # the list of results for Alfred
    if check_for_limit('apm', args.search):
        for service in apm:
            wf.add_item(title="APM: {service}".format(service=service['service']),
                        # subtitle=trace['search'],
                        # subtitle=project['path_with_namespace'],
                        arg="https://{api_url}/apm/service/{service_name}".format(api_url=wf.settings['api_url'], service_name=service['service']),
                        valid=True,
                        icon=None,
                        uid=service['service'])

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow3(update_settings={
        'github_slug': 'lukewaite/alfred-datadog',
        'version': __version__,
        'frequency': 1
    })
    log = wf.logger
    sys.exit(wf.run(main))