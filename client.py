# Python program to implement client side of chat room.
from operator import truediv
import socket
import select
import sys


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))

success = False
while not success:
    x = int(input("1. Login\n2. Sign Up\n3. Quit\n"))
    if x == 1:
        usr = input("Enter user name")
        pwd = input("Enter your password")
        to_send = "{}:{}:{}".format(1, usr, pwd).encode('utf-8')
        if (len(to_send) > 512):
            print("Exceeded maximum length \nRetry\n")
            continue

        server.sendall(to_send)
        confirm = server.recv(1)
        confirm = confirm.decode('utf-8')
        if (confirm == "y"):
            success = True
        else:
            print("Invalid username or password\n")

    elif x == 2:
        usr = input("Enter user name")
        pwd = input("Enter your password")
        to_send = "{}:{}:{}".format(2, usr, pwd).encode('utf-8')
        if (len(to_send) > 512):
            print("Exceeded maximum length \nRetry\n")
            continue

        server.sendall(to_send)
        confirm = server.recv(1)
        confirm = confirm.decode('utf-8')
        if (confirm == "y"):
            success = True
        else:
            print("Username already taken\n")

    elif x == 3:
        server.sendall(b"quit")
        exit()

    else:
        print("Invalid Input")

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    """ There are two possible input situations. Either the
	user wants to give manual input to send to other people,
	or the server is sending a message to be printed on the
	screen. Select returns from sockets_list, the stream that
	is reader for input. So for example, if the server wants
	to send a message, then the if condition will hold true
	below.If the user wants to send a message, the else
	condition will evaluate as true"""
    read_sockets, write_socket, error_socket = select.select(
        sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            print(message.decode('utf-8'))
        else:
            message = sys.stdin.readline()
            server.send(bytes(message, 'utf-8'))
            sys.stdout.write("<You>")
            sys.stdout.write(message)
            sys.stdout.flush()

server.close()
