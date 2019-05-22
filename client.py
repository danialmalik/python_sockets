import socket
import sys
import select
import errno

SERVER_PORT = 12345
SERVER_IP = '127.0.0.1'
HEADER_LENGTH = 10
UTF_8 = 'utf-8'

my_username_raw = input ('username  : ')

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.gaierror:
    print('socket creation error')
    sys.exit(1)

client_socket.connect((SERVER_IP, SERVER_PORT))
client_socket.setblocking(False)


my_username = my_username_raw.encode(UTF_8)
username_header = f'{len(my_username):<{HEADER_LENGTH}}'.encode(UTF_8)
client_socket.send(username_header + my_username)

# Start chatting
while(True):
    message = input(f'{my_username_raw} >>> ')
    if message:
        message = message.encode(UTF_8)
        message_header = f'{len(message):<{HEADER_LENGTH}}'.encode(UTF_8)
        client_socket.send(message_header + message)

    try:
        while True:
            # recieve msg
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()
            
            username_length = int(username_header.decode(UTF_8).strip())
            username = client_socket.recv(username_length).decode(UTF_8)
            
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode(UTF_8).strip())
            message = client_socket.recv(message_length).decode(UTF_8)

            print(f'{username} >>> {message}')


    except IOError as e:
        if e.errno != errno.EAGAIN or e.errno !=errno.EWOULDBLOCK:
            print('Error while reading message.', e)
            sys.exit()
        continue

    except Exception as e:
        print('General Error.', e)
