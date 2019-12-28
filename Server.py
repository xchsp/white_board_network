import socket
import threading
import time

# Here we have the global variables
# The Clients consists of the list of thread objects clients
# The logs consists of all the messages send through the server, it is used to redraw when someone new connects
Clients = []
Logs = {}


# -------------------------------SERVER ----------------------------------------
# This is the Server Thread, it is responsible for listening to connexions
# It opens new connections as it is a thread constantly listening at the port for new requests
class Server:
    ID = 1

    def __init__(self, host, port):
        self.host = host
        self.port = port

        # Initialize network
        self.network = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.network.bind((self.host, self.port))
        self.network.listen(10)
        print("The Server Listens at {}".format(port))

        # Start the pinger
        threading.Thread(target=self.pinger).start()

    # Here we have the main listener
    # As somebody connects we send a small hello as confirmation
    # Also we give him an unique ID that will be able to differentiate them from other users
    # We send the server logs so the new user can redraw at the same state in the board
    # We send the list of connected users to construct the permission system
    def start(self):
        while True:
            connexion, infos_connexion = self.network.accept()
            print("Sucess at " + str(infos_connexion))
            connexion.send('HLO'.encode())
            time.sleep(0.1)

            # Send all ID's so user cannot repeat any id's
            msg = " "
            for client in Clients:
                msg = msg + " " + client.clientID
            connexion.sendall(msg.encode())
            time.sleep(0.1)

            # Here we start a thread to wait for the users nickname input
            # We do this so a server can wait for a nickname input and listen to new connections
            threading.Thread(target=self.wait_for_user_nickname, args=[connexion]).start()

    # This function was created just to wait for the users input nickname
    # Once it's done if sends the logs so the user can be up to date with the board
    # And finally it creates the Client Thread which will be responsible for listening to the user messages
    def wait_for_user_nickname(self, connexion):
        # Receive the chosen ID from user
        try:
            new_user_id = connexion.recv(1024).decode()

            for log in Logs:
                connexion.send(Logs[log])

            new_client = Client(connexion, new_user_id)
            new_client.load_users()
            Clients.append(new_client)
            Server.ID = Server.ID + 1
            new_client.start()
        except ConnectionResetError:
            pass
        except ConnectionAbortedError:
            pass


    # Function used by pinger
    # Sends a removal message to alert all users of the disconnection
    def announce_remove_user(self, disconnectedClient):
        msg = 'RE' + ' ' + str(disconnectedClient.clientID) + ' ' + 'Ø'
        msg = msg.encode('ISO-8859-1')
        print(threading.enumerate())
        for client in Clients:
            client.connexion.sendall(msg)

    # This is the pinger function, it is used to check how many users are currently connected
    # It pings all connections, if it receives a disconnection error, it does the following things:
    # 1.Sends a removal message to alert all users of the disconnection
    # 2.Removes client from list of clients to avoid sending messages to it again
    # 3.Sends the permission to delete the disconnected user stuff from the board!
    def pinger(self):
        while True:
            time.sleep(0.1)
            for client in Clients:
                try:
                    msg = "ß".encode('ISO-8859-1')
                    print('ß')
                    client.connexion.send(msg)
                except ConnectionResetError:
                    client.terminate()
                    Clients.remove(client)
                    self.announce_remove_user(client)
                except ConnectionAbortedError:
                    client.terminate()
                    Clients.remove(client)
                    self.announce_remove_user(client)


# -----------------------------------CLIENTS -------------------------------------
# This is the client thread, it is responsible for dealing with the messages from all different clients
# There is one thread for every connected client, this allows us to deal with them all at the same time
class Client():
    MessageID = 0

    def __init__(self, connexion, clientID):
        self.connexion = connexion
        self.clientID = clientID
        self._run = True

    def load_users(self):
        for client in Clients:
            msg = 'A' + ' ' + str(client.clientID) + ' ' + 'Ø'
            self.connexion.send(msg.encode('ISO-8859-1'))
            msg = 'A' + ' ' + str(self.clientID) + ' ' + 'Ø'
            client.connexion.send(msg.encode('ISO-8859-1'))

    def terminate(self):
        self._run = False

    def start(self):
        while self._run:
            try:
                # Here we start by reading the messages
                # Split according to the protocol
                msg = ""
                while True:
                    data = self.connexion.recv(1).decode('ISO-8859-1')
                    if data == "Ø":
                        break
                    msg = msg + data

                splitted_msg = msg.split()

                # We do not want to keep the logs
                if splitted_msg[0] in ['TA']:
                    self.echoesAct3(msg)
                    continue
            # We pass the Connection Reset Error since the pinger will deal with it more effectivelly
            except ConnectionResetError:
                pass
            except ConnectionAbortedError:
                pass

    # Main echoes function!
    # This is responsible for echoing the message between the clients
    def echoesAct3(self, msg):
        msg = msg + " Ø"
        msg = msg.encode('ISO-8859-1')
        for client in Clients:
            client.connexion.sendall(msg)

if __name__ == "__main__":
    host = ''
    port = 5000
    server = Server(host, port)
    server.start()


