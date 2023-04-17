import pandas as pd
import os
from ..utils.config import load_config


def load_input_csv(config_file: dict, input_type: str) -> pd.DataFrame:
    """Uses the passed information to load the relevant input table from the
        Current Input folder into a dataframe.

    Args:
        config_file (dict): A dict containing all the config information
        input_type (str): A string indicating what the input file type is
        Can take a value from the set {"LDHC_monthly", "Participation"}

    Returns:
        pd.DataFrame: Uses the passed information to load the relevant input table from the
        Current Input folder into a dataframe.
    """    
    root = config_file["root_directory"]
    path_to_input_folder = f"{root}\\Input\\Current\\"
    input_file_name = load_input_file_names(path_to_input_folder)[input_type]
    input_df = pd.read_csv(path_to_input_folder + input_file_name[0])
    return input_df

def load_input_file_names(path_to_input_folder: str) -> dict:
    """Gets a dictionary mapping the two filetypes to their filenames as they
    appear in the input folder

    Args:
        path_to_input_folder (str): path to input folder

    Returns:
        dict: A dict mapping file_type {"LDHC_monthly", "Participation"} to filename
    """    
    input_file_names = os.listdir(path_to_input_folder)
    input_file_names_map = {
        "LDHC_monthly": [name for name in input_file_names if "Ind_Input_Details_LDHC" in name],
        "Participation": [name for name in input_file_names if "QS Part Status-LDHC" in name]
    }
    return input_file_names_map

def load_indicator_to_measure_map(config_file: dict) -> pd.DataFrame:
    """Loads a file into a dataframe that maps the indicator value to its relevant measures e.g.:
    
    |Indicator   |Measure|
    |Indicator 1| Measure a|
    |Indicator 1| Measure b|
    |Indicator 2| Measure c|
    |Indicator 2| Measure d|

    Args:
        config_file (dict): dict containing holding all config information

    Returns:
        pd.DataFrame:  A dataframe mapping each indicator in the collection to its corresponding
        measure.
    """    
    root = config_file["root_directory"]
    path_to_ind_meas_map = f"{root}\\Data_dictionaries\\indicator_to_measure_map.csv"
    df_ind_meas_map = pd.read_csv(path_to_ind_meas_map)
    return df_ind_meas_map

def load_DQ_checks_history(config: dict) -> dict:
    """Loads a file contaiing the DQ checks from every past run

    Args:
        config (dict): A dict holding all information from the config file

    Returns:
        dict: A dictionary mapping each of the sheets in the DQ history to the 
        associated table.
    """ 
    root = config["root_directory"]
    dq_check_path = f"{root}\\Checks\\DQ_check_results.xlsx"
    sheet_dict = pd.read_excel(dq_check_path, sheet_name=None, engine="openpyxl")
    return sheet_dict