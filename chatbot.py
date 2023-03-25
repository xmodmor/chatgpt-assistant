import os
import openai
import pymongo
from speech_recognition import Recognizer, Microphone
from dotenv import load_dotenv
import datetime 
from pprint import pprint
import inquirer

load_dotenv()

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client[os.getenv("MONGODB_DATABASE_NAME")]
collection = db[os.getenv("MONGODB_COLLECTION_NAME")]

# Check the connection to MongoDB
try:
    client.server_info() # test the connection by fetching server info
    print("Connected to MongoDB successfully!")
except:
    print("Error: Could not connect to MongoDB.")


# Set up OpenAI API key and model ID
openai.api_key = os.getenv("OPENAI_API_KEY")
engine_model = os.getenv("OPENAI_MODEL_ENGINE")


# Retrieve all conversations from the collection
conversations = collection.find()
conversation_list=[None]

# get each choices
for conversation in conversations:
    conversation_list.append(conversation["_id"])
    
conversation_opt = [
    inquirer.List(
        "id",
        message="Do you continue the past conversation?",
        choices=conversation_list,
    ),
]
selected_conversation = inquirer.prompt(conversation_opt)

# Define function to send message to ChatGPT and store conversation in MongoDB
def chat(message, conversation_id=None):
    message_history = []
    response_history = []
    final_prompt =[]

    if conversation_id:
        # If conversation ID is provided, retrieve the conversation from MongoDB
        conversation = collection.find_one({"_id": conversation_id})
        print(conversation)
        message_history = conversation["message_history"]
        response_history = conversation["response_history"]
        
        #final_prompt.append({"role": "system", "content": "You are a helpful assistant that translates English to French."})
    if message_history:
        for index, val in enumerate(message_history):
            final_prompt.append({"role": "user", "content": val})
            final_prompt.append({"role": "assistant", "content": response_history[index]})
            final_prompt.append({"role": "user", "content": message})
    else:
        final_prompt.append({"role": "user", "content": message})

    # Send prompt to ChatGPT
    result = openai.ChatCompletion.create(
        model=engine_model,
        messages=final_prompt,
        # max_tokens=1024,
        # n=1,
        # stop=None,
        # temperature=0.7,
        # frequency_penalty=0,
        # presence_penalty=0,
    )

    # Extract response from result and update conversation history
    response = result.choices[0].message.content.strip()
    message_history.append(message)
    response_history.append(response)

    # Store conversation in MongoDB
    time_now = datetime.datetime.utcnow()
    conversation = {
        "message_history": message_history,
        "response_history": response_history,
        "status": "ongoing",
        "finish_reason": result.choices[0].finish_reason,
        "updated_at": time_now,
    }
    if conversation_id:
        collection.update_one({"_id": conversation_id}, {"$set": conversation})
    else:
        conversation_id = collection.insert_one(conversation).inserted_id

    return response, conversation_id

# Define function to end an ongoing conversation
def end_conversation():
    existing_conversation = collection.find_one({"status": "ongoing"})
    if existing_conversation:
        collection.update_one({"_id": existing_conversation["_id"]}, {"$set": {"status": "ended"}})
        print("Conversation ended.")


# Define function to convert speech to text using Persian language model
def speech_to_text():
    recognizer = Recognizer()
    microphone = Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        message = recognizer.recognize_google(audio, language='fa-IR')
        print("You:", message)
        return message
    except Recognizer.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return ""
    except Recognizer.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

# Test the chat function
conversation_id = selected_conversation["id"]
while True:
    # Prompt the user to speak or type a message
    input_type = input("Type 'text' to type a message or 'voice' to speak: ")
    if input_type.lower() == "voice":
        message = speech_to_text()
    else:
        message = input("You: ")

    if message.lower() == "end":
        end_conversation()
        break
    if message.lower() == "exit":
        end_conversation()
        break
    elif message:
        response, conversation_id = chat(message, conversation_id)
        print("Bot:", response)
