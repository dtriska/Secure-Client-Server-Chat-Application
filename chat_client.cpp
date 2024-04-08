#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

// can choose any port # as long as set up with server accordingly
#define PORT 8888
#define MAX_MSG_LEN 1024

int sock = 0;
char username[100];

void *receive_messages(void *arg) {
    char buffer[MAX_MSG_LEN] = {0};
    int valread;

    while (1) {
        valread = read(sock, buffer, MAX_MSG_LEN);
        if (valread > 0) { // valread will be greater than 0 if a message is successfully received
            printf("%s\n", buffer);
            memset(buffer, 0, sizeof(buffer)); // clears anything left in buffer so can easily be read for next message
        }
    }

    return NULL;
}

int main(int argc, char *argv[]) {
    struct sockaddr_in serv_addr;
    char message[MAX_MSG_LEN];

    // Decided to get name on client side and prepend name to each message sent to server
    printf("Enter your name: ");
    fgets(username, 100, stdin);
    username[strcspn(username, "\n")] = 0; // Remove newline character

    // Handle stuff that goes wrong
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("\n Socket creation error \n");
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    // Handle stuff that goes wrong
    if(inet_pton(AF_INET, "10.110.130.241", &serv_addr.sin_addr)<=0) { // Replace 127 with actual IP
        printf("\nInvalid address/ Address not supported \n");
        return -1;
    }

    // Handle stuff that goes wrong
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        printf("\nConnection Failed \n");
        return -1;
    }

    printf("Connected to server. Type 'exit' to quit.\n");

    // Need One thread for listening to messages and one to send
    // Threading allows multiple process to be executed simultaneously 
    // Create a separate thread to receive messages from the server
    
    pthread_t recv_thread; // Declares new thread variable
    if (pthread_create(&recv_thread, NULL, receive_messages, NULL) != 0) { // creates new thread attached to recv_thread IMPORTANT receive_messages is the method this thread is resp for
        printf("\nThread creation error\n");
        return -1;
    }

    // Main thread for sending messages
    while (1) {
        printf("Enter message: ");
        fgets(message, MAX_MSG_LEN, stdin);
        if (strcmp(message, "exit\n") == 0) {
            break;
        }
        // Prepend username to message
        char full_message[MAX_MSG_LEN + 100]; // Max message length + username length
        snprintf(full_message, sizeof(full_message), "%s: %s", username, message);
        send(sock, full_message, strlen(full_message), 0);
    }

    printf("Closing connection.\n");
    close(sock);
    pthread_join(recv_thread, NULL); // Wait for receive thread to finish
    return 0;
}
