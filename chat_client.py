import socket
import select
import errno
import sys
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from cryptography.fernet import Fernet
import base64
import os
from tkinter import messagebox

# Constants for network communication
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8888

# Initialize the tkinter GUI
root = tk.Tk()
root.title("Chat Client")
root.geometry("400x300")
root.resizable(True, True)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=3)

# Create GUI frames
login_frame = tk.Frame(root)
main_frame = tk.Frame(root)

# Configure frames
for frame in (login_frame, main_frame):
    frame.configure(bg="#202020")
    frame.grid(row=0, column=0, sticky="news")

# Define font styles
font_style = ("Arial", 12)
font_style_bold = ("Arial", 12, "bold")

# Labels and entry for login
title_label = tk.Label(login_frame, text="Chat App Client", font=font_style, bg="#202020", fg="#00FF00")
title_label.grid(row=0, column=0, columnspan=2, sticky="news")
username_label = tk.Label(login_frame, text="Username:", font=font_style, bg="#202020", fg="#00FF00")
username_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
username_entry = tk.Entry(login_frame, font=font_style, bg="#202020", fg="#00FF00")
username_entry.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)
username_entry.focus_set()

# Label and entry for Fernet key input
key_label = tk.Label(login_frame, text="Key:", font=font_style, bg="#202020", fg="#00FF00")
key_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
key_entry = tk.Entry(login_frame, font=font_style, bg="#202020", fg="#00FF00")
key_entry.grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)

# Method to handle key submission with Enter key
def submit_key(event=None):
    login()

# Button to submit key
submit_key_button = tk.Button(login_frame, text="Enter", command=submit_key, font=font_style, bg="#00FF00", fg="#202020", activebackground="#00FF00", activeforeground="#202020")
submit_key_button.grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)

# Text widget for displaying messages
messages_text = tk.Text(main_frame, height=20, width=50, font=font_style, bg="#202020", fg="#00FF00")
messages_text.configure(state="disabled", borderwidth=0, background=main_frame.cget('background'))
messages_text.grid(row=0, column=0, columnspan=2, sticky="news")

# Configure message text tags
messages_text.tag_configure("timestamp_tag", foreground="#A4A4A4")
messages_text.tag_configure("my_username_tag", foreground="#2dfcd9", font=font_style_bold)
messages_text.tag_configure("my_text_tag", foreground="#2dfcd9")
messages_text.tag_configure("other_username_tag", font=font_style_bold)

# Entry for typing messages
message_entry = tk.Entry(main_frame, font=font_style, bg="#202020", fg="#00FF00")
message_entry.grid(row=1, column=0, sticky="news")

# Create and connect client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# Method to send a message
def send_message(entry, event=None):
    message = entry.get()
    if message:
        encrypted_message = fernet.encrypt(message.encode('utf-8'))
        message_header = f"{len(encrypted_message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + encrypted_message)
        message_entry.delete(0, tk.END)

# Send Usernames
def send_username(entry, event=None):
    message = entry.get()
    if message:
        message_data = message.encode('utf-8')
        message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message_data)
        message_entry.delete(0, tk.END)

# Method to continuously receive messages
def receive_messages():
    while True:
        try:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')

            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                print('Connection closed by the server')
                sys.exit()
            message_length = int(message_header.decode('utf-8').strip())
            encrypted_message = client_socket.recv(message_length)

            print("Received encrypted message:", encrypted_message)  # Debugging print and shows encryption
            # Decrypt the message
            decrypted_message = fernet.decrypt(encrypted_message).decode('utf-8')
            print("Decrypted message:", decrypted_message)  # Debugging print and shows successful decryption

            timestamp = datetime.now().strftime("%H:%M:%S")
            messages_text.configure(state="normal")
            messages_text.insert(tk.END, f'[{timestamp}] ', "timestamp_tag")
            messages_text.insert(tk.END, f'{username}', "my_username_tag" if my_username == username else "other_username_tag")
            messages_text.insert(tk.END, f' > {decrypted_message}\n', "my_text_tag" if my_username == username else "")
            messages_text.see(tk.END)
            messages_text.configure(state="disabled", borderwidth=0, background=main_frame.cget('background'))
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error1: {}'.format(str(e)))
                sys.exit()
            continue
        except Exception as e:
            print('Reading error2: {}'.format(str(e)))
            import traceback
            traceback.print_exc()
            sys.exit()

# Method to start the sending thread
def start_sending_thread():
    send_thread = threading.Thread(target=send_message, args=(message_entry,))
    send_thread.start()

# Method to start the receiving thread
def start_receiving_thread():
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

# Method for user login
def login():
    global my_username
    my_username = username_entry.get()
    # Retrieve the Fernet key entered by the user
    key = key_entry.get().encode('utf-8')
    # Initialize Fernet with the user-entered key
    global fernet
    fernet = Fernet(key)
    send_username(username_entry)
    start_receiving_thread()
    main_frame.tkraise()

# Button for user login
login_button = tk.Button(login_frame, text="Login", command=login, font=font_style, bg="#00FF00", fg="#202020", activebackground="#00FF00", activeforeground="#202020")
login_button.grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)

# Button for sending messages
send_button = tk.Button(main_frame, text="Send", command=start_sending_thread, font=font_style, bg="#00FF00", fg="#202020", activebackground="#00FF00", activeforeground="#202020")
send_button.grid(row=1, column=1, sticky="news")

# Function to generate a random Fernet key
def generate_key():
    key = base64.urlsafe_b64encode(os.urandom(32))
    key_entry.delete(0, tk.END)  # Clear the existing content in the key entry field
    key_entry.insert(0, key)  # Insert the generated key into the key entry field

# Button for generating key
generate_key_button = tk.Button(login_frame, text="Generate Key", command=generate_key, font=font_style, bg="#00FF00", fg="#202020", activebackground="#00FF00", activeforeground="#202020")
generate_key_button.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)

# Show login frame
login_frame.tkraise()
root.mainloop()
