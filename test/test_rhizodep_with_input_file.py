# -*- coding: latin-1 -*-
import numpy as np
import pandas as pd
import os
import rhizodep2111.src.rhizodep.simulation as simulation
import rhizodep2111.src.rhizodep.model as model

# outputs directory path:
OUTPUTS_DIRPATH = 'outputs'

# root images directory path:
IMAGES_DIRPATH = os.path.join('outputs','root_images')
if not os.path.exists(IMAGES_DIRPATH):
    # Then we create it:
    os.mkdir(IMAGES_DIRPATH)
else:
    # Otherwise, we delete all the images that are already present inside:
    for root, dirs, files in os.walk(IMAGES_DIRPATH):
        for file in files:
            os.remove(os.path.join(root, file))

# MTG files directory path:
MTG_DIRPATH = os.path.join('outputs','MTG_files')
if not os.path.exists(MTG_DIRPATH):
    # Then we create it:
    os.mkdir(MTG_DIRPATH)
else:
    # Otherwise, we delete all the images that are already present inside:
    for root, dirs, files in os.walk(MTG_DIRPATH):
        for file in files:
            os.remove(os.path.join(root, file))

# MTG properties directory path:
MTG_PROP_DIRPATH = os.path.join('outputs','MTG_properties')
if not os.path.exists(MTG_PROP_DIRPATH):
    # Then we create it:
    os.mkdir(MTG_PROP_DIRPATH)
else:
    # Otherwise, we delete all the images that are already present inside:
    for root, dirs, files in os.walk(MTG_PROP_DIRPATH):
        for file in files:
            os.remove(os.path.join(root, file))

# desired outputs filename:
DESIRED_RESULTS_FILENAME = 'desired_simulation_results.csv'
# actual outputs filename:
ACTUAL_RESULTS_FILENAME = 'actual_simulation_results.csv'

PRECISION = 6
RELATIVE_TOLERANCE = 10 ** -PRECISION
ABSOLUTE_TOLERANCE = RELATIVE_TOLERANCE

def compare_actual_to_desired(data_dirpath, desired_data_filename, actual_data_filename, overwrite_desired_data=False):
    """
    Function that compares the actual simulation results to desired simulation results.
    An exception is raised if the actual results do not matched the desired ones.

    :param str data_dirpath: The directory path were the simulation results are stored.
    :param str desired_data_filename: The filename of the desired simulation results.
    :param str actual_data_filename: The filename of the actual simulation results.
    :param bool overwrite_desired_data: If True, the desired simulation results are overwritten by the actual simulation results.
    """
    # read desired results
    desired_data_filepath = os.path.join(data_dirpath, desired_data_filename)
    desired_data_df = pd.read_csv(desired_data_filepath)

    # read actual results
    actual_data_filepath = os.path.join(data_dirpath, actual_data_filename)
    actual_data_df = pd.read_csv(actual_data_filepath)

    if overwrite_desired_data:
        # in case we want to update the desired data when the model was changed on purpose
        desired_data_filepath = os.path.join(data_dirpath, desired_data_filename)
        actual_data_df.to_csv(desired_data_filepath, na_rep='NA', index=False)
    else:
        # keep only numerical data
        for column in ([]):
            if column in desired_data_df.columns:
                assert desired_data_df[column].equals(actual_data_df[column])
                del desired_data_df[column]
                del actual_data_df[column]

    # compare to the desired data:
    error_message = "Sorry, the test failed, the new outputs are different from the previous ones!" +\
                    "\nIn particular, final root length is " + str(desired_data_df['Root length (m)'].iloc[-1]) +\
                    " cm in the original outputs, and " + str(actual_data_df['Root length (m)'].iloc[-1]) + \
                    " cm in the new outputs." + " \nSee details below:"
    np.testing.assert_allclose(actual_data_df.values, desired_data_df.values, RELATIVE_TOLERANCE, ABSOLUTE_TOLERANCE,
                               err_msg=error_message,
                               verbose=False)

def run_ref_simulation_with_input_file():
    # We initiate the properties of the MTG "g":
    g = model.initiate_mtg(random=True)

    # We launch the main simulation program:
    print("Simulation starts ...")
    simulation.main_simulation(g, simulation_period_in_days=20., time_step_in_days=1./24.,
                               radial_growth="Possible", ArchiSimple=False, ArchiSimple_C_fraction=0.10,
                               input_file=os.path.join("inputs", "sucrose_input_test.csv"),
                               outputs_directory=OUTPUTS_DIRPATH,
                               forcing_constant_inputs=False, constant_sucrose_input_rate=1.e-6,
                               constant_soil_temperature_in_Celsius=20,
                               nodules=False,
                               root_order_limitation=False,
                               root_order_treshold=2,
                               specific_model_option=None,
                               simulation_results_file=ACTUAL_RESULTS_FILENAME,
                               recording_interval_in_days=5,
                               recording_images=True,
                               root_images_directory=IMAGES_DIRPATH,
                               z_classification=False, z_min=0., z_max=1., z_interval=0.5,
                               z_classification_file='z_classification.csv',
                               printing_sum=False,
                               recording_sum=True,
                               printing_warnings=False,
                               recording_g=False,
                               g_directory=MTG_DIRPATH,
                               recording_g_properties=True,
                               g_properties_directory=MTG_PROP_DIRPATH,
                               random=True,
                               plotting=True,
                               scenario_id=1,
                               displayed_property="C_hexose_root", displayed_vmin=1e-6, displayed_vmax=1e-0,
                               log_scale=True, cmap='jet',
                               x_center=0, y_center=0, z_center=-1, z_cam=-2,
                               camera_distance=4., step_back_coefficient=0., camera_rotation=False, n_rotation_points=24 * 5)

def test_run(overwrite_desired_data=False):
    """
    Run a test that compare the results of a reference simulation of RhizoDep that uses an input file, to desired simulation results.
    An exception is raised if the actual results do not matched the desired ones.

    :param bool overwrite_desired_data: If True, the desired simulation results are overwritten by the actual simulation results.
    """
    # run the reference simulation
    run_ref_simulation_with_input_file()

    # compare actual to desired outputs (an exception is raised if the test failed)
    print('')
    print('Comparing {} to {}'.format(ACTUAL_RESULTS_FILENAME, DESIRED_RESULTS_FILENAME),'...')
    compare_actual_to_desired(OUTPUTS_DIRPATH, DESIRED_RESULTS_FILENAME, ACTUAL_RESULTS_FILENAME,
                              overwrite_desired_data)
    print('The test is passed! {} is OK!'.format(ACTUAL_RESULTS_FILENAME))


if __name__ == '__main__':
    test_run(overwrite_desired_data=False)
