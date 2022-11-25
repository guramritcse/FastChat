from pwn import process
import os
import datetime
import time

# For servers and loadbalancers
q = []
nq = 4

# For clients
p = []
np = 3

# First lets run the servers and the loadbalancers
q.append(process(['python3', 'loadbalancerL.py', '127.0.0.1', '7999']))
for i in range(nq - 1):
    q.append(process(['python3', 'serverL.py', '127.0.0.1', str(8000+i)]))


# First lets sign up all three
for i in range(np):
    p.append(process(['python3', 'clientL.py', '127.0.0.1', '7999']))
    print(p[i].recvuntil("t"))
    p[i].sendline(b'2')
    print(p[i].recvuntil(":"))
    p[i].sendline(f"i".encode('utf-8'))
    print(p[i].recvuntil(":"))
    p[i].sendline(f"i".encode('utf-8'))
    print(p[i].recvuntil("t"))


print("Loop Overs")
