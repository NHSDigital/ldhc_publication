import pandas as pd
from ...data import load 

def get_problem_rows_df(LDHC_input_df: pd.DataFrame, config_file: dict) -> pd.DataFrame:
    """Returns 1 dataframe highlighting which rows violate the 2 information issues
    covered by DQ check 2. Where the individual issues are defined as:

    # Missing information
    'All practices who have submitted data must have submitted data for each indicator/measure in
    the collection' 

    # Additional information
    'All practices who have submitted data must have not submitted any indicator/measure
    information that is not contained in the data dictionary'

    Args:
        LDHC_input_df (pd.DataFrame): The main LDHC input
        config_file (dict): A dictionary containing all config information

    Returns:
        pd.DataFrame: A dataframe with a column highlighting whether a row is violating 
        one of the above issues
    """    
    ind_meas_map_df = load.load_indicator_to_measure_map(config_file)
    DQ2_df = pd.concat([
        isolate_problem_rows_for_prac(LDHC_input_df, ind_meas_map_df, practice) for practice in set(LDHC_input_df.ORG_CODE)
    ])
    return DQ2_df

def isolate_problem_rows_for_prac(LDHC_input_df: pd.DataFrame, ind_meas_map_df: pd.DataFrame, practice: str) -> pd.DataFrame:
    """
    filters LDHC_input_df to only contain rows pertaining to the practice
    |
    merges in the info from the measure dicitonary
    |
    queries the new df to only find rows that violate the chosen
    DQ2 rule
    |
    Selects the columns we want returned
    |
    Takes a deep copy to avoid 'setting on copy' pandas warnings
    |
    Inserts in practice information to the df before returning 

    Args:
        LDHC_input_df (pd.DataFrame): Main LDHC input
        ind_meas_map_df (pd.DataFrame): A dictionary that maps each indicator to the measures that 
        make it up
        practice (str): A string of the practice code

    Returns:
        pd.DataFrame: A dataframe for the practice with a column highlighting whether a row is violating 
        one of the 2 DQ2 issues.
    """
    practice_problem_rows_df = (
        LDHC_input_df
        .query("ORG_CODE == @practice")
        .merge(ind_meas_map_df, how="outer", on=["FIELD_NAME", "IND_CODE"], indicator=True)
        .loc[:, ["ORG_CODE", "IND_CODE", "FIELD_NAME", "_merge"]]
        .copy(deep=True)
    )
    practice_problem_rows_df = format_merge_col(practice_problem_rows_df)
    practice_problem_rows_df["ORG_CODE"] = practice
    return practice_problem_rows_df

def format_merge_col(practice_problem_rows_df: pd.DataFrame) -> pd.DataFrame:
    """renames the merge column and replaces the string indicators so
    that they are more relevant.

    Args:
        practice_problem_rows_df (pd.DataFrame): A dataframe for a practice containing the _merge col

    Returns:
        pd.DataFrame: The practice df with a fully formatted merge col
    """    
    practice_problem_rows_df.rename(columns={"_merge": "Type_of_information_issue"}, inplace=True)
    practice_problem_rows_df["Type_of_information_issue"] = (
        practice_problem_rows_df["Type_of_information_issue"]
        .map({"right_only": "missing", "left_only": "additional"})
    )
    return practice_problem_rows_df
