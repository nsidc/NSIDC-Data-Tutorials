import icepyx as ipx
from icepyx.core import Earthdata


class is2:
    """
    Icepyx wrapper to place ATL data orders
    """
    def __init__(self, credentials):
        self.credentials = credentials
        cap_url = 'https://n5eil02u.ecs.nsidc.org/egi/capabilities/ATL06.003.xml'
        self._session = Earthdata.Earthdata(
            uid=credentials['username'],
            email=credentials['email'],
            pswd=credentials['password'],
            capability_url=cap_url)
        self._session.start_session()

    def query(self, parameters):
        dataset = parameters['dataset']
        date_range = [parameters['start'], parameters['end']]
        bounding_box = [round(float(coord), 4) for coord in parameters['bbox'].split(',')]
        query = ipx.Query(dataset, bounding_box, date_range)
        query._email = self.credentials['email']
        query._session = self._session.session
        return query

    def simplify_atl03(self, files, variables, filters):
        return None

    def simplify_atl06(self, files, variables, filters):
        return None

    def simplify_atl07(self, files, variables, filters):
        return None

    def simplify_atl08(self, files, variables, filters):
        return None
