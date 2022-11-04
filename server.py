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

cur.execute('''CREATE TABLE IF NOT EXISTS CREDENTIALS
      (USERNAME VARCHAR(50) PRIMARY KEY NOT NULL,
	  PASSWORD VARCHAR(50) NOT NULL);''')

cur.execute('''CREATE TABLE IF NOT EXISTS ONLINE
      (USERNAME VARCHAR(50) PRIMARY KEY NOT NULL,
	  PORT TEXT NOT NULL);''')

cur.execute('''CREATE TABLE IF NOT EXISTS GROUPS
      (NAME VARCHAR(50) NOT NULL,
      ADMIN VARCHAR(50) NOT NULL,
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
      MEMBER20 VARCHAR(50),
	  CONSTRAINT PK_GROUP PRIMARY KEY(NAME, ADMIN));''')


cur.execute('''CREATE TABLE IF NOT EXISTS IND_MSG
      (SENDER VARCHAR(50) NOT NULL,
	  RECEIVER VARCHAR(50) NOT NULL,
	  MESSAGE TEXT NOT NULL);''')

cur.execute('''CREATE TABLE IF NOT EXISTS GRP_MSG
      (GRPNAME VARCHAR(50) NOT NULL,
	  SENDER VARCHAR(50) NOT NULL,
	  MESSAGE TEXT NOT NULL);''')

dbconn.commit()


def clientthread(conn, addr):
    username = ""
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
                to_check = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{inp[1]}' "
                cur.execute(to_check)
        else:
            if (inp[0] == "2"):
                conn.send(bytes("n", 'utf-8'))
            else:
                if (inp[2] == selected_entry[1]):
                    conn.send(bytes("y", 'utf-8'))
                    success = True
                else:
                    conn.send(bytes("n", 'utf-8'))

    username_conn[username] = conn
    while True:
        try:
            message = conn.recv(512).decode('utf-8')
            print(message)
            if(not message or message == "quit"):
                print("to")
                to_send="q".encode('utf-8')
                conn.send(to_send)
                remove(conn, username)
                return
            message = message.split(":")
            code = message[0]
            if code == "cg":
                grp_name = message[1]
                find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' "
                cur.execute(find_grp)
                entry = cur.fetchone()
                if entry == None:
                    out = "n".encode('utf-8')
                    conn.sendall(out)
                else:
                    out = "y".encode('utf-8')
                    conn.sendall(out)
            elif code == "ci":
                ind_name = message[1]
                find_ind = f"SELECT * FROM CREDENTIALS WHERE NAME = '{ind_name}' "
                cur.execute(find_ind)
                entry = cur.fetchone()
                if entry == None:
                    out = "n".encode('utf-8')
                    conn.sendall(out)
                else:
                    out = "y".encode('utf-8')
                    conn.sendall(out)
            elif code == "ng":
                grp_name = message[1]
                find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                cur.execute(find_grp)
                entry = cur.fetchone()
                if entry == None:
                    postgres_insert_query = f"INSERT INTO GROUPS (NAME, ADMIN, NUMBER, MEMBER1) VALUES ('{grp_name}', '{username}', 1, '{username}')"
                    cur.execute(postgres_insert_query)
                    dbconn.commit()
                    out = "y".encode('utf-8')
                    conn.sendall(out)
                else:
                    out = "n".encode('utf-8')
                    conn.sendall(out)
            elif code == "eg":
                grp_name = message[1]
                find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                cur.execute(find_grp)
                entry = cur.fetchone()
                if entry == None:
                    out = "n".encode('utf-8')
                    conn.sendall(out)
                else:
                    out = "y".encode('utf-8')
                    conn.sendall(out)
            elif code == "fa":
                grp_name = message[1]
                find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' "
                cur.execute(find_grp)
                entry_grp = cur.fetchone()
            elif code == "ai":
                grp_name = message[1]
                find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                cur.execute(find_grp)
                entry_grp = cur.fetchone()
                ind_name = message[2]
                find_ind = f"SELECT * FROM CREDENTIALS WHERE NAME = '{ind_name}' "
                cur.execute(find_ind)
                entry_ind = cur.fetchone()
                if entry_ind == None:
                    out = "n".encode('utf-8')   #non-exs.
                    conn.sendall(out)
                else:
                    if entry_grp[2] == 20:
                        out = "l".encode('utf-8')   #lim-exc.
                        conn.sendall(out)
                    elif ind_name in entry_grp[3:]:
                        out = "p".encode('utf-8')   #al-pre.
                        conn.sendall(out)
                    else:
                        num_present=entry_grp[2]
                        column="member"+f"{num_present+1}"
                        update_query=f"UPDATE GROUPS SET {column} = '{ind_name}' WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                        cur.execute(update_query)
                        dbconn.commit()
                        out = "y".encode('utf-8')   # added
                        conn.sendall(out)
            elif code == "ri":
                grp_name = message[1]
                find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                cur.execute(find_grp)
                entry_grp = cur.fetchone()
                ind_name = message[2]
                try :
                    index=entry_grp[4:].index(ind_name)
                    num_present=entry_grp[2]
                    column1="member"+f"{index+2}"
                    column2="member"+f"{num_present}"
                    update_query=f"UPDATE GROUPS SET {column1} = {column2}, {column2} = NULL, NUMBER = {num_present-1} WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                    cur.execute(update_query)
                    dbconn.commit()
                    out = "y".encode('utf-8')   #pre.
                    conn.sendall(out)
                except:
                    out = "n".encode('utf-8')   #not-pre.
                    conn.sendall(out)    
            elif code == "wg":
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

            elif code == "wi":
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

                        
        except:
            continue


"""The following function simply removes the object
from the list that was created at the beginning of
the program"""


def remove(connection, usr):
    del username_conn[usr]
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