# Python program to implement client side of chat room.
from operator import truediv
import socket
import select
import sys
import threading

from _thread import *


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))


def user_interface():
    while (True):
        choice1 = input(
            "What do you want to do?\n1. For managing groups enter 'g'\n2. For sending a message in group enter 'b'\n3. For sending a DM enter 'd'\n4. To logout enter 'l'\n")

        if (choice1 == 'g'):
            server.sendall(choice1.encode('utf-8'))
            choice2 = input(
                "Group Settings\n1. For creating a new group enter 'n'\n2. For managing an existing group enter 'e'\n3. To return to previous menu enter 'q'\n")
            if (choice2 == 'n'):
                grp_name = input("Enter group name:")
                pass
            elif (choice2 == 'e'):
                pass
            elif (choice2 == 'q'):
                continue
            else:
                print("Please give valid input")

        elif (choice1 == 'b'):
            server.sendall(choice1.encode('utf-8'))
            pass

        elif (choice1 == 'd'):
            server.sendall(choice1.encode('utf-8'))

            receiver = input("Who do you want to send the message to ?\n")
            server.sendall(receiver.encode('utf-8'))

            message = input("Please enter the message\n")
            server.sendall(message.encode('utf-8'))

        elif (choice1 == 'l'):
            server.sendall(choice1.encode('utf-8'))
            pass
        else:
            print("Please give valid input")


def receiving_func():
    # message not none

    while (True):
        message = server.recv(2048)
        print(message.decode('utf-8'))


success = False
while not success:
    x = int(input("1. Login\n2. Sign Up\n3. Quit\n\n"))
    usr = ""
    if x == 1:
        usr += input("Enter user name: ")
        pwd = input("Enter your password: ")
        to_send = "{}:{}:{}".format(1, usr, pwd).encode('utf-8')
        if (len(to_send) > 512):
            print("Exceeded maximum length \nRetry\n")
            continue

        server.sendall(to_send)
        confirm = server.recv(1)
        confirm = confirm.decode('utf-8')
        if (confirm == "y"):
            success = True
            print('Successfully logged in\n')
        else:
            print("Invalid username or password\n")

    elif x == 2:
        usr += input("Enter user name: ")
        pwd = input("Enter your password: ")
        to_send = "{}:{}:{}".format(2, usr, pwd).encode('utf-8')
        if (len(to_send) > 512):
            print("Exceeded maximum length \nRetry\n")
            continue

        server.sendall(to_send)
        confirm = server.recv(1)
        confirm = confirm.decode('utf-8')
        print(confirm)
        if (confirm == "y"):
            success = True
            print('Successfully signed up\n')
        else:
            print("Username already taken\n")

    elif x == 3:
        server.sendall(b"quit")
        exit()

    else:
        print("Invalid Input")
# user is now logged in

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

    # start_new_thread(receiving_func, ())
    # start_new_thread(user_interface, ())

    # read_sockets, write_socket, error_socket = select.select(
    # sockets_list, [], [])
    # print("tttttttttt")
    # print(read_sockets)
    # print("tttttttttt")

    thread1 = threading.Thread(target=receiving_func, args=())
    thread2 = threading.Thread(target=user_interface, args=())
    # Starting thread 1
    thread1.start()

   # Starting thread 2
    thread2.start()

    # Wait until thread 1 is completely executed
    thread1.join()

   # Wait until thread 2 is completely executed
    thread2.join()

    # for socks in read_sockets:
    #     if socks == server:
    #         # print("ttt")
    #         start_new_thread(receiving_func, ()).start()
    #     else:
    #         inp = sys.stdin.readline().strip()
    #         start_new_thread(user_interface, ()).start()
    # print("aa")
    # start_new_thread(receiving_func, ()).join()
    # start_new_thread(user_interface, ()).join()
    # message = sys.stdin.readline()
    # server.send(bytes(message, 'utf-8'))
    # sys.stdout.write("<You>")
    # sys.stdout.write(message)
    # sys.stdout.flush()


server.close()