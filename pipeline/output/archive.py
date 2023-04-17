import pandas as pd
import shutil
import os
from ..utils.dates.dates import get_achievement_date
def archive(config: dict, LDHC_output_df: pd.DataFrame) -> None:
    """This function moves all files from the input folder 'Current' to the input 
    folder 'Archive\\LDHC_monthly' or 'Archive\\Participation' depending on 
    file type

    Args:
        config (dict): A dictionary continaing all the information from the config file.
        LDHC_output_df (pd.Dataframe): The main LDHC output.
    """
    root_dir = config["root_directory"]
    current_input_folder = f"{root_dir}\\Input\\Current"
    input_archive_folder = f"{root_dir}\\Input\\Archive"
    date_info = get_achievement_date(LDHC_output_df).strftime("%Y-%m")
    for file_name in os.listdir(current_input_folder):
        if ".csv" in file_name:
            if "Ind_Input_Details_LDHC" in file_name:
                shutil.move(f"{current_input_folder}\\{file_name}", f"{input_archive_folder}\\LDHC_monthly\\LDHC_main_{date_info}.csv")
            elif "QS Part Status-LDHC" in file_name:
                shutil.move(f"{current_input_folder}\\{file_name}", f"{input_archive_folder}\\Participation\\LDHC_Participation_{date_info}.csv")
    return