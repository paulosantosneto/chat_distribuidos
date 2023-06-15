from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
import os
import threading

# Definição dos parâmetros necessários para instancias uma aplicação em Flask
app = Flask(__name__)
app.config["SECRET_KEY"] = "chat_sistemas_distribuidos"
socketio = SocketIO(app)

# Dicionário que armazena os IDs das salas e histórico dos membros
rooms = {}

# threads dos clientes
client_threads = {}

# função responsável por realizer o post e o get na interface inicial da aplicação
@app.route('/', methods=['POST', 'GET'])
def home():
    # reseta os dados presentes no input
    session.clear()
    if request.method == 'POST':
        # recebimento dos inputs do html
        username = request.form.get('username')
        join_id = request.form.get('join_id')
        create_id = request.form.get('create_id')
        join_btn = request.form.get('join_token', False)
        create_btn = request.form.get('create_token', False)
        
        # caso o usuário não tenha inserido o nome retorna uma mensagem de aviso o usuário
        if not username:
            return render_template("home.html", error="Insira um nome antes de entrar/criar uma sala.", join_id=join_id, create_id=create_id, username=username)
        
        # caso o input para entrar em uma sala não tenha sido inserido retorna uma mensagem de aviso para o usuário
        if join_btn != False and not join_id:
            return render_template("home.html", error="Insira o ID para entrar na sala.", join_id=join_id, username=username, create_id=create_id)
        
        # caso o input para criar uma sala não tenha sido inserido retorna uma mensagem de aviso para o usuário
        if create_btn != False and not create_id:
            return render_template('home.html', error='Insira o ID para criar a sala.', join_id=join_id, create_id=create_id, username=username)
        
        # se o ID inserido já estiver me uso, retorna uma mensagem dea aviso ao usuário (ID único)
        if create_id in rooms:
            return render_template('home.html', error='A sala já existe, tente outro ID.', join_id=join_id, create_id=create_id, username=username)
        
        # define a variável que irá armazenar o ID da sala no histórico de salas
        opt_id = None
        if create_btn != False:
            # adiciona no dicionários de sessões um novo chat
            rooms[create_id] = {'length': 0, 'messages': [], 'members': []}
            opt_id = create_id
        elif join_btn != False:
            opt_id = join_id
        elif opt_id not in rooms:
            # retorna uma mensagem de aviso caso o ID da sala não exista no histórico de salas
            return render_template('home.html', error="A sala não existe.", join_id=join_id, create_id=create_id, username=username)
        session['room'] = opt_id
        session['name'] = username
        
        # faz o redirecionamento para sala
        return redirect(url_for('room'))
    
    # rediciona para a interface inicial por default
    return render_template("home.html")

# função responsável por renderizar
@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    """
    Esta função serve para comunicar as mensagens de cada usuário.
    Cada mensagem é armazenada em um dicionário de acordo com o ID da sala.
    Caso o ID não exista, o usuário retorna para o menu inicial.
    """
    room = session.get("room")
    # para quando não existe o ID no dicionário de salas
    if room not in rooms:
        return 
    
    # conteúdo da mensagem que será recebida pelo socket em javascript
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    # envia o conteúdo da mensagem e adiciona a mensagem na lista (histórico de mensagens)
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    """
    Esta função é responsável por realizar a conexão de um usuário/membro
    em uma sala com determinado ID.
    """

    room = session.get('room')
    name = session.get('name')
    # para quando não existe o ID no dicinário de salas 
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    # acrescenta o número de membros online em 1
    rooms[room]['length'] += 1
    rooms[room]['members'].append(name)
    # emite o evento broadcast para atualizar a presença de um novo membro para todos do chat
    emit('members_update', rooms[room]['members'], broadcast=True)
    
    # Cria uma nova thread para lidar com as ações do cliente
    client_threads[(name, room)] = threading.Thread(target=handle_client_threads, args=(room, name))
    client_threads[(name, room)].start()
    print(f"{name} joined room {room}")

def handle_client_threads(room, name):
    """
    Esta função é executada em uma thread separada para lidar com o cliente. 
    """

    thread_ids = [thread.ident for thread in threading.enumerate()]

    print(f"Threads em uso: {thread_ids}")
        
@socketio.on("disconnect")
def disconnect():
    """
    Esta função é responsável por realizar a desconexão de um usuário/membro
    em uma sala com determinado ID.
    """

    room = session.get("room")
    name = session.get('name')
    leave_room(room)

    if room in rooms:
        # verifica se há membros online
        if rooms[room]['length'] > 0:
            # remove o membro que se desconectou
            rooms[room]['members'].remove(name)
            rooms[room]['length'] -= 1
            # emite um evento para atualizar a interface
            emit('members_update', rooms[room]['members'], broadcast=True)
        if rooms[room]['length'] <= 0:
            # remove a sessão inteira quando não há nenhum membro nela
            del rooms[room]



if __name__ == '__main__':
    # recolhe das variáveis do ambiente a porta, caso não haja, define como padrão a porta 5000
    port = int(os.environ.get("PORT", 5000)) 
    # instancia a aplicação 
    socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
    #socketio.run(app, debug=True) 


