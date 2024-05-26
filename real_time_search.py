import requests
import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_KEY = os.getenv("GOOGLE_SEARCH_API")
search_id = os.getenv('SEARCH_ENGINE_ID')


def search_online(question):


    url = 'https://www.googleapis.com/customsearch/v1'

    params = {
        'q': question,
        'key': GOOGLE_KEY,
        'cx': search_id
    }

    response = requests.get(url, params=params)
    results = response.json()['items']
    answers = ""
    for item in results:
        answers+=item['snippet']
    return answers


search_online_desc = {
        "name": "search_online",
        "description": "get the most recent and latest data from web",
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