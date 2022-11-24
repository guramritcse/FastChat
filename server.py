# Python program to implement server side of chat room.
import socket
import select
import sys
import psycopg2
from passlib.hash import sha256_crypt
import rsa
import cryptocode
import datetime

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

username_conn = {}

dbconn = psycopg2.connect(database="fastchat", user="postgres",
                          password="", host="127.0.0.1", port="5432")
cur = dbconn.cursor()

SERVER_POOL = [('127.0.0.1', 8000), ('127.0.0.1', 8001), ('127.0.0.1', 8002)]
fellow_servers = {}


# The following socket would help in contact between load balancer and the server itself
lb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# This number can be anything we just assumed it to be this as address of the load balancer
lb.connect(('127.0.0.1', 7999))

# Need to make sure load balancer is free to answer queries or not
# We would need boolean value telling us it is free or not
lb_free = True

# Sending the signal to the load balancer that we are source
lb.sendall("s".encode('utf-8'))

def letsconnect(ip, port):
    global SERVER_POOL, fellow_servers
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((ip, port))
    conn.sendall("s".encode('utf-8'))
    my_address = f"('{IP_address}', {Port})"
    their_address = f"('{ip}', {port})"
    fellow_servers[their_address] = conn
    # Sending my address
    conn.sendall(str(len(my_address)).zfill(3).encode('utf-8'))
    conn.sendall(my_address.encode('utf-8'))

    # Make infinte while recieve loop
    while (True):
        code = conn.recv(2).decode('utf-8')
        if code == "wi":
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            from_user = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(conn.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size%86 == 0:
                msg.append(conn.recv(128))

            # Lets send the message to the user
            uss_conn = username_conn[to_usr]
            uss_conn.sendall("u".encode('utf-8'))

            uss_conn.sendall(str(len(from_user)).zfill(3).encode('utf-8'))
            uss_conn.sendall(from_user.encode('utf-8'))

            username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)


        elif code == "ii":
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            from_user = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size%86 == 0:
                msg.append(conn.recv(128))

            username_conn[to_usr].sendall('b'.encode('utf-8'))
            username_conn[to_usr].sendall(str(len(from_user)).zfill(3).encode('utf-8'))
            username_conn[to_usr].sendall(from_user.encode('utf-8'))
            username_conn[to_usr].sendall(str(len(ext)).zfill(1).encode('utf-8'))
            username_conn[to_usr].sendall(ext.encode('utf-8'))
            username_conn[to_usr].sendall(str(len(str(size))).zfill(2).encode('utf-8'))
            username_conn[to_usr].sendall(str(size).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)

        elif code == "wg":
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            from_user = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            to_grp = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(conn.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size%86 == 0:
                msg.append(conn.recv(128))

            # Lets send the message to the user
            uss_conn = username_conn[to_usr]
            uss_conn.sendall("g".encode('utf-8'))

            uss_conn.sendall(str(len(from_user)).zfill(3).encode('utf-8'))
            uss_conn.sendall(from_user.encode('utf-8'))

            uss_conn.sendall(str(len(to_grp)).zfill(3).encode('utf-8'))
            uss_conn.sendall(to_grp.encode('utf-8'))

            username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)

        elif code == "ig":
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            from_user = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            to_grp = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size%86 == 0:
                msg.append(conn.recv(128))

            username_conn[to_usr].sendall('a'.encode('utf-8'))
            username_conn[to_usr].sendall(str(len(from_user)).zfill(3).encode('utf-8'))
            username_conn[to_usr].sendall(from_user.encode('utf-8'))
            username_conn[to_usr].sendall(str(len(to_grp)).zfill(3).encode('utf-8'))
            username_conn[to_usr].sendall(to_grp.encode('utf-8'))
            username_conn[to_usr].sendall(str(len(ext)).zfill(1).encode('utf-8'))
            username_conn[to_usr].sendall(ext.encode('utf-8'))
            username_conn[to_usr].sendall(str(len(str(size))).zfill(2).encode('utf-8'))
            username_conn[to_usr].sendall(str(size).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)

        elif code == "gk":
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            for_grp = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(conn.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size%86 == 0:
                msg.append(conn.recv(128))

            # Lets send the message to the user
            uss_conn = username_conn[to_usr]
            uss_conn.sendall("k".encode('utf-8'))
            username_conn[to_usr].sendall(str(len(for_grp)).zfill(3).encode('utf-8'))
            username_conn[to_usr].sendall(for_grp.encode('utf-8'))
            username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)
            
            grp_pvt_len = conn.recv(4)
            grp_pvt_key = conn.recv(
                int(grp_pvt_len.decode('utf-8')))
            print(grp_pvt_len, grp_pvt_key)
            conn.sendall(grp_pvt_len)
            conn.sendall(grp_pvt_key)
            print("sent")
       
for i in SERVER_POOL:
    if i[1] < Port:
        start_new_thread(letsconnect, (i[0], i[1]))
    else:
        break

def clientthread(conn, addr):
    global lb, fellow_servers, username_conn
    serv_connected = ''
    if (conn.recv(1).decode('utf-8') == "c"):
        to_remove= "DELETE FROM IND_MSG WHERE TIME < NOW() - INTERVAL '2 HOURS' "
        cur.execute(to_remove)
        dbconn.commit()

        username = conn.recv(int(conn.recv(3).decode('utf-8'))).decode('utf-8')
        username_conn[username] = conn

       
        # Before going further we can arrange that all the previous messages are being sent to
        # the user.
        to_check = f"SELECT * FROM IND_MSG WHERE RECEIVER = '{username}' "
        cur.execute(to_check)
        selected_entry = cur.fetchall()
        conn.sendall(str(len(selected_entry)).zfill(4).encode('utf-8'))
        for e in selected_entry:
            if e[4] == None:
                if e[5] == None:
                    conn.sendall("in".encode('utf-8'))
                    conn.sendall(str(len(e[0])).zfill(3).encode('utf-8'))
                    conn.sendall(e[0].encode('utf-8'))
                    conn.sendall(str(e[6]).zfill(4).encode('utf-8'))
                    size = int(e[6])
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size%86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)

                else:
                    conn.sendall("iy".encode('utf-8'))
                    conn.sendall(str(len(e[0])).zfill(3).encode('utf-8'))
                    conn.sendall(e[0].encode('utf-8'))
                    conn.sendall(str(len(e[5])).zfill(1).encode('utf-8'))
                    conn.sendall(e[5].encode('utf-8'))
                    conn.sendall(str(len(e[6])).zfill(2).encode('utf-8'))
                    conn.sendall(e[6].encode('utf-8'))
                    size = int(e[6])
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size%86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)
            else:
                if e[5]==None:
                    conn.sendall("gn".encode('utf-8'))
                    conn.sendall(str(len(e[0])).zfill(3).encode('utf-8'))
                    conn.sendall(e[0].encode('utf-8'))
                    conn.sendall(str(len(e[4])).zfill(3).encode('utf-8'))
                    conn.sendall(e[4].encode('utf-8'))
                    conn.sendall(str(e[6]).zfill(4).encode('utf-8'))
                    size = int(e[6])
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size%86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)
                else:
                    conn.sendall("gy".encode('utf-8'))
                    conn.sendall(str(len(e[0])).zfill(3).encode('utf-8'))
                    conn.sendall(e[0].encode('utf-8'))
                    conn.sendall(str(len(e[4])).zfill(3).encode('utf-8'))
                    conn.sendall(e[4].encode('utf-8'))
                    conn.sendall(str(len(e[5])).zfill(1).encode('utf-8'))
                    conn.sendall(e[5].encode('utf-8'))
                    conn.sendall(str(len(e[6])).zfill(2).encode('utf-8'))
                    conn.sendall(e[6].encode('utf-8'))
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size%86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)

        to_do = f"DELETE FROM IND_MSG WHERE RECEIVER = '{username}'"
        cur.execute(to_do)
        dbconn.commit()

        while True:
            try:
                message = conn.recv(512).decode('utf-8')
                if (not message or message == "quit"):
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
                    conn.sendall("e".encode('utf-8'))
                    if entry == None:
                        out = "n".encode('utf-8')
                        conn.sendall(out)
                    else:
                        out = "y".encode('utf-8')
                        conn.sendall(out)

                        # Need to get the public key of the fellow
                        lb.sendall("cg".encode('utf-8'))

                        lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                        lb.sendall(grp_name.encode('utf-8'))

                        len_key = int(lb.recv(4).decode('utf-8'))
                        keyofrecv = lb.recv(len_key)
                        print("received key")

                        conn.sendall(
                            str(len(keyofrecv)).zfill(4).encode('utf-8'))
                        conn.sendall(keyofrecv)
                        print("sent public key to grp")

                elif code == "ci":
                    ind_name = message[1]
                    find_ind = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{ind_name}' "
                    cur.execute(find_ind)
                    entry = cur.fetchone()
                    conn.sendall("e".encode('utf-8'))
                    if entry == None:
                        out = "n".encode('utf-8')
                        conn.sendall(out)
                    else:
                        out = "y".encode('utf-8')
                        conn.sendall(out)

                        # Need to get the public key of the fellow
                        lb.sendall("ci".encode('utf-8'))

                        lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                        lb.sendall(ind_name.encode('utf-8'))

                        len_key = int(lb.recv(4).decode('utf-8'))
                        keyofrecv = lb.recv(len_key)
                        print("received key")

                        conn.sendall(
                            str(len(keyofrecv)).zfill(4).encode('utf-8'))
                        conn.sendall(keyofrecv)
                        print("sent public key to user")

                elif code == "ng":
                    # new group
                    grp_name = message[1]
                    pub_len = conn.recv(4)
                    pub_key = conn.recv(
                        int(pub_len.decode('utf-8')))
                    pvt_len = conn.recv(4)
                    pvt_key = conn.recv(
                        int(pvt_len.decode('utf-8')))
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' "
                    cur.execute(find_grp)
                    entry = cur.fetchone()
                    if entry == None:
                        postgres_insert_query = f"INSERT INTO GROUPS (NAME, ADMIN, PUB_KEY, PVT_KEY1, NUMBER, MEMBER1) VALUES ('{grp_name}', '{username}', decode('{pub_key.hex()}', 'hex'), decode('{pvt_key.hex()}', 'hex'), 1, '{username}')"
                        cur.execute(postgres_insert_query)
                        dbconn.commit()
                        lb.sendall("ag".encode('utf-8'))
                        lb.sendall(str(len(grp_name)).zfill(3).encode('utf-8'))
                        lb.sendall(grp_name.encode('utf-8'))
                        lb.sendall(str(int(pub_len.decode('utf-8'))).zfill(4).encode('utf-8'))
                        lb.sendall(pub_key)
                        out = "y".encode('utf-8')
                        conn.sendall(out)
                    else:
                        out = "n".encode('utf-8')
                        conn.sendall(out)

                elif code == "eg":
                    # existing group with admin priveleges
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
                            out = "t".encode('utf-8')  # al-pre.
                            conn.sendall(out)

                        else:
                            num_present = entry_grp[23]
                            try:
                                lb.sendall("ci".encode('utf-8'))

                                lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                                lb.sendall(ind_name.encode('utf-8'))

                                len_key = int(lb.recv(4).decode('utf-8'))
                                keyofrecv = lb.recv(len_key)
                                print("received key")
                                conn.sendall('e'.encode('utf-8'))
                                conn.sendall('y'.encode('utf-8'))
                                conn.sendall(
                                    str(len(keyofrecv)).zfill(4).encode('utf-8'))
                                conn.sendall(keyofrecv)

                                conn.sendall('p'.encode('utf-8'))
                                conn.sendall(str(len(bytes(entry_grp[3]))).zfill(4).encode('utf-8'))
                                conn.sendall(bytes(entry_grp[3]))
                                print("sent ad key")
                                size = int(conn.recv(4).decode('utf-8'))
                                iter = size//86
                                msg = []
                                for i in range(iter):
                                    msg.append(conn.recv(128))
                                if not size%86 == 0:
                                    msg.append(conn.recv(128))

                                print("sent public key to user")
                                # Need to get the public key of the fellow
                                lb.sendall("cs".encode('utf-8'))
                                lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                                lb.sendall(ind_name.encode('utf-8'))
                                ip_len = int(lb.recv(3).decode('utf-8'))
                                serv_connected = lb.recv(ip_len).decode('utf-8')
                                print(serv_connected)



                                if (serv_connected == f"('{IP_address}', {Port})"):
                                    # Recieving user is active
                                    username_conn[ind_name].sendall('k'.encode('utf-8'))

                                    username_conn[ind_name].sendall(
                                        str(len(grp_name)).zfill(3).encode('utf-8'))
                                    username_conn[ind_name].sendall(grp_name.encode('utf-8'))

                                    username_conn[ind_name].sendall(str(size).zfill(4).encode('utf-8'))
                                    for elem in msg:
                                        username_conn[ind_name].sendall(elem)

                                    grp_pvt_len = username_conn[ind_name].recv(4)
                                    print("hello")
                                    print(grp_pvt_len)
                                    print(grp_pvt_len.decode('utf-8'))
                                    grp_pvt_key = username_conn[ind_name].recv(int(grp_pvt_len.decode('utf-8')))
                                    print("rcvd")

                                    column1 = "member"+f"{num_present+1}"
                                    column2 = "pvt_key"+f"{num_present+1}"
                                    update_query = f"UPDATE GROUPS SET {column1} = '{ind_name}', number = number + 1, {column2} = decode('{grp_pvt_key.hex()}', 'hex') WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                                    cur.execute(update_query)
                                    dbconn.commit()

                                    print("done")

                                elif (serv_connected == "n"):
                                    # check table
                                    column = "member"+f"{num_present+1}"
                                    update_query = f"UPDATE GROUPS SET {column} = '{ind_name}', number = number + 1  WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                                    cur.execute(update_query)
                                    dbconn.commit()
                                    dt= datetime.datetime.now()
                                    to_store = b''.join(msg)
                                    postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, GROUP, EXT, SIZE) VALUES ('{username}', '{ind_name}', '{dt}', decode('{to_store.hex()}', 'hex'), '{grp_name}' ,'GROUP KEY' ,{str(size)});'''
                                    cur.execute(postgres_insert_query)
                                    dbconn.commit()

                                else:
                                    serv_conn = fellow_servers[serv_connected]
                                    serv_conn.sendall("gk".encode('utf-8'))
                                    serv_conn.sendall(
                                        str(len(ind_name)).zfill(3).encode('utf-8')
                                    )
                                    serv_conn.sendall(ind_name.encode('utf-8'))

                                    serv_conn.sendall(
                                        str(len(grp_name)).zfill(3).encode('utf-8'))
                                    serv_conn.sendall(grp_name.encode('utf-8'))

                                    serv_conn.sendall(str(size).zfill(4).encode('utf-8'))
                                    for elem in msg:
                                        serv_conn.sendall(elem)

                                    grp_pvt_len = serv_conn.recv(4)
                                    grp_pvt_key = serv_conn.recv(int(grp_pvt_len.decode('utf-8')))

                                    column1 = "member"+f"{num_present+1}"
                                    column2 = "pvt_key"+f"{num_present+1}"
                                    update_query = f"UPDATE GROUPS SET {column1} = '{ind_name}', number = number + 1, {column2} = decode('{grp_pvt_key.hex()}', 'hex') WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                                    cur.execute(update_query)
                                    dbconn.commit()

                                conn.sendall("y".encode('utf-8'))

                            except:
                                conn.sendall("n".encode('utf-8'))


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
                        for m in entry_grp[24:24+entry_grp[23]]:
                            members = members + m + ':'
                        members = members[:-1]
                        conn.sendall(members.encode('utf-8'))
                    except:
                        conn.sendall('n'.encode('utf-8'))

                elif code == "wg":
                    to_grp = message[1]
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    size = int(conn.recv(4).decode('utf-8'))
                    iter = size//86
                    msg = []
                    for i in range(iter):
                        msg.append(conn.recv(128))
                    if not size%86 == 0:
                        msg.append(conn.recv(128))

                    try:
                        find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{to_grp}'"
                        cur.execute(find_grp)
                        entry_grp = cur.fetchone()


                        for to_usr in entry_grp[3:3 + entry_grp[2]]:
                            if to_usr == username:
                                continue

                            lb.sendall("cs".encode('utf-8'))
                            lb.sendall(str(len(to_usr)).zfill(3).encode('utf-8'))
                            lb.sendall(to_usr.encode('utf-8'))
                            ip_len = int(lb.recv(3).decode('utf-8'))
                            serv_connected = lb.recv(ip_len).decode('utf-8')
                            print(serv_connected)
                            
                            
                            if (serv_connected == f"('{IP_address}', {Port})"):
                                # Recieving user is active
                                username_conn[to_usr].sendall('g'.encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    str(len(username)).zfill(3).encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    username.encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    str(len(grp_name)).zfill(3).encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    grp_name.encode('utf-8'))

                                username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
                                
                                for elem in msg:
                                    username_conn[to_usr].sendall(elem)

                            elif serv_connected == "n" :
                                # check table
                                # postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, MESSAGE, GRP) VALUES ('{username}', '{to_usr}', '{msg.decode('utf-8')}', '{grp_name}');'''
                                dt= datetime.datetime.now()
                                postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, GRP, SIZE) VALUES ('{username}', '{to_usr}', '{dt}', decode('{bytes(msg).hex()}', 'hex'), '{grp_name}', {str(size)});'''
                                cur.execute(postgres_insert_query)
                                dbconn.commit()

                            else:
                                serv_conn = fellow_servers[serv_connected]
                                serv_conn.sendall("wg".encode('utf-8'))
                                serv_conn.sendall(
                                    str(len(to_usr)).zfill(3).encode('utf-8')
                                )
                                serv_conn.sendall(to_usr.encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(username)).zfill(3).encode('utf-8'))
                                serv_conn.sendall(username.encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(to_grp)).zfill(3).encode('utf-8'))

                                serv_conn.sendall(to_grp.encode('utf-8'))                               

                                serv_conn.sendall(str(size).zfill(4).encode('utf-8'))
                                for elem in msg:
                                    serv_conn.sendall(elem)

                        conn.sendall("y".encode('utf-8'))
                    except:
                        conn.sendall("n".encode('utf-8'))

                elif code=="ig":
                    to_grp = message[1]
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                    size = int(conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                    iter = size//86
                    msg = []
                    for i in range(iter):
                        msg.append(conn.recv(128))
                    if not size%86 == 0:
                        msg.append(conn.recv(128))
                    try:
                        find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{to_grp}'"
                        cur.execute(find_grp)
                        entry_grp = cur.fetchone()

                        for to_usr in entry_grp[3:3 + entry_grp[2]]:
                            if to_usr == username:
                                continue

                            lb.sendall("cs".encode('utf-8'))
                            lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                            lb.sendall(ind_name.encode('utf-8'))
                            ip_len = int(lb.recv(3).decode('utf-8'))
                            serv_connected = lb.recv(ip_len).decode('utf-8')
                            print(serv_connected)

                            if (serv_connected == f"('{IP_address}', {Port})"):
                                # Recieving user is active
                                username_conn[to_usr].sendall('a'.encode('utf-8'))
                                username_conn[to_usr].sendall(str(len(to_usr)).zfill(2).encode('utf-8'))
                                username_conn[to_usr].sendall(to_usr.encode('utf-8'))
                                username_conn[to_usr].sendall(str(len(grp_name)).zfill(2).encode('utf-8'))
                                username_conn[to_usr].sendall(grp_name.encode('utf-8'))
                                username_conn[to_usr].sendall(str(len(ext)).zfill(1).encode('utf-8'))
                                username_conn[to_usr].sendall(ext.encode('utf-8'))
                                username_conn[to_usr].sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                                username_conn[to_usr].sendall(str(size).encode('utf-8'))
                                for elem in msg:
                                    username_conn[to_usr].sendall(elem)

                            elif (serv_connected == "n"):
                                # check table
                                dt= datetime.datetime.now()
                                postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, GRP, EXTENSION, SIZE) VALUES ('{to_usr}', '{to_usr}', '{dt}', decode('{bytes(msg).hex()}', 'hex'), '{grp_name}', '{ext}', {str(size)});'''
                                cur.execute(postgres_insert_query)
                                dbconn.commit()

                            else:
                                serv_conn = fellow_servers[serv_connected]
                                serv_conn.sendall("ig".encode('utf-8'))

                                serv_conn.sendall(str(len(to_usr)).zfill(3).encode('utf-8'))
                                serv_conn.sendall(to_usr.encode('utf-8'))

                                serv_conn.sendall(str(len(username)).zfill(3).encode('utf-8'))
                                serv_conn.sendall(username.encode('utf-8'))

                                serv_conn.sendall(str(len(grp_name)).zfill(3).encode('utf-8'))
                                serv_conn.sendall(grp_name.encode('utf-8'))

                                serv_conn.sendall(str(len(ext)).zfill(1).encode('utf-8'))
                                serv_conn.sendall(ext.encode('utf-8'))

                                serv_conn.sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                                serv_conn.sendall(str(size).encode('utf-8'))
                                for elem in msg:
                                    serv_conn.sendall(elem)

                        conn.sendall("y".encode('utf-8'))
                    except:
                        conn.sendall("n".encode('utf-8'))

                elif code == "wi":
                    to_usr = message[1]
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    # Updated the max limit of message
                    size = int(conn.recv(4).decode('utf-8'))
                    iter = size//86
                    msg = []
                    for i in range(iter):
                        msg.append(conn.recv(128))
                    if not size%86 == 0:
                        msg.append(conn.recv(128))
                    try:
                        # Need to get the public key of the fellow
                        lb.sendall("cs".encode('utf-8'))
                        lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                        lb.sendall(ind_name.encode('utf-8'))
                        ip_len = int(lb.recv(3).decode('utf-8'))
                        serv_connected = lb.recv(ip_len).decode('utf-8')
                        print(serv_connected)

                        if (serv_connected == f"('{IP_address}', {Port})"):
                            # Recieving user is active
                            username_conn[to_usr].sendall('u'.encode('utf-8'))

                            username_conn[to_usr].sendall(
                                str(len(username)).zfill(3).encode('utf-8'))

                            username_conn[to_usr].sendall(
                                username.encode('utf-8'))

                            username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
                            for elem in msg:
                                username_conn[to_usr].sendall(elem)

                            # username_conn[to_usr].sendall(
                            #     str(len(msg)).zfill(4).encode('utf-8'))

                            # username_conn[to_usr].sendall(msg)

                        elif (serv_connected == "n"):
                            # check table
                            # postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, MESSAGE) VALUES ('{username}', '{to_usr}', decode('{msg.hex()}', 'hex'));'''
                            dt= datetime.datetime.now()
                            to_store = b''.join(msg)
                            postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, SIZE) VALUES ('{username}', '{to_usr}', '{dt}', decode('{to_store.hex()}', 'hex'), {str(size)});'''

                            cur.execute(postgres_insert_query)
                            dbconn.commit()

                        else:
                            serv_conn = fellow_servers[serv_connected]
                            serv_conn.sendall("wi".encode('utf-8'))
                            serv_conn.sendall(
                                str(len(to_usr)).zfill(3).encode('utf-8')
                            )
                            serv_conn.sendall(to_usr.encode('utf-8'))

                            serv_conn.sendall(
                                str(len(username)).zfill(3).encode('utf-8'))
                            serv_conn.sendall(username.encode('utf-8'))

                            serv_conn.sendall(str(size).zfill(4).encode('utf-8'))
                            for elem in msg:
                                serv_conn.sendall(elem)

                        conn.sendall("y".encode('utf-8'))

                    except:
                        conn.sendall("n".encode('utf-8'))

                elif code == "ii":
                    to_usr = message[1]
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                    size = int(conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                    iter = size//86
                    msg = []
                    for i in range(iter):
                        msg.append(conn.recv(128))
                    if not size%86 == 0:
                        msg.append(conn.recv(128))

                    try: 
                        # Need to get the public key of the fellow
                        lb.sendall("cs".encode('utf-8'))
                        lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                        lb.sendall(ind_name.encode('utf-8'))
                        ip_len = int(lb.recv(3).decode('utf-8'))
                        serv_connected = lb.recv(ip_len).decode('utf-8')
                        print(serv_connected)

                        if (serv_connected == f"('{IP_address}', {Port})"):
                            # Recieving user is active
                            username_conn[to_usr].sendall('b'.encode('utf-8'))
                            username_conn[to_usr].sendall(str(len(username)).zfill(3).encode('utf-8'))
                            username_conn[to_usr].sendall(username.encode('utf-8'))
                            username_conn[to_usr].sendall(str(len(ext)).zfill(1).encode('utf-8'))
                            username_conn[to_usr].sendall(ext.encode('utf-8'))
                            username_conn[to_usr].sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                            username_conn[to_usr].sendall(str(size).encode('utf-8'))
                            for elem in msg:
                                username_conn[to_usr].sendall(elem)
                        
                        elif (serv_connected == "n"):
                            # check table
                            dt= datetime.datetime.now()
                            to_store = b''.join(msg)
                            postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, GRP, EXTENSION, SIZE) VALUES ('{username}', '{to_usr}', '{dt}', decode('{bytes(to_store).hex()}', 'hex'), NULL, '{ext}', {str(size)});'''
                            cur.execute(postgres_insert_query)
                            dbconn.commit()

                        else:
                            serv_conn = fellow_servers[serv_connected]
                            serv_conn.sendall("ii".encode('utf-8'))

                            serv_conn.sendall(str(len(to_usr)).zfill(3).encode('utf-8'))
                            serv_conn.sendall(to_usr.encode('utf-8'))

                            serv_conn.sendall(str(len(username)).zfill(3).encode('utf-8'))
                            serv_conn.sendall(username.encode('utf-8'))

                            serv_conn.sendall(str(len(ext)).zfill(1).encode('utf-8'))
                            serv_conn.sendall(ext.encode('utf-8'))

                            serv_conn.sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                            serv_conn.sendall(str(size).encode('utf-8'))
                            for elem in msg:
                                serv_conn.sendall(elem)

                        conn.sendall("y".encode('utf-8'))
                    except:
                        conn.sendall("n".encode('utf-8'))
            except:
                continue

    else:
        # Handle fellow server's requests

        # Lets store for whom this server is made for as tuple
        address = conn.recv(int(conn.recv(3).decode('utf-8'))).decode('utf-8')
        # Update your dictionary
        fellow_servers[address] = conn

        # Start the read of infinte while loop here
        # Make infinte while recieve loop
        while True:
            code = conn.recv(2).decode('utf-8')
            if code == "wi":
                to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                from_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(4).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size%86 == 0:
                    msg.append(conn.recv(128))

                # Lets send the message to the user
                uss_conn = username_conn[to_usr]
                uss_conn.sendall("u".encode('utf-8'))

                uss_conn.sendall(str(len(from_user)).zfill(3).encode('utf-8'))
                uss_conn.sendall(from_user.encode('utf-8'))

                username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)

            elif code == "ii":
                to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                from_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size%86 == 0:
                    msg.append(conn.recv(128))

                username_conn[to_usr].sendall('b'.encode('utf-8'))
                username_conn[to_usr].sendall(str(len(from_user)).zfill(3).encode('utf-8'))
                username_conn[to_usr].sendall(from_user.encode('utf-8'))
                username_conn[to_usr].sendall(str(len(ext)).zfill(1).encode('utf-8'))
                username_conn[to_usr].sendall(ext.encode('utf-8'))
                username_conn[to_usr].sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                username_conn[to_usr].sendall(str(size).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)

            elif code == "wg":
                to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                from_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                to_grp = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(4).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size%86 == 0:
                    msg.append(conn.recv(128))

                # Lets send the message to the user
                uss_conn = username_conn[to_usr]
                uss_conn.sendall("g".encode('utf-8'))

                uss_conn.sendall(str(len(from_user)).zfill(3).encode('utf-8'))
                uss_conn.sendall(from_user.encode('utf-8'))

                uss_conn.sendall(str(len(to_grp)).zfill(3).encode('utf-8'))
                uss_conn.sendall(to_grp.encode('utf-8'))

                username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)

            elif code == "ig":
                to_usr = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                from_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                to_grp = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size%86 == 0:
                    msg.append(conn.recv(128))

                username_conn[to_usr].sendall('a'.encode('utf-8'))
                username_conn[to_usr].sendall(str(len(from_user)).zfill(3).encode('utf-8'))
                username_conn[to_usr].sendall(from_user.encode('utf-8'))
                username_conn[to_usr].sendall(str(len(to_grp)).zfill(3).encode('utf-8'))
                username_conn[to_usr].sendall(to_grp.encode('utf-8'))
                username_conn[to_usr].sendall(str(len(ext)).zfill(1).encode('utf-8'))
                username_conn[to_usr].sendall(ext.encode('utf-8'))
                username_conn[to_usr].sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                username_conn[to_usr].sendall(str(size).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)

            elif code == "gk":
                to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                for_grp = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(4).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size%86 == 0:
                    msg.append(conn.recv(128))

                # Lets send the message to the user
                uss_conn = username_conn[to_usr]
                uss_conn.sendall("k".encode('utf-8'))
                username_conn[to_usr].sendall(str(len(for_grp)).zfill(3).encode('utf-8'))
                username_conn[to_usr].sendall(for_grp.encode('utf-8'))
                username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)
                
                grp_pvt_len = conn.recv(4)
                grp_pvt_key = conn.recv(
                    int(grp_pvt_len.decode('utf-8')))
                print(grp_pvt_len, grp_pvt_key)
                conn.sendall(grp_pvt_len)
                conn.sendall(grp_pvt_key)
                print("sent")


"""The following function simply removes the object
from the list that was created at the beginning of
the program"""


def remove(connection, usr):
    # client logs out
    del username_conn[usr]
    lb.sendall("cl".encode('utf-8'))
    lb.sendall(str(len(usr)).zfill(3).encode('utf-8'))
    lb.sendall(usr.encode('utf-8'))


while True:

    """Accepts a connection request and stores two parameters,
    conn which is a socket object for that user, and addr
    which contains the IP address of the client that just
    connected"""
    conn, addr = server.accept()

    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread, (conn, addr))

dbconn.close()
conn.close()
server.close()