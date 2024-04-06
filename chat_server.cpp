#include <stdio.h>  
#include <string.h>   //strlen  
#include <stdlib.h>  
#include <errno.h>  
#include <unistd.h>   //close  
#include <arpa/inet.h>    //close  
#include <sys/types.h>  
#include <sys/socket.h>  
#include <netinet/in.h>  
#include <sys/time.h> //FD_SET, FD_ISSET, FD_ZERO macros  

#define TRUE   1  
#define FALSE  0  
#define PORT 8888  

int main(int argc , char *argv[])   
{   
    int opt = TRUE;   
    int master_socket , addrlen , new_socket , client_socket[30] ,  
          max_clients = 30 , activity, i , valread , sd;   
    int max_sd;   
    struct sockaddr_in address; // structure to handle IPv4
    char buffer[1025];  //data buffer of 1K  
    fd_set readfds;   
    char *message = "WELCOME TO THE CHAT! \r\n";   

    for (i = 0; i < max_clients; i++) {  
        client_socket[i] = 0;   
    }   

    // Create master socket for server
    if ((master_socket = socket(AF_INET , SOCK_STREAM , 0)) == 0) {   
        perror("socket failed");   
        exit(EXIT_FAILURE);   
    }   

    // Set all Socket Options for Master Socket
    if (setsockopt(master_socket, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt)) < 0) {   
        perror("setsockopt");   
        exit(EXIT_FAILURE);   
    }   

    // Set address struct
    address.sin_family = AF_INET;   
    address.sin_addr.s_addr = INADDR_ANY; // change to ip of actual server
    address.sin_port = htons(PORT);   

    // Binds socket to address
    if (bind(master_socket, (struct sockaddr *)&address, sizeof(address)) < 0) {   
        perror("bind failed");   
        exit(EXIT_FAILURE);   
    }   
    printf("Listener on port %d \n", PORT);   

    // Listen for connections
    if (listen(master_socket, 3) < 0) {   
        perror("listen");   
        exit(EXIT_FAILURE);   
    }   

    addrlen = sizeof(address);   
    puts("Waiting for connections ...");   

    while (TRUE) {   // Continuous Loop to await connections
        FD_ZERO(&readfds);   // Clear file descriptor
        FD_SET(master_socket, &readfds);  // Add master socket to set of file descriptors for reading 
        max_sd = master_socket;   // sets max socket descriptor value to master socket val

        // Loop through client sockets
        for (i = 0; i < max_clients; i++) {   
            sd = client_socket[i];   // Assigns val of each client socket to sd
            if (sd > 0)   
                FD_SET(sd, &readfds);   
            if (sd > max_sd)   // Update max_sd if curr client socket is greater than current
                max_sd = sd;   
        }   

        activity = select(max_sd + 1, &readfds, NULL, NULL, NULL);   // Awaits activity on one of file descriptors

        if ((activity < 0) && (errno != EINTR)) {   
            printf("select error");   
        }   

        // Checks for activity on master socket -> new connection req
        if (FD_ISSET(master_socket, &readfds)) {   
            if ((new_socket = accept(master_socket, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) { 
                perror("accept");   
                exit(EXIT_FAILURE);   
            }   
            printf("New connection , socket fd is %d , ip is : %s , port : %d\n" , new_socket , inet_ntoa(address.sin_addr) , ntohs(address.sin_port));   
            if (send(new_socket, message, strlen(message), 0) != strlen(message)) {   
                perror("send");   
            }   
            puts("Welcome message sent successfully");   
            for (i = 0; i < max_clients; i++) {   
                if (client_socket[i] == 0) {   
                    client_socket[i] = new_socket;   
                    printf("Adding to list of sockets as %d\n" , i);   
                    break;   
                }   
            }   
        }   

        // Loop through client sockets, looking for activity
        for (i = 0; i < max_clients; i++) {   
            sd = client_socket[i];   
            if (FD_ISSET(sd, &readfds)) {   
                if ((valread = read(sd, buffer, 1024)) == 0) {   
                    getpeername(sd, (struct sockaddr*)&address, (socklen_t*)&addrlen);   
                    printf("Host disconnected , ip %s , port %d\n" , inet_ntoa(address.sin_addr) , ntohs(address.sin_port));   
                    close(sd);   
                    client_socket[i] = 0;   
                }   
                else {   
                    buffer[valread] = '\0';   
                    // Broadcast the message to all other clients
                    for (int j = 0; j < max_clients; j++) {
                        if (client_socket[j] != 0 && client_socket[j] != sd) {
                            send(client_socket[j], buffer, strlen(buffer), 0);
                        }
                    }
                }   
            }   
        }   
    }   
    return 0;   
}
