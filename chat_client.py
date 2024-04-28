import socket
import select
import errno
import sys
import threading

HEADER_LENGTH = 10
IP = "127.0.0.1" # 127 is local address, should change if running on two different machines
PORT = 8888 

# set username, will be sent to server
my_username = input("Enter your name: ")

# Socket Creation
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT)) # connect to server address
client_socket.setblocking(False) # non-blocking mode

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

def receive_messages():
    # continuosly receive messages from the server
    while True:
        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()
                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')
                print(f'{username} > {message}')

        # I/O error handling
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            continue
        # other exceptions (just good practice)
        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()

# Receive thread is used to handle message from server continusosly
# We dont block main thread from sending messages
receive_thread = threading.Thread(target=receive_messages) 
receive_thread.daemon = True # daemon makes this thread terminate when the main thread terminates
receive_thread.start()

while True:
    # main thread for sending messages
    message = input(f'{my_username} > ')

    if message:
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
