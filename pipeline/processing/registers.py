import pandas as pd

def create_register_df(LDHC_input_df: pd.DataFrame, relevant_indicator: str) -> pd.DataFrame:
    """This is a wrapper function that calls the individual sub-processes used to calculate 
    the relevant register

    Args:
        LDHC_input_df (pd.DataFrame): The main LDHC input dataframe
        relevant_indicator (str): The indicator code that relates to the age bracket of interest
                            ("LDHCMI034" -> 14 to 17)
                            ("LDHCMI035" -> 18 and over)

    Returns:
        pd.DataFrame: The LDHC register for the chosen age brakcet
    """    
    filtered_df = register_filter(LDHC_input_df, relevant_indicator)
    aggregated_df = register_aggregation(filtered_df)
    final_register = register_format(aggregated_df, relevant_indicator, LDHC_input_df)
    return final_register

def register_filter(LDHC_input_df: pd.DataFrame, relevant_indicator: str) -> pd.DataFrame:
    """Filter out all information that isn't used to calculate the 
    relevant LDHC register.

    Args:
        LDHC_input_df (pd.DataFrame): The main LDHC input dataframe
        relevant_indicator (str): The indicator code that relates to the age bracket of interest
                            ("LDHCMI034" -> 14 to 17)
                            ("LDHCMI035" -> 18 and over)

    Returns:
        pd.DataFrame: A dataframe containing only the information needed to calculate the chosen register
    """    
    query_text = "IND_CODE == @relevant_indicator & FIELD_NAME in ['Denominator', 'HLTHCHKDEC']"
    return LDHC_input_df.query(query_text)

def register_aggregation(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """Sums the register value in the filtered df for each practice

    Args:
        filtered_df (pd.DataFrame): output from register filter function

    Returns:
        pd.DataFrame: A dataframe mapping the practice to its associated register account
    """    
    return filtered_df.groupby("ORG_CODE", as_index=False).sum()[['ORG_CODE', 'VALUE']]

def register_format(aggregated_df: pd.DataFrame, relevant_indicator: str, LDHC_input_df: pd.DataFrame) -> pd.DataFrame:
    """Formats the register dataframe to be in the same form as the LDHC main df

    Args:
        aggregated_df (pd.DataFrame): output from register aggregation
        relevant_indicator (str): The indicator code that relates to the age bracket of interest
                            ("LDHCMI034" -> 14 to 17)
                            ("LDHCMI035" -> 18 and over)
        LDHC_input_df (pd.DataFrame): The main LDHC input dataframe

    Returns:
        pd.DataFrame: A dataframe formatted in the same fashion as LDHC input but containing information 
        about the chosen register
    """    
    if relevant_indicator == "LDHCMI034":
        ind_code_value = "LD_REG_1417"
    elif relevant_indicator == "LDHCMI035":
        ind_code_value = "LD_REG_18OV"
    col_value_map = {
        "QUALITY_SERVICE": LDHC_input_df.QUALITY_SERVICE[0],
        "ACH_DATE": LDHC_input_df.ACH_DATE[0],
        "FIELD_NAME": "Count",
        "IND_CODE": ind_code_value
    }
    for new_col, value in col_value_map.items():
        aggregated_df[new_col] = value
    return aggregated_df   
