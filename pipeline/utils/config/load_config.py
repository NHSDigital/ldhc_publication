import json 

def load_config(path: str) -> dict:
    """Loads config file into python dict

    Args:
        path (str): file path to config file

    Returns:
        dict: dictionary with json file contents
    """    
    with open(path) as f:
        file = json.load(f)
    return file
