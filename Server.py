import socket
import threading
import time

# Handle individual client connections-> Transparency
def handle_client(client_socket, client_address, clients, channels, nicknames):
    try:
        # Input prompt for nickname on connection
        client_socket.send("Enter your nickname: ".encode())
        nickname = client_socket.recv(1024).decode().strip()

        # Save client's info in dictionaries
        clients[client_socket] = client_address
        nicknames[client_socket] = nickname

        print(f"New connection from {client_address}, nickname: {nickname}")

        # Main loop for receiving messages from client
        while True:
            message = client_socket.recv(1024).decode()
            # Check the message type (private, join/leave channel, disconnect, or broadcast)
            if message.startswith('@'):  
                recipient, message = message.split(' ', 1)
                recipient = recipient[1:]
                send_private_message(client_socket, clients, channels, nicknames, recipient, message)
            elif message.startswith('/join'):  
                channel_name = message.split(' ', 1)[1]
                join_channel(client_socket, channels, channel_name)
            elif message.startswith('/leave'):  
                leave_channel(client_socket, channels)
            elif message.startswith('/disconnect'):  
                disconnect_client(client_socket, clients, channels, nicknames)
                break
            else:  
                broadcast_message(client_socket, channels, nicknames, message)
    except Exception as e:
        print(f"Error: {e}")
        # Handle client disconnection or errors
        disconnect_client(client_socket, clients, channels, nicknames)

# Add client to a channel
def join_channel(client_socket, channels, channel_name):
    channels[client_socket] = channel_name
    client_socket.send(f"You joined channel: {channel_name}".encode())

# Remove client from their channel
def leave_channel(client_socket, channels):
    if client_socket in channels:
        del channels[client_socket]
        client_socket.send("You have left the channel".encode())
    else:
        client_socket.send("You are not in any channel".encode())

# Disconnect a client cleanly -> failure handling
def disconnect_client(client_socket, clients, channels, nicknames):
    try:
        nickname = nicknames.get(client_socket, "Unknown")
        goodbye_message = "You are disconnected from the server".encode()
        client_socket.send(goodbye_message)
        time.sleep(1)  # waiting period for client to receive the message
    except Exception as e:
        print(f"Error during disconnect: {e}")
    finally:
        # Clean up all references to the client
        if client_socket in nicknames: del nicknames[client_socket]
        if client_socket in clients: del clients[client_socket]
        if client_socket in channels: del channels[client_socket]
        if client_socket: 
            client_socket.close()
        # Notify other clients in the same channel of the disconnection
        broadcast_message(client_socket, channels, nicknames, f"{nickname} has left the chat")

# Broadcast a message to all clients in the same channel
def broadcast_message(sender_socket, channels, nicknames, message):
    sender_channel = channels.get(sender_socket, "Unknown")
    for client_socket, channel in channels.items():
        if channel == sender_channel and client_socket != sender_socket:
            client_socket.send(f"{nicknames[sender_socket]}: {message}".encode())

# Send a private message to a specified client
def send_private_message(sender_socket, clients, channels, nicknames, recipient, message):
    for client_socket, nickname in nicknames.items():
        if nickname == recipient:
            client_socket.send(f"(Private) {nicknames[sender_socket]}: {message}".encode())
            return
    sender_socket.send(f"User {recipient} not found or offline.".encode())

def main(): # Scalability
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(5)

    print("Server is running on localhost:5555")

    # Dictionarie to manage clients, their channels, and nicknames
    clients = {}
    channels = {}
    nicknames = {}

    # Main loop to accept and handle client connections
    while True:
        client_socket, client_address = server.accept()
        # Handle each client in a separate thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, clients, channels, nicknames))
        client_thread.start()

if __name__ == "__main__":
    main()
