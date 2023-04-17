from ..data import load
from ..utils.dates import dates
import pandas as pd
from typing import Union
def write_DQ_check_results(config: dict, DQ_flag_1_df: pd.DataFrame, DQ_flag_2_df: pd.DataFrame, DQ_flag_3_practice_series: pd.Series, LDHC_input_df: pd.DataFrame) -> None:
    """The function loads in the DQ check history.
        
        Inserts in a row of the string "No issues found" to the current DQ df/series 
        if the relevant DQ check passed.

        Adds in date information to the current DQ checks dfs

        Appends the current check dfs to the relevant historic table

        Overwrites the previous DQ check history with the updated table

    Args:
        config (dict): A dict cotaining config informtion
        DQ_flag_1_df (pd.DataFrame): A df containing DQ flag 1 information (see DQ_check_1 module for more info)
        DQ_flag_2_dict (pd.DataFrame): A dict containing the two information checks(missing and additional)
        DQ_flag_3_practice_series (pd.Series): A series containing DQ flag 3 info (see DQ_check_3 module for more info)
        LDHC_input_df (pd.DataFrame): The input LDHC dataframe
    """       
    # Load in history of DQ checks
    sheet_dict_DQ_hist = load.load_DQ_checks_history(config)
    # Split DQ check2 into its 2 subcomponents
    DQ2_missing_information = DQ_flag_2_df.query("Type_of_information_issue == 'missing'").drop(columns="Type_of_information_issue").copy(deep=True)
    DQ2_additional_information = DQ_flag_2_df.query("Type_of_information_issue == 'additional'").drop(columns="Type_of_information_issue").copy(deep=True)
    print(DQ2_additional_information)
    # Format dfs with no issues
    DQ_flag_1_df = format_dfs_with_no_issues(DQ_flag_1_df)
    DQ2_missing_information_df = format_dfs_with_no_issues(DQ2_missing_information)
    DQ2_additional_information_df = format_dfs_with_no_issues(DQ2_additional_information)
    DQ_flag_3_practice_series = format_dfs_with_no_issues(DQ_flag_3_practice_series)
    # Add in date info to current DQ checks
    DQ_flag_1_df_dated = add_date_cols(DQ_flag_1_df, LDHC_input_df)
    DQ2_missing_information_df_dated = add_date_cols(DQ2_missing_information_df, LDHC_input_df)
    DQ2_additional_information_df_dated = add_date_cols(DQ2_additional_information_df, LDHC_input_df)
    DQ_flag_3_df_dated = add_date_cols(DQ_flag_3_practice_series, LDHC_input_df)
    # Append current data to historic to tables
    DQ_flag_1_out = append_current_data_to_hist(DQ_flag_1_df_dated, sheet_dict_DQ_hist["DQ_1"])
    DQ2_missing_information_out = append_current_data_to_hist(DQ2_missing_information_df_dated, sheet_dict_DQ_hist["DQ_2_missing_info"])
    DQ2_additional_information_out = append_current_data_to_hist(DQ2_additional_information_df_dated, sheet_dict_DQ_hist["DQ_2_missing_info"])
    DQ_flag_3_out = append_current_data_to_hist(DQ_flag_3_df_dated, sheet_dict_DQ_hist["DQ_3"])
    # Overwrite history files
    root = config["root_directory"]
    path = f"{root}\\Checks\\DQ_check_results.xlsx"
    writer = pd.ExcelWriter(path, engine="openpyxl")
    DQ_flag_1_out.to_excel(writer, sheet_name="DQ_1", index=False)
    DQ2_missing_information_out.to_excel(writer, sheet_name="DQ_2_missing_info", index=False)
    DQ2_additional_information_out.to_excel(writer, sheet_name="DQ_2_additional_info", index=False)
    DQ_flag_3_out.to_excel(writer, sheet_name="DQ_3", index=False)
    writer.close()
    return

def format_dfs_with_no_issues(DQ_data: Union[pd.DataFrame, pd.Series]) -> Union[pd.DataFrame,pd.Series]:
    """Checks if the dataframe has no DQ issues. If this is the case adds in a row indicating no
    issues were found

    Args:
        DQ_data (Union[pd.DataFrame,pd.Series]): The dataframe/series of the relevant current DQ check. Could or coulf not
        contain flagged issues 

    Returns:
        Union[pd.DataFrame,pd.Series]: The same data object containing a row/entry of the string "No issues found" if the 
        object inidcated the DQ check had passed
    """    
    if len(DQ_data) == 0:
        if isinstance(DQ_data, pd.DataFrame):
            DQ_data.loc[len(DQ_data)] = ["No issues found"] * len(DQ_data.columns)
        elif isinstance(DQ_data, pd.Series):
            DQ_data[0] = "No issues found"
    return DQ_data

def add_date_cols(DQ_data: Union[pd.DataFrame,pd.Series], LDHC_input_df: pd.DataFrame) -> pd.DataFrame:
    """Adds in a 'date run' column and an 'achievemnt date' column with the relevant date information included

    Args:
        DQ_data (Union[pd.DataFrame,pd.Series]): The current DQ dataframe
        LDHC_input_df (pd.DataFrame): The main LDHC input table

    Returns:
        pd.DataFrame: DQ data with added columns indicating the relevant run date (date the process was run)
        and achiement date.
    """    
    if isinstance(DQ_data, pd.DataFrame):
        DQ_data["DATE_RUN"] = dates.get_run_date().strftime("%d/%m/%Y")
        DQ_data["ACH_DATE"] = dates.get_achievement_date(LDHC_input_df).strftime("%d/%m/%Y")
    elif isinstance(DQ_data, pd.Series):
        run_date_col = pd.Series(data=[dates.get_run_date().strftime("%d/%m/%Y")]*len(DQ_data), name="DATE_RUN")
        ach_date_col = pd.Series(data=[dates.get_achievement_date(LDHC_input_df).strftime("%d/%m/%Y")]*len(DQ_data), name="ACH_DATE")
        DQ_data = pd.concat([DQ_data, run_date_col, ach_date_col], axis=1)
    return DQ_data

def append_current_data_to_hist(DQ_data: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    """Appends the current check to the historic file so that we have one 
    table which contains the historic DQ information as well as the current 
    DQ information.  

    Args:
        DQ_data (pd.DataFrame): Relevant current DQ data
        history (pd.DataFrame): Relevant DQ check history

    Returns:
        pd.DataFrame: _description_
    """    
    return pd.concat([DQ_data, history]).reset_index(drop=True)