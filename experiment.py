import json
import requests

API_URL = 'http://ec2-52-11-215-50.us-west-2.compute.amazonaws.com/api'
#API_URL = 'http://localhost:8000/api'

class Experiment:
    def __init__(self,
                 name,
                 description='',
                 parameters=None,
                 outcome=None,
                 access_token=None,
                 likelihood='GAUSSIAN'): # other option is NOISELESS
        self.name = name
        self.parameters = parameters
        self.outcome = outcome
        self.access_token = access_token
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

    def call_api(self, name, method, params):
        url = '{0}/{1}/'.format(API_URL, name)
        headers = {'Authorization': 'Bearer ' + self.access_token}
        if method.lower() == 'post':
            r = requests.post(url, headers=headers, data=json.dumps(params))
        elif method.lower() == 'get':
            r = requests.get(url, headers=headers, params=params)
        return r.json()

    def suggest(self):
        api_params = {'name': self.name}
        r = self.call_api('get_suggestion', method='get', params=api_params)
        if 'error' in r:
            raise RuntimeError('failed to get suggestion from spearmint. error: ' + r['error'])
        else:
            return r['params']

    def update(self, param_values, outcome_val):
        api_params = {'name': self.name, 'outcome_val': outcome_val}
        r = self.call_api('post_update', method='post', params=api_params)
        if 'error' in r:
            raise RuntimeError('failed to post update to spearmint. error: ' + r['error'])
