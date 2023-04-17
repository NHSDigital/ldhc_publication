import datetime
import pandas as pd
def get_achievement_date(LDHC_in: pd.DataFrame) -> datetime.datetime:
    """Gets the achievement date as a datetime object

    Args:
        LDHC_in (pd.DataFrame): The LDHC dataframe containing the relevant achievement date.
        Note that df must have the achievement date stored in the form
        YYYYMMDD. The achievement date 

    Returns:
        datetime.datetime: Achievement date of the input as a datetime object
    """    
    Date = datetime.datetime.strptime(str(LDHC_in.ACH_DATE[0]), "%Y%m%d")
    return Date

def get_run_date() -> datetime.datetime:
    """
    Returns:
        datetime.datetime: The current date as datetime object
    """    
    return datetime.date.today()