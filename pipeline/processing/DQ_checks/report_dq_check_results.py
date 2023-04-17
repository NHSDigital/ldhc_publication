import pandas as pd
import warnings
from typing import Union, List
def report(DQ_flag_1_df: pd.DataFrame, DQ_flag_2_df: pd.DataFrame, DQ_flag_3_practice_series: pd.Series, config_file: dict):
    """Assesses whether any of the DQ results have been violated. If they have, the relevant 
    DQ check is printed and a warning is issued. Alternatively if a DQ check has passed, a 
    message is printed indicating no issues have been found for the given DQ check.

    The 'Raise exception if DQ issues found' key in the config file controls the 
    functionality of this function: 
    
    If it is set to 'True' the function will error out if any DQ issues are found.
    If it is instead set to 'False' it will not error out if any DQ issues are found.

    By default this key should be set to 'True' to force the user to investigate the DQ
    issue. However, if after this the user wishes to still run the pipeline, they can 
    set the variable to 'False' and re-run.


    Args:
        DQ_flag_1_df (pd.DataFrame): Dataframe of practice codes and associated indicator 
        codes that violate DQ check 1.
        DQ_flag_2_df (pd.DataFrame): A dataframe containing the practice/indicator/measure 
        combinations that aren't represented in the input LDHC main df for the given practice
        DQ_flag_3_practice_series (pd.Series): A Series contianing only practices that violate the DQ 3 rule
        config_file (dict): A dictionary containing all the information from the config file

    Raises:
        Exception: Exception raised if 'Raise exception if DQ issues found' (located in the config)
        is set equal to 'True' and one of the DQ rules has been violated.
    """    
    failure_flag = config_file["Raise exception if DQ issues found"]
    failures = []

    DQ2_missing_information = DQ_flag_2_df.query("Type_of_information_issue == 'missing'")
    DQ2_additional_information = DQ_flag_2_df.query("Type_of_information_issue == 'additional'")

    print_DQ_results(DQ_flag_1_df, "DQ_1", failures)
    print_DQ_results(DQ2_missing_information, "DQ2_missing_information", failures)
    print_DQ_results(DQ2_additional_information, "DQ2_additional_information", failures)
    print_DQ_results(DQ_flag_3_practice_series, "DQ_3", failures)
    
    if (len(failures) > 0) & (failure_flag == "True"):
        raise Exception(f"""The following DQ checks failed: {failures} check the DQ history file for more details.
        if you are aware of these issues and want to re-run the package without this exception being raised set
        the 'Raise exception if DQ issues found' variable in config to False""")
    elif (len(failures) > 0) & (failure_flag == "False"):
        warnings.warn(f"The following DQ checks failed {failures} check the DQ history file for more details")
    else:
        print("All DQ checks passed")
    return 

def print_DQ_results(DQ_flag_data: Union[pd.Series, pd.DataFrame], DQ_check_indicator: str, failures: list) -> List[str]:
    """Parses the dq flag data type to workout if the relevant DQ rule has been violated.
    
    If it has, a message indicating this failure is printed and a relevant DQ check indicator
    is appended to  the holder list 'failures'.

    Conversely, if it hasn't, a pass meassage is printed and the DQ check is not appended to
    the holder list 'failures'.

    Args:
        DQ_flag_data (Union[pd.Series, pd.DataFrame]): A pandas object holding the relevant DQ flag data. Can only be
        from the set {DQ_flag_1_df, DQ_flag_2_df, DQ_flag_3_practice_series}.
        DQ_check_indicator (str): A string indicating the relevant DQ check name. Can only come from the set {'DQ1', 'DQ2', 'DQ3'}
        failures (list): A holder list that has the relevant DQ_check_indicator appended to it if a failure is found 

    Returns:
        List[str]: The failures list, only updated if a DQ violation is found
    """    
    print(f"{DQ_check_indicator} results:")
    if isinstance(DQ_flag_data, pd.Series):
        if "No issues found" in list(DQ_flag_data):
            print("   No Issues")
        else:
            print("   Issues found check DQ history file")
            failures.append(f"{DQ_check_indicator}")
    elif isinstance(DQ_flag_data, pd.DataFrame):
        if "No issues found" in list(DQ_flag_data.ORG_CODE):
            print("   No Issues")
        else:
            print("   Issues found check DQ history file")
            failures.append(f"{DQ_check_indicator}")
    return failures