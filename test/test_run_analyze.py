# Public packages
import os, sys
# Model packages
from root_cynaps.root_cynaps import Model
# Utility packages
from log.logging import Logger
from analyze.analyze import analyze_data
from initialize.initialize import MakeScenarios as ms


def single_run(scenario, outputs_dirpath="outputs", simulation_length=2500, echo=True, log_settings={}):
    root_cynaps = Model(time_step=3600, **scenario)

    logger = Logger(model_instance=root_cynaps, outputs_dirpath=outputs_dirpath, 
                    time_step_in_hours=1, logging_period_in_hours=24,
                    echo=echo, **log_settings)
    
    try:
        for _ in range(simulation_length):
            # Placed here also to capture mtg initialization
            logger()
            logger.run_and_monitor_model_step()
            #root_cynaps.run()

    except (ZeroDivisionError, KeyboardInterrupt):
        logger.exceptions.append(sys.exc_info())

    finally:
        logger.stop()
        analyze_data(scenarios=[os.path.basename(outputs_dirpath)], outputs_dirpath=outputs_dirpath, target_properties=None, **log_settings)

def test_run(simulation_length=1, echo=True):
    scenarios = ms.from_table(file_path="inputs/Scenarios_24_06.xlsx", which=["Reference_Fischer"])
    
    for scenario_name, scenario in scenarios.items():
        print(f"[INFO] Launching scenario {scenario_name}...")
        single_run(scenario=scenario, outputs_dirpath=os.path.join("outputs", str(scenario_name)), simulation_length=simulation_length,
                    echo=echo, log_settings=Logger.light_log)
        
if __name__ == "__main__":
    test_run()