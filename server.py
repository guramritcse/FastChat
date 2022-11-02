# Python program to implement server side of chat room.
import socket
import select
import sys
import psycopg2

'''Replace "thread" with "_thread" for python 3'''
from _thread import *

"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()

# takes the first argument from command prompt as IP address
IP_address = str(sys.argv[1])

# takes second argument from command prompt as port number
Port = int(sys.argv[2])

"""
binds the server to an entered IP address and at the
specified port number.
The client must be aware of these parameters
"""
server.bind((IP_address, Port))

"""
listens for 100 active connections. This number can be
increased as per convenience.
"""
server.listen(100)

list_of_clients = []
username_conn = {}

dbconn = psycopg2.connect(database="fastchat", user="postgres",
                          password="", host="127.0.0.1", port="5432")
cur = dbconn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS GROUPS
      (NAME VARCHAR(50) NOT NULL,
      ADMIN VARCHAR(50) NOT NULL,
	  CONSTRAINT PK_GROUP PRIMARY KEY(NAME, ADMIN));''')

cur.execute('''CREATE TABLE IF NOT EXISTS CREDENTIALS
      (USERNAME VARCHAR(50) PRIMARY KEY NOT NULL,
	  PASSWORD VARCHAR(50) NOT NULL);''')

cur.execute('''CREATE TABLE IF NOT EXISTS ONLINE
      (USERNAME VARCHAR(50) PRIMARY KEY NOT NULL,
	  PORT TEXT NOT NULL);''')

cur.execute('''CREATE TABLE IF NOT EXISTS INDVMSSGS
      (SENDER VARCHAR(50) NOT NULL,
	  RECV VARCHAR(50) NOT NULL,
	  MESSAGE TEXT NOT NULL);''')

cur.execute('''CREATE TABLE IF NOT EXISTS GRPMSSGS
      (GRPNAME VARCHAR(50) NOT NULL,
	  SENDER VARCHAR(50) NOT NULL,
	  MESSAGE TEXT NOT NULL);''')

dbconn.commit()


def clientthread(conn, addr):
    username = 0
    # sends a message to the client whose user object is conn
    success = False
    while not success:
        inp = conn.recv(512)
        inp = inp.decode('utf-8')
        if (inp == "quit"):
            remove(conn)
            return

        inp = inp.split(":")
        username = inp[1]
        to_check = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{inp[1]}' "
        cur.execute(to_check)
        selected_entry = cur.fetchone()

        if selected_entry == None:
            if (inp[0] == "1"):
                conn.send(bytes("n", 'utf-8'))
            else:
                postgres_insert_query = f'''INSERT INTO CREDENTIALS (USERNAME, PASSWORD) VALUES ('{inp[1]}', '{inp[2]}')'''
                cur.execute(postgres_insert_query)
                dbconn.commit()
                conn.send(bytes("y", 'utf-8'))
                success = True
                to_check = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{inp[1]}' "
                cur.execute(to_check)
        else:
            if (inp[0] == "2"):
                conn.send(bytes("n", 'utf-8'))
            else:
                if (inp[2] == selected_entry[0]):
                    conn.send(bytes("y", 'utf-8'))
                    success = True
                else:
                    conn.send(bytes("n", 'utf-8'))

    username_conn[username] = conn
    while True:
        try:
            message = conn.recv(1).decode('utf-8')
            print(message)
            if message == "d":
                to_usr = conn.recv(512).decode('utf-8')
                to_msg = conn.recv(512)
                print(to_usr)

                find_usr = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{to_usr}' "
                cur.execute(find_usr)
                entry = cur.fetchone()
                if entry == None:
                    # Send client that user does not exist
                    a = "user does not exist"
                    conn.sendall(a.encode('utf-8'))
                    pass
                else:
                    if to_usr in username_conn.keys():
                        # Recieving user is active
                        username_conn[to_usr].send(to_msg)
                    else:
                        postgres_insert_query = f'''INSERT INTO INDVMSSGS (SENDER, RECV, MESSAGE) VALUES ('{username}', '{to_usr}', '{to_msg.decode('utf-8')}')'''
                        cur.execute(postgres_insert_query)
                        dbconn.commit()
            elif message == "g":
                pass
            elif message == "b":
                pass
            elif message == "l":
                pass
            if message:

                """prints the message and address of the
                user who just sent the message on the server
                terminal"""
                print("<" + addr[0] + "> " + message.decode('utf-8'))

                # Calls broadcast function to send message to all
                message_to_send = "<" + addr[0] + \
                    "> " + message.decode('utf-8')
                broadcast(message_to_send, conn)

            else:
                """message may have no content if the connection
                is broken, in this case we remove the connection"""
                remove(conn)

        except:
            continue


"""Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """


def broadcast(message, connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.send(bytes(message, 'utf-8'))
            except:
                clients.close()

                # if the link is broken, we remove the client
                remove(clients)


"""The following function simply removes the object
from the list that was created at the beginning of
the program"""


def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)


while True:

    """Accepts a connection request and stores two parameters,
    conn which is a socket object for that user, and addr
    which contains the IP address of the client that just
    connected"""
    conn, addr = server.accept()

    """Maintains a list of clients for ease of broadcasting
	a message to all available people in the chatroom"""
    list_of_clients.append(conn)

    # prints the address of the user that just connected
    print(addr[0] + " connected")

    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread, (conn, addr))

dbconn.close()
conn.close()
server.close()