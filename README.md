# Secure Client-Server Chat Application

This project is a secure client-server chat application where the server acts as a middleman among clients, allowing up to 10 clients to connect simultaneously. The server broadcasts messages from one client to all other connected clients, essentially creating a chat room environment.

## Reference

- [Project Topics: Network Programming - Secure Client-Server Chat Application](https://www.projecttopics.org/network-programming-secure-client-server-chat-application.html)
- [Bogotobogo: Python Network Programming - TCP Server & Client Chat Application](https://www.bogotobogo.com/python/python_network_programming_tcp_server_client_chat_ser)

## Description

The Secure Client-Server Chat Application provides a platform for multiple clients to communicate securely through a central server. Each client can send messages that are broadcasted to all other connected clients by the server. This allows for real-time communication in a chat room-like setting.

## Features

- Secure communication between clients and server using encryption.
- Ability to handle up to 10 clients simultaneously.
- Broadcasting of messages from one client to all other clients.
- User-friendly interface for easy interaction.

## Usage

1. Clone the repository.
2. Navigate to the directory containing the project files.
3. Run the server script.
4. Run the client script on each client's machine.
5. Have the first client generate a key
6. Client then shares key securley to all other clients
7. Connect to the server using the provided IP address and port number.
8. Enter the Fernet key for encryption when prompted.
9. Start sending and receiving messages securely.
