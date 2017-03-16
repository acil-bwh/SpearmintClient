import json
import requests
import importlib

remote_api="http://spmint.chestimagingplatform.org/api"
local_api="http://localhost:8000/api"


class Experiment:
    def __init__(self,
                 name,
                 description='',
                 parameters=None,
                 outcome=None,
                 access_token=None,
                 api_url=remote_api,
                 likelihood='GAUSSIAN', # other option is NOISELESS
                 run_mode='LOCAL'): # other option is WEB
        self.access_token = access_token
        self.api_url=api_url
        api_params = {'name': name}
        r = self.call_api('find_experiment', method='get', params=api_params)
        if (r['result']): # found experiment
            print 'resuming experiment ' + name + '...'
        else:
            api_params['parameters'] = parameters
            api_params['outcome'] = outcome
            r = self.call_api('create_experiment', method='post', params=api_params)
            if 'error' in r:
                raise RuntimeError('failed to create experiment ' + name + '. error: ' + r['error'])
            else:
                print 'experiment ' + name + ' was created.'
        self.username = r['username']
        if run_mode.upper() == 'LOCAL':
            #Get Spearmint MongoDB credentials from Server
            r = self.call_api('get_mongodb_uri',method='get',params={})
            db_uri=r['db_uri']
            spearmint = importlib.import_module('spearmint') # import spearmint only if needed
            self.experiment = spearmint.Experiment(self.username + '.' + name,
                                                   description=description,
                                                   parameters=parameters,
                                                   outcome=outcome,
                                                   access_token=access_token,
                                                   db_uri=db_uri,
                                                   likelihood=likelihood)
        else:
            self.experiment = WebExperiment(name, access_token,api_url)

    def call_api(self, name, method, params):
        url = '{0}/{1}/'.format(self.api_url, name)
        headers = {'Authorization': 'Bearer ' + self.access_token}
        if method.lower() == 'post':
            r = requests.post(url, headers=headers, data=json.dumps(params))
        elif method.lower() == 'get':
            r = requests.get(url, headers=headers, params=params)
        return r.json()

    def suggest(self):
        return self.experiment.suggest()

    def update(self, param_values, outcome_val):
        return self.experiment.update(param_values, outcome_val)

class WebExperiment(Experiment):
    """ use web APIs to perform spearmint operations
    """
    def __init__(self, name, access_token=None,api_url=remote_api):
        self.name = name
        self.access_token = access_token
        self.api_url = api_url
    def suggest(self):
        api_params = {'name': self.name}
        r = self.call_api('get_suggestion', method='get', params=api_params)
        if 'error' in r:
            raise RuntimeError('failed to get suggestion from spearmint. error: ' + r['error'])
        else:
            return r['params']

    def update(self, param_values, outcome_val):
        api_params = {'name': self.name,
                      'param_values': param_values,
                      'outcome_val': outcome_val}
        r = self.call_api('post_update', method='post', params=api_params)
        if 'error' in r:
            raise RuntimeError('failed to post update to spearmint. error: ' + r['error'])
