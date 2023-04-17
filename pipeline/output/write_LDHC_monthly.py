import pandas as pd
from ..utils.dates import dates
import datetime

def write_LDHC(LDHC_output_df: pd.DataFrame, config_file: dict, service_year="22_23"):
    """Writes the main LDHC file to the output folder with the correct file_name     

    Args:
        LDHC_output_df (pd.DataFrame): The final LDHC main df after all processing has been applied
        config_file (dict): A dictionary containing all the config file information
        service_year (str, optional): The relevant service year of the publication being run in the form
        yy_yy. Defaults to "22_23".
    """    
    root = config_file["root_directory"]
    output_folder = f"{root}\\Output\\{service_year}"
    file_name_date_component = get_date_for_file_name(LDHC_output_df)
    file_name = f"\\learning-disabilities-health-check-scheme-eng-{file_name_date_component}.csv"
    output_path = f"{output_folder}{file_name}"
    LDHC_output_df.to_csv(output_path, index=False)
    return

def get_date_for_file_name(LDHC_output_df: pd.DataFrame) -> datetime.datetime:
    """Gets the file_name date in the correct format based on the achievemnt date of LDHC
    out.

    Args:
        LDHC_output_df (pd.DataFrame): The final LDHC main df after all processing has been applied

    Returns:
        datetime.datetime: The achievement date for the input df in the form: month name shorthand-full year
    """
    date_object = dates.get_achievement_date(LDHC_output_df)
    return date_object.strftime("%b-%Y")
