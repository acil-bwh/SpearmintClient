import numpy as np
import math
import SpearmintClient

def branin(x, y):

    result = np.square(y - (5.1/(4*np.square(math.pi)))*np.square(x) +
         (5/math.pi)*x - 6) + 10*(1-(1./(8*math.pi)))*np.cos(x) + 10

    result = float(result)

    print 'Result = %f' % result
    #time.sleep(np.random.randint(60))
    return result


parameters = {'x':{'min':-5, 'max':10, 'type':'float'},
              'y':{'min':0, 'max':15, 'type':'float'}
             }
outcome = {'name':'Function_Value', 'minimize':True} # additional outcome parameter 'minimize'
#access_token = 'uykCmyN8y0gUxYiTkBDt8lr9QdDnQr'
access_token = 'dsv9crwrv87UEroGVw1F1PFD3muNjp'

scientist = SpearmintClient.Experiment(name="branin_tuner",
                                       description="Tuning a simple Spearmint example",
                                       parameters=parameters,
                                       outcome=outcome,
                                       access_token=access_token)

for i in range(5):
    # Get a hyperparameter suggestion from Whetlab
    params = scientist.suggest()

    score = 1.0 * branin(params['x'], params['y'])

    scientist.update(params, score)
