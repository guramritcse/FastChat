# FastChat by Thrice as Nice

# Members
| Name | Roll number |
| ----------- | ----------- |
| Guramrit Singh | 210050061 |
| Isha Arora | 210050070 |
| Karan Godara | 210050082 |

# Description about repository
- This repository contains the course project of CS 251 : Software Systems Lab 
- Code files and report are contained within the repository

## Implementation so far

### Postgresql
Database Fastchat is created which contains these tables: 
- credentials : User name, password
- groups : Group name, admin, member count and usernames in group
- msg : Stored messages for offline users

## Signup and login
  A client firstly connects to load balancer where a user gets a chance to either signup or login. When signing up, loadbalancer firstly check if a successful signup can be made or not by making sure that the username is unique, it then updates its dictionary containing every user's public/private key to add a new user. 
  Whereas on a successful login the loadbalancer sends the user its stored private key as well as the address of the server to which it needs to be connected to and closing the existing socket connection.
### Menu options
- Main menu
- Group Settings
- Group Message
- Direct Message

### Textual and image/text files
At the core of every chatting program lies its numerous feature of conecting to other fellow users and the mutual give and take of information between them. So for that our program have the ability to allow texts/images from one user to other either in dm or in a group message. Key things in the program for this purpose being:
- Text sent through terminal limited to size
  Our chatting program as based on terminals allows user to type in their messages in their terminal window and popping these messages to the receiver's terminal at the same time or when they come online whichever the case be. The max limit of text size we allow is roughly 512 bytes. These texts are end-to-end encrypted and hence making the chat safe and secure. This communication encrytpion is dicussed below in the encryption section.
 
- Image (.png, .jpeg, .jpg) and Text (.txt) are supported
  A picture speaks a thousand work and so our program allows them to do so. Our chatting program rather than being just restricted to the texts messages allows user to share between each other images of type png, jpeg and jpg. These images too following the footsteps of text messages are sent safely and securely using the same encyrption methods as for texts.
  As image are nothing more than a text file with unique extensions, after the successful addition of image transfer feature we extended our program to also send files having .txt extension too between the users so that one may not have to write everything in the terminal.
  
- Threading and Locking
  One server, many clents. The condition on the one hand provides smoothly monitored conversation while on other a challenge of maintaining how everyone can simultaneously uses the same program at once without causing breakdown of server.
  So to overcome this challenge, we used the concept of threading. These threading allows the successful hadling of large number of clients efficiently without any concurrency clashes. 
  Also in inevitable cases where concurrency of variables posed as the necessary devil, we used locking to make sure only one part of the program can access/modify these variables at any particular time.

### Groups
Our fastchat program allows users to create groups with max limit of 20. The addition and removal of members can be done by the admin/creator of the group. Each group name is unique to ease the storage/implementation of the feature.
A message sent in group is broadcasted to every other member of the group and delivering to them later if they are offline at the moment.

### Encryption
For encryption we use SHA(Secure Hashing Algorithm) and RSA (Rivest, Shamir, Adleman) algorithms using the libraries:
- cryptocode
- Crypto
- passlib

Password is stored as an hashed version of itelf using passlib library in the database. It makes it non-decryptabe but only verifiable. RSA library Crypto allows us to create public/private keys for each user and group which is used to send and receive messages/images across the network. This private key itself is stored in the load balancer in an encrypted fashion using cryptocode which encrypts it using the user's password. This can only be decrypted only using the user's password and hence making it impossible for the server to crack it even though it has it.

### Server Load Balancing
Load balancer of ours as of now in a round robin manner after a successful verification of a user directs it to a particular server. This verification of user is done by sendng the encrypted password of an user to the client program where it is verified with the inputted password. 
The load balancer aims to reduce the load of each server by making sure each gets almost equal number of clients. The load balancer also stores in it public/private keys associated with every username and a dictionary which maintains which all users are online and are connected which server.
A user on successful login receives its private key from it and also public keys of other groups or users if it wants to send them a message (textual or images).
This strategy works as each server is also connected to every other server of the network and whenever load balancer want to direct a message to some other server it is done by using those intra-server sockets.

## Running the code files
1. Start loadbalancer in a terminal using `python3 loadbalancer.py 127.0.0.1 7999`
2. In ascending order of ports start all the servers first using `python3 server.py 127.0.0.1 <port>` where port ranges from 8000 to 8002.
3. Finally to start any client use `python3 client.py 127.0.0.1 7999`
## Yet to be done
- Documentation using sphinx
- Performance analysis
- Minor modifications is all the aforementioned features to ensure smooth functioning.

## Team members' contributions
Each and every task of the code was contributed equally by each member. All the features were coded in phases where some part of it was done by each member whereas the ideation of same was done together by the team as a whole.
