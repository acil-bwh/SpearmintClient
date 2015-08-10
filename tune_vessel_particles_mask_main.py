import os.path
import subprocess
import numpy as np
import tempfile, shutil
import pdb
import nrrd
from cip_python.utils.compute_dice_coefficient import compute_dice_coefficient
from cip_python.nipype.workflows.vessel_particles_mask_workflow \
  import VesselParticlesMaskWorkflow
import SpearmintClient

access_token = 'uykCmyN8y0gUxYiTkBDt8lr9QdDnQr'

parameters = {'alpha':{'min':0.01, 'max':1, 'type':'float'},
              'beta':{'min':0.01, 'max':1, 'type':'float'},
              'C':{'min':1, 'max':300, 'type':'float'},
              'num_steps':{'min':2, 'max':7, 'type':'int'},
              'amount':{'min':0.01, 'max':1, 'type':'float'},
              'smart':{'min':1, 'max':5, 'type':'int'}}

outcome = {'name':'Score'}
scientist = SpearmintClient.Experiment(name="vessel_particles_mask_tuner",
                               description="Tuning the params of the vessel \
particle mask workflow to optimize performance",
                               parameters=parameters,
                               outcome=outcome,
                               access_token=access_token)

for i in range(30):
    # Get a hyperparameter suggestion from Whetlab
    params = scientist.suggest()

    #print "------------- iteration {0} -------------".format(i)
    #print params

    # Get the path to the this test so that we can reference the test data
    this_dir = os.path.dirname(os.path.realpath(__file__))

    # Set up the inputs and run the workflow
    ct_file_name = '/Users/jinho/Github/ChestImagingPlatform/Testing/Data/Input/vessel.nrrd'
    label_map_file_name = '/Users/jinho/Github/ChestImagingPlatform/Testing/Data/Input/vessel_volumeMask.nrrd'
    seeds_mask_file_name = '/Users/jinho/Github/ChestImagingPlatform/Testing/Data/Input/vessel_vesselSeedsMask.nrrd'
    tmp_dir = tempfile.mkdtemp()
    vessel_seeds_mask_file_name = os.path.join(tmp_dir, 'vesselSeedsMask.nrrd')

    gaussianStd = [0.7, 4.0, params['num_steps']]

    wf = VesselParticlesMaskWorkflow(ct_file_name, label_map_file_name,
                                     tmp_dir, vessel_seeds_mask_file_name)
    wf.get_node('compute_feature_strength').inputs.alpha = params['alpha']
    wf.get_node('compute_feature_strength').inputs.beta = params['beta']
    wf.get_node('compute_feature_strength').inputs.C = params['C']
    wf.get_node('compute_feature_strength').inputs.std = gaussianStd
    wf.get_node('unu_heq').inputs.amount = params['amount']
    wf.get_node('unu_heq').inputs.smart = params['smart']
    wf.run()

    ref, ref_header = nrrd.read(seeds_mask_file_name)
    test, test_header = nrrd.read(vessel_seeds_mask_file_name)
    score = compute_dice_coefficient(ref, test, 1)
    #print vessel_seeds_mask_file_name

    scientist.update(params, score)

    shutil.rmtree(tmp_dir)
