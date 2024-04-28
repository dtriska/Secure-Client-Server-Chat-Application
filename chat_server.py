import socket
import select
import tkinter as tk
import threading

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8888 

# Tkinter setup
root = tk.Tk()
root.title("Chat Server")
root.configure(bg="#F0F0F0")

# Custom Fonts
font_style = ("Arial", 12)

# Text widget to display messages
messages_text = tk.Text(root, height=20, width=50, font=font_style)
messages_text.pack()

# Function to receive a new message from client
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False

# Function to run server in a separate thread
def run_server():
    # Socket Creation
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()

    sockets_list = [server_socket]
    clients = {}

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if user is False:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
                # Print out a message in the Tkinter window
                messages_text.insert(tk.END, f'Accepted new connection from {client_address[0]}:{client_address[1]}, username: {user["data"].decode("utf-8")}\n')
                messages_text.see(tk.END)
            else:
                message = receive_message(notified_socket)
                if message is False:
                    print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
                user = clients[notified_socket]
                print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
                # Broadcast the received message to all clients, including the sender
                for client_socket in clients:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                # Display the message in the Tkinter window
                messages_text.insert(tk.END, f'{user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}\n')
                messages_text.see(tk.END)

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]

# Start the server in a separate thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

# Start the Tkinter event loop
root.mainloop()
