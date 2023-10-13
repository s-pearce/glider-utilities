"""module to read info from the Deployments google spreadsheet"""
# SP 2023-10-03

import pandas as pd

DEPLOYMENT_SHEET_URL = (
    'https://docs.google.com/spreadsheets/d/'      
    '1GuSMH5a_IIP37Mcf1jJK0q181cSeMTIObfIF8Ah_xR8/gviz/'
    'tq?tqx=out:csv&sheet=Deployments')

class DeploymentsGSheet(object):
    """provide an instance of the Deployments google sheet as a pandas data
    frame.
    """
    def __init__(self):
        self.url =  DEPLOYMENT_SHEET_URL
        # pandas reads csvs via urls, no need for separate HTML requests
        self.info = pd.read_csv(self.url)

_deployments = DeploymentsGSheet()

def deployment_row(glider, deployment_num):
    """ Get the glider deployment row 
    
    params
    ------
    glider : str or int
        the serial number of the glider to look up.
    deployment_num : str or int
        the deployment number row to return.
     
     returns
     -------
     deployment_info : pandas.DataFrame
        a single row data frame with the deployment info
     """
    if isinstance(glider, str):
        if glider.isdigit():
            glider_name = "ce_" + glider
        elif glider.startswith('ce_'):
            glider_name = glider
        else:
            raise GliderIDError(
                "incorrectly formatted `glider`, use the serial "
                "number alone as a string or int, or a string "
                "that starts with 'ce_'")
    elif isinstance(glider, (float,int)):
        glider_name = "ce_" + str(glider)
    else:
        raise GliderIDError("bad `glider` type")
    
    if isinstance(deployment_num, str) and deployment_num.isdigit():
        deploy_num = int(deployment_num)
    elif isinstance(deployment_num, int):
        deploy_num = deployment_num
    else:
        raise DeploymentNumberError("bad `deployment_num` type")
    
    # retrieve index for specific glider deployment
    deployii = np.flatnonzero(np.logical_and(
        _deployments.info['Glider'] == glider_name, 
        _deployments.info['Deployment Number'] == deploy_num))
    if len(deployii) == 0:
        print("No deployments found")
        return None
    elif len(deployii) > 1:
        print("Too many deployments found, refine inputs and try again")
        return None

    deployment_info = _deployments.info.iloc[deployii]
    return deployment_info

def deployment_dates_pdts(glider, deployment_num):
    """ deployment boundary dates as pandas datetime objects
    
    params
    ------
    glider : str or int
        the serial number of the glider to look up.
    deployment_num : str or int
        the deployment number row to return.
    
    returns
    -------
    start, end : tuple of pandas datetime objects
        The `start` and `end` datetimes of the deployment
    """
    dinfo = deployment_row(glider, deployment_num)
    start = pd.to_datetime(dinfo.loc[dinfo.index[0], 'Deploy Date (UTC)'])
    end = pd.to_datetime(dinfo.loc[dinfo.index[0], 'Recover Date (UTC)'])
    return (start, end)

def deployment_dates(glider, deployment_num):
    """ deployment boundary dates as ISO strings
    
    params
    ------
    glider : str or int
        the serial number of the glider to look up.
    deployment_num : str or int
        the deployment number row to return.
    
    returns
    -------
    start, end : tuple of strings
        The `start` and `end` ISO format date strings of the deployment
    """
    fmt = "%Y-%m-%dT%H:%M:%S"
    start, end = deployment_dates_pdts(glider, deployment_num)
    return start.strftime(fmt), end.strftime(fmt)

class GliderIDError(Exception):
    """exception for when a glider input is invalid"""
    pass

class DeploymentNumberError(Exception):
    """exception for when a deployment number is incorrectly formatted"""
    pass