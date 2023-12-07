from selenium import webdriver
from flask import Flask, request, jsonify
import sqlite3
import time

app_selenium = Flask(__name__)

# Rota para receber dados do Flask
@app_selenium.route('/rota_para_receber_dados', methods=['POST'])
def receber_dados_selenium():
    if request.method == 'POST':
        dados = request.json
        email = dados.get('email')
        senha = dados.get('senha')
        palavras_chave = dados.get('palavras_chave')
        texto_personalizado = dados.get('texto_personalizado')

        # Chama a função principal do Selenium passando os dados
        automacao_linkedin(email, senha, palavras_chave, texto_personalizado)

        return jsonify({"status": "success"})

# Função para iniciar o servidor Flask do Selenium
def iniciar_servidor_selenium():
    app_selenium.run(port=5002)

def abrir_navegador(email, senha):
    navegador = webdriver.Edge()
    navegador.get("https://www.linkedin.com/home")
    time.sleep(5)
    
    # Insere email e senha
    email_field = navegador.find_element_by_id("session_key")
    email_field.send_keys(email)

    senha_field = navegador.find_element_by_id("session_password")
    senha_field.send_keys(senha)

    # Clica em Entrar
    entrar_button = navegador.find_element_by_id("sign-in-form__submit-btn")
    entrar_button.click()

    # Aguarda carregar a página
    time.sleep(5)
    return navegador

def conectar_banco():
    try:
        conn = sqlite3.connect("linkedin_bd.sqlite")
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS linkedin_HTTP_dados (email TEXT, senha TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS linkedin_chats_enviados (email TEXT, nome TEXT)")
        
        conn.commit()
        return conn, cursor
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
        raise e

def verificar_chat_existente(cursor, email, nome):
    cursor.execute("SELECT * FROM linkedin_chats_enviados WHERE email = ? AND nome = ?", (email, nome))
    return cursor.fetchone() is not None

def registrar_chat_enviado(conn, cursor, email, nome):
    cursor.execute("INSERT INTO linkedin_chats_enviados (email, nome) VALUES (?, ?)", (email, nome))
    conn.commit()

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
