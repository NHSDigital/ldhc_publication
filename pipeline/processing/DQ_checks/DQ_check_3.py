import numpy as np
import pandas as pd
def get_problem_practice_series(register_14_17_df: pd.DataFrame, register_18_ov_df: pd.DataFrame, LDHC_input_df: pd.DataFrame) -> pd.Series:
    """Wrapper function for DQ3 that retrieves all practices that violate DQ3 where 
    DQ3 is defined as:

    'The payment count for an indicator must not be greater than the LD register' 

    Args:
        register_14_17_df (pd.DataFrame): A df containing the LDHC register of people aged 14 to 17
        for each practice
        register_18_ov_df (pd.DataFrame): A df containing the LDHC register of people aged 18 and over
        for each practice
        LDHC_input_df (pd.DataFrame): The main LDHC input dataframe

    Returns:
        pd.Series: Series of practices that violate DQ3 rule.
    """    
    combined_register_df = append_registers(register_14_17_df, register_18_ov_df)
    total_register_df = get_total_LD_reg_per_prac(combined_register_df)
    LDHC_counts = filter_input_to_contain_counts(LDHC_input_df)
    merged_df = merge_LDHC_counts_and_register(LDHC_counts, total_register_df)
    problem_pracs_series = compare_to_get_problem_pracs(merged_df)
    return problem_pracs_series

def append_registers(register_14_17_df: pd.DataFrame, register_18_ov_df: pd.DataFrame) -> pd.DataFrame:
    """Combines the two inidividual registers into one table

    Args:
        register_14_17_df (pd.DataFrame): A df containing the LDHC register of people aged 14 to 17
        for each practice
        register_18_ov_df (pd.DataFrame): A df containing the LDHC register of people aged 18 and over
        for each practice

    Returns:
        pd.DataFrame: The two input dataframes combined vertically
    """    
    combined_register_df = register_14_17_df.append(register_18_ov_df)
    return combined_register_df

def get_total_LD_reg_per_prac(combined_register_df: pd.DataFrame) -> pd.DataFrame:
    """Produces a dataframe that gets the total register per practice

    Args:
        combined_register_df (pd.DataFrame): A df containing the LDHC register of people aged 14 to 17 and 
        18 and over (as seperate entires) for each practice.

    Returns:
        pd.DataFrame: A df containing the total LDHC register for each practice
    """    
    total_register_df = combined_register_df.groupby("ORG_CODE", as_index = False).sum()
    total_register_df = total_register_df.rename(columns={"VALUE": "TOTAL_LD_REGISTER"})
    return total_register_df

def filter_input_to_contain_counts(LDHC_input_df: pd.DataFrame) -> pd.DataFrame:
    """Filter the input dataframe to only contain the payment count
    indicator LDHC021

    Args:
        LDHC_input_df (pd.DataFrame): The main LDHC input dataframe

    Returns:
        pd.DataFrame: LDHC input filtered to only contain payment counts per practice
    """    
    LDHC_input_df_filtered = LDHC_input_df.query("IND_CODE == 'LDHC021'")
    LDHC_input_df_filtered = LDHC_input_df_filtered.rename(columns={"VALUE": "PAYMENT_COUNT"})
    return LDHC_input_df_filtered

def merge_LDHC_counts_and_register(LDHC_counts: pd.DataFrame, total_reg_df: pd.DataFrame) -> pd.DataFrame:
    """Merge the payment count and register df in order to get the 
    payment count and register count, per practice, into a
    single dataframe

    Args:
        LDHC_counts (pd.DataFrame): df listing payment counts per practice
        total_reg_df (pd.DataFrame): A df containing the total LDHC register for each practice

    Returns:
        pd.DataFrame: A dataframe containing the register info and payment count per practice
    """    
    return LDHC_counts.merge(total_reg_df, on = "ORG_CODE", how="left")
     
def compare_to_get_problem_pracs(merged_df: pd.DataFrame) -> pd.Series:
    """Retrieves A series of the practices that violate DQ 3 by comparing counts
    to registers for each practice.

    Args:
        merged_df (pd.DataFrame): A dataframe containing the register info and payment count per practice

    Returns:
        pd.Series: A Series contianing only practices that violate the DQ 3 rule
    """    
    return merged_df.query("PAYMENT_COUNT > TOTAL_LD_REGISTER").ORG_CODE