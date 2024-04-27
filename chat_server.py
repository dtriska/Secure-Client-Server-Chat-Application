import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1" # 127 is for easy test on personal system
PORT = 8888

# Socket Creation TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allows us to reuse the address in case of quick restart
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to address and port set above
server_socket.bind((IP, PORT))
# set socket to passivley listen for new connections
server_socket.listen()

# Hold our connections
sockets_list = [server_socket]
# Hold client info in dict
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Function to receive a new message from client
# Will return a dict containing the message and data
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header): # in event of client disconnect
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False

# Where we identify a new connection
while True:
    # Awaits new socket from a new client to be added to sockets_list
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # iterate sockets with activity
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            # socket gets accepted
            client_socket, client_address = server_socket.accept()
            # Username info received
            user = receive_message(client_socket) 
            if user is False: # username retrieve fails
                continue
            sockets_list.append(client_socket) 
            clients[client_socket] = user # store client info
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
        else:
            message = receive_message(notified_socket)
            if message is False: # case where client closes connection
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            # get clients socket and username
            user = clients[notified_socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            # Broadcast message to all connected clients
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Remove excess sockets and their info
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
