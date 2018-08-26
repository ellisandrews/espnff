import requests
from espnff import League
from espnff.exception import AuthorizationError


class ESPNFF(object):

    def __init__(self, username=None, password=None):
        """Give an ESPN.com username and password to be able to fetch league data from the API."""
        self.__username = username
        self.__password = password
        self.__auth_swid = None
        self.__auth_s2 = None

    def authorize(self):
        """Obtain auth_swid and auth_s2 to be able to fetch a private league."""
        headers = {'Content-Type': 'application/json'}
        r = requests.post(
            'https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US',
            headers=headers
        )

        if r.status_code != 200 or 'api-key' not in r.headers:
            raise AuthorizationError('failed to get API key')

        api_key = r.headers['api-key']
        headers['authorization'] = 'APIKEY ' + api_key

        payload = {'loginValue': self.__username, 'password': self.__password}

        r = requests.post(
            'https://ha.registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/guest/login?langPref=en-US',
            headers=headers, json=payload
        )

        if r.status_code != 200:
            raise AuthorizationError("Unable to authorize (status_code={})".format(r.status_code))

        data = r.json()

        if data['error'] is not None:
            raise AuthorizationError("Unable to obtain authorization. Error:\n{}".format(data['error']))

        # Need these for private leagues!
        self.__auth_swid = data['data']['profile']['swid']
        self.__auth_s2 = data['data']['s2']

    def get_league(self, league_id, year):
        """Fetch the League object, passing auth_s2 and auth_swid for a private league."""
        return League(league_id, year, self.__auth_s2, self.__auth_swid)
