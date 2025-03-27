import speech_recognition as sr
from googletrans import Translator
import tkinter as tk
from tkinter import ttk
import requests
import threading
import os

# Configuração do Ollama
ollama_host = os.getenv("OLLAMA_HOST", "localhost")  # Usa 'ollama' na rede Docker ou 'localhost' localmente
ollama_url = f"http://localhost:7869/api/generate"

# Configuração inicial
recognizer = sr.Recognizer()
translator = Translator()

# Função para capturar e processar áudio
def listen_and_process(source, text_box, get_lang_from, get_lang_to):
    with source as s:
        # Ajuste inicial do microfone para ruído ambiente
        recognizer.adjust_for_ambient_noise(s, duration=1)
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, "Aguardando áudio...\n")
        
        while True:
            try:
                audio = recognizer.listen(s, timeout=None)
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, "Processando áudio...\n")
                
                # Reconhecimento de fala
                text = recognizer.recognize_google(audio, language=get_lang_from())
                translated = translator.translate(text, src=get_lang_from(), dest=get_lang_to()).text
                
                # Exibir legenda
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, f"Original: {text}\nTraduzido: {translated}")
                
                # Enviar para Ollama (resumo simples)
                ollama_response = get_ollama_response(text)
                text_box.insert(tk.END, f"\nResumo (IA): {ollama_response}")
            except sr.UnknownValueError:
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, "Não consegui entender o áudio.\n")
            except sr.RequestError as e:
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, f"Erro na API de reconhecimento: {str(e)}\n")
            except Exception as e:
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, f"Erro: {str(e)}\n")

# Comunicação com Ollama
def get_ollama_response(text):
    payload = {
        "model": "gemma3:1b",  # Usando tinyllama para menos memória, ajuste conforme necessário
        "prompt": f"Resuma este texto: {text}",
        "stream": False
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("response", "Erro ao processar")
    except requests.RequestException as e:
        return f"Erro ao conectar ao Ollama: {str(e)}"

# Interface gráfica
root = tk.Tk()
root.title("LiveTranslate Assistant - MVP")
root.geometry("600x400")

# Seleção de idiomas
langs = ["en", "pt", "es"]
lang_from = tk.StringVar(value="pt")
lang_to = tk.StringVar(value="en")

tk.Label(root, text="Idioma Falado:").pack()
ttk.Combobox(root, textvariable=lang_from, values=langs).pack()
tk.Label(root, text="Idioma Traduzido:").pack()
ttk.Combobox(root, textvariable=lang_to, values=langs).pack()

# Área de texto
text_box = tk.Text(root, height=15, width=70)
text_box.pack(pady=10)

# Iniciar captura de áudio em uma thread separada
mic = sr.Microphone()
thread = threading.Thread(
    target=listen_and_process,
    args=(mic, text_box, lambda: lang_from.get(), lambda: lang_to.get()),
    daemon=True
)
thread.start()

root.mainloop()