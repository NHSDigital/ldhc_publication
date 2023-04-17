from .data import load
from .processing import registers, format, original_mapping, original_suppression, insert_additional_info_into_LDHC
from .processing.DQ_checks import DQ_check_1, DQ_check_2, DQ_check_3, report_dq_check_results, remove_incomplete_pracs
from .output import write_DQ_checks, write_LDHC_monthly, archive
from .processing.participation import participation_table
from .utils.config import load_config
import pandas as pd
def run(config_file: dict) -> None:
    """Acts as a wrapper function that calls the different 
        stages of the pipeline 
    Args:
        config_file (dict): Dict containing all config file information
    """    
    input_dict = data_load(config_file)
    LDHC_output_df = processing(input_dict, config_file)
    output(LDHC_output_df, config_file)
    return

def data_load(config_file: dict) -> dict:
    """Calls all parts of the data loading procedure and returns 
        inputs

    Args:
        config_file (dict): Dictionary containing all config file information

    Returns:
        dict: A dictionary with keys denoting the input file type
        and their associated values being the relevant Pandas 
        dataframe.
    """    
    LDHC_in = load.load_input_csv(config_file, "LDHC_monthly")
    Participation_in = load.load_input_csv(config_file, "Participation")
    input_dict = {
        "LDHC_Monthly_df": LDHC_in,
        "Participation_df": Participation_in
    }
    return input_dict

def processing(input_dict: dict, config_file: str) -> pd.DataFrame:
    """REGISTERS
        The function first gets the register dfs for the age ranges 14-17 and 18 and over.
        
        DQ CHECKS
        It then runs through the data quality checks and writes the results to the relevant files
        The DQ check results are then printed to the terminal. The "Raise exception if DQ issues 
        found" key in the config file should be set by default to True. In this scenario, if a 
        DQ is found the process will forcably error. If you are aware of the issues and wish to
        avoid the error set the key value to False.

        INSERT IN REGISTER INFORMATION
        Here the register information calculated in the earlier stage is inserted into the
        main LDHC table

        REMOVE PROBLEM PRACTICES
        As of 24/03/23 some practices are opening/signing upafter the extraction date but doing
        manual entry in CQRS and only submitting payment counts. We have taken the decision to 
        remove these practices with incomplete information from the output LDHC df. This function 
        performs this subtraction

        FORMATTING
        A step is then included to apply all the relevant formatting to the main LDHC df

        MAPPING
        The practice code is then mapped to the following information which is then joined onto
        the table: PRACTICE_NAME	PCN_ODS_CODE	PCN_NAME	ONS_SUB_ICB_LOC_CODE	
        SUB_ICB_LOC_CODE	SUB_ICB_LOC_NAME	ONS_ICB_CODE	ICB_CODE	ICB_NAME	
        ONS_COMM_REGION_CODE	COMM_REGION_CODE	COMM_REGION_NAME.

        SUPPRESSION
        Sensitive values are replaced with a '*'

        RETURN
        Finally the fully processed output is returnedfrom the function

    Args:
        input_dict (dict): A dictionary with keys denoting the input file type
        and their associated values being the relevant Pandas 
        dataframe. 
        config_file (str): A dictionary containing all the information from the 
        config

    Returns:
        pd.DataFrame: The main LDHC output df with all the relevant processing steps 
        applied to it.
    """    
    LDHC_input_df = input_dict["LDHC_Monthly_df"]
    Participation_df = input_dict["Participation_df"]
    register_14_17_df = registers.create_register_df(LDHC_input_df, "LDHCMI034")
    register_18_ov_df = registers.create_register_df(LDHC_input_df, "LDHCMI035")
    DQ_flag_1_df = DQ_check_1.get_problem_prac_ind_df(LDHC_input_df)
    DQ_flag_2_df = DQ_check_2.get_problem_rows_df(LDHC_input_df, config_file)
    DQ_flag_3_practice_series = DQ_check_3.get_problem_practice_series(register_14_17_df,register_18_ov_df,LDHC_input_df)
    write_DQ_checks.write_DQ_check_results(config_file, DQ_flag_1_df, DQ_flag_2_df, DQ_flag_3_practice_series, LDHC_input_df)
    report_dq_check_results.report(DQ_flag_1_df, DQ_flag_2_df, DQ_flag_3_practice_series, config_file)
    LDHC_input_df = insert_additional_info_into_LDHC.insert(LDHC_input_df, register_14_17_df, register_18_ov_df)
    LDHC_problem_pracs_removed = remove_incomplete_pracs.remove(LDHC_input_df, config_file, DQ_flag_2_df)
    LDHC_formatted = format.apply_formatting(LDHC_problem_pracs_removed)
    LDHC_suppressed = original_suppression.suppress_output(
        main_table=LDHC_formatted,
        config_file=config_file,
        measure_dict_meas_col_name='MEASURE',
        measure_dict_meas_type_col_name='MEASURE_TYPE',
        measure_dict_meas_description_col_name='MEASURE_DESCRIPTION',
        main_table_meas_col_name='MEASURE',
        main_table_value_col_name='VALUE',
        main_table_prac_code_col_name='PRACTICE_CODE',
        main_table_ind_code_col_name='IND_CODE'
    )
    LDHC_mapped = original_mapping.mapping(LDHC_suppressed, config_file)
    create_participation_table = participation_table.create_participation_table(Participation_df, LDHC_input_df, config_file)
    return LDHC_mapped

   
    
def output(LDHC_output_df: pd.DataFrame, config_file: dict):
    """Writes main LDHC file and performs necessary archiving

    Args:
        LDHC_output_df (pd.DataFrame): The LDHC main dataframe in the correct format fot outputting
        config_file (dict): A dictionary with all the config information in it
    """    
    write_LDHC_monthly.write_LDHC(LDHC_output_df, config_file)
    archive.archive(config_file, LDHC_output_df)
    return
