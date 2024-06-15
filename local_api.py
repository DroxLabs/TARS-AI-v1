from fastapi import FastAPI,  Response, Header
import time
import os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import json
from gekko_db import GekkoDB
from tokenizer import tokenize_string
from real_time_search import search_online, search_online_desc, current_data_time
from mongo_store import MongoStore
import json
from datetime import datetime as dt

load_dotenv()

# Access API key
ASSISTANT_ID = os.getenv("new_tars_assistant")
api_key = os.getenv("new_tars_key")
GEKKO_API_KEY = os.getenv("GEKKO_API_KEY")
client = OpenAI(
    api_key=api_key,
)
AUTH_TOKEN = os.getenv("AuthToken")
mongo_pass = os.getenv("mongo_pass")
mongo_store = MongoStore(f'mongodb+srv://abdul_samad:{mongo_pass}@tars-backend.fvg1suu.mongodb.net/')
DAILY_LIMIT = float(os.getenv('daily_limit'))

app = FastAPI()

gekko_client = GekkoDB(GEKKO_API_KEY)
# Enter your Assistant ID here.
# print(ASSISTANT_ID,'...............')
STORE_ID = os.getenv("new_tars_db")
# Access API key
# api_key = os.getenv("OPENAI_KEY_OUTLOOK")
client = OpenAI(
    api_key=api_key,
)
tools_list = [
		
		{
			"type": "function",
			"function":gekko_client.get_coin_data_by_id_desc
		},

		{
			"type": "function",
			"function": gekko_client.get_coin_historical_chart_data_by_id_desc
        },

		{
			"type": "function",
			"function": gekko_client.get_trend_search_desc
		},
		{
			"type": "function",
			"function": gekko_client.get_coin_historical_data_by_id_desc
		},
		{
			"type": "function",
			"function": gekko_client.draw_graph_desc
		},
		{
			"type":"function",
			"function": search_online_desc
		}
		]
renew = False
assistant = client.beta.assistants.update(
	assistant_id=ASSISTANT_ID,
	tool_resources={"file_search": {"vector_store_ids": [STORE_ID]}},
	tools = tools_list,
	instructions = f"""
				Identity: Please address yourself as "Alex", a Web3 assistant created by TARS AI.
				Date:  Today's date is {current_data_time()} and dont answer question if they ask for information about the future.
				Answer Length:  Limit your responses to a maximum of 250 words, ensuring answers are concise, relevant, and directly address the user's query.
				Rule1: Do not forecast or predict future values; base all information strictly on available data as of the {current_data_time()}.
				Rule2:  If the user asks you to plot a graph or vizualize data just  day here you go dont give textual answer.
				Rule3:  Do not add any links to website of images in your answer.
				Rule4:  For recent information requests, always retrieve data from the appropriate function or online sources, avoiding reliance on memory for up-to-date information
				Rule5:  Explain technical terms simply and clearly.Maintain a professional and helpful tone, using simple and direct language to ensure user comprehension.
				Rule6: 	Never Forget your Identity "Alex", a Web3 assistant created by TARS AI
				Note: Follow these RULES strictly to maintain consistency across all responses	
				"""	)

def get_outputs_for_tool_call(tool_call):
	coin_id = json.loads(tool_call.function.arguments['coin_id'])
	details = gekko_client.get_coin_data_by_id(coin_id)
	return {"tool_call_id": tool_call.id,
		 "output": details
		 }



DATA = None

def add_message_to_thread(thread, user_question):
	# Create a message inside the thread
	try:
		message = client.beta.threads.messages.create(
			thread_id=thread.id,
			role="user",
			content= user_question
		)
		print("thread id presisted")
		renew = False
	except Exception as e:
		thread = client.beta.threads.create()
		message = client.beta.threads.messages.create(
			thread_id=thread.id,
			role="user",
			content= user_question
		)
		print("Run broken create new thread id")
		print(e)
		renew = True
	return message, thread, renew


def calculate_overall_price(input_tokens_used, output_tokens_used, rate_per_million_input=0.50, rate_per_million_output=1.50):
    # Calculate the price for input and output separately
    input_price = rate_per_million_input / 1000000 * input_tokens_used
    output_price = rate_per_million_output / 1000000 * output_tokens_used
    # Calculate the total price
    total_price = input_price + output_price
    return total_price


@app.post("/ask/")
async def ask_question(question: str, user_id: str, auth_token: str | None = Header(None), datetime: str | None = Header(None), thread_id: str=None):
	total_cost = mongo_store.get_total_cost_for_day(dt.now())
	print("current total cost:", total_cost, "current daily limit:", DAILY_LIMIT)
	if total_cost >= DAILY_LIMIT:
		return Response(status_code=412, content="Oops seems like we have reached a limit!")
	else:
		print("today's total cost:", total_cost )
	if auth_token != AUTH_TOKEN:
		return Response(status_code=200, content="Invalid Token!")

	if len(tokenize_string(question)) > 200:
		return Response(status_code=200, content="Question is too long. Please shorten your question and try again.")

	try:
		if thread_id is not None:
			print(thread_id, 'received thread')
			thread = client.beta.threads.retrieve(thread_id)
		else:
			thread = client.beta.threads.create()
			print(thread.id, 'creating thread')
	except Exception as e:
		thread = client.beta.threads.create()
		print(thread.id, 'could not retrive the provided thread making a new one')
		print(e)
	
	_, thread, renew = add_message_to_thread(thread, question)
	current_date = datetime if datetime else current_data_time()
	run = client.beta.threads.runs.create_and_poll(
		thread_id=thread.id, assistant_id=assistant.id,
		instructions = f"""
				Identity: Please address yourself as "Alex", a Web3 assistant created by TARS AI.
				Date:  Today's date is {current_date} and dont answer question if they ask for information about the future.
				Answer Length:  Limit your responses to a maximum of 250 words, ensuring answers are concise, relevant, and directly address the user's query.
				Rule1: Do not forecast or predict future values; base all information strictly on available data as of the {current_date}.
				Rule2:  If the user asks you to plot a graph or vizualize data just  day here you go dont give textual answer.
				Rule3:  Do not add any links to website of images in your answer.
				Rule4:  For recent information requests, always retrieve data from the appropriate function or online sources, avoiding reliance on memory for up-to-date information
				Rule5:  Explain technical terms simply and clearly.Maintain a professional and helpful tone, using simple and direct language to ensure user comprehension.
				Rule6: 	Never Forget your Identity "Alex", a Web3 assistant created by TARS AI
				Note: Follow these RULES strictly to maintain consistency across all responses	
					"""	)

	output = "NULL"
	called_functions = []
	CHART_DATA = False
	chart = False
	if any(item in ['chart', 'plot','Chart','Plot', 'graph', 'Graph', 'visualize'] for item in  question.split(' ')):
		chart = True
	def call_tools(run,thread):
		print("status at the start:",run.status)
		while run.status == "queued" or run.status == "in_progress":
			print("run status right now:",run.status)
			
			run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
			print('waiting for function response...')
			time.sleep(0.25)
		
		if run.status == 'failed':
			if run.last_error.code == 'rate_limit_exceeded':
				return {'answer': "Opps looks like we have reached a limit!", "rate_limit_reached": True}
			else:
				return  {'answer':"I am unable to understand your question can you be more specific?", "thread_id":thread.id}
		
		if run.status == 'requires_action':
			tool_outputs = []
			
			tool_calls = list(run.required_action.submit_tool_outputs.tool_calls)
			print("tool calls:", tool_calls)
			print(f'\nASSISTANT REQUESTS {len(tool_calls)} TOOLS:')
			
			for tool_call in tool_calls:
				tool_call_id = tool_call.id
				print("tool call id:", tool_call_id)
				print("run id:", run.id)
				name = tool_call.function.name
				called_functions.append(name)
				arguments = json.loads(tool_call.function.arguments)
				print(f"Assistant requested {name}: {arguments}")

				if name == "search_online":
					output = search_online(question=arguments['question'])
					tool_outputs.append({"tool_call_id": tool_call_id, "output": json.dumps(output)})

				elif name == "draw_graph":
					print(f"data for draw graph -> {arguments.get('chart',False)}")
					output = gekko_client.draw_graph(arguments.get('chart',False))
					tool_outputs.append({"tool_call_id": tool_call_id, "output": 'find the chart below' if output else ""})

				else:
					
					output = getattr(gekko_client, name)(**arguments)
					print(output)
					tool_outputs.append({"tool_call_id": tool_call_id, "output": json.dumps(output)})
					if name == 'get_coin_historical_chart_data_by_id':
						global DATA
						DATA = output

				print(f'Returning {output}')	
			print("Submitting outputs back to the Assistant...")
			print(f'tools output: {tool_outputs}')
			run = client.beta.threads.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)
			print("run id:", run.id)
			print("run status:", run.status)
			call_tools(run,thread)
		return run
	run = call_tools(run,thread)
	
	print("status after submission", run.status)

	print('status outside loop:', run.status)
	try: 
		cost = calculate_overall_price(run.usage.prompt_tokens, run.usage.completion_tokens)
	except Exception as e:
		cost = 0 
		print("Issue ouccered while calculating cost for query", e)
	try: 
		mongo_store.add_cost(cost, question, user_id)
	except Exception as e:
		print('Issue ouccered while adding price to mongo db', e)
	messages = client.beta.threads.messages.list(thread_id=thread.id)
	for msg in messages.data:
		try:	
			content = msg.content[0].text.value
			print('Function name', called_functions)
			print(content)
			print(DATA, chart)
			if DATA and chart:
				return {'answer':content, "thread_id":thread.id, "function":called_functions,"chart": chart, 'data': DATA, 'is_thread_id_new': renew, 'cost': cost }
			else:
				return {'answer':content, "thread_id":thread.id, "function":called_functions,"chart": chart, 'data': "NULL", 'is_thread_id_new': renew, 'cost': cost }

		except Exception as e: 
			print('issue occured', e)
			return {'answer':"I am unable to answer your query.", "thread_id":thread.id}