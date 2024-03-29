import ipaddress
import threading
import socket
import time

print('           ______ _____  _____    _____                          ')
print('     /\   |  ____/ ____|/ ____|  / ____|                         ')
print('    /  \  | |__ | |    | (___   | (___   ___ _ ____   _____ _ __ ')
print('   / /\ \ |  __|| |     \___ \   \___ \ / _ \ \'__\ \ / / _ \ \'__|')
print('  / ____ \| |___| |____ ____) |  ____) |  __/ |   \ V /  __/ |   ')
print(' /_/    \_\______\_____|_____/  |_____/ \___|_|    \_/ \___|_|   ')
print('          AECS Server               Ver 0.13')
# Connection Data
host = input("Input host ip: ")
port = input("Input listen port: ")

# Debug
# host = "192.168.50.168"
# port = "12345"

#Check user input
check_input_state = False
while True:
    if host == "" or port == "":
        print("You must fill in all the fields.")
        host = input("Input host ip: ")
        port = input("Input port: ")
    elif host != "" or port != "":
        try:
            ipaddress.ip_address(host)
            try:
                port_check = int(port)
                if port_check < 0 or port_check > 65353:
                    print("Invalid port number.")
                    port = input("Input port: ")
                else:
                    check_input_state = True
                    break
            except ValueError:
                print("Invalid port number.")
                port = input("Input port: ")
        except ValueError:
            print("Invalid IP address.")
            host = input("Input server ip: ")

# Starting Server
if check_input_state == True:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, int(port)))
    server.listen()
else:
    exit()

# Lists For Clients , Their Nicknames and key
clients = []
nicknames = []
keys = []
# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)
        
# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024) #1024 bytes is recv_size
            
            index = clients.index(client)
            if(index == 1):
                clients[0].send(message)
            else:
                clients[1].send(message)
            #broadcast(message)
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            key = keys[index]
            broadcast('SYSTEM_MESSAGE{} left!'.format(nickname).encode('ascii'))
            print(nickname + ' disconnected!')
            nicknames.remove(nickname)
            keys.remove(key)
            time.sleep(0.1)
            user_number = len(clients)
            broadcast("SYSTEM_MESSAGE%USER_NUMCurrent online user number: {}".format(user_number).encode('ascii'))
            break
            
# Exchange public key
def exchangekey():
    print('Start exchange public key......')
    clients[0].send('GET_PUBLIC_KEY'.encode('ascii'))
    clients[0].send(keys[1].encode('ascii'))
    
    clients[1].send('GET_PUBLIC_KEY'.encode('ascii'))
    clients[1].send(keys[0].encode('ascii'))
    print('Public key exchange is successful!!!')
    
# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        
        if(len(clients) == 2):
            client.send('SYSTEM_MESSAGEThe server is full!!!'.encode('ascii'))
            client.close()
            continue
        
        # Request And Store Nickname
        client.send('REQUEST_NICKNAME'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)
        
        # Request And Store the public key
        client.send('REQUEST_PUBLIC_KEY'.encode('ascii'))
        key = client.recv(1024).decode('ascii')
        keys.append(key)
            
        # Print And Broadcast Nickname, Current User Number
        print("New users joined to the server - {}".format(nickname))
        user_number = len(clients)
        print(f'{"Current online user number:"} {user_number}')
        
        if len(clients) == 2:
            exchangekey()
        
        time.sleep(1)
        broadcast("SYSTEM_MESSAGE{} joined!".format(nickname).encode('ascii'))
        time.sleep(0.1)
        broadcast("SYSTEM_MESSAGE%USER_NUMCurrent online user number: {}".format(user_number).encode('ascii'))
        
        client.send('SYSTEM_MESSAGEConnected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()