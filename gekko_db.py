import requests
from dotenv import load_dotenv
import os


class GekkoDB:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://pro-api.coingecko.com/api/v3"
        # Call the parse_file() function during initialization
        self.supported_currencies_list = self.parse_file(endpoint = "https://pro-api.coingecko.com/api/v3/simple/supported_vs_currencies")
        self.coin_list_id_map = self.parse_file(endpoint = "https://pro-api.coingecko.com/api/v3/coins/list")
        self.platform_list_id_map = self.parse_file(endpoint = "https://pro-api.coingecko.com/api/v3/asset_platforms")

    def parse_file(self, endpoint):
        response = self._make_request(endpoint)
        return response

    def _make_request(self, endpoint, params=None):
        headers = {
            "accept": "application/json",
            "x-cg-pro-api-key": self.api_key,
        }
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()
    
    def get_coin_list_id_map(self, coin_name):
        for crypto in self.coin_list_id_map:
            if crypto['name'].lower() == coin_name.lower():
                return crypto['id']
        return None
    
    get_coin_list_id_map_desc = {
        "name": "get_coin_list_id_map",
        "description": "query coin id against coin namefrom a list of dictionaries",
        "parameters": {
            "type": "object",
            "properties": {
                "coin_name": {
                    "type": "string",
                    "description": "name of a coin to retrieve it's id"
                            }
                        },
            "required": [
            "coin_name"
            ]
				}
			}


    def get_coin_list(self):
        """
        Fetches the list of all supported coins from CoinGecko.
        """
        endpoint = "https://pro-api.coingecko.com/api/v3/coins/list"
        return self._make_request(endpoint)
    
    get_coin_data_by_id_desc = {
        "name": "get_coin_data_by_id",
        "description": "query all the coin data of a coin on CoinGecko coin page based on a particular coin id",
        "parameters": {
            "type": "object",
            "properties": {
                "coin_id": {
                    "type": "string",
                    "description": "unique id for coin"
                            }
                        },
            "required": [
            "coin_id"
            ]
				}
        }
    
    def get_coin_data_by_id(self, coin_id):
        """
        Fetches detailed information about a specific coin by its ID.
        """
        endpoint = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/"

        respose = self._make_request(endpoint)
        retrieve_data = ['id','symbol','name','block_time_in_minutes','hashing_algorithm', 'market_data','description']
        filtered_respose = {key: respose[key] for key in retrieve_data if key in respose}


        return filtered_respose



    def get_coin_info(self, coin_id,currency='USD', include_maket_cap=False, include_24hr_vol=False, include_24hr_change=False, include_last_updated_at=False):
        """
        Fetches detailed information about a specific coin by its ID.
        """
        endpoint = "https://pro-api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, 'vs_currencies': 'USD'}
        params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "include_market_cap": False,
        "include_24hr_vol": False,
        "include_24hr_change": False,
        "include_last_updated_at": False,
        }
        return self._make_request(endpoint,params)

    # Add more methods for other specific API endpoints as needed



if __name__ == "__main__":
    load_dotenv()
    GEKKO_API_KEY = os.getenv("GEKKO_API_KEY")
    # Example usage
    gekko_db = GekkoDB(GEKKO_API_KEY)
    # # Get the list of all coins
    # coin_list = gekko_db.get_coin_list()
    # print("List of coins:")
    # for coin in coin_list:
    #     print(f"{coin['id']}: {coin['name']} ({coin['symbol']})")

    # Get detailed info for a specific coin (e.g., Bitcoin)
    bitcoin_info = gekko_db.get_coin_data_by_id("bitcoin")
    print("Bitcoin info", bitcoin_info)
    print("\nBitcoin Info:")
    print(bitcoin_info)
    print(f"Name: {bitcoin_info['name']}")
    print(f"Symbol: {bitcoin_info['symbol']}")
    print(f"Description: {bitcoin_info['description']['en']}")
