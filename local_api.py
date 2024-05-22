from fastapi import FastAPI,  Response
import time
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from gekko_db import GekkoDB
from tokenizer import tokenize_string
import json
import logging
logger = logging.getLogger(__name__)

load_dotenv()

# Access API key
ASSISTANT_ID = os.getenv("GPT3-5Assistant_id")
api_key = os.getenv("OPEN_AI_KEY_MY")
GEKKO_API_KEY = os.getenv("GEKKO_API_KEY")
client = OpenAI(
    api_key=api_key,
)

app = FastAPI()

gekko_client = GekkoDB(GEKKO_API_KEY)

# Enter your Assistant ID here.
# print(ASSISTANT_ID,'...............')
STORE_ID = os.getenv("OPENAI_STORE_ID")
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
		}

		]

assistant = client.beta.assistants.update(
	assistant_id=ASSISTANT_ID,
	tool_resources={"file_search": {"vector_store_ids": [STORE_ID]}},
	tools = tools_list,
	)

def get_outputs_for_tool_call(tool_call):
	coin_id = json.loads(tool_call.function.arguments['coin_id'])
	details = gekko_client.get_coin_data_by_id(coin_id)
	return {"tool_call_id": tool_call.id,
		 "output": details
		 }



@app.post("/ask/")
async def ask_question(question: str, user_id: str, thread_id: str=None):

	if len(tokenize_string(question)) > 200:
		return Response(status_code=200, content="Question is too long. Please shorten your question and try again.")

	
	# Upload the user provided file to OpenAI

	# Create a thread and attach the file to the message
	if thread_id:
		print(thread_id, 'received thread')
		thread = client.beta.threads.retrieve(thread_id)
	else:
		thread = client.beta.threads.create()
		print(thread.id, 'creating thread')

	
	message = client.beta.threads.messages.create(
		thread_id=thread.id,
		role="user",
        content=f"{question}",

	)

	run = client.beta.threads.runs.create_and_poll(
		thread_id=thread.id, assistant_id=assistant.id,
		instructions="Please address yourself as Alex an assistant who helps users with their questions and don't answer more than 250 words "
	)


	while True:
		print('in loop')
		time.sleep(4)
		run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
   		)

		if run_status.status == 'completed':
			messages = client.beta.threads.messages.list(thread_id=thread.id)
			for msg in messages.data:
				try:
					content = msg.content[0].text.value
					return {'answer':content}
				except:
					print(msg.content[0].image_file.file_id)
					img_file_id = msg.content[0].image_file.file_id
					image_file = client.files.content(img_file_id)
					image_data_bytes = image_file.read()
					headers = {"Content-Type": "image/jpeg"}

					text = msg.content[1].text.value
					return Response(content=image_data_bytes, headers=headers)
				
			break
		elif run_status.status == 'requires_action':
			print("Function Calling")
			required_actions = run_status.required_action.submit_tool_outputs.model_dump()
			tool_outputs = []
			import json
			for action in required_actions["tool_calls"]:
				func_name = action['function']['name']
				arguments = json.loads(action['function']['arguments'])
				print(func_name, arguments)
				if func_name == "get_coin_data_by_id":
					output = gekko_client.get_coin_data_by_id(coin_id=arguments['coin_id'])
					tool_outputs=[
								{
								"tool_call_id": action['id'],
								"output": f'query: {output}'
								}
							]
				
				elif func_name == "get_coin_historical_data_by_id":
					output = gekko_client.get_coin_historical_data_by_id(coin_id=arguments['coin_id'], days=arguments['days'], interval=arguments['interval'])
					tool_outputs=[
                                {
                                "tool_call_id": action['id'],
                                "output": f'query: {output}'
                                }
                            ]
				elif func_name == "get_trend_search":
					output = gekko_client.get_trend_search()
					tool_outputs=[
                                {
                                "tool_call_id": action['id'],
                                "output": f'query: {output}'
                                }
                            ]
				else:
					raise ValueError(f"Unknown function: {func_name}")
				print("Submitting outputs back to the Assistant...")
				client.beta.threads.runs.submit_tool_outputs(
					thread_id=thread.id,
					run_id=run.id,
					tool_outputs=tool_outputs
				)
			else:
				print("waiting for outputs...")
				time.sleep(3)


	# messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

	# thread = client.beta.threads.retrieve(thread.id)

	# message_content = messages[0].content[0].text
	# return  {"answer": message_content.value, "thread_id": thread.id}