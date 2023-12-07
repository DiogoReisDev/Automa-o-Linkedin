from flask import Flask, render_template, request, jsonify, make_response
import sqlite3
import subprocess
import requests
from flask_cors import CORS
import time
from app_selenium import *

app = Flask(__name__)
CORS(app, methods=["POST"], origins="http://127.0.0.1:5500")

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect("linkedin_bd.sqlite")
    cursor = conn.cursor()
    return conn, cursor

# Função para enviar dados ao Selenium
def enviar_dados_selenium(email, senha, palavras_chave, texto_personalizado):
    # Modifique o URL conforme necessário
    url_selenium = "http://localhost:5001/receber_dados_selenium"
    
    dados = {
        "email": email,
        "senha": senha,
        "palavras_chave": palavras_chave,
        "texto_personalizado": texto_personalizado
    }
    try:
        response = requests.post(url_selenium, json=dados)
        response.raise_for_status()
        print("Dados enviados com sucesso para o servidor Selenium!")
    except request.exceptions.RequestException as e:
        print(f"Erro ao enviar dados para o servidor Selenium: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

# Rota para receber dados do formulário HTML
@app.route('/rota_para_receber_dados', methods=['POST', 'OPTIONS'])

# Rota para iniciar automação
@app.route('/iniciar_automacao', methods=['POST'])
def iniciar_automacao():
    if request.method == 'POST':
        dados = request.json
        email = dados.get('email')
        senha = dados.get('senha')
        palavras_chave = dados.get('palavras_chave')
        texto_personalizado = dados.get('texto_personalizado')

        # Chama a função de automação Selenium
        automacao_linkedin(email, senha, palavras_chave, texto_personalizado)

        return jsonify({"status": "success"})

# Função para iniciar a automação Selenium
def automacao_linkedin(email, senha, palavras_chave, texto_personalizado):
    # Abrindo navegador
    navegador = abrir_navegador(email, senha)

    # Conectando ao banco de dados do usuário
    conn, cursor = conectar_banco()

    # Encontra os elementos que contêm informações sobre os contatos E clica nele.
    ver_conexao = navegador.find_element_by_css_selector("a[href='https://www.linkedin.com/mynetwork/?']")
    ver_conexao.click()


    time.sleep(3)
    # Encontra o elemento da lista de conexoes linkedin e clica nele.
    lista_conexao = navegador.find_element_by_css_selector("a[href='/mynetwork/invite-connect/connections/']")
    lista_conexao.click()

    # Guarda as palavras_chaves definidas pelo Site HTML em uma lista e separa as palavras por virgula.
    if palavras_chave:
        palavras_chave = palavras_chave.split(',')

    try:
        while True:
            # Rola a página para baixo
            navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(5)  # Aguarda o carregamento da nova parte da lista

            # Encontra todos os elementos de conexão
            conexoes = navegador.find_elements_by_xpath('//li[contains(@class, "mn-connection-card")]')

            if not conexoes:
                print("Nenhum contato encontrado. Saindo do loop.")
                break

            for pessoa in conexoes:
                # Obtém o nome
                nome = pessoa.find_element_by_xpath('.//span[contains(@class, "mn-connection-card__name")]').text

                # Obtém a bio (se disponível)
                try:
                    bio = pessoa.find_element_by_xpath('.//p[contains(@class, "mn-connection-card__occupation")]').text
                except:
                    bio = "Bio não disponível"

                # A partir deste ponto, você pode utilizar o nome e a bio conforme necessário
                print(f"Nome: {nome}, Bio: {bio}")

            # Verifica se o nome não está no banco de dados
            if not verificar_chat_existente(cursor, email, nome):                    
                # Se não estiver no banco de dados, continua o processamento
                if any(palavra in nome or palavra in bio for palavra in palavras_chave):
                    # Clique no botão "Enviar Mensagem"
                    # O botao tem classe igual para TODOS os contatos e ID's diferentes para cada pessoa
                    botao_enviar_mensagem = pessoa.find_element_by_xpath('.//button[contains(@class, "artdeco-button--2")]')
                    botao_enviar_mensagem.click()
                    time.sleep(3)

                    # Pegando nome do chat
                    nome_chat = navegador.find_element_by_id("app-aware-link  profile-card-one-to-one__profile-link").text

                    # Criando o texto automático da mensagem com o nome do chat
                    texto_mensagem = f"Olá {nome_chat} Tudo bem? \n{texto_personalizado}"

                    # Insere o texto na caixa de mensagem
                    caixa_mensagem = navegador.find_element_by_class_name("msg-form__contenteditable")
                    caixa_mensagem.send_keys(texto_mensagem)

                    # Clica no botão de enviar
                    enviar_button = navegador.find_element_by_class_name("msg-form__send-button artdeco-button artdeco-button--1")
                    enviar_button.click()

                    # Clica no botão "X" para ir para o próximo contato
                    botao_x = navegador.find_element_by_class_name("msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view")
                    botao_x.click()

                    # Insere o nome na tabela do banco de dados
                    registrar_chat_enviado(conn, cursor, email, nome)
    except Exception as e:
        print(f"Erro: {str(e)}")
    finally:
        navegador.close()
        conn.close()
        
def receber_dados():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    if request.method == 'POST':
        email = request.json.get('email')  # Use .json ao invés de .form
        senha = request.json.get('senha')

        # Conectar ao banco de dados
        conn, cursor = conectar_banco()

        try:
            # Inserir dados na tabela do banco de dados
            cursor.execute("INSERT INTO linkedin_HTTP_dados (email, senha) VALUES (?, ?)", (email, senha))
            conn.commit()

            # Iniciar scripts Flask e Selenium após receber dados
            subprocess.Popen(["python", "C:\\Users\\C\\Desktop\\DEV POINT\\Códigos\\Linkedin Project\\start_app.py"])

            response = jsonify({"status": "success"})
            response.headers.add("Access-Control-Allow-Origin", "*")  # Configuração manual do CORS
            return response
        except Exception as e:
            response = jsonify({"status": "error", "message": str(e)})
            response.headers.add("Access-Control-Allow-Origin", "*")  # Configuração manual do CORS
            return response
        finally:
            conn.close()

if __name__ == "__main__":
    app.run(port=5000, debug=True)