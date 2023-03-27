Chatbot with OpenAI and MongoDB
===============================

This is a simple chatbot project that uses OpenAI's GPT-3.5 architecture for natural language processing and MongoDB for storing conversation history. The chatbot can process text input or speech input using Google's Speech Recognition API, and responds with text output.

Installation
------------

1.  Clone this repository
2.  Install the required Python packages using pip:

Copy code

`python -m venv env`

`.\env\Scripts\activate`

`pip install -r requirements.txt`

3.  Create a `.env` file in the root directory of the project and add the following variables:

makefileCopy code

`OPENAI_API_KEY=<your OpenAI API key> MONGODB_DATABASE_NAME=<name of your MongoDB database> MONGODB_COLLECTION_NAME=<name of your MongoDB collection>`

4.  Install PyAudio (required for speech input):

Copy code

`pip install pyaudio`

Usage
-----

1.  Run the `app.py` script:

Copy code

`python app.py`

2.  Choose whether to use text or voice input by typing "text" or "voice" at the prompt.
3.  Type or speak your message.
4.  The chatbot will respond with a message.
5.  To exit the chatbot, type "exit" at the prompt.

Contributing
------------

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
-------

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
