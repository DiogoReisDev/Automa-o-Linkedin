## ⚠️ ALERTA IMPORTANTE ⚠️
```
O linkedin é extremamente rigoroso e chato quando se trata de automação de envio de mensagens ou ações robóticas.
Fiz testes em contas que haviam poucos contatos e não tomei Ban da plataforma, porém o código foi feito para realizar o envio para uma grande massa de contatos/conexões que você houver em sua conta! Sendo assim, o risco para você ser suspenso da plataforma é bem maior!!!
```

# Ideia de funcionamento do código:


HTML (index.html):
    Apresenta um formulário simples com campos para email, senha, palavras-chave e texto personalizado.
    Contém um botão que, ao ser clicado, chama a função enviarDados() que utiliza o fetch para enviar os dados para a rota /rota_para_receber_dados no Flask.
----------------------------
Flask (flask.py):
    Define uma função conectar_banco() que retorna uma conexão e um cursor para o banco de dados SQLite.
    Define uma função enviar_dados_selenium() que constrói um dicionário com os dados do formulário e chama uma rota no Selenium (ainda não totalmente implementada).
    Define a rota principal ("/") que renderiza o template HTML.
    Define a rota /rota_para_receber_dados que recebe dados do formulário, insere esses dados no banco SQLite e retorna um status de sucesso ou erro.
----------------------------
Selenium (selenium.py):
    Define uma rota /receber_dados_selenium que é chamada pelo Flask para receber dados do formulário.
    Inicia um servidor Flask em uma thread separada.
    Define funções auxiliares para abrir o navegador, conectar ao banco de dados SQLite, verificar a existência de chats e registrar chats enviados.
    Define a função principal main() que utiliza Selenium para realizar ações no LinkedIn, como abrir o navegador, clicar em elementos, rolar a página, enviar mensagens, etc.
    A função principal é chamada com os dados do formulário quando a rota /receber_dados_selenium é acessada pelo Flask.
----------------------------
Start applicativo (start_app.py)
    Comandos para iniciar o código flask para recebimento de dados do usuário e em seguida comando para iniciar código selenium para execução de processos automatizados.
----------------------------


# Passo a Passo para Execução: Automatizador LinkedIn

### Requisitos Iniciais:

Certifique-se de ter o Python instalado em sua máquina. Caso não tenha, você pode baixá-lo em [python.org]((https://www.python.org/)).

### Configuração do Ambiente:

Abra um terminal ou prompt de comando e navegue até o diretório onde os arquivos do projeto estão localizados.

### Execute o seguinte comando para instalar as dependências necessárias:

pip install -r requirements.txt

### Banco de Dados SQLite:

Certifique-se de que o SQLite está instalado. Caso não esteja, você pode baixá-lo em [sqlite.org](https://sqlite.org/index.html)

### Execute o seguinte comando para criar o banco de dados SQLite e as tabelas necessárias:

python create_database.py

### Iniciar Flask, Execute o seguinte comando para iniciar o servidor Flask:

python app.py
O servidor Flask será iniciado e estará aguardando em http://127.0.0.1:5000/.

### Preencher o Formulário HTML:

acesse pelo arquivo index.html definido com seu IP

Preencha o formulário com suas credenciais, palavras-chave e texto personalizado.

Clique no botão "Iniciar Automação" para enviar os dados ao servidor Flask.

### Executar Selenium:

Enquanto o servidor Flask está em execução, abra um novo terminal ou prompt de comando.

Execute o seguinte comando para iniciar o servidor Selenium em uma nova thread:

python selenium.py
O servidor Selenium estará aguardando em http://127.0.0.1:5001/.

### Observações Finais:

Certifique-se de manter os terminais abertos enquanto os scripts estão em execução.

Ao concluir, você pode interromper a execução pressionando Ctrl + C nos terminais abertos.

Lembre-se de ajustar as configurações do navegador no arquivo selenium.py conforme necessário, como o caminho do driver WebDriver para o navegador escolhido.

Dentro da plataforma do linkedin, evite deixar chats em aberto, feche todos.

Evite deixar sua conta logada no linkedin, pois o bot precisa acessar sua conta.

Este é um exemplo geral de como os scripts podem ser utilizados. Certifique-se de personalizar conforme suas necessidades específicas.
