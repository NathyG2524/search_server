import socket
from timeit import timeit

HEADER = 64
PORT = 64511
SERVER = '127.0.1.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECTED!"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg): 
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' *(HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

# CONNECTED = True
# while CONNECTED:
#         msg_length = client.recv(HEADER).decode(FORMAT)
#         if msg_length:
#             msg_length = int(msg_length)
#             msg = client.recv(msg_length).decode(FORMAT)
#             if msg == DISCONNECT_MESSAGE:
#                 CONNECTED = False
#             print(f'[message] {msg}')
            # msg_list.append(msg)

msg1= '4;0;1;28;0;8;5;0;'
msg2= '200k.txt'
msg3= 'DISCONNECTED!'

# send_time = timeit(lambda: send(msg1), number=10000)
# send_time1 = timeit(lambda: send(msg2), number=10000)
# send_time = timeit(lambda: send(msg3), number=10000)
# print(f'send={send_time:.3f} ')
# print(f'send={send_time:.3f} ')
# print(f'send={send_time:.3f} ')
send(msg1)
send(msg2)
send(msg3)

data = client.recv(1024).decode(FORMAT)
print(f'message {data}')
