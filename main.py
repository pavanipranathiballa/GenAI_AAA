#Personal Siri: Voice/chat Assistant using LLM

import streamlit as st

#configure the app page
st.set_page_config(
    page_title="Personal SIRI",
    layout="wide"
)

#import other require libraries

import os #access the API key from local env
#import time 
import pyttsx3 #convert text to speech 
import speech_recognition as sr #convert speech to text
from groq import Groq #help to convert with the online LLM
from dotenv import load_dotenv #import the data from local environment(load the API key from local environment)

# load the key inside code from local env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Checking API Key availlable or not
if not GROQ_API_KEY:
    st.error("Missing Groq API key")
    st.stop()

#initialize the LLM model
client = Groq(api_key= GROQ_API_KEY)
MODEL = "openai/gpt-oss-20b"

# Initilize Speech to text recognizer
@st.cache_resource
def get_recognizer():
    return sr.Recognizer()
recognizer = get_recognizer()

#initialize text to speech
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        st.error(f'Failed to initialize the TTS engine: {e}')
        return None

#This will activate the icrophone on laptop, record voice and covert to text
def listen_to_speech():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, phrase_time_limit=10)

        text = recognizer.recognize_google(audio) #convert audio to text
        return text.lower()
    except sr.UnknownValueError:
        return "Sorry, I couldn't catch you"
    except sr.RequestError:
        return "Speech service not available"
    except Exception as e:
        return f"Error: {e}"

def gen_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model= MODEL,
            messages = messages,
            temperature = 0.7
        )
        result = response.choices[0].message.content
        return result.strip() if result else "Sorry, I could not generate the response"
    except Exception as e:
        return f"Error getting AO respnse: {e}"

def speak(text, voice_gender = "girl"):
    try:
        engine = get_tts_engine()
        if engine is None:
            return
        voices = engine.getProperty('voices')
        if voices:
            if voice_gender == "boy":
                for voice in voices:
                    if "male" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            else:
                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
        engine.setProperty('rate', 150) #bigger value fast that will speak
        engine.setProperty('volume',0.8) 
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error(f"TTS Error: {e}")

def main():
    st.title("Personal SIRI Voice Assistant")
    st.markdown("---")

    #creating a list of chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content" : "You are helpful voice and chat assisstant. Reply answer in just one line"}
        ]
    #list of message to show on the screen 
    if "messages" not in st.session_state:
        st.session_state.messages = []
    with st.sidebar:
        st.header("CONTROLS")
        tts_enabled = st.checkbox("Enable Text to Speech")

        voice_gender = st.selectbox(
            "Voice Gender",
            options = ['girl', 'boy'],
            index = 0,
            help = "This option is to decide the AI voice"
        )

        if st.button("START", type = "primary", use_container_width=True):
            with st.spinner("Listening..."):
                user_input = listen_to_speech() #Task1 : Recieve the voice
                if user_input and user_input not in ["Sorry, I couldn't catch you", "Speech service not available"]:
                    st.session_state.messages.append({"role": "user", "content":user_input})
                    st.session_state.chat_history.append({'role': "user", "content":user_input})

                    #Get LLM reply
                    with st.spinner("Thinking..."):
                        ai_response = gen_ai_response(st.session_state.chat_history)
                        st.session_state.messages.append({"role": "assistant", "content":ai_response})
                        st.session_state.chat_history.append({'role': "assistant", "content":ai_response})

                    if tts_enabled:
                        speak(ai_response, voice_gender)

                    st.rerun()


        #Sending the mssg to LLM with Text box
        st.markdown("Text input")
        user_text = st.text_input("Type your message: ", key = "text_input")
        if st.button("SEND", type="primary", use_container_width=True) and user_text:
            st.session_state.messages.append({"role": "user", "content":user_text})
            st.session_state.chat_history.append({'role': "user", "content":user_text})

            #Get LLM reply
            with st.spinner("Thinking..."):
                ai_response = gen_ai_response(st.session_state.chat_history)
                st.session_state.messages.append({"role": "assistant", "content":ai_response})
                st.session_state.chat_history.append({'role': "assistant", "content":ai_response})
            
            if tts_enabled:
                speak(ai_response, voice_gender)
            
            st.rerun()
        st.markdown("---")
        #We will add a button to clean all the previous conversations
        if st.button("Clear Chat", type = "primary"):
            st.session_state.messages = []
            st.session_state.chat_history = [
                {"role": "system", "content" : "You are helpful voice and chat assisstant. Reply answer in just one line"}
            ]
            st.rerun()

    st.subheader("CONVERSATION")

    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    #in start add welcome message
    if not st.session_state.messages:
        st.info("Welcome! to the chatbot. Click on Start button to start a convo")

    #Copyright

    st.markdown("---")
    st.markdown(
        """
        <div style = "text_align: center, color: #666;">
            <p> Chatbot & Voice assistant powerd by Groq, streamlit. copyright @pranathi </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
