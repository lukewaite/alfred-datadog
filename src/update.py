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


def get_trace_saved_views(url, shard, auth):
    # log.debug("Calling trace searches API with auth={auth} shard={shard}".format(auth=auth, shard=shard))
    headers = {'Cookie':"dogweb={auth}; DD-PSHARD={shard}".format(auth=auth, shard=shard)}
    params = dict(type='trace')
    r = web.get('https://' + url + '/api/v1/logs/views', params=params, headers=headers)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by Kibana and extract the saved objects
    result = r.json()['logs_views']

    return result

def main(wf):
    try:
        api_url = wf.settings.get('api_url')
        shard = wf.settings.get('dd_shard')
        auth = wf.settings.get('dd_auth')

        # A wrapper function for the cached call below
        def search_wrapper():
            return get_saved_searches(api_url, shard, auth)

        def trace_wrapper():
            return get_trace_saved_views(api_url, shard, auth)

        saved_searches = wf.cached_data('saved_searches', search_wrapper, max_age=3600)
        traces = wf.cached_data('traces', trace_wrapper, max_age=3600)

        # Record our progress in the log file
        log.debug('{} saved views cached'.format(len(saved_searches)))
        log.debug('{} trace saved views cached'.format(len(traces)))

    except PasswordNotFound:  # API key has not yet been set
        # Nothing we can do about this, so just log it
        wf.logger.error('No API key saved')

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    wf.run(main)