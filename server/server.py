import threading
import socket

clients = []

def main():


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind(('localhost', 8080))
        server.listen()
    except:
        return print('\nNão foi possível iniciar o servidor!')

    while True:
        client, address = server.accept()
        clients.append(client)

        server_thread = threading.Thread(target=messages_treatment, args=[client])
        server_thread.start()

def messages_treatment(client):

    while True:
        try:
            message = client.recv(2048)
            broadcast(message, client)
        except:
            remove_client(client)
            break

def broadcast(message, client):

    for client_item in clients:
        if client_item != client:
            try:
                client_item.send(message)
            except:
                remove_client(client_item)
                
def remove_client(client):

    clients.remove(client)

if __name__ == '__main__':

    main()
