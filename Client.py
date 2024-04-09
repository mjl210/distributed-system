import socket
import threading

# receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == "You are disconnected from the server":
                break  # Exit loop if disconnected
            print(message)
        except Exception as e:
            print(f"Connection error: {e}")
            break
    client_socket.close()  # Ensure socket is closed

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5555))

    # Start a thread to listen for messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Main loop to send messages to the server
    while True:
        message = input()
        client_socket.send(message.encode())
        if message == '/disconnect':
            client_socket.close()
            break  # Exit if disconnected

if __name__ == "__main__":
    main()
