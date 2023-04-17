
> Warning: This is the README for the publically accessible version of the LDHC package. If you are an analyst please don't use the below instructions to run the publication process.

<p>&nbsp;</p>

# LDHC 

## Contact Information

Repository owner: Primary Care Domain Analytical Team

Email: primarycare.domain@nhs.net

To contact us raise an issue on Github or via email and we will respond promptly.

<p>&nbsp;</p>

## Publication Summary

The learning disabilities health check scheme is designed to encourage practices to identify all patients aged 14 and over with learning disabilities, to maintain a learning disabilities 'health check' register and offer them an annual health check, which will include producing a health action plan.

The learning disabilities health check scheme is one of a number of GP enhanced services. Enhanced services are voluntary reward programmes that cover primary medical services; one of their main aims is to reduce the burden on secondary care services. Data for other enhanced services are published annually, the latest release of these data is available under related links below.

The publications can be found here:

https://digital.nhs.uk/data-and-information/publications/statistical/learning-disabilities-health-check-scheme

<p>&nbsp;</p>

## Set up

1. Make a [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) of the repository on your local machine.
2. Navigate to the cloned version of the repository in a command line terminal by setting your current directory to the location of the cloned repository.
3. Create and activate the correct environment by entering the below two sperate commands into your terminal:
```
conda env create --name ldhc --file environment.yml
```
```
conda activate ldhc
```
Note that you only need to create your environment once. If you wish to return to the project again, you can omit the 'conda env create' command.

<p>&nbsp;</p>

## Creating a file structure 

To run this process locally you will need to create the below file structure on your machine and insert the provided files in the 'public_metadata' folder as instructed in the 'Instructions for producing publication' steps.

```
root
│
├───Checks
│       DQ_check_results.xlsx
│       LDHC_participation_totals.xlsx
│
├───Data_dictionaries
│       indicator_to_measure_map.csv
│       LDHC Data Dictionary_Python_only.xlsx
│
├───Input 
│   │
│   ├───Archive
│   │   ├───LDHC_monthly
│   │   │
│   │   └───Participation
│   │
│   └───Current
│           synthetic-LDHC_Ind_Input_Details_LDHC.csv
│           synthetic-LDHC_Participation_YYYY-MM
│       
├───Output
    └───22_23
        │
        └───Archive
```

<p>&nbsp;</p>

## Instructions for publication production

After the above set up steps have been completed you can follow the below instructions to create the publication. Please note that you will not be able to run the code as this requires access to a private server.
The data on the private server contains reference data that is used for mapping purposes. The reference tables used contain data from the [PCN API Call](https://digital.nhs.uk/services/organisation-data-service/export-data-files/csv-downloads/gp-and-gp-practice-related-data), [GP Practice API call](https://digital.nhs.uk/services/organisation-data-service/export-data-files/csv-downloads/gp-and-gp-practice-related-data) and [ONS code history database](https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/codehistorydatabasechd)

1. Move the 'config.json' from the 'public_metadata' folder into the package at the same level as this 'README'.
2. In the config file edit the root directory value so that it matches the root of the directory that you set up earlier. Make use of escape characters e.g. "\\\\example\\root\\directory".
3. Move the synthetic-LDHC_Ind_Input_Details_LDHC.csv and the synthetic-LDHC_Participation_YYYY-MM from the public_metadata folder into your {root_directory}\Input\Current as is shown on the above project directory tree.
4. Move the indicator_to_measure_map.csv and LDHC Data Dictionary_Python_only from the public metadata folder into your {root_directory}\Input\Data_dictionaries folder
5. Move the DQ_check_results and the LDHC_participation_totals files from the public metadata folder into your {root_directory}\Checks folder
6. Run the main file by typing the below command into your terminal (make sure your terminal has it's current directory set to that of the cloned repo):
```
python -m main
```

After the process has run the output will be in the {root_directory}\Output\22_23 folder

<p>&nbsp;</p>

> WARNING: Please note that python uses the '\\' character as an escape character. To ensure your inserted paths work insert an additional '\\' each time it appears in your defined path. E.g.  'C:\Python25\Test scripts' becomes 'C:\\\Python25\\\Test scripts'

<p>&nbsp;</p>

## Licence
LDHC codebase is released under the MIT License.

The documentation is © Crown copyright and available under the terms of the Open Government 3.0 licence.
