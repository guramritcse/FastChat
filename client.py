# Python program to implement client side of chat room.
import importlib
from operator import truediv
import colorama
from colorama import Fore
import socket
import select
import sys
import threading
from passlib.hash import sha256_crypt
import rsa
import cryptocode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os
import datetime
import re

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

# Initially connected to load balancer, after getting the server address we will
# remove the connection with the load balancer
server.connect((IP_address, Port))


group = ""
user = ""
confirm = ""
to_public = ""
prvt_key = ""
grp_prvt_keys = {}
grp_key_str = ""

last = -1


def user_interface(display_menu=0):
    global confirm, last, to_public, prvt_key, grp_key_str
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
                key = RSA.generate(1024)
                grp_pub_key_str = key.publickey().exportKey('PEM')
                grp_priv_key_str = key.exportKey('PEM')
                encrypted_pvt_key = cryptocode.encrypt(grp_priv_key_str.decode(), pwd)
                server.sendall(str(len(grp_pub_key_str)).zfill(4).encode('utf-8'))
                server.sendall(grp_pub_key_str)
                server.sendall(str(len(encrypted_pvt_key)).zfill(4).encode('utf-8'))
                server.sendall(encrypted_pvt_key.encode('utf-8'))
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                if (confirm == "y"):
                    confirm = "n"
                    grp_prvt_keys[grp_name] = grp_priv_key_str
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
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                co = 0
                if (confirm == "y"):
                    confirm = "n"
                    co = 1
                else:
                    # set for all confirm messages
                    print(f"{Fore.RED}No user found\n")
                lock.release()
                if co == 1:
                    public = RSA.importKey(to_public)
                    public = PKCS1_OAEP.new(public)
                    while (last == 1):
                        continue
                    lock.acquire()
                    last = 1
                    lock.release()
                    size = len(grp_key_str)
                    server.sendall(str(size).zfill(4).encode('utf-8'))
                    iter = size//86
                    for i in range(iter):
                        data = public.encrypt(grp_key_str[i*86:(i+1)*86].encode())
                        server.sendall(data)

                    if not size%86 == 0:
                        data = public.encrypt(grp_key_str[iter*86:].encode())
                        server.sendall(data)

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
                public = RSA.importKey(to_public)
                public = PKCS1_OAEP.new(public)
                msg = msg.encode('utf-8')

                if (len(to_send) > 2048):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    server.sendall("ab".encode('utf-8'))
                    continue

                server.sendall("co".encode('utf-8'))
                size = len(msg)
                server.sendall(str(size).zfill(4).encode('utf-8'))

                iter = size//86
                for i in range(iter):
                    data = public.encrypt(msg[i*86:(i+1)*86])
                    server.sendall(data)

                if not size%86 == 0:
                    data = public.encrypt(msg[iter*86:])
                    server.sendall(data)

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
                    server.sendall("ab".encode('utf-8'))
                    continue
                server.sendall("co".encode('utf-8'))
                try:
                    myfile = open(img_add, 'rb')
                    bytes = myfile.read()
                    size = len(bytes)
                except:
                    print(f"{Fore.RED}Error in loading the file\n")
                    server.sendall("ab".encode('utf-8'))
                    continue
                server.sendall("co".encode('utf-8'))
                public = RSA.importKey(to_public)
                public = PKCS1_OAEP.new(public)

                server.sendall(str(len(split_path[1])).zfill(1).encode('utf-8'))
                server.sendall(split_path[1].encode('utf-8'))
                server.sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                server.sendall(str(size).encode('utf-8'))
                
                iter = size//86
                for i in range(iter):
                    data = public.encrypt(bytes[i*86:(i+1)*86])
                    server.sendall(data)

                if not size%86 == 0:
                    data = public.encrypt(bytes[iter*86:])
                    server.sendall(data)
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
                public = RSA.importKey(to_public)
                public = PKCS1_OAEP.new(public)
                msg = msg.encode('utf-8')

                if (len(msg) > 2048):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    server.sendall("ab".encode('utf-8'))
                    continue

                server.sendall("co".encode('utf-8'))

                size = len(msg)
                server.sendall(str(size).zfill(4).encode('utf-8'))
                iter = size//86
                for i in range(iter):
                    data = public.encrypt(msg[i*86:(i+1)*86])
                    server.sendall(data)

                if not size%86 == 0:
                    data = public.encrypt(msg[iter*86:])
                    server.sendall(data)

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
                    server.sendall("ab".encode('utf-8'))
                    continue
                server.sendall("co".encode('utf-8'))
                try:
                    myfile = open(img_add, 'rb')
                    bytes = myfile.read()
                    size = len(bytes)
                except:
                    print(f"{Fore.RED}Error in loading the file\n")
                    server.sendall("ab".encode('utf-8'))
                    continue
                server.sendall("co".encode('utf-8'))
                public = RSA.importKey(to_public)
                public = PKCS1_OAEP.new(public)

                server.sendall(str(len(split_path[1])).zfill(1).encode('utf-8'))
                server.sendall(split_path[1].encode('utf-8'))
                server.sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                server.sendall(str(size).encode('utf-8'))
               
                iter = size//86
                for i in range(iter):
                    data = public.encrypt(bytes[i*86:(i+1)*86])
                    server.sendall(data)

                if not size%86 == 0:
                    data = public.encrypt(bytes[iter*86:])
                    server.sendall(data)

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


def receiving_func():
    global last, confirm, to_public, prvt_key, counter, grp_key_str
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

        elif (msg_to_come == "t"):
            confirm = "n"

        elif (msg_to_come == "e"):
            cnf = server.recv(1).decode('utf-8')
            if (cnf == "n"):
                confirm = "n"
            else:
                cnt = int(server.recv(4).decode('utf-8'))
                to_public = server.recv(cnt).decode('utf-8')
                confirm = "y"

        elif (msg_to_come == "k"):
            grp = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg=[]
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            p_key = b''.join(msg)
            enc_grp_pvt_key = cryptocode.encrypt(p_key.decode(), pwd)
            to_send = "{}:{}:".format("gk", grp).ljust(512, '0').encode('utf-8')
            server.sendall(to_send)
            server.sendall(str(len(enc_grp_pvt_key)).zfill(4).encode('utf-8'))
            server.sendall(enc_grp_pvt_key.encode('utf-8'))
            print(Fore.GREEN + f"You were added to group: {grp}")
            last=1

        elif (msg_to_come == "p"):
            grp_key_str = server.recv(
                    int(server.recv(4).decode('utf-8'))).decode('utf-8')
            grp_key_str = cryptocode.decrypt(grp_key_str, pwd)


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
            user = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            message = b''.join(msg)
            print(Fore.RED + "<" + user + "> " + message.decode('utf-8'))
            last = 1

        elif (msg_to_come == "g"):
            g_pvt_key_str = server.recv(int(server.recv(4).decode('utf-8'))).decode('utf-8')
            g_pvt_key_str = cryptocode.decrypt(g_pvt_key_str, pwd)
            g_prvt_key = RSA.importKey(g_pvt_key_str.encode())
            g_prvt_key = PKCS1_OAEP.new(g_prvt_key)
            user = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            grp = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            message = b''.join(msg)
            print(Fore.RED + "<Group: " + grp + "> " + "<User: " + user + "> " + message.decode('utf-8'))
            last = 1

        elif (msg_to_come == "a"):
            g_pvt_key_str = server.recv(int(server.recv(4).decode('utf-8'))).decode('utf-8')
            g_pvt_key_str = cryptocode.decrypt(g_pvt_key_str, pwd)
            g_prvt_key = RSA.importKey(g_pvt_key_str.encode())
            g_prvt_key = PKCS1_OAEP.new(g_prvt_key)
            user = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            grp = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            ext = server.recv(int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            message = b''.join(msg)
            print(Fore.RED + "<Group: " + grp + "> " + "<User: " + user + "> " + "Sent a file which is placed at " + f"__received__{usr}__/{grp}_{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(f"__received__{usr}__/{grp}_{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter+= 1
            last = 1
        
        elif (msg_to_come == "b"):
            user = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            ext = server.recv(int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            message = b''.join(msg)
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
server.sendall("c".encode('utf-8'))
while not success:
    try:
        x = int(input(f"{Fore.MAGENTA}1. Login\n2. Sign Up\n3. Quit\n{Fore.YELLOW}"))
    except:
        print(f"{Fore.RED}Invalid option\n")
        continue
    
    # login
    if x == 1:
        usr = input(f"{Fore.CYAN}Enter user name: ")
        pwd = input(f"{Fore.CYAN}Enter your password: ")

        # Need to change this, no need to send the password
        to_send = "{}:{}:{}".format(1, usr, pwd).encode('utf-8')
        if (len(to_send) > 512):
            print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
            continue
        server.sendall(to_send)
        user_found = server.recv(1).decode('utf-8')
        if (user_found == "y"):
            encrypted_len = server.recv(4)
            password = server.recv(
                int(encrypted_len.decode('utf-8'))).decode('utf-8')
            if (sha256_crypt.verify(pwd, password)):
                success = True
                server.sendall(bytes("y", 'utf-8'))
                private_key_str = server.recv(
                    int(server.recv(4).decode('utf-8'))).decode('utf-8')

                private_key_str = cryptocode.decrypt(private_key_str, pwd)
                prvt_key = RSA.importKey(private_key_str.encode())
                prvt_key = PKCS1_OAEP.new(prvt_key)
                print(f"{Fore.GREEN}Successfully logged in\n")
            else:
                server.sendall(bytes("n", 'utf-8'))
                print(f"{Fore.RED}Invalid username or password\n")
        elif user_found == "n":
            print(f"{Fore.RED}Invalid username or password\n")
        else:
            print(f"{Fore.RED}Already logged in at another screen\n")

    # signup
    elif x == 2:
        usr = input(f"{Fore.CYAN}Enter user name: ")
        pwd = input(f"{Fore.CYAN}Enter your password: ")
        to_send = "{}:{}:{}".format(
            2, usr, sha256_crypt.hash(pwd)).encode('utf-8')
        if (len(to_send) > 1024):
            print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
            continue
        server.sendall(to_send)
        confirm = server.recv(1)
        confirm = confirm.decode('utf-8')
        if (confirm == "y"):
            key = RSA.generate(1024)
            public_key_str = key.publickey().exportKey('PEM')
            priv_key = key.exportKey('PEM')
            encrypted_pvt_key = cryptocode.encrypt(priv_key.decode(), pwd)
            server.sendall(str(len(public_key_str)).zfill(4).encode('utf-8'))
            server.sendall(public_key_str)
            server.sendall(str(len(encrypted_pvt_key)).zfill(4).encode('utf-8'))
            server.sendall(encrypted_pvt_key.encode('utf-8'))

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
server_data = eval(server.recv(
    int(server.recv(3).decode('utf-8'))).decode('utf-8'))

# Closing the connection
server.close()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connected to new server, closed the previous connection
server.connect((server_data[0], server_data[1]))
server.sendall("c".encode('utf-8'))

server.sendall(str(len(usr)).zfill(3).encode('utf-8'))
server.sendall(usr.encode('utf-8'))

# Receiving all the messages here first
num_msgs = int(server.recv(4).decode('utf-8'))
if num_msgs > 0:
    print(Fore.GREEN + "The messages received by you while you were offline are:")
    default_length = 128
    for i in range(num_msgs):
        code = server.recv(2).decode('utf-8')
        if code == "in":
            user = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            message = b''.join(msg)
            print(Fore.RED + "<" + user + "> " + message.decode('utf-8'))

        elif code == "iy":
            user = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            ext = server.recv(int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            message = b''.join(msg)
            print(Fore.RED + "<" + user + "> " + "Sent a file which is placed at " + f"__received__{usr}__/{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(f"__received__{usr}__/{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter+= 1
        elif code == "gn":
            g_pvt_key_str = server.recv(int(server.recv(4).decode('utf-8'))).decode('utf-8')
            g_pvt_key_str = cryptocode.decrypt(g_pvt_key_str, pwd)
            g_prvt_key = RSA.importKey(g_pvt_key_str.encode())
            g_prvt_key = PKCS1_OAEP.new(g_prvt_key)
            user = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            grp = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            message = b''.join(msg)
            print(Fore.RED + "<Group: " + grp + "> " + "<User: " + user + "> " + message.decode('utf-8'))
        elif code == "gy":     
            g_pvt_key_str = server.recv(int(server.recv(4).decode('utf-8'))).decode('utf-8')
            g_pvt_key_str = cryptocode.decrypt(g_pvt_key_str, pwd)
            g_prvt_key = RSA.importKey(g_pvt_key_str.encode())
            g_prvt_key = PKCS1_OAEP.new(g_prvt_key)
            user = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            grp = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            ext = server.recv(int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            message = b''.join(msg)
            print(Fore.RED + "<Group: " + grp + "> " + "<User: " + user + "> " + "Sent a file which is placed at " + f"__received__{usr}__/{grp}_{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(f"__received__{usr}__/{grp}_{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter+= 1
        elif code == "gk":
            grp = server.recv(int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg=[]
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size%86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            p_key = b''.join(msg)
            enc_grp_pvt_key = cryptocode.encrypt(p_key.decode(), pwd)
            to_send = "{}:{}:".format("gk", grp).ljust(512, '0').encode('utf-8')
            server.sendall(to_send)
            server.sendall(str(len(enc_grp_pvt_key)).zfill(4).encode('utf-8'))
            server.sendall(enc_grp_pvt_key.encode('utf-8'))
            print(Fore.GREEN + f"You were added to group: {grp}")

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
