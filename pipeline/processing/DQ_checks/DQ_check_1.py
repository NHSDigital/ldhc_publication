import pandas as pd
def get_problem_prac_ind_df(LDHC_input_df: pd.DataFrame) -> pd.DataFrame:
    """Wrapper function that calls all individual parts of the process used to assess DQ 1.
    Where DQ 1 rule is defined as:

    'The Denominator must be greater than the numerator. If the Numerator > Denominator for any inidvidual
    practice/fractional indicator pair, DQ 1 has been violated. '

    Args:
        LDHC_input_df (pd.DataFrame): The main LDHC input dataframe

    Returns:
        pd.Dataframe: Dataframe of practice codes and associated indicator codes that violate DQ check 1.
    """    
    denominator_df = filter_df_by_field_name(LDHC_input_df, "Denominator")
    numerator_df = filter_df_by_field_name(LDHC_input_df, "Numerator")
    merged_df = merge_denom_and_nume_dfs(denominator_df, numerator_df)
    problem_pracs_df = compare_to_get_problem_pracs_df(merged_df)
    return problem_pracs_df[["ORG_CODE", "IND_CODE"]]

def filter_df_by_field_name(LDHC_input_df: pd.DataFrame, field_name: str) -> pd.DataFrame:
    """Filter input dataframe to only contain the input fieldname

    Args:
        LDHC_input_df (pd.DataFrame): The input LDHC main df
        field_name (str): The name of the field we are trying to isolate. Possible values
        are {'Denominator', 'Numerator'}

    Returns:
        pd.DataFrame: The input filtered to only contain the field of interest
    """    
    return LDHC_input_df.query("FIELD_NAME == @field_name")

def merge_denom_and_nume_dfs(denominator_df: pd.DataFrame, numerator_df: pd.DataFrame) -> pd.DataFrame:
    """_summary_

    Args:
        denominator_df (pd.DataFrame): Input LDHC df filtered to only contian denominator values
        numerator_df (pd.DataFrame): Input LDHC df filtered to only contian numerator values

    Returns:
        pd.DataFrame: merged denominator and numerator df
    """    
    return denominator_df.merge(numerator_df, on=["ORG_CODE", "IND_CODE"], how='left')

def compare_to_get_problem_pracs_df(merged_df: pd.DataFrame) -> pd.DataFrame:
    """Compare the denominator to the numerator for each practice and only keeps
    those that satisfy the problem condition that Numerator > Denominator

    Args:
        merged_df (pd.DataFrame): merged denominator and numerator df

    Returns:
        pd.DataFrame: A dataframe contianing only rows that violate the DQ 1 rule
    """    
    return merged_df.query("VALUE_x < VALUE_y")