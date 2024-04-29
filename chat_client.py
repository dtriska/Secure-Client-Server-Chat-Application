import socket
import select
import errno
import sys
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

HEADER_LENGTH = 10
IP = "127.0.0.1" # 127 is local address, should change if running on two different machines
PORT = 8888 

# Tkinter setup
root = tk.Tk()
root.title("Chat Client")


# creating two frames as child of the root
login_frame = tk.Frame(root)
main_frame = tk.Frame(root)

for frame in (login_frame, main_frame):
    frame.configure(bg="#202020") # set background to black
    frame.grid(row = 0, column = 0, sticky = "news")

# Custom Fonts
font_style = ("Arial", 12)

## tkinter widgets for login frame
title_label = tk.Label(login_frame, text="Chat App Client", font=font_style, bg="#202020", fg="#00FF00")  # Set text color to light green
title_label.grid(row = 0, column = 0, columnspan = 2, sticky = "news")
username_label = tk.Label(login_frame, text="Username:", font=font_style, bg="#202020", fg="#00FF00")  # Set text color to light green
username_label.grid(row = 1, column = 0, sticky = "news")
username_entry = tk.Entry(login_frame, font=font_style, bg="#202020", fg="#00FF00")  # Set text and background color to black and light green respectively
username_entry.grid(row = 1, column = 1, sticky = "news")
username_entry.focus_set()

### tkinter widgets for main frame
# Text widget to display messages
messages_text = tk.Text(main_frame, height=20, width=50, font=font_style, bg="#202020", fg="#00FF00")  # Set text and background color to black and light green respectively
messages_text.grid(row = 0, column = 0, columnspan = 2, sticky = "news")

# Entry field for sending messages
message_entry = tk.Entry(main_frame, font=font_style, bg="#202020", fg="#00FF00")  # Set text and background color to black and light green respectively
message_entry.grid(row = 1, column = 0, sticky = "news") 

# the buttons need to be defined after the following function declarations

# Socket Creation
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

def send_message(entry,event=None):
    message = entry.get()
    if message:
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        message_entry.delete(0, tk.END)

def receive_messages():
    # continuously receive messages from the server
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

# Receive thread is used to handle message from server continuously
# We don't block main thread from sending messages
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # daemon makes this thread terminate when the main thread terminates
receive_thread.start()

root.bind("<Return>", send_message)

def login():
    send_message(username_entry)
    main_frame.tkraise()

# login button for the login frame
send_button = tk.Button(login_frame, text="Login", command=login, font=font_style, bg="#00FF00", fg="#202020", activebackground="#00FF00", activeforeground="#202020")  # Set button colors to light green and black
send_button.grid(row = 2, column = 0,columnspan = 2, sticky = "news", pady=5)

# send message button for main frame
send_button = tk.Button(main_frame, text="Send", command=lambda:send_message(message_entry), font=font_style, bg="#00FF00", fg="#202020", activebackground="#00FF00", activeforeground="#202020")  # Set button colors to light green and black
send_button.grid(row = 1, column = 1, sticky = "news")

# by default start with the login frame
login_frame.tkraise()
root.mainloop()
