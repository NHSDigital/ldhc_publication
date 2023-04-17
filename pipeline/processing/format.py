import pandas as pd

def apply_formatting(LDHC_df: pd.DataFrame) -> pd.DataFrame:
    """Applies the following formatting steps to the input df:
    
    1. Drop approved column
    2. Renames Practice code and Measure column
    3. Replcaces the 'Number (Scaled)' string in the measure column with 'Count'

    Args:
        LDHC_df (pd.DataFrame): The main LDHC dataframe

    Returns:
        pd.DataFrame: The fully formatted LDHC dataframe
    """    
    LDHC_approve_col_rem = LDHC_df.drop("APPROVED", axis=1)
    LDHC_renamed = LDHC_approve_col_rem.rename(columns={"ORG_CODE": "PRACTICE_CODE", "FIELD_NAME": "MEASURE"})
    LDHC_renamed["MEASURE"] = LDHC_renamed["MEASURE"].replace("Number (Scaled)", "Count")
    return LDHC_renamed