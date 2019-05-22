import logging
import socket 
import select
import sys  

PORT = 12345
LISTEN_BACKLOG = 15
LISTEN_IP = '0.0.0.0'
HEADER_LENGTH = 10


try: 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 ) # 1=True 
    logging.info('Socket successfully created')
    print('Socket successfully created')
except socket.error as err: 
    logging.error('socket creation failed with error '%(err) )
    print('socket creation failed with error '%(err))

server_socket.bind((LISTEN_IP, PORT))

server_socket.listen(LISTEN_BACKLOG)
logging.info('server is listenning')
print('listenning')


sockets_list = [server_socket]
clients = {}


def recv_msg(client_socket):
    try:
        msg_header = client_socket.recv(HEADER_LENGTH)
        if not msg_header:
            return False
        msg_length = int(msg_header.decode('utf-8').strip()) 
        return {
            'header': msg_header,
            'data': client_socket.recv(msg_length)
        }
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list) # read. write, err sockets

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = recv_msg(client_socket)
            if not user:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = user

            print(f'accepted new connection from {client_address[0]}:{client_address[1]} || username : {user["data"].decode("utf-8")}')
        else:
            msg = recv_msg(notified_socket)
            if not msg:
                print(f'Closed Connection from {clients[notified_socket]["data"].decode("utf-8")}')
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f'recieved msg from {user["data"].decode("utf-8")}: {msg["data"].decode("utf-8")}')

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + msg['header'] + msg['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
