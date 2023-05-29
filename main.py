from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "chat_sistemas_distribuidos"
socketio = SocketIO(app)

rooms = {}

@app.route('/', methods=['POST', 'GET'])
def home():
    session.clear()
    if request.method == 'POST':
        username = request.form.get('username')
        join_id = request.form.get('join_id')
        create_id = request.form.get('create_id')
        join_btn = request.form.get('join_token', False)
        create_btn = request.form.get('create_token', False)

        if not username:
            return render_template("home.html", error="Insira um nome antes de entrar/criar uma sala.", join_id=join_id, create_id=create_id, username=username)

        if join_btn != False and not join_id:
            return render_template("home.html", error="Insira o ID para entrar na sala.", join_id=join_id, username=username, create_id=create_id)
        
        if create_btn != False and not create_id:
            return render_template('home.html', error='Insira o ID para criar a sala.', join_id=join_id, create_id=create_id, username=username)
        opt_id = None
        if create_btn != False:
            # adiciona no dicionários de sessões um novo chat
            rooms[create_id] = {'length': 0, 'messages': [], 'members': []}
            opt_id = create_id
        elif join_btn != False:
            opt_id = join_id
        elif opt_id not in rooms:
            return render_template('home.html', error="A sala não existe.", join_id=join_id, create_id=create_id, username=username)
        session['room'] = opt_id
        session['name'] = username
        return redirect(url_for('room'))

    return render_template("home.html")

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

    print(f"{name} joined room {room}")

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
    socketio.run(app, debug=True)
