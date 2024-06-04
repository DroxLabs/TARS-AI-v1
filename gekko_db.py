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
        retrieve_data = {}
        try:
            retrieve_data['id'] = respose['id']
            retrieve_data['symbol'] = respose['symbol']
            retrieve_data['name'] = respose['name']
            retrieve_data['block_time_in_minutes'] = respose['block_time_in_minutes']
            retrieve_data['hashing_algorithm'] = respose['hashing_algorithm']
            retrieve_data['description'] = respose['description']['en']
            retrieve_data['market_data']={
                'current_price': respose['market_data']['current_price'],
                'total_volume': respose['market_data']['total_volume'],
                'market_cap': respose['market_data']['market_cap']
            }

            return retrieve_data
        
        except KeyError as e:
            print(f"Error: {e}")
            return "I am unable to answer your query. can you be more specific"
    
    def get_coin_historical_data_by_id(self, coin_id='bitcoin',date='01-01-2024'):
        endpoint = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/history?date={date}"
        response = self._make_request(endpoint)
        response = response['market_data']
        return response
    
    get_coin_historical_data_by_id_desc = {
        "name": "get_coin_historical_data_by_id",
        "parameters": {
            "type": "object",
            "properties": {
                "coin_id": {
                    "type": "string",
                    "description": "unique id for coin"
                },
                "date": {
                    "type": "string",
                    "description": "date in Format: dd-mm-yyyy"
                    },
                
            },
                    "required": [
                    "coin_id",
                    'date'
                    ]

            }       
        }       
    
    def get_coin_historical_chart_data_by_id(self,coin_id='bitcoin', currency='USD',days=5, interval='daily', precision=3, data_type='price'):
        endpoint = f"https://pro-api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={currency}&days={days}&interval={interval}&precision={precision}"
        response = self._make_request(endpoint)
        return response
    
    
    get_coin_historical_chart_data_by_id_desc = {
        "name": "get_coin_historical_chart_data_by_id",
        "parameters": {
            "type": "object",
            "properties": {
            "coin_id": {
                "type": "string",
                "description": "unique id for coin"
            },
            "days": {
                "type": "integer",
                "description": "number of days of historical data"
            },
            "interval": {
                "type": "string",
                "description": "interval of historical data"
            },
            "precision": {
                "type": "integer",
                "description": "precision of historical data"
            },
            
            "currency": {
                    "type": "string",
                    "description": "currency of historical data"
                },
            "data_type": {
                "type": "string",
                "description": "can be a market_caps, prices , total_volumes of a coin "
            }
            
        },
        "required": [
            "coin_id",
            "days",
            "data_type",
            'interval',
            ]
        },
        "description": "get historical chart to help user make a chart data related to crypto currency from CoinGecko coin page based on a particular coin id"
    }



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

    def get_trend_search(self):
        """
        Fetches the list of all threading coins NTF and platforms.
        """
        endpoint = "https://pro-api.coingecko.com/api/v3/search/trending"
        response = self._make_request(endpoint)
        data = {'coins': []}
        for coin in  response['coins']:
            data['coins'].append({'coin': coin['item']['id'], 'name': coin['item']['name'], 'description': coin['item']['data']['content']})
        data['nfts'] = []
        for nft in  response['nfts']:
            data['nfts'].append({'id': nft['id'], 'name': nft['name'], 'symbol': nft['symbol'],'nft_contract_id': nft['nft_contract_id']})
        data['categories'] = []
        for category in  response['categories']:
            data['categories'].append({'id': category['id'], 'name': category['name'], 'slug': category['slug']})

        return data
    
    get_trend_search_desc ={
        "name": "get_trend_search",
        "description": "get all the trending coins, nft and categories",
        "parameters": {
            "type": "object",
            "properties": {
                "dummy_property": {
                    "type": "null",
                }
            }
        }

    }
    

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
    # coin_info = gekko_db.get_coin_historical_chart_data_by_id('bitcoin', interval='hourly')
    # coin_info = gekko_db.get_coin_data_by_id('bitcoin')
    coin_info = gekko_db.get_trend_search()
    print(coin_info)
