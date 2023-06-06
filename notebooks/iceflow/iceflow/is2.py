import icepyx as ipx


class is2:
    """
    Icepyx wrapper to place ATL data orders
    """
    def __init__(self, credentials):
        self.credentials = credentials

    def query(self, parameters):
        dataset = parameters['dataset']
        date_range = [parameters['start'], parameters['end']]
        bounding_box = [round(float(coord), 4) for coord in parameters['bbox'].split(',')]
        query = ipx.Query(dataset, bounding_box, date_range)
        query.earthdata_login()
        return query

    def simplify_atl03(self, files, variables, filters):
        return None

    def simplify_atl06(self, files, variables, filters):
        return None

    def simplify_atl07(self, files, variables, filters):
        return None

    def simplify_atl08(self, files, variables, filters):
        return None
