import netrc 
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger()

SENSORS = {
    "eng": '00-ENG000000',
    "parad": '01-PARADM000',
    "flort": '02-FLORTM000',
    "adcpa": '03-ADCPAM000',
    "dosta": '04-DOSTAM000',
    "ctdgv": '05-CTDGVM000'}
    
par_aliases = ["par", "parad", "par", "bsipar"]
flo_aliases = ["eco", "ecopuck", "flo", "flor", "chlorophyll", "chlor", "cdom", "backscatter", "bb", "fl", "cd", "flbbcd"]
dvl_aliases = ["adcp", "dvl"]
oxy_aliases = ["oxy", "doxy", "optode", "4831", "aadi", "oxygen", "oxy4"]
ctd_aliases = ["ctd", "temp", "temperature", "depth", "pressure", "pres", "press", "cond", "conductivity"]


PROD_DOMAIN = "ooinet.oceanobservatories.org"
DEV1_DOMAIN = "ooinet-dev1-west.intra.oceanobservatories.org"
DEV2_DOMAIN = "ooinet-dev2-west.intra.oceanobservatories.org"

class m2mSession(object):
    """A class to manage urls, credentials, and a requests session for
    the OOI M2M API systems"""

    def __init__(self, netrc_account=PROD_DOMAIN, server_target="prod"):
        """M2M session for ingestion and information requests

        :param netrc_account: str | netrc account name that has the
            api_key, user email address, and api_token credentials stored
        :param server_target: str | `prod`, `dev01`, or `dev02` to select
            which server url base to use.
        :param debug: bool | If True, prints the ingest request instead
            of submitting to the session. Default False.
        :return: json object with the site-node-sensor-deployment specific
            sensor metadata
        """

        # setup constants used to access the data from the different M2M interfaces
        self.session = requests.Session()
        retry = Retry(connect=3, total=4, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)
        self.session.headers.update({'Content-Type': 'application/json'})

        # select the base domain name for urls based on `server_target`
        if server_target == 'dev01':
            self._base_dn = DEV1_DOMAIN
        elif server_target == 'dev02':
            self._base_dn = DEV2_DOMAIN
        else:
            self._base_dn = PROD_DOMAIN

        # create the api urls
        self.base_url = 'https://{:s}/api/m2m/'.format(self._base_dn)
        self.base_url += '12587/events/deployment/inv/'

        self._get_credentials(netrc_account)
    
    def _get_credentials(self, netrc_account):
        """retrieve credentials from .netrc file and apply them them to
        the requests session"""

        # if the netrc call is given a bad account/machine name, it
        # just returns `None`
        credentials = netrc.netrc().authenticators(netrc_account)
        if not credentials:
            # first try the default
            credentials = netrc.netrc().authenticators(PROD_DOMAIN)
            # then fail with exit if credentials not found.
            if not credentials:
                # Rather than annoying traceback message for a known
                # problem just write the error to the screen and exit
                # with non-zero. This only works nicely though if this
                # class is run as a whole module.
                logger.error(
                    "the netrc account given {:s} returns no "
                    "credentials".format(netrc_account))
                self.session.close()
                return

        api_key, user_email, api_token = credentials
        self.user_email = user_email
        self.session.auth = (api_key, api_token)

    def get_deployment_info(self, gliderid, deployment, sensor=None):
        """
        Uses the metadata information available from the system for an instrument
        deployment to obtain the asset and calibration information for the
        specified sensor and deployment. This information is part of the sensor
        metadata specific to that deployment.

        :param site: Site name to query
        :param node: Node name to query
        :param sensor: Sensor name to query
        :param deploy: Deployment number
        :return: json object with the site-node-sensor-deployment specific sensor
                 metadata
        """
        if gliderid > 600:
            node = "G{:04d}".format(gliderid)
        else:
            node = "GL{:d}".format(gliderid)
        
        if not sensor or sensor not in SENSORS:
            instr = SENSORS["eng"]
        else:
            instr = SENSORS[sensor]
        
        url = self.base_url + "/CE05MOAS/{:s}/{:s}/{:s}".format(
            node, instr, str(deployment))
            
        try:
            r = self.session.get(url, timeout=30)
        except requests.exceptions.ConnectTimeout as err:
            logger.error("Could not connect to {:s}".format(self._base_dn))
            sys.exit(2)

        if r.ok:
            return r.json()
        else:
            return

    def get_deployment_dates(self, gliderid, deployment, sensor="ctdgv"):
    #def get_deployment_dates(self, site, node, sensor, deploy):
        """
        Based on the site, node and sensor names and the deployment number,
        determine the start and end times for a deployment.

        :param site: Site name to query
        :param node: Node name to query
        :param sensor: Sensor name to query
        :param deploy: Deployment number
        :return: start and stop dates for the deployment of interest
        """
        # request the sensor deployment metadata
        
        data = self.get_deployment_info(gliderid, deployment, sensor)

        # use the metadata to extract the start and end times for the deployment
        if data:
            start = time.strftime(
                '%Y-%m-%dT%H:%M:%SZ',
                time.gmtime(data[0]['eventStartTime'] / 1000.))
        else:
            return None, None

        if data[0]['eventStopTime']:
            # check to see if there is a stop time for the deployment, if so use it ...
            stop = time.strftime(
                '%Y-%m-%dT%H:%M:%SZ',
                time.gmtime(data[0]['eventStopTime'] / 1000.))
        else:
            # ... otherwise this is an active deployment, no end date
            stop = None

        return start, stop
# --- end m2mSession class ---