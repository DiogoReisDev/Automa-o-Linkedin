import subprocess
import time
import requests

def wait_for_flask():
    url = "http://127.0.0.1:5000"
    max_retries = 30
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return
        except requests.ConnectionError:
            pass

        retries += 1
        time.sleep(1)

    raise Exception("Timeout esperando pelo Flask iniciar")

def start_flask():
    subprocess.Popen(["python", "app.py"])

def start_selenium():
    subprocess.Popen(["python", "app_selenium.py"])

if __name__ == "__main__":
    start_flask()   # Inicia o Flask para receber dados do servidor HTTP
    wait_for_flask()  # Aguardando até que o Flask esteja totalmente iniciado
    time.sleep(10) # Espera 10 segundos
    start_selenium()  # Inicia código selenium

