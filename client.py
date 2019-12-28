import time
from threading import Thread
from graphical_widgets import ExternalWindows
from network import MConnection
from whiteboard import Whiteboard


class Client(Thread,Whiteboard):


    def __init__(self):
        self.my_connexion = MConnection()
        Whiteboard.__init__(self)
        Thread.__init__(self)
        self.setDaemon(True)

        # This part refers to the class that allows user to exchange messages between themselves

    # The run handles the messages
    # As it recognizes the type it assigns to the proper class that will handle it!
    def run(self):
        while True:
            try:
                msg = self.my_connexion.receive_message()
                if msg[0] == "ß":
                    print(msg[0])
            except ValueError:
                pass
            except IndexError:
                pass
            except ConnectionResetError:
                ExternalWindows.show_error_box("Server down please save your work")
                self.save_and_load.save()
                self.myWhiteBoard.destroy()



if __name__ == '__main__':
    c = Client()
    c.start()
    c.show_canvas()
