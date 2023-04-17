import pandas as pd
from datetime import timedelta, date, datetime
import pyodbc 
import sqlalchemy as db
def mapping(dataFrame, config_file):
    """
    TO BE REPLACED AND UPDATED
    """    
    
    ## Set up (new to package) #######################################################################
    use_corporate_reference = False
    manual_reference_file = config_file["Path to manual reference file"]
    
    headings = [
    'QUALITY_SERVICE', 'PRACTICE_CODE', 'PRACTICE_NAME', 
    'PCN_ODS_CODE', 'PCN_NAME', 
    'ONS_SUB_ICB_LOC_CODE', 'SUB_ICB_LOC_CODE', 'SUB_ICB_LOC_NAME', 
    'ONS_ICB_CODE', 'ICB_CODE','ICB_NAME',
    'ONS_COMM_REGION_CODE','COMM_REGION_CODE','COMM_REGION_NAME', 
    'ACH_DATE', 'IND_CODE', 'MEASURE', 'VALUE'
    ]

    ach_date = datetime.strptime(str(dataFrame.ACH_DATE[0]), "%Y%m%d").strftime("%Y-%m-%d")

    SQL_connection_list = config_file["SQL connection string"]
    ##################################################################################################
    ## connect to SQL server
    def connect(SQL_connection_list):
        try:
            driver = SQL_connection_list[0]
            server = SQL_connection_list[1]
            database = SQL_connection_list[2]
            trusted_connection = SQL_connection_list[3]
            conn = db.create_engine(f"mssql+pyodbc://{server}/{database}?driver={driver}?Trusted_Connection={trusted_connection}")
        except:
            raise Exception("Database Connection unsuccessful")
            conn = None
        return conn  

    conn = connect(SQL_connection_list)


    ## This function needs you to define an ach_date
        ## this has been done earlier in the code here but any ach_date will work providing it is YYYY-MM-DD format

    ## A connection string is also included in the function but may be uneccesary if a connection to DSS_PROD is defined

    ## The function returns a file including practices, and PCN names and codes
        ## easiest way to add to your practice mapping table is with a left join onto your chosen table    
    def create_pcn_mappings(ach_date):
        pcn_string = f"""
        select DISTINCT o.Name AS PRACTICE_NAME,
        o.organisationID AS PRACTICE_CODE,
        re.StartDate AS RELATIONSHIP_START_DATE,
        re.EndDate AS RELATIONSHIP_END_DATE,
        target.name AS PCN_NAME,
        target.organisationID AS PCN_ODS_CODE,
        o.SysStartTime as API_SYSTEM_UPDATE_DATE
        from [dbo].[ODSAPIOrganisationDetails] o, 
        [dbo].[ODSAPIRoleDetails] r,
        [dbo].[ODSAPICodeSystemDetails] rolename,
        [dbo].[ODSAPIRelationshipDetails] re,
        [dbo].[ODSAPICodeSystemDetails] relname, 
        [dbo].[ODSAPIOrganisationDetails] target, 
        [dbo].[ODSAPIRoleDetails] targetrole, 
        [dbo].[ODSAPICodeSystemDetails] targetrolecode
        where o.datetype ='Operational'
        AND target.datetype = 'Operational'
        AND r.datetype = 'Operational'
        AND targetRole.dateType = 'Operational'
        AND (rolename.displayname = 'GP PRACTICE' OR rolename.displayname = 'PRESCRIBING COST CENTRE')
        AND o.organisationID = r.organisationID
        AND r.roleID = rolename.ID
        AND targetrole.roleID = 'RO272' and targetrole.primaryRole=1 
        AND re.organisationID = o.organisationID
        AND re.relationshipID = relname.ID
        AND re.targetOrganisationID = target.organisationID
        AND relname.displayname = 'IS PARTNER TO' 
        AND target.organisationID = targetrole.organisationID
        AND targetrole.roleID = targetrolecode.ID
        AND NOT (o.organisationID = 'E85069' AND re.StartDate = '2021-11-01')
        AND re.StartDate <= ?
        AND (re.EndDate >= ?
        OR re.EndDate IS NULL)
        order by o.name, target.name
        """


        ## Create table and select the 4 relevant columns
        pcn_map = pd.read_sql(pcn_string, conn, params = (ach_date,)*2)
        pcn_map = pcn_map[['PRACTICE_NAME','PRACTICE_CODE','PCN_NAME','PCN_ODS_CODE']]

        return pcn_map


    def corporate_reference_mapping():
        mapping_max_query = """SELECT DISTINCT a.DATE_OF_OPERATION, a.DH_GEOGRAPHY_CODE, a.DH_GEOGRAPHY_NAME, a.GEOGRAPHY_CODE
        FROM [dbo].[ONS_CHD_GEO_EQUIVALENTS] as a
        INNER JOIN (SELECT DH_GEOGRAPHY_CODE, MAX(DATE_OF_OPERATION) AS DATE_OF_OPERATION FROM [dbo].[ONS_CHD_GEO_EQUIVALENTS] WHERE DATE_OF_OPERATION <= ? GROUP BY DH_GEOGRAPHY_CODE) as b
        ON a.DATE_OF_OPERATION = b.DATE_OF_OPERATION
        AND a.DH_GEOGRAPHY_CODE = b.DH_GEOGRAPHY_CODE"""
        mapping_max = pd.read_sql_query(mapping_max_query, conn, params=(ach_date,))
        return mapping_max


    def manual_file_mapping():
        df = pd.read_csv(manual_reference_file)
        df = df.rename(columns={'NAME':'DH_GEOGRAPHY_NAME', 'ONS_CODE':'GEOGRAPHY_CODE', 'ODS_CODE':'DH_GEOGRAPHY_CODE'})
        df = df.drop(columns=['GEOGRAPHY'])
        df['DATE_OF_OPERATION'] = ach_date
        return df
    
    
    practice_mapping_query = """SELECT a.[CODE] AS PRACTICE_CODE
                                         , a.[NAME] AS PRACTICE_NAME
                                         , a.POSTCODE
                                         , a.[COMMISSIONER_ORGANISATION_CODE] AS SUB_ICB_LOC_CODE
                                         , a.[HIGH_LEVEL_HEALTH_GEOGRAPHY] AS ICB_CODE
                                         , a.[NATIONAL_GROUPING] AS COMM_REGION_CODE
                                    FROM [dbo].[ODS_PRACTICE_V02] as a
                                    WHERE a.OPEN_DATE <= ?
                                    AND (a.CLOSE_DATE IS NULL OR a.CLOSE_DATE >= ?)
                                    AND a.DSS_RECORD_START_DATE <= ?
                                    AND (a.DSS_RECORD_END_DATE IS NULL OR a.DSS_RECORD_END_DATE >= ?)
                                    ORDER BY a.CODE"""

    #AND a.CODE IN (SELECT DISTINCT PRACTICE_CODE FROM [DSS_CORPORATE].[dbo].[GP_PATIENT_LIST] WHERE EXTRACT_DATE = ?)
    practice_mapping = pd.read_sql_query(practice_mapping_query, conn, params=(ach_date,)*4)

    
    if use_corporate_reference:
        mapping_max = corporate_reference_mapping()
    else:
        mapping_max = manual_file_mapping()

  
    mapping = pd.merge(practice_mapping,
                           mapping_max,
                           left_on = "SUB_ICB_LOC_CODE",
                           right_on = "DH_GEOGRAPHY_CODE",
                           how = "left").drop(columns = [
                                "DATE_OF_OPERATION", 
                                "DH_GEOGRAPHY_CODE"
                            ]).rename(columns={
                                "DH_GEOGRAPHY_NAME":"SUB_ICB_LOC_NAME",
                                "GEOGRAPHY_CODE":"ONS_SUB_ICB_LOC_CODE"
                            })

    mapping = pd.merge(mapping,
                           mapping_max,
                           left_on = "ICB_CODE",
                           right_on = "DH_GEOGRAPHY_CODE",
                           how = "left").drop(columns = [
                                "DATE_OF_OPERATION", 
                                "DH_GEOGRAPHY_CODE"
                            ]).rename(columns={
                                "DH_GEOGRAPHY_NAME":"ICB_NAME",
                                "GEOGRAPHY_CODE":"ONS_ICB_CODE"
                            })

    mapping = pd.merge(mapping,
                           mapping_max,
                           left_on = "COMM_REGION_CODE",
                           right_on = "DH_GEOGRAPHY_CODE",
                           how = "left").drop(columns = [
                                "DATE_OF_OPERATION", 
                                "DH_GEOGRAPHY_CODE"
                            ]).rename(columns={
                                "DH_GEOGRAPHY_NAME":"COMM_REGION_NAME",
                                "GEOGRAPHY_CODE":"ONS_COMM_REGION_CODE"
                            })
    

    # ADD A DAY TO ACHEIVEMENT DATE TO FILL IN NULL END DATES
    ach_date_slice = ach_date[0:10]
    ach_date_datetime = datetime.strptime(ach_date_slice, "%Y-%m-%d")
    ach_date_add1 = ach_date_datetime + pd.DateOffset(days=1)
    output_date = datetime.strftime(ach_date_datetime, "%d%b%Y")


    # Sort the mapping of the practices and order of the columns before doing anything with the data
    mapping_cols = [
            "PUBLICATION", 
            "ACH_DATE", 
            "PRACTICE_CODE",
            "PRACTICE_NAME",
            "POSTCODE",
            "PCN_ODS_CODE",
            "PCN_NAME",
            "ONS_SUB_ICB_LOC_CODE", 
            "SUB_ICB_LOC_CODE", 
            "SUB_ICB_LOC_NAME",
            "ONS_ICB_CODE", 
            "ICB_CODE",
            "ICB_NAME",
            "ONS_COMM_REGION_CODE",
            "COMM_REGION_CODE",
            "COMM_REGION_NAME"
        ]

    
    pcn_map = create_pcn_mappings(ach_date)
    
    
    mapping = pd.merge(mapping, pcn_map, how='left',on=['PRACTICE_CODE','PRACTICE_NAME']).drop_duplicates()
    mapping.PCN_ODS_CODE.fillna("U", inplace = True)
    mapping.PCN_NAME.fillna("Unallocated", inplace = True)
    mapping["PUBLICATION"] = "GP_PRAC_PAT_LIST"
    mapping["ACH_DATE"] = output_date
    practices_with_mapping = pd.DataFrame(mapping[mapping_cols])

    ##Ready for export
    mapping_export = practices_with_mapping.rename(columns={"POSTCODE":"PRACTICE_POSTCODE"})

    
    # Drop achievement date from mapping file so we don't have duplicate columns when mapping to data
    practices_with_mapping = practices_with_mapping.drop(columns=["ACH_DATE"])
        
    LDHC_with_mappings = pd.merge(practices_with_mapping, dataFrame, on='PRACTICE_CODE')
    dataFrame = LDHC_with_mappings[headings]
    return dataFrame