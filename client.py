# Python program to implement client side of chat room.
import imp
import os
import datetime
import re
from operator import truediv
import colorama
from colorama import Fore
import socket
import select
import sys
import threading

from _thread import *
lock = threading.Lock()

allowed_ext=[".png", ".jpg", ".jpeg", ".txt"]
counter=int(''.join(re.findall(r'\d+', str(datetime.datetime.utcnow()))))

menu_option = []
menu_option.append(f"{Fore.GREEN}***** Main Menu *****\n{Fore.CYAN}Press {Fore.RED}'g' {Fore.CYAN}for managing groups\nPress {Fore.RED}'b' {Fore.CYAN}to send group message\nPress {Fore.RED}'d' {Fore.CYAN}to send direct message\nPress {Fore.RED}'l' {Fore.CYAN}to logout\n{Fore.RED}")
menu_option.append(f"{Fore.GREEN}***** Group Settings *****\n{Fore.CYAN}Press {Fore.RED}'n' {Fore.CYAN}to create a new group\nPress {Fore.RED}'m' {Fore.CYAN}to manage an existing group\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n{Fore.RED}")
menu_option.append(f"{Fore.GREEN}***** Manage Existing Group *****\n{Fore.CYAN}Press {Fore.RED}'a' {Fore.CYAN}to add a new member\nPress {Fore.RED}'r' {Fore.CYAN}to remove a member\nPress {Fore.RED}'s' {Fore.CYAN}to see all members in the group\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n{Fore.RED}")
menu_option.append(f"{Fore.GREEN}***** Group message *****\n{Fore.CYAN}Press {Fore.RED}'t' {Fore.CYAN}to type a message\nPress {Fore.RED}'i' {Fore.CYAN}to send an image or text file\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n{Fore.RED}")
menu_option.append(f"{Fore.GREEN}***** Direct message *****\n{Fore.CYAN}Press {Fore.RED}'t' {Fore.CYAN}to type a message\nPress {Fore.RED}'i' {Fore.CYAN}to send an image or text file\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n{Fore.RED}")

inp_option = []
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter group name to manage: ")
inp_option.append(
    f"{Fore.LIGHTMAGENTA_EX}Enter username to add to the group: ")
inp_option.append(
    f"{Fore.LIGHTMAGENTA_EX}Enter username to remove from the group: ")
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter group name to create: ")
inp_option.append(
    f"{Fore.LIGHTMAGENTA_EX}Enter group name to which you want to send message: ")
inp_option.append(
    f"{Fore.LIGHTMAGENTA_EX}Enter username to whom you want to send message: ")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))


group = ""
user = ""
confirm = ""

last = -1


def user_interface(display_menu=0):
    global confirm, last
    while (True):
        choice = input(menu_option[display_menu])
        if display_menu == 0:

            if choice == 'g':
                display_menu = 1

            elif choice == 'b':
                grp_name = input(inp_option[4])
                to_send = "{}:{}".format("cg", grp_name).encode('utf-8')

                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)

                while (last == 1):
                    continue
                lock.acquire()
                last = 1

                if (confirm == "y"):
                    confirm = "n"
                    group = grp_name  # This line was added later
                    display_menu = 3
                else:
                    print(f"{Fore.RED}No group found\n")
                lock.release()

            elif choice == 'd':
                ind_name = input(inp_option[5])
                to_send = "{}:{}".format("ci", ind_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1

                if (confirm == "y"):
                    confirm = "n"
                    user = ind_name
                    display_menu = 4
                else:
                    print(f"{Fore.RED}No user found\n")
                lock.release()

            elif choice == 'l':
                to_send = "quit".encode('utf-8')
                server.sendall(to_send)
                return

            else:
                print(f"{Fore.RED}Invalid option")

        elif display_menu == 1:
            if choice == 'n':
                grp_name = input(inp_option[3])
                to_send = "{}:{}".format("ng", grp_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)

                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}New group created\n")
                else:
                    print(f"{Fore.RED}Group already exists\n")
                lock.release()

            elif choice == 'm':
                grp_name = input(inp_option[0])
                to_send = "{}:{}".format("eg", grp_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if (confirm == "y"):
                    confirm = "n"
                    group = grp_name
                    display_menu = 2
                else:
                    print(f"{Fore.RED}No group found\n")
                lock.release()

            # elif choice == 's':
            #     to_send = "{}:{}".format("fa", group).encode('utf-8')
            #     server.sendall(to_send)

            elif choice == 'q':
                display_menu = 0

            else:
                print(f"{Fore.RED}Invalid option")

        elif display_menu == 2:
            if choice == 'a':
                ind_name = input(inp_option[1])
                to_send = "{}:{}:{}".format(
                    "ai", group, ind_name).encode('utf-8')
                if (len(to_send) > 10):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}User added\n")
                else:
                    # set for all confirm messages
                    print(f"{Fore.RED}No user found\n")
                lock.release()

            elif choice == 'r':
                ind_name = input(inp_option[2])
                to_send = "{}:{}:{}".format(
                    "ri", group, ind_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}User removed\n")
                else:
                    print(f"{Fore.RED}No user found in group\n")
                lock.release()

            elif choice == 's':
                to_send = "{}:{}".format("sa", group).encode('utf-8')
                server.sendall(to_send)

                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                confirm = "n"
                lock.release()

            elif choice == 'q':
                display_menu = 1

            else:
                print(f"{Fore.RED}Invalid option")

        elif display_menu == 3:
            if choice == 't':
                to_send = "wg:{}".format(group).encode('utf-8')
                server.sendall(to_send)
                msg = input()
                to_send = "{}".format(msg).encode('utf-8')

                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    server.send("ab".encode('utf-8'))
                    continue
                
                server.send("co".encode('utf-8'))
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
                lock.release()

            elif choice=='i':
                to_send = "{}:{}".format("ig", group).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                img_add=input(f"{Fore.GREEN}Give complete address of image or text file from current working directory:\n")
                split_path=os.path.splitext(img_add)
                if not split_path[1] in allowed_ext:
                    print(f"{Fore.RED}Extension not supported\n")
                    server.send("ab".encode('utf-8'))
                    continue
                server.send("co".encode('utf-8'))
                try:
                    myfile = open(img_add, 'rb')
                    bytes = myfile.read()
                    size = len(bytes)
                except:
                    print(f"{Fore.RED}Error in loading the file\n")
                    server.send("ab".encode('utf-8'))
                    continue
                server.send("co".encode('utf-8'))
                server.send(str(len(split_path[1])).zfill(1).encode('utf-8'))
                server.sendall(split_path[1].encode('utf-8'))
                server.send(str(len(str(size))).zfill(2).encode('utf-8'))
                server.sendall(str(size).encode('utf-8'))
                server.sendall(bytes)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if(confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
                lock.release()

            elif choice == 'q':
                display_menu = 0
            else:
                print(f"{Fore.RED}Invalid option")

        elif display_menu == 4:
            if choice == 't':
                to_send = "wi:{}".format(user).encode('utf-8')
                server.sendall(to_send)
                msg = input()
                to_send = "{}".format(msg).encode('utf-8')

                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    server.send("ab".encode('utf-8'))
                    continue
                server.send("co".encode('utf-8'))
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
                lock.release()

            elif choice=='i':
                to_send = "{}:{}".format("ii", user).encode('utf-8')
                if(len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                img_add=input(f"{Fore.GREEN}Give complete address of image or text file from current working directory:\n")
                split_path=os.path.splitext(img_add)
                if not split_path[1] in allowed_ext:
                    print(f"{Fore.RED}Extension not supported\n")
                    server.send("ab".encode('utf-8'))
                    continue
                server.send("co".encode('utf-8'))
                try:
                    myfile = open(img_add, 'rb')
                    bytes = myfile.read()
                    size = len(bytes)
                except:
                    print(f"{Fore.RED}Error in loading the file\n")
                    server.send("ab".encode('utf-8'))
                    continue
                server.send("co".encode('utf-8'))
                server.send(str(len(split_path[1])).zfill(1).encode('utf-8'))
                server.sendall(split_path[1].encode('utf-8'))
                server.send(str(len(str(size))).zfill(2).encode('utf-8'))
                server.sendall(str(size).encode('utf-8'))
                server.sendall(bytes)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if(confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
                lock.release()

            elif choice == 'q':
                display_menu = 0
            else:
                print(f"{Fore.RED}Invalid option")
        # lock.release()


def receiving_func():
    global last, confirm, counter
    while (True):
        while (last == 2):
            continue
        lock.acquire()
        last = 2
        msg_to_come = server.recv(1).decode('utf-8')

        if (msg_to_come == "c"):
            confirm = server.recv(1).decode('utf-8')

        elif (msg_to_come == "y"):
            confirm = "y"

        elif (msg_to_come == "n"):
            confirm = "n"

        elif (msg_to_come == "l"):
            confirm = "n"

        elif (msg_to_come == "p"):
            confirm = "n"

        elif (msg_to_come == "s"):
            members = server.recv(2048).decode('utf-8')
            if (members == 'n'):
                confirm = "n"
            else:
                print(Fore.WHITE +
                      "The following members are present in the group:")
                members = members.split(":")
                for member in members:
                    print(Fore.YELLOW+member)
                confirm = "y"

        elif (msg_to_come == "u"):
            user = server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8')
            message = server.recv(512).decode('utf-8')
            print(Fore.RED + "<" + user + "> " + message)
            last = 1

        elif (msg_to_come == "g"):
            user = server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8')
            grp = server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8')
            message = server.recv(512).decode('utf-8')
            print(Fore.RED + "<Group: " + grp + "> " +
                  "<User: " + user + "> " + message)
            last = 1

        elif (msg_to_come == "a"):
            user = server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8')
            grp = server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8')
            ext = server.recv(int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            message = server.recv(size)
            print(Fore.RED + "<Group: " + grp + "> " + "<User: " + user + "> " + "Sent a file which is placed at " + f"__received__{usr}__/{grp}_{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(f"__received__{usr}__/{grp}_{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter+= 1
            last = 1

        elif (msg_to_come == "b"):
            user = server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8')
            ext = server.recv(int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            message = server.recv(size)
            print(Fore.RED + "<" + user + "> " + "Sent a file which is placed at " + f"__received__{usr}__/{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(f"__received__{usr}__/{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter+= 1
            last = 1

        elif (msg_to_come == "q"):
            print(Fore.GREEN+"Logged out successfully")
            return
        lock.release()


usr = ""
success = False
while not success:
    x = int(
        input(f"{Fore.MAGENTA}1. Login\n2. Sign Up\n3. Quit\n{Fore.YELLOW}"))
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
        if (confirm == "y"):
            print(f"{Fore.GREEN}Successfully signed up\nPlease login\n")
        else:
            print(f"{Fore.RED}Username already taken\n")

    elif x == 3:
        to_send = "quit".encode('utf-8')
        server.sendall(to_send)
        exit()

    else:
        print("Invalid Input")
# user is now logged in


# Receiving all the messages here first
num_msgs = int(server.recv(2).decode('utf-8'))
if num_msgs > 0:
    print(Fore.GREEN + "The messages received by you while you were offline are:")
for i in range(num_msgs):
    code = server.recv(2).decode('utf-8')
    if code == "in":
        msg = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
        print(Fore.RED + msg)
    elif code == "iy":
        user = server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8')
        ext = server.recv(int(server.recv(1).decode('utf-8'))).decode('utf-8')
        size = int(server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8'))
        message = server.recv(size)
        print(Fore.RED + "<" + user + "> " + "Sent a file which is placed at " + f"__received__{usr}__/{user}_{counter}{ext}")
        if not os.path.exists(f"__received__{usr}__"):
            os.makedirs(f"__received__{usr}__")
        myfile = open(f"__received__{usr}__/{user}_{counter}{ext}", 'wb')
        myfile.write(message)
        myfile.close()
        counter+= 1
    elif code == "gn":
        msg = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
        print(Fore.RED + msg)
    elif code == "gy":     
        user = server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8')
        grp = server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8')
        ext = server.recv(int(server.recv(1).decode('utf-8'))).decode('utf-8')
        size = int(server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8'))
        message = server.recv(size)
        print(Fore.RED + "<Group: " + grp + "> " + "<User: " + user + "> " + "Sent a file which is placed at " + f"__received__{usr}__/{grp}_{user}_{counter}{ext}")
        if not os.path.exists(f"__received__{usr}__"):
            os.makedirs(f"__received__{usr}__")
        myfile = open(f"__received__{usr}__/{grp}_{user}_{counter}{ext}", 'wb')
        myfile.write(message)
        myfile.close()
        counter+= 1
print()


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