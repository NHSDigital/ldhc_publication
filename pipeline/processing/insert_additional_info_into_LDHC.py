import pandas as pd

def insert(LDHC_input_df: pd.DataFrame, register_14_17_df: pd.DataFrame, register_18_ov_df: pd.DataFrame) -> pd.DataFrame:
    """Inserts practice's register information for the age brackets 14-17 and 18 and over 
    into the main LDHC dataframe

    Args:
        LDHC_input_df (pd.DataFrame): The main LDHC dataframe
        register_14_17_df (pd.DataFrame): A datframe containing information for each practice's 
        register of patients aged between 14 and 17.
        register_18_ov_df (pd.DataFrame): A datframe containing information for each practice's 
        register of patients aged 18 and over.

    Returns:
        pd.DataFrame: The main LDHC datframe with register information inserted
    """    
    return pd.concat([LDHC_input_df, register_14_17_df, register_18_ov_df]).reset_index(drop=True)