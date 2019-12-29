import time
from threading import Thread

from drawing_tools import DrawingTools
from graphical_widgets import ExternalWindows
from network import MConnection
from whiteboard import Whiteboard


class Client(Thread,DrawingTools):

    # Tracks whether left mouse is down
    left_but = "up"

    # x and y positions for drawing with pencil
    x_pos, y_pos = None, None

    # Tracks x & y when the mouse is clicked and released
    x1_line_pt, y1_line_pt, x2_line_pt, y2_line_pt = None, None, None, None

    # class variable to keep track of the list of people who you have allowed you to delete their stuff
    # And the people you gave permission to delete theirs

    # list of objects that the whiteboard can draw
    Objects = {'line': 'L', 'oval': 'O', 'circle': 'C', 'rectangle': 'R', 'square': 'S', 'erase': 'E', 'drag': 'DR'}

    def __init__(self):
        my_connexion = MConnection()

        DrawingTools.__init__(self,my_connexion)
        Thread.__init__(self)
        self.setDaemon(True)
        self._init_mouse_action()
        self.text = "WOW"


        # This part refers to the class that allows user to exchange messages between themselves

    # The run handles the messages
    # As it recognizes the type it assigns to the proper class that will handle it!
    def run(self):
        while True:
            try:
                msg = self.my_connexion.receive_message()
                if( msg[0] in ['O', 'C', 'L', 'R', 'S', 'E', 'D', 'Z', 'T', 'DR']):
                    self.draw_from_message(msg)
            except ValueError:
                pass
            except IndexError:
                pass
            except ConnectionResetError:
                ExternalWindows.show_error_box("Server down please save your work")
                self.save_and_load.save()
                self.myWhiteBoard.destroy()



    def _init_mouse_action(self):
        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.left_but_down)
        self.drawing_area.bind("<ButtonRelease-1>", self.left_but_up)

    # ---------- CATCH MOUSE UP ----------
    # Here when the mouse is pressed we register it's first position and change the state of the button
    # The x_pos and y_pos are used for drawing with the mouse, since for mouse drawing we need to update
    # the positions as we draw
    # ---------- CATCH MOUSE UP ----------
    def left_but_down(self, event=None):
        self.left_but = "down"
        # Set x & y when mouse is clicked
        self.x1_line_pt = event.x
        self.y1_line_pt = event.y

        self.x_pos = event.x
        self.y_pos = event.y

        if self.drawing_tool == "eraser":
            self.delete_item(event)

        # Get tag of current object clicked object for dragging function
        try:
            self.user_last_object_clicked = self.drawing_area.gettags('current')[0]
            self.last_object_clicked = self.drawing_area.gettags('current')[1]
        except IndexError:
            self.user_last_object_clicked = None
            self.last_object_clicked = None

    # ---------- CATCH MOUSE UP ----------
    # When the mouse is released we save the position of the release in x2_line_pt and y2_line_pt
    # Once we have the 4 coordinates required for the drawing we call the drawing function,
    # the drawing function depends on the tool selected by the user
    # The tool is selected by pressing the widget on the main screen
    # Here we finally draw when the mouse is released
    # When the mouse is released we call object draw that is responsible for drawing a object
    # Or the text draw responsible for drawing text
    def left_but_up(self, event=None):
        self.left_but = "up"

        # Reset the line
        self.x_pos = None
        self.y_pos = None

        # Set x & y when mouse is released
        self.x2_line_pt = event.x
        self.y2_line_pt = event.y

        # If mouse is released and line tool is selected
        # draw the line
        if self.drawing_tool in ['line', 'oval', 'rectangle', 'circle', 'square', 'drag']:
            self.obj_draw(self.drawing_tool)
        elif self.drawing_tool == "text":
            self.text_draw()

    # ---------- CATCH MOUSE MOVEMENT ----------
    # Every time the mouse moves we call this function
    # If the selected tool is the pencil, we call the function to draw with the pencil
    def motion(self, event=None):
        if self.drawing_tool == "pencil":
            self.pencil_draw(event)
        if self.drawing_tool == "eraser":
            self.delete_item(event)

    # ---------- DRAW PENCIL ----------
    # Here we draw with the pencil, this function send's it's own messages because it is drawn differently than
    # the other tools
    # That is the main reason why the message is send through here and not through the send message function
    # We take the x.pos and y.pos which are initially set by pressing the mouse
    # And draw a line between this position and the mouse position 0.02 seconds later
    # We them update x.pos and y.pos with the mouse current position
    # Send it all through a message so it can be draw by the others

    def pencil_draw(self, event=None):
        if self.left_but == "down":
            # Make sure x and y have a value
            # if self.x_pos is not None and self.y_pos is not None:
            # event.widget.create_line(self.x_pos, self.y_pos, event.x, event.y, smooth=TRUE)
            time.sleep(0.02)
            msg = ('D', self.x_pos, self.y_pos, event.x, event.y, self.color, self.my_connexion.ID)
            self.my_connexion.send_message(msg)

            self.x_pos = event.x
            self.y_pos = event.y

    # This section is for drawing the different objects
    # The function we call depends on the different drawing tool we are used
    # Since we always have to send the same four coordinates, we only change the type of object we are drawing
    def obj_draw(self, obj):
        if obj in self.Objects:
            self.send_item(self.Objects[obj])

    # ---------- DRAW TEXT ----------
    # Here we draw text!
    # Since drawing text is different than the other types of message we send this is also done here
    # For text the messages are longer, since they require to send the text we want to draw
    def text_draw(self):
        if None not in (self.x1_line_pt, self.y1_line_pt):
            # Show all fonts available
            self.text = ExternalWindows.return_text()
            msg = ('T', self.text, self.x1_line_pt, self.y1_line_pt, self.color, self.my_connexion.ID)
            self.my_connexion.send_message(msg)

    # ------- Sending Messages for drawing ------------------------------------------------------
    # In this function we prepare the messages that will be sent by the connexion class
    # The messages here are a tuple of format:
    # (A,B,C,D,E,F) where A is the letters refering to the type, B,C,D,E are coordinates E is the color and F is the user ID
    # For the drag message things are different, first the type, them the object clicked, them the changes in coordinates
    def send_item(self, msg_type):
        if msg_type in ['L', 'C', 'O', 'R', 'S']:
            msg = (msg_type, self.x1_line_pt, self.y1_line_pt, self.x2_line_pt, self.y2_line_pt,
                   self.color, self.my_connexion.ID)
            self.my_connexion.send_message(msg)
        if msg_type in ['DR']:
            msg = (msg_type, self.last_object_clicked, self.x2_line_pt - self.x1_line_pt,
                   self.y2_line_pt - self.y1_line_pt)
            self.my_connexion.send_message(msg)

    # DELETE STUFF ####################################
    # Here we find the canvas id of whatever we clicked on
    # From the canvas id we find the tag we globally assigned for all users referring to that object
    # Afterwards we send that ID as a message to delete the objects in all possible canvas
    def delete_item(self, event):
        if self.left_but == "down":
            indice = 0
            try:
                canvas_item_id = self.drawing_area.find_overlapping(event.x+2,event.y+2,event.x-2,event.y-2)
                canvas_item_id = (max(canvas_item_id),)
                indice = len(self.drawing_area.gettags(canvas_item_id))
            except ValueError:
                pass
            if indice == 3:
                user, global_id,whatever = self.drawing_area.gettags(canvas_item_id)
                self.my_connexion.send_message(('Z', global_id))
            elif indice == 2:
                user, global_id = self.drawing_area.gettags(canvas_item_id)
                self.my_connexion.send_message(('Z', global_id))


if __name__ == '__main__':
    c = Client()
    c.start()
    c.show_canvas()
