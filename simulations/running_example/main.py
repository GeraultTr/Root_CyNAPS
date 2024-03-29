import os
import shutil
from datetime import datetime

from root_cynaps.simulation_no_C import N_simulation


def previous_outputs_clearing():
    root_path = os.path.dirname(__file__)
    try:
        # We remove all files and subfolders:
        try:
            shutil.rmtree(root_path + '/outputs')
            print("Deleted the 'outputs' folder...")
            print("Creating a new 'outputs' folder...")
            os.mkdir(root_path + '/outputs')
        except OSError:
            print("Creating a new 'outputs' folder...")
            os.mkdir(root_path + '/outputs')
    except OSError as e:
        print("An error occured when trying to delete the output folder: %s - %s." % (e.filename, e.strerror))


def main(z_soil_Nm_max, output_path,  init='root00020.pckl', steps_number=2400, time_step=3600, echo=False):
    """
    :Parameters
    Every unchanged argument should be placed as default parameter for ease of multiprocessing
    """
    # This step is essential to ensure a systematic reference of subdirectories
    current_file_dir = os.path.dirname(__file__)
    if echo:
        plotting_2D = True
        plotting_STM = True
    else:
        plotting_2D = False
        plotting_STM = False

    N_simulation(z_soil_Nm_max, output_path, current_file_dir=current_file_dir, init=init, steps_number=steps_number, time_step=time_step, echo=echo,
                 plotting_2D=plotting_2D, plotting_STM=plotting_STM, logging=True)


if __name__ == '__main__':
    previous_outputs_clearing()
    start_time = datetime.now().strftime("%y.%m.%d_%H.%M")
    main(z_soil_Nm_max=0, output_path=os.path.dirname(__file__) + f'/outputs/{start_time}.nc', echo=True)
