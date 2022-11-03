# Python program to implement client side of chat room.
from operator import truediv
import colorama
from colorama import Fore
import socket
import select
import sys
import threading

from _thread import *

menu_option=[]
menu_option.append(f"{Fore.GREEN}***** Main Menu *****\n{Fore.CYAN}Press {Fore.RED}'g' {Fore.CYAN}for managing groups\nPress {Fore.RED}'b' {Fore.CYAN}to send group message\nPress {Fore.RED}'d' {Fore.CYAN}to send direct message\nPress {Fore.RED}'l' {Fore.CYAN}to logout\n{Fore.RED}")
menu_option.append(f"{Fore.GREEN}***** Group Settings *****\nPress 'n' {Fore.CYAN}to create a new group\nPress 'm' {Fore.CYAN}to manage an existing group\nPress 'q' {Fore.CYAN}to go to previous menu\n")
menu_option.append(f"{Fore.GREEN}***** Manage Existing Group *****\n{Fore.CYAN}Press 'a' {Fore.CYAN}to add a new member\nPress {Fore.RED}'r' {Fore.CYAN}to remove a member\nPress {Fore.RED}'s' {Fore.CYAN}to see all members in the group\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n{Fore.RED}")
menu_option.append(f"{Fore.GREEN}***** Group message *****\n{Fore.CYAN}Press 't' {Fore.CYAN}to type a message\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n{Fore.RED}")
menu_option.append(f"{Fore.GREEN}***** Direct message *****\n{Fore.CYAN}Press 't' {Fore.CYAN}to type a message\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n{Fore.RED}")
# menu_option.append(f"{Fore.CYAN}Press {Fore.RED}'t' {Fore.CYAN}to type another message\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n{Fore.RED}")

inp_option=[]
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter group name to manage: ")
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter username to add to the group: ")
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter username to remove from the group: ")
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter group name to create: ")
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter group name to which you want to send message: ")
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter username to whom you want to send message: ")




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))


usr = ""
group = ""
user = ""
confirm = ""

def user_interface(display_menu=0):
    while (True):
        choice=input(menu_option[display_menu])
        if display_menu==0:
            if choice=='g':
                display_menu=1
            elif choice=='b':
                grp_name=input(inp_option[4])
                to_send = "{}:{}:{}".format("cg", usr, grp_name).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # confirm = server.recv(1)
                # confirm = confirm.decode('utf-8')
                if(confirm == "y"):
                    display_menu=3
                else:
                    print(f"{Fore.RED}No group found\n")
            elif choice=='d':
                ind_name=input(inp_option[5])
                to_send = "{}:{}:{}".format("ci", usr, ind_name).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # confirm = server.recv(1)
                # confirm = confirm.decode('utf-8')
                if(confirm == "y"):
                    user=ind_name
                    display_menu=4
                else:
                    print(f"{Fore.RED}No user found\n")
            elif choice=='l':
                to_send="quit".encode('utf-8')
                server.sendall(to_send)
                exit()
            else:
                print("Invalid option")
        elif display_menu==1:
            if choice=='n':
                grp_name=input(inp_option[3])
                to_send = "{}:{}:{}".format("ng", usr, grp_name).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # confirm = server.recv(1)
                # confirm = confirm.decode('utf-8')
                if(confirm == "y"):
                    print(f"{Fore.GREEN}New group created\n")
                else:
                    print(f"{Fore.RED}Group already exists\n")
            elif choice=='m':
                grp_name=input(inp_option[0])
                to_send = "{}:{}:{}".format("eg", usr, grp_name).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # confirm = server.recv(1)
                # confirm = confirm.decode('utf-8')
                if(confirm == "y"):
                    group = grp_name
                else:
                    print(f"{Fore.RED}No group found\n")
                    display_menu=2
            elif choice=='q':
                display_menu=0
            else:
                print("Invalid option")
        elif display_menu==2:
            if choice=='a':
                ind_name=input(inp_option[1])
                to_send = "{}:{}:{}:{}".format("ai", usr, group, ind_name).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # confirm = server.recv(1)
                # confirm = confirm.decode('utf-8')
                if(confirm == "y"):
                     print(f"{Fore.GREEN}User added\n")
                else:
                    print(f"{Fore.RED}No user found\n")
            elif choice=='r':
                ind_name=input(inp_option[1])
                to_send = "{}:{}:{}:{}".format("ri", usr, group, ind_name).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # confirm = server.recv(1)
                # confirm = confirm.decode('utf-8')
                if(confirm == "y"):
                    print(f"{Fore.GREEN}User removed\n")
                else:
                    print(f"{Fore.RED}No user found in group\n")
            elif choice=='s':
                to_send = "{}:{}:{}".format("fa", usr, group).encode('utf-8')
                server.sendall(to_send)
            elif choice=='q':
                display_menu=1
            else:
                print("Invalid option")
        elif display_menu==3:
            if choice=='t':
                msg=input()
                to_send = "{}:{}:{}:{}".format("wg", usr, group, msg).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # confirm = server.recv(1)
                # confirm = confirm.decode('utf-8')
                if(confirm == "y"):
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
            elif choice=='q':
                display_menu=0
            else:
                print("Invalid option")
        elif display_menu==4:
            if choice=='t':
                msg=input()
                to_send = "{}:{}:{}:{}".format("wi", usr, user, msg).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # confirm = server.recv(1)
                # confirm = confirm.decode('utf-8')
                if(confirm == "y"):
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
            elif choice=='q':
                display_menu=0
            else:
                print("Invalid option")
        # elif display_menu==5:
        #     if choice=='t':
        #         pass
        #     elif choice=='q':
        #         display_menu=0
        #     else:
        #         print("Invalid option")
       

def receiving_func():
    while (True):
        msg_to_come=server.recv(1).decode('utf-8')
        if(msg_to_come=="c"):
            confirm=server.recv(1).decode('utf-8')
        elif(msg_to_come=="s"):
            members=server.recv(2048).decode('utf-8')
            members=members.split(":")
            for member in members:
                print(Fore.YELLOW+member)



success = False
while not success:
    x = int(input(f"{Fore.MAGENTA}1. Login\n2. Sign Up\n3. Quit\n"))
    if x == 1:
        usr = input(f"{Fore.CYAN}Enter user name: ")
        pwd = input(f"{Fore.CYAN}Enter your password: ")
        to_send = "{}:{}:{}".format(1, usr, pwd).encode('utf-8')
        if (len(to_send) > 512):
            print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
            continue
        server.sendall(to_send)
        confirm = server.recv(1)
        confirm = confirm.decode('utf-8')
        if (confirm == "y"):
            success = True
            print(f"{Fore.GREEN}Successfully logged in\n")
        else:
            print(f"{Fore.RED}Invalid username or password\n")

    elif x == 2:
        usr = input(f"{Fore.CYAN}Enter user name: ")
        pwd = input(f"{Fore.CYAN}Enter your password: ")
        to_send = "{}:{}:{}".format(2, usr, pwd).encode('utf-8')
        if (len(to_send) > 512):
            print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
            continue
        server.sendall(to_send)
        confirm = server.recv(1)
        confirm = confirm.decode('utf-8')
        print(confirm)
        if (confirm == "y"):
            success = True
            print(f"{Fore.GREEN}Successfully signed up\n")
        else:
            print(f"{Fore.RED}Username already taken\n")

    elif x == 3:
        to_send="quit".encode('utf-8')
        server.sendall(to_send)
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

server.close()
