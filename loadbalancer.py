import socket
import sys
import select
import sys
import psycopg2
from passlib.hash import sha256_crypt
import rsa
import cryptocode
import random
import re
from itertools import cycle

from _thread import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()

file = open("logs.txt", "w")

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
listens for 150 active connections. This number can be
increased as per convenience.
"""
server.listen(150)

# List of servers I have
SERVER_POOL = [('127.0.0.1', 8000), ('127.0.0.1', 8001), ('127.0.0.1', 8002)]

dbconn = psycopg2.connect(database="fastchat", user="postgres",
                          password="", host="127.0.0.1", port="5432")
cur = dbconn.cursor()

#creating the databases

cur.execute('''CREATE TABLE IF NOT EXISTS CREDENTIALS
      (USERNAME VARCHAR(50) PRIMARY KEY NOT NULL,
	  PASSWORD VARCHAR(500) NOT NULL,
      PUB_KEY BYTEA NOT NULL,
      PVT_KEY BYTEA NOT NULL);''')

cur.execute('''CREATE TABLE IF NOT EXISTS GROUPS
      (NAME VARCHAR(50) PRIMARY KEY NOT NULL,
      ADMIN VARCHAR(50) NOT NULL,
      PUB_KEY BYTEA NOT NULL,
      PVT_KEY1 BYTEA NOT NULL,
      PVT_KEY2 BYTEA,
      PVT_KEY3 BYTEA,
      PVT_KEY4 BYTEA,
      PVT_KEY5 BYTEA,
      PVT_KEY6 BYTEA,
      PVT_KEY7 BYTEA,
      PVT_KEY8 BYTEA,
      PVT_KEY9 BYTEA,
      PVT_KEY10 BYTEA,
      PVT_KEY11 BYTEA,
      PVT_KEY12 BYTEA,
      PVT_KEY13 BYTEA,
      PVT_KEY14 BYTEA,
      PVT_KEY15 BYTEA,
      PVT_KEY16 BYTEA,
      PVT_KEY17 BYTEA,
      PVT_KEY18 BYTEA,
      PVT_KEY19 BYTEA,
      PVT_KEY20 BYTEA,
      NUMBER INT NOT NULL,
      MEMBER1 VARCHAR(50) NOT NULL,
      MEMBER2 VARCHAR(50),
      MEMBER3 VARCHAR(50),
      MEMBER4 VARCHAR(50),
      MEMBER5 VARCHAR(50),
      MEMBER6 VARCHAR(50),
      MEMBER7 VARCHAR(50),
      MEMBER8 VARCHAR(50),
      MEMBER9 VARCHAR(50),
      MEMBER10 VARCHAR(50),
      MEMBER11 VARCHAR(50),
      MEMBER12 VARCHAR(50),
      MEMBER13 VARCHAR(50),
      MEMBER14 VARCHAR(50),
      MEMBER15 VARCHAR(50),
      MEMBER16 VARCHAR(50),
      MEMBER17 VARCHAR(50),
      MEMBER18 VARCHAR(50),
      MEMBER19 VARCHAR(50),
      MEMBER20 VARCHAR(50));''')

cur.execute('''CREATE TABLE IF NOT EXISTS IND_MSG
      (SENDER VARCHAR(50) NOT NULL,
	  RECEIVER VARCHAR(50) NOT NULL,
      TIME TIMESTAMP NOT NULL,
	  MESSAGE BYTEA NOT NULL,
      GRP VARCHAR(50),
      EXTENSION VARCHAR(20),
      SIZE VARCHAR(100),
      PVT_KEY BYTEA);''')

dbconn.commit()

# Stores the socket object corresponding to the server address
server_con = {}

# stores which username is connected to which server address
user_con = {}

# Would store the tuple of private and public key respectively
user_keys = {}
cur.execute("SELECT * FROM CREDENTIALS")
all_entries = cur.fetchall()
for selected_entry in all_entries:
    user_keys[selected_entry[0]] = (selected_entry[3], selected_entry[2])

# Would store group's public key
grp_keys = {}
cur.execute("SELECT * FROM GROUPS")
all_entries = cur.fetchall()
for selected_entry in all_entries:
    grp_keys[selected_entry[0]] = (selected_entry[2])

# iterate on the server pool
ITER = cycle(SERVER_POOL)
num_conn = {}
for ser in SERVER_POOL:
    num_conn[ser]=0
    print(ser, num_conn, num_conn[ser])

#round robin to get the server to which the incoming client would get connected to
def round_robin(iter):
    global num_conn
    to_select = next(iter)
    num_conn[to_select] += 1
    print(to_select)
    return to_select

# getting the server with the least connections at the moment
def least_connection(server_list):
    global num_conn
    to_select = min(num_conn, key=num_conn.get)
    num_conn[to_select] += 1
    print(to_select)
    return to_select


#function deciding what algorithm to use for selecting server for next incoming client
def select_server(server_list, algorithm):
    global num_conn
    #selecting server at random
    if algorithm == 'random':
        to_select = random.choice(server_list)
        print(to_select)
        num_conn[to_select] += 1
        return to_select
    elif algorithm == 'round robin':
        return round_robin(ITER)
    elif algorithm == 'least connection':
        return least_connection(server_list)
    else:
        raise Exception('Unknown algorithm: %s' % algorithm)


def clientthread(conn, addr):
    global num_conn
    print(num_conn)
    c = conn.recv(1).decode('utf-8')
    if (c == 's'):
        # Adding into the dictionary
        server_con[conn] = addr
        while (True):
            code = conn.recv(2).decode('utf-8')
            print(code)
            # ci here is to see to which server is my receiver attached to
            # And it gives me the address of that server

            # It also at the same time gives me the public key of the receiver
            if code == 'ci':
                for_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                conn.sendall(
                    str(len(user_keys[for_user][1])).zfill(4).encode('utf-8'))
                conn.sendall(user_keys[for_user][1])
                print("sent public key")

            #sending the group keys
            elif code == 'cg':
                for_grp = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                conn.sendall(
                    str(len(grp_keys[for_grp])).zfill(4).encode('utf-8'))
                conn.sendall(grp_keys[for_grp])
                print("sent public key")

            # alloting a server to the client as par the algorithm
            elif code == 'cs':
                print("in cs")
                for_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                try:
                    serv = user_con[for_user]
                    print("------------------")
                    print(serv)
                    conn.sendall(str(len(serv)).zfill(3).encode('utf-8'))
                    conn.sendall(serv.encode('utf-8'))
                except:
                    conn.sendall(str(1).zfill(3).encode('utf-8'))
                    conn.sendall("n".encode('utf-8'))
            # user is offline now
            # removing its connections
            elif code == "cl":
                print("in cl")
                logout_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                try:
                    print(user_con[logout_user])
                    num_conn[eval(user_con[logout_user])] -= 1
                    print(num_conn)
                    del user_con[logout_user]
                except Exception as e:
                    # this point will never be reached
                    print(e)

            elif code == "ag":
                print("in ag")
                grp_name = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                pub_len = conn.recv(4)
                pub_key = conn.recv(
                    int(pub_len.decode('utf-8')))
                grp_keys[grp_name] = pub_key
                print(grp_name)

    # login of the user
    elif (c == 'c'):
        username = ""
        success = False
        while not success:
            inp = conn.recv(1024)
            inp = inp.decode('utf-8')
            if (inp == "quit"):
                # remove(conn)
                return
            inp = inp.split(":")
            username = inp[1]
            to_check = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{inp[1]}' "
            # check if the username already exists
            cur.execute(to_check)
            selected_entry = cur.fetchone()

            if selected_entry == None:
                if (inp[0] == "1"):
                    conn.sendall(bytes("n", 'utf-8'))
                else:
                    # getting the publlic key and private key of the user
                    conn.sendall(bytes("y", 'utf-8'))
                    pub_len = conn.recv(4)
                    pub_key = conn.recv(
                        int(pub_len.decode('utf-8')))
                    pvt_len = conn.recv(4)
                    pvt_key = conn.recv(
                        int(pvt_len.decode('utf-8')))

                    # insertion in dictionary
                    user_keys[username] = (pvt_key, pub_key)

                    # have to delete the entry into public_key
                    # postgres_insert_query = f'''INSERT INTO CREDENTIALS (USERNAME, PASSWORD, PUBLIC_KEY, PVT_KEY) VALUES ('{inp[1]}', '{inp[2]}','{public_key}', '{pvt_key}');'''
                    postgres_insert_query = f'''INSERT INTO CREDENTIALS (USERNAME, PASSWORD, PUB_KEY, PVT_KEY) VALUES ('{inp[1]}', '{inp[2]}', decode('{pub_key.hex()}', 'hex'), decode('{pvt_key.hex()}', 'hex'));'''
                    cur.execute(postgres_insert_query)
                    dbconn.commit()

            else:
                if inp[0] == "2":
                    conn.sendall(bytes("n", 'utf-8'))
                elif inp[1] in user_con.keys():
                    conn.sendall(bytes("a", 'utf-8'))
                else:
                    conn.sendall(bytes("y", 'utf-8'))
                    conn.sendall(
                        str(len(selected_entry[1])).zfill(4).encode('utf-8'))
                    conn.sendall((selected_entry[1]).encode('utf-8'))
                    verified = conn.recv(1).decode('utf-8')
                    if (verified == "y"):
                        # login is successful
                        # have to send user private key

                        conn.sendall(
                            str(len(user_keys[username][0])).zfill(4).encode('utf-8'))
                        conn.sendall(user_keys[username][0])

                        success = True

        # Need to assign the server to it here
        server_info = select_server(SERVER_POOL, 'least connection')

        # Maintaining the record of which user is connected to which server
        user_con[username] = str(server_info)

        conn.sendall(str(len(str(server_info))).zfill(3).encode('utf-8'))
        conn.sendall(str(server_info).encode('utf-8'))

        return

        # Assuming the client has now successfully connected to the server assigned
        # we will delete this thread


"""The following function simply removes the object
from the list that was created at the beginning of
the program"""


while True:

    # Accepts a connection request and stores two parameters,
    # conn which is a socket object for that user, and addr
    # which contains the IP address of the client that just
    # connected
    conn, addr = server.accept()

    # prints the address of the user that just connected
    print(addr[0] + " connected")

    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread, (conn, addr))

file.close()