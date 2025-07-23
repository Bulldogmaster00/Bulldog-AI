import openai
import speech_recognition as sr
from gtts import gTTS
import os
import re
import time
import pygame
from pygame import mixer
import tempfile
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configuração da API do ChatGPT
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("API key não encontrada. Verifique seu arquivo .env")

# Configuração de áudio
pygame.init()
mixer.init()
mixer.music.set_volume(0.8)  # Volume reduzido para o Pi Zero

# Otimizações para o Raspberry Pi
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  # Ajuste para ambiente com ruído
microphone = sr.Microphone(device_index=0)

def listen_for_wake_word():
    """Ouve até detectar o comando de ativação"""
    print("🔈 Aguardando 'Olá GBT'...")
    with microphone as source:
        while True:
            try:
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=2)
                text = recognizer.recognize_google(audio, language='pt-BR').lower()
                
                if re.search(r'olá\s+(gbt|gpt|jet)', text):
                    return re.sub(r'olá\s+(gbt|gpt|jet)\s*', '', text, flags=re.IGNORECASE).strip()
                    
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                continue
            except Exception as e:
                print(f"Erro no listener: {str(e)}")
                time.sleep(1)

def get_chatgpt_response(prompt):
    """Obtém resposta otimizada para o Pi Zero"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente eficiente para Raspberry Pi. Responda em 1-2 frases."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro: {str(e)}"

def text_to_speech(text):
    """Síntese de voz eficiente para o Pi Zero"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as fp:
            tts = gTTS(text=text, lang='pt-br')
            tts.save(fp.name)
            
            mixer.music.load(fp.name)
            mixer.music.play()
            
            while mixer.music.get_busy():
                time.sleep(0.1)
                
    except Exception as e:
        print(f"Erro no TTS: {str(e)}")

def main_loop():
    """Loop principal otimizado"""
    print("✅ Assistente pronto - Diga 'Olá GBT'")
    text_to_speech("Assistente pronto")
    
    while True:
        try:
            if listen_for_wake_word():
                text_to_speech("Sim, diga sua pergunta")
                
                with microphone as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
                    question = recognizer.recognize_google(audio, language='pt-BR')
                    
                    print(f"🤔 Pergunta: {question}")
                    response = get_chatgpt_response(question)
                    print(f"💡 Resposta: {response}")
                    
                    text_to_speech(response)
                    
        except sr.WaitTimeoutError:
            text_to_speech("Não ouvi sua pergunta")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️ Erro: {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_loop()
    finally:
        mixer.quit()
        pygame.quit()
        print("🔴 Assistente encerrado")
