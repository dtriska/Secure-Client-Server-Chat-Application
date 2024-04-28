import socket
import select
import errno
import sys
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8888 

# Tkinter setup
root = tk.Tk()
root.title("Chat Application")
root.configure(bg="#F0F0F0")

# Custom Fonts
font_style = ("Arial", 12)

# Entry field for username
username_label = tk.Label(root, text="Enter your name:", font=font_style, bg="#F0F0F0")
username_label.pack()
username_entry = tk.Entry(root, font=font_style)
username_entry.pack()
username_entry.focus_set()

# Text widget to display messages
messages_text = tk.Text(root, height=20, width=50, font=font_style)
messages_text.pack()

# Entry field for sending messages
message_entry = tk.Entry(root, font=font_style)
message_entry.pack()

# Socket Creation
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

def send_message(event=None):
    message = message_entry.get()
    if message:
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        message_entry.delete(0, tk.END)

def receive_messages():
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
                timestamp = datetime.now().strftime("%H:%M:%S")  # Get current timestamp
                messages_text.insert(tk.END, f'{timestamp} {username} > {message}\n')
                messages_text.see(tk.END)  # Scroll to the end

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            continue
        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

root.bind("<Return>", send_message)

send_button = tk.Button(root, text="Send", command=send_message, font=font_style, bg="#FF6B6B", fg="white", activebackground="#FF8F8F", activeforeground="white")
send_button.pack(pady=5)

root.mainloop()
