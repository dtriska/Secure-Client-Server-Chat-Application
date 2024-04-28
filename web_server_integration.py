from flask import Flask, render_template
from flask_socketio import SocketIO, emit
#import threading
import socket
#import errno
#import json

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

HEADER_LENGTH = 10
#gots to match chat_server
IP = "127.0.0.1"
PORT = 8888

# Create a socket for communication with the chat server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# Function to send message to chat server
def send_message_to_server(message):
    try:
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        print("Message is sent to server")
    except Exception as e:
        print("Error sending message to server:", str(e))

# Handle message received from client's browser
@socketio.on('message')
def handle_message(message):
    # Forward message to chat server
    send_message_to_server(message)

# Function to receive messages from chat server
# def receive_messages():
#     while True:
#         try:
#             username_header = client_socket.recv(HEADER_LENGTH)
#             if not len(username_header):
#                 print('Connection closed by the server')
#                 break
#             username_length = int(username_header.decode('utf-8').strip())
#             username = client_socket.recv(username_length).decode('utf-8')
#             message_header = client_socket.recv(HEADER_LENGTH)
#             message_length = int(message_header.decode('utf-8').strip())
#             message = client_socket.recv(message_length).decode('utf-8')
#             print("Message received from server")
#             # Emit message to client's browser
#             emit('message', json.dumps({'username': username, 'message': message}))
#         except IOError as e:
#             if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
#                 print('Reading error: {}'.format(str(e)))
#                 break
#         except Exception as e:
#             print('Reading error: '.format(str(e)))
#             break

# Start receiving messages from chat server in a separate thread
# receive_thread = threading.Thread(target=receive_messages)
# receive_thread.daemon = True
# receive_thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
