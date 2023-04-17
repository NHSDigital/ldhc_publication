import pandas as pd
import warnings
def remove(LDHC_input_df: pd.DataFrame, config_file: dict, DQ_flag_2_df: pd.DataFrame) -> pd.DataFrame:
    """Some practices open/sign up after the extraction date but still submit payment 
    counts manually. This function removes practices from the table that do not submit 
    complete information. 
    
    Note that due to potential alternate input data quality issues, practices not effected 
    by the above condition may still have incomplete information. Always check the DQ2 log/
    underlying data to verify that you understand the reasons behind a practice being 
    removed. We may be able to resolve the data issue without removing the practice 
    from the output.

    Args:
        LDHC_input_df (pd.Dataframe): The main LDHC input df
        config_file (dict): A dictionary contianing all the config information
        DQ_flag_2_df (pd.Dataframe): A dataframe containing all the practice/indicator/measure combinations 
        that should be but aren't in the input LDHC main df. i.e. a dataframe containing all the
        missing information.

    Returns:
        pd.Dataframe: The main LDHC table filtered to only contain practices that have submitted
        all indicators/measures given in the data dictionary.
    """    
    DQ2_missing_information = DQ_flag_2_df.query("Type_of_information_issue == 'missing'")
    if config_file["Remove pracs with incomplete info"] == "False":
        if "No issues found" in list(DQ2_missing_information.ORG_CODE):
            return LDHC_input_df
        else:
            warnings.warn("Practice(s) with incomplete information found but not removed")
    else:
        problem_pracs = list(DQ2_missing_information.ORG_CODE.unique())
        warnings.warn(f"The following practice(s) are being removed from the output due to incomplete information for the organisation being present in the input data: {problem_pracs}")
        return LDHC_input_df.query("ORG_CODE not in @problem_pracs")


