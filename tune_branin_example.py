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
access_token = '1ErTbMOLw6cNo7n3p8CgnNEPjGmq4O' # local root

scientist = SpearmintClient.Experiment(name="branin_tuner3",
                                       description="Tuning a simple Spearmint example",
                                       parameters=parameters,
                                       outcome=outcome,
                                       access_token=access_token,
                                       run_mode='local') # default run_mode = 'local' (requires local spearmint installation)

for i in range(5):
    # Get a hyperparameter suggestion from Whetlab
    params = scientist.suggest()

    score = 1.0 * branin(params['x'], params['y'])

    scientist.update(params, score)
