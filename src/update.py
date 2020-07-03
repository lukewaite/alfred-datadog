# encoding: utf-8

from workflow import web, Workflow, PasswordNotFound

def get_saved_searches(url, shard, auth):
    # log.debug("Calling searches API with auth={auth} shard={shard}".format(auth=auth, shard=shard))
    # params = dict(type='search', per_page=100, page=page, search_fields='title')
    headers = {'Cookie':"dogweb={auth}; DD-PSHARD={shard}".format(auth=auth, shard=shard)}
    r = web.get('https://' + url + '/api/v1/logs/views/', headers=headers)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by Kibana and extract the saved objects
    result = r.json()['logs_views']

    return result

# def get_dashboards(api_key, url):
#     """
#     Parse all pages of projects
#     :return: list
#     """
#     return get_dashboard_page(api_key, url, 1, [])

# def get_saved_searches_page(api_key, url, page, list):


# def get_dashboard_page(api_key, url, page, list):
#     log.info("Calling dashboards API page {page}".format(page=page))
#     params = dict(type='dashboard', per_page=100, page=page, search_fields='title')
#     headers = {'accept-encoding':'gzip'}
#     r = web.get(url + '/api/saved_objects/', params, headers)
#
#     # throw an error if request failed
#     # Workflow will catch this and show it to the user
#     r.raise_for_status()
#
#     # Parse the JSON returned by Kibana and extract the saved objects
#     result = list + r.json()['saved_objects']
#
#     nextpage = r.headers.get('X-Next-Page')
#     if nextpage:
#         result = get_dashboard_page(api_key, url, nextpage, result)
#
#     return result

def main(wf):
    try:
        api_url = wf.settings.get('api_url')
        shard = wf.settings.get('dd_shard')
        auth = wf.settings.get('dd_auth')

        # A wrapper function for the cached call below
        def search_wrapper():
            return get_saved_searches(api_url, shard, auth)

        # def dashboard_wrapper():
        #     return get_dashboards('', api_url)

        saved_searches = wf.cached_data('saved_searches', search_wrapper, max_age=3600)
        # dashboards = wf.cached_data('dashboards', dashboard_wrapper, max_age=3600)

        # Record our progress in the log file
        log.debug('{} kibana searches cached'.format(len(saved_searches)))
        # log.debug('{} kibana dashboards cached'.format(len(dashboards)))

    except PasswordNotFound:  # API key has not yet been set
        # Nothing we can do about this, so just log it
        wf.logger.error('No API key saved')

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    wf.run(main)