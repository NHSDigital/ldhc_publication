import pandas as pd
import datetime
from pipeline.utils.dates import dates
from openpyxl import load_workbook


def create_participation_table(Participation_df: pd.DataFrame, LDHC_input_df : pd.DataFrame, config_file: dict) -> pd.DataFrame:
    """Wrapper function for calling sub functions
       to create the participation table 

    Args:
        Participation_df (pd.DataFrame): Original dataframe as read from the input Participation CSV file
        LDHC_input_df (pd.DataFrame):  Original dataframe as read from the input LDHC Monthly CSV file
    """
    participation = read_participation_table_into_df(Participation_df)
    unique_practices = get_unique_practices(participation)
    monthly_participation_totals = create_table(participation, unique_practices, LDHC_input_df )
    write_to_CSV(monthly_participation_totals, config_file)
    return monthly_participation_totals


def read_participation_table_into_df(Participation_df: pd.DataFrame)-> pd.DataFrame:
    """Function to format participation table to contain only the rows with participation data and 
       standard column names

    Args:
        Participation_df (pd.DataFrame): Original dataframe as read from the input Participation CSV file_

    Returns:
        participation(pd.DataFrame):  Formatted participation dataframe
    """
    
    Participation_df.columns = Participation_df.iloc[8]
    participation = Participation_df.iloc[9:].copy(deep=True)
    participation.rename(columns={'Service\nProvider Id':'PRACTICE_CODE', 
                                  'Status Date': 'STATUS_DATE',
                                  'Status' : 'STATUS'}, inplace = True)

    return participation


def get_unique_practices(participation: pd.DataFrame)-> pd.DataFrame:
    """Function to get only the practices that have participated along with their
       participation dates

    Args:
        participation (pd.DataFrame): Formatted participation dataframe

    Returns:
        unique_practices (pd.DataFrame): Dataframe containing all the unique practices that 
                                         participated along with their dates
    """
    required_cols = ['PRACTICE_CODE','STATUS','STATUS_DATE']
    unique_practices = participation[required_cols]
    unique_practices = unique_practices[unique_practices['STATUS'] == 'Approved']\
                    .sort_values('STATUS_DATE', ascending=False).drop_duplicates(['PRACTICE_CODE'])
    return unique_practices


def create_table(participation : pd.DataFrame, unique_practices : pd.DataFrame, 
                 LDHC_input_df : pd.DataFrame) -> pd.DataFrame :
    """Function that creates the final dataframe that summarizes the monthly participation totals 

    Args:
        participation (pd.DataFrame): Formatted participation dataframe
        unique_practices (pd.DataFrame): Dataframe containing all the unique practices that 
                                         participated along with their dates
        LDHC_input_df (pd.DataFrame): Original dataframe as read from the input LDHC Monthly CSV file

    Returns:
        monthly_participation_totals (pd.DataFrame):  Final participation dataframe that contains all the three counts 
                                                      for the given month that is to be 
                                                      written to output Participation Totals CSV file
    """                

    no_active_practices = participation['PRACTICE_CODE'].nunique()
    no_participated_practices = unique_practices.shape[0]
    no_collected_practices = LDHC_input_df['ORG_CODE'].nunique()
    ach_date =  dates.get_achievement_date(LDHC_input_df)

    monthly_participation_totals = pd.DataFrame(columns = ['ACH_DATE', 'Description', 'Count'])
    monthly_participation_totals = append_and_format_rows(monthly_participation_totals, ach_date, no_active_practices, no_participated_practices, no_collected_practices)
    
    print('monthly_participation_totals\n', monthly_participation_totals)
    return monthly_participation_totals


def append_and_format_rows(monthly_participation_totals, ach_date, no_active_practices,
                no_participated_practices,no_collected_practices)-> pd.DataFrame:
    """Function that populates the rows of the dataframe for the given month

    Args:
        monthly_participation_totals 
        ach_date 
        no_active_practices 
        no_participated_practices
        no_collected_practices

    Returns:
        monthly_participation_totals (pd.DataFrame): Dataframe that contains all the three counts for the given month
    """    
    monthly_participation_totals['Description'] = ['Active practices', 'Participated','Data Collected']
    monthly_participation_totals['ACH_DATE'] = ach_date
    monthly_participation_totals['Count'] = [no_active_practices, no_participated_practices, no_collected_practices]
    monthly_participation_totals['Percentage'] = (100*monthly_participation_totals['Count']
                                                .astype(int)/int(no_active_practices))\
                                                .round(decimals=2).apply(str)
    monthly_participation_totals.at[0, 'Percentage'] = 'z'
    return monthly_participation_totals

def write_to_CSV(monthly_participation_totals: pd.DataFrame, config_file: dict):
    """This function writes the monthly participation total to the LDHC_participation_totals CSV file
       if it does not already contain an entry for that achievement date

    Args:
        monthly_participation_totals (pd.DataFrame): Dataframe that contains all the three counts for the given month
    """
    root = config_file["root_directory"]
    participation_total_filepath = f"{root}\\Checks\\LDHC_participation_totals.xlsx"
    aggregate_participation_totals = pd.read_excel(participation_total_filepath)
    ach_date = monthly_participation_totals['ACH_DATE'].iloc[0]

    if (ach_date in aggregate_participation_totals.ACH_DATE.values):
        print("Data for this month already exists in ldhc-participation-totals.")
    else:   
        result = pd.concat([aggregate_participation_totals, monthly_participation_totals], ignore_index=True)
        result.to_excel(participation_total_filepath, index=False)