import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import speech_recognition as sr
from google.cloud import texttospeech_v1
import pygame
import random

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "ttsBotServiceAccount.json"
client = texttospeech_v1.TextToSpeechClient()

os.environ['GOOGLE_SST_CREDENTIALS'] = "sttBotServiceAccount.json"

pygame.mixer.init()

'''languages = ["Arabic",
             "Bengali",
             "Chinese",
             "Danish",
             "Dutch",
             "English",
             "Filipino",
             "French",
             "German",
             "Gujarati",
             "Hebrew",
             "Hindi",
             "Hungarian",
             "Indonesian",
             "Italian",
             "Japanese",
             "Kannada",
             "Korean",
             "Malay",
             "Malayalam",
             "Mandarin",
             "Marathi",
             "Norwegian",
             "Polish",
             "Portuguese",
             "Punjabi",
             "Romanian",
             "Russian",
             "Spanish",
             "Swedish",
             "Tamil",
             "Telugu",
             "Turkish",
             "Vietnamese"]'''

languages = ["Arabic",
             "Chinese",
             "Dutch",
             "English",
             "French",
             "German",
             "Hebrew",
             "Hindi",
             "Italian",
             "Japanese",
             "Korean",
             "Malayalam",
             "Polish",
             "Portuguese",
             "Russian",
             "Spanish",
             "Vietnamese"]

language_codes = ["ar-XA-Standard-A",
                  "yue-HK-Standard-B",
                  "nl-NL-Standard-B",
                  "en-GB-Standard-B",
                  "fr-FR-Standard-B",
                  "de-DE-Standard-B",
                  "he-IL-Standard-B",
                  "hi-IN-Standard-B",
                  "it-IT-Standard-B",
                  "ja-JP-Standard-C",
                  "ko-KR-Standard-C",
                  "ml-IN-Standard-B",
                  "pl-PL-Standard-B",
                  "pt-BR-Standard-B",
                  "ru-RU-Standard-B",
                  "es-ES-Standard-B",
                  "vi-VN-Standard-B"]


# templated context for Ollama
template = """
Translate the sentence below into the given langauge. Only respond with the translated text.

Language: {context}

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

def game_loop():
    
    SCORE = 0
    
    print("\n Welcome to THE LANGUAGE GAME\n\n",
          "When you begin an attempt, speak a sentence into the microphone.\n\n",
          "The program will then repeat the sentence, but translated into a random language\n\n",
          "After it is done, say what language you think it was\n\n",
          "If you are correct you get a point!\n\n",
          "Enjoy :)\n")
    
    #read_message(voice, "Welcome to THE LANGUAGE GAME! When you begin an attempt, speak a sentence into the microphone. The program will then repeat the sentence, but translated into a random language. After it is done, type the language you think it is into the console. If you are correct you get a point! Enjoy!")
          
    while True:
        
        print("Current Score: ",SCORE, "\n")
        
        language_idx = random.randint(0, 16)
        language = languages[language_idx]
        voice_name = language_codes[language_idx]
        if language_idx != 1:
            language_code = voice_name[:5]
        else:
            language_code = voice_name[:6]
        
        '''print("IDX: ", language_idx)
        print("Language: ", language)
        print("Voice Name: ", voice_name)
        print("Lang Code: ", language_code)'''
        
        ui = input("Press enter to begin: ")
        if ui == 'exit':
            break
        
        voice.name = voice_name
        voice.language_code = language_code
        
        speech = get_audio()
        
        result = chain.invoke({"context": language, "question": speech})
        #print("Bot: ", result)
        #context += f"\nUser: {user_input}\nAI:{result}"
        read_message(voice, result)
        
        print("Now say what language you think that was")
        user_guess = get_audio()
        #print(user_guess.strip().lower())
        #print(language.lower())
        
        if user_guess.strip().lower() == language.lower():
            print("CORRECT! Good job")
            SCORE = SCORE + 1
        else:
            print("Sorry, but that's incorrect.\nThe correct answer was", language)
    


game_loop()