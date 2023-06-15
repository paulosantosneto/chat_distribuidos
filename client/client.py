import threading
import socket
from datetime import datetime

def main():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPV4 & TCP

    try:
        client.connect(('localhost', 8080))
    except:
        return print('\nNão foi possível conectar.')

    username = input('Usuário>')
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
    loggin_message = f'\n{username} se conectou ao chat! [{data_hora}]'
     
    receive_thread = threading.Thread(target=receive_message, args=[client])
    send_thread = threading.Thread(target=send_message, args=[client, username])

    receive_thread.start()
    send_thread.start()
    

def receive_message(client):

    while True:
        try:
            message = client.recv(2048).decode('utf-8')
            print(message+'\n')
        except:
            print('\nConexão encerrada!')
            print('\nPress Enter to continue...')
            client.close()
            break

def send_message(client, username):

    while True:
        try:
            message = input('')
            client.send(f'<{username}> {message}'.encode('utf-8'))
        except:
            return

if __name__ == '__main__':

    main()

