import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import speech_recognition as sr
from google.cloud import texttospeech_v1
import pygame

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "ttsBotServiceAccount.json"
client = texttospeech_v1.TextToSpeechClient()

os.environ['GOOGLE_SST_CREDENTIALS'] = "sttBotServiceAccount.json"

pygame.mixer.init()

# templated context for Ollama
template = """
Answer the question below. Try to keep your responses brief. Less than 2 short paragraphs is good.

Here is the conversation history: {context}

Question: {question}

Answer: 
"""

model = OllamaLLM(model="llama3.1")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""
        
        try:
            said = r.recognize_google_cloud(audio, credentials_json=os.environ['GOOGLE_SST_CREDENTIALS'])
            print(said)
        except Exception as e:
            print("Exception: " + str(e))
    
    return said

# TTS STUFF

sample_text = "a"

voice = texttospeech_v1.VoiceSelectionParams(
    name='en-US-Standard-B',
    language_code = 'en-US'
    #name='ja-JP-Standard-B',
    #language_code='ja-JP'
)

audio_config = texttospeech_v1.AudioConfig(
    audio_encoding=texttospeech_v1.AudioEncoding.MP3
)

def read_message(voice_input, message) :
    synthesis_input = texttospeech_v1.SynthesisInput(text = message)
    
    response = client.synthesize_speech(
        input = synthesis_input,
        voice = voice_input,
        audio_config=audio_config
    )
    
    with open('message.mp3', 'wb') as output1:
        output1.write(response.audio_content)

    pygame.mixer.music.load('message.mp3')
    pygame.mixer.music.set_volume(0.9)
    pygame.mixer.music.play()

    busy = True
    while busy == True:
        if pygame.mixer.music.get_busy() == False:
            busy = False

    os.remove('message.mp3')
    
def handle_conversation():
    context = ""
    print("Welcome to the AI Chatbot!\nType 'exit' to quit\n")
    while True:
        user_input = input("Press enter to start speaking or type exit to stop: ")
        if user_input.lower() == "exit":
            break
        
        speech = get_audio()
        
        result = chain.invoke({"context": context, "question": speech})
        print("Bot: ", result)
        context += f"\nUser: {user_input}\nAI:{result}"
        read_message(voice, result)


handle_conversation()