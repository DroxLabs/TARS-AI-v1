from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
import openai
import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm
import json

load_dotenv()

# Access API key
api_key = os.getenv("OPENAI_KEY_OUTLOOK")
client = OpenAI(
    api_key=api_key,
)

app = FastAPI()


# Enter your Assistant ID here.
ASSISTANT_ID = os.getenv("GPT3-5Assistant_id")
STORE_ID = os.getenv("DROX_LABS_STROE")
# Access API key
# api_key = os.getenv("OPENAI_KEY_OUTLOOK")
client = OpenAI(
    api_key=api_key,
)

@app.post("/upload/")
async def upload_files(files: List[UploadFile]):
	for file in files:
		with open(file.filename, "wb") as buffer:
			buffer.write(await file.read())

	file_streams = [open(file.filename, "rb") for file in files]
	file_names = [file.filename for file in files]
	file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
	vector_store_id=STORE_ID, files=file_streams
	)	
	return {'upload status': file_batch.status, 'upload_files': file_names}	


@app.post("/ask/")
async def ask_question(question: str):
	assistant = client.beta.assistants.update(
	assistant_id=ASSISTANT_ID,
	tool_resources={"file_search": {"vector_store_ids": [STORE_ID]}},
	)
	# Upload the user provided file to OpenAI

	# Create a thread and attach the file to the message
	thread = client.beta.threads.create()
	
	message = client.beta.threads.messages.create(
		thread_id=thread.id,
		role="user",
        content=f"{question}"
	)

	run = client.beta.threads.runs.create_and_poll(
		thread_id=thread.id, assistant_id=assistant.id
	)

	messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

	message_content = messages[0].content[0].text
	return  {"answer": message_content.value}
