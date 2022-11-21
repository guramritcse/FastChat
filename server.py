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
	  MESSAGE TEXT NOT NULL,
      GRP VARCHAR(50),
      EXTENSION VARCHAR(20));''')

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
                conn.sendall(bytes("n", 'utf-8'))
            else:
                postgres_insert_query = f'''INSERT INTO CREDENTIALS (USERNAME, PASSWORD) VALUES ('{inp[1]}', '{inp[2]}')'''
                cur.execute(postgres_insert_query)
                dbconn.commit()
                conn.sendall(bytes("y", 'utf-8'))
                to_check = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{inp[1]}' "
                cur.execute(to_check)
        else:
            if (inp[0] == "2"):
                conn.sendall(bytes("n", 'utf-8'))
            else:
                if (inp[2] == selected_entry[1]):
                    conn.sendall(bytes("y", 'utf-8'))
                    success = True
                else:
                    conn.sendall(bytes("n", 'utf-8'))

    username_conn[username] = conn

    # Before going further we can arrange that all the previous messages are being sent to
    # the user.
    to_check = f"SELECT * FROM IND_MSG WHERE RECEIVER = '{username}' "
    cur.execute(to_check)
    selected_entry = cur.fetchall()
    conn.sendall(str(len(selected_entry)).zfill(2).encode('utf-8'))
    for e in selected_entry:
        if e[3] == None:
            if e[4] == None:
                conn.send("in".encode('utf-8'))
                msg = "<{}> {}".format(e[0], e[2])
                conn.sendall(str(len(msg)).zfill(3).encode('utf-8'))
                conn.sendall(msg.encode('utf-8'))
            else:
                conn.send("iy".encode('utf-8'))
                conn.send(str(len(e[0])).zfill(2).encode('utf-8'))
                conn.send(e[0].encode('utf-8'))
                conn.send(str(len(e[4])).zfill(1).encode('utf-8'))
                conn.send(e[4].encode('utf-8'))
                conn.send(str(len(str(len(e[2])))).zfill(2).encode('utf-8'))
                conn.send(str(len(e[2])).encode('utf-8'))
                conn.send(e[2].encode('utf-8'))
        else:
            if e[4]==None:
                conn.send("gn".encode('utf-8'))
                msg = "<Group:{}> <User:{}> {}".format(e[3], e[0], e[2])
                conn.sendall(str(len(msg)).zfill(3).encode('utf-8'))
                conn.sendall(msg.encode('utf-8'))
            else:
                conn.send("gy".encode('utf-8'))
                conn.send(str(len(e[0])).zfill(2).encode('utf-8'))
                conn.send(e[0].encode('utf-8'))
                conn.send(str(len(e[3])).zfill(2).encode('utf-8'))
                conn.send(e[3].encode('utf-8'))
                conn.send(str(len(e[4])).zfill(1).encode('utf-8'))
                conn.send(e[4].encode('utf-8'))
                conn.send(str(len(str(len(e[2])))).zfill(2).encode('utf-8'))
                conn.send(str(len(e[2])).encode('utf-8'))
                conn.send(e[2].encode('utf-8'))
    to_do = f"DELETE FROM IND_MSG WHERE RECEIVER = '{username}'"
    cur.execute(to_do)
    dbconn.commit()

    while True:
        try:
            message = conn.recv(512).decode('utf-8')
            # print(message)
            if (not message or message == "quit"):
                print("to")
                to_send = "q".encode('utf-8')
                conn.sendall(to_send)
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
                find_ind = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{ind_name}' "
                cur.execute(find_ind)
                entry = cur.fetchone()
                if entry == None:
                    out = "n".encode('utf-8')
                    conn.sendall(out)
                else:
                    out = "y".encode('utf-8')
                    conn.sendall(out)

            elif code == "ng":
                # new group
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
                # existing group
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
                find_ind = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{ind_name}' "
                cur.execute(find_ind)
                entry_ind = cur.fetchone()

                if entry_ind == None:
                    out = "n".encode('utf-8')  # non-exs.
                    conn.sendall(out)

                else:
                    if entry_grp[2] == 20:
                        out = "l".encode('utf-8')  # lim-exc.
                        conn.sendall(out)

                    elif ind_name in entry_grp[3:]:
                        out = "p".encode('utf-8')  # al-pre.
                        conn.sendall(out)

                    else:
                        num_present = entry_grp[2]
                        column = "member"+f"{num_present+1}"
                        update_query = f"UPDATE GROUPS SET {column} = '{ind_name}', number = number + 1  WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
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

                try:
                    index = entry_grp[4:].index(ind_name)
                    num_present = entry_grp[2]
                    column1 = "member"+f"{index+2}"
                    column2 = "member"+f"{num_present}"
                    update_query = f"UPDATE GROUPS SET {column1} = {column2}, NUMBER = {num_present-1} WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                    cur.execute(update_query)
                    dbconn.commit()
                    update_query = f"UPDATE GROUPS SET {column2} = NULL WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                    cur.execute(update_query)
                    dbconn.commit()
                    out = "y".encode('utf-8')  # pre.
                    conn.sendall(out)
                except:
                    out = "n".encode('utf-8')  # not-pre.
                    conn.sendall(out)

            elif code == "sa":
                grp_name = message[1]
                find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                cur.execute(find_grp)
                entry_grp = cur.fetchone()
                conn.sendall("s".encode('utf-8'))
                try:
                    members = ''
                    for m in entry_grp[3:3+entry_grp[2]]:
                        members = members + m + ':'
                    members = members[:-1]
                    conn.sendall(members.encode('utf-8'))
                except:
                    conn.sendall('n'.encode('utf-8'))

            elif code == "wg":
                to_grp = message[1]
                msg = conn.recv(512)
                try:
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{to_grp}'"
                    cur.execute(find_grp)
                    entry_grp = cur.fetchone()

                    for to_usr in entry_grp[3:3 + entry_grp[2]]:
                        if to_usr == username:
                            continue
                        elif to_usr in username_conn.keys():
                            # Recieving user is active
                            username_conn[to_usr].send('g'.encode('utf-8'))
                            username_conn[to_usr].send(str(len(username)).zfill(2).encode('utf-8'))
                            username_conn[to_usr].send(username.encode('utf-8'))
                            username_conn[to_usr].send(str(len(grp_name)).zfill(2).encode('utf-8'))
                            username_conn[to_usr].send(grp_name.encode('utf-8'))
                            username_conn[to_usr].send(msg)
                        else:
                            # check table
                            postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, MESSAGE, GRP) VALUES ('{username}', '{to_usr}', '{msg.decode('utf-8')}', '{grp_name}');'''
                            cur.execute(postgres_insert_query)
                            dbconn.commit()

                    conn.sendall("y".encode('utf-8'))
                except:
                    conn.sendall("n".encode('utf-8'))

            elif code=="ig":
                to_grp = message[1]
                ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                msg = conn.recv(size)
                try:
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{to_grp}'"
                    cur.execute(find_grp)
                    entry_grp = cur.fetchone()

                    for to_usr in entry_grp[3:3 + entry_grp[2]]:
                        if to_usr == username:
                            continue
                        elif to_usr in username_conn.keys():
                            # Recieving user is active
                            username_conn[to_usr].send('a'.encode('utf-8'))
                            username_conn[to_usr].send(str(len(username)).zfill(2).encode('utf-8'))
                            username_conn[to_usr].send(username.encode('utf-8'))
                            username_conn[to_usr].send(str(len(grp_name)).zfill(2).encode('utf-8'))
                            username_conn[to_usr].send(grp_name.encode('utf-8'))
                            username_conn[to_usr].send(str(len(ext)).zfill(1).encode('utf-8'))
                            username_conn[to_usr].send(ext.encode('utf-8'))
                            username_conn[to_usr].send(str(len(str(size))).zfill(2).encode('utf-8'))
                            username_conn[to_usr].send(str(size).encode('utf-8'))
                            username_conn[to_usr].send(msg)
                        else:
                            # check table
                            postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, MESSAGE, GRP, EXTENSION) VALUES ('{username}', '{to_usr}', '{msg.decode('utf-8')}', '{grp_name}', '{ext}');'''
                            cur.execute(postgres_insert_query)
                            dbconn.commit()

                    conn.sendall("y".encode('utf-8'))
                except:
                    conn.sendall("n".encode('utf-8'))


            elif code == "wi":
                to_usr = message[1]
                msg = conn.recv(512)
                try:
                    if to_usr in username_conn.keys():
                        # Recieving user is active
                        username_conn[to_usr].send('u'.encode('utf-8'))
                        username_conn[to_usr].send(str(len(username)).zfill(2).encode('utf-8'))
                        username_conn[to_usr].send(username.encode('utf-8'))
                        username_conn[to_usr].send(msg)
                    else:
                        # check table
                        postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, MESSAGE) VALUES ('{username}', '{to_usr}', '{msg.decode('utf-8')}');'''
                        cur.execute(postgres_insert_query)
                        dbconn.commit()

                    conn.sendall("y".encode('utf-8'))
                except:
                    conn.sendall("n".encode('utf-8'))
            
            elif code == "ii":
                to_usr = message[1]
                ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                msg = conn.recv(size)
                try:
                    if to_usr in username_conn.keys():
                        # Recieving user is active
                        username_conn[to_usr].send('b'.encode('utf-8'))
                        username_conn[to_usr].send(str(len(username)).zfill(2).encode('utf-8'))
                        username_conn[to_usr].send(username.encode('utf-8'))
                        username_conn[to_usr].send(str(len(ext)).zfill(1).encode('utf-8'))
                        username_conn[to_usr].send(ext.encode('utf-8'))
                        username_conn[to_usr].send(str(len(str(size))).zfill(2).encode('utf-8'))
                        username_conn[to_usr].send(str(size).encode('utf-8'))
                        username_conn[to_usr].send(msg)
                    else:
                        # check table
                        postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, MESSAGE, GRP, EXTENSION) VALUES ('{username}', '{to_usr}', '{msg.decode('utf-8')}', NULL, '{ext}');'''
                        cur.execute(postgres_insert_query)
                        dbconn.commit()

                    conn.sendall("y".encode('utf-8'))
                except:
                    conn.sendall("n".encode('utf-8'))
            


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