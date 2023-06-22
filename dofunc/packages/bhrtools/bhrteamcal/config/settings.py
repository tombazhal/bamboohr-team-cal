import os
import yaml
from dotenv import dotenv_values

config = {}

def load_config(timeoffs_config, config_dir):
    """
        Load values from config.yml using provided time offs group
        and append with variables set in the .env file

    :param timeoffs_config: name of the time offs group to choose
    :param config_dir: directory containing config.yml
    :return: sets global config variable
    """
    global config

    config_file_path = os.path.join(config_dir, 'config.yml')
    with open(config_file_path, 'r') as config_file:
        all_config = yaml.safe_load(config_file)

    # Select the specific config based on TIMEOFFS input variable
    for timeoff in all_config['timeoffs']:
        if timeoffs_config in timeoff:
            config = timeoff[timeoffs_config]
            break
    else:
        raise ValueError(f'No configuration found for {timeoffs_config} timeoffs.')

    # Include bamboohr config
    config.update(all_config['bamboohr'])

    # Read .env and append environment variables into config
    for key, value in dotenv_values().items():
        config[key] = value

    return config
