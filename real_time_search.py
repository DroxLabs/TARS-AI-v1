import requests
import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_KEY = os.getenv("greg_search_api_key")
search_id = os.getenv('greg_search_engine_id')

def current_data_time():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
 
current_data_time_desc = {
     "name": "current_data_time",
        "description": "get current date time for question for recent this function should be use when user query consist words like recent, latest, last, not right now. This function will be used when you can't answer the query from other function",
        "parameters": {
            "type": "object",
            "properties": {
                    },
            }
    }

def search_online(question):


    url = 'https://www.googleapis.com/customsearch/v1'

    params = {
        'q': question,
        'key': GOOGLE_KEY,
        'cx': search_id
    }
    print('Searching for :', question)

    response = requests.get(url, params=params)
    # print('real tiem search api response', response.json())
    try:
        results = response.json()['items']
        answers = ""
        for item in results:
            answers+=item['snippet']
        return answers
    except KeyError as e:
        return "I am unable to answer your query. can you be more specific"


search_online_desc = {
        "name": "search_online",
        "description": "This function is used to get real world information and current/recent/last/latest events example: when was last bitcoin halving ?, what is bitcoin dominace now?",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "question asked my the user"
                            }
                        },
            "required": [
            "question"
            ]
				}
			}

def main():
    print(search_online('when was the recent bitcoin havling'))

if __name__ =="__main__":
    main()