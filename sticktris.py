from tkinter import *
from time import sleep
from random import randint
import colorsys

def rgbtohex(r, g, b):
    if not (isinstance(r, int) and isinstance(g, int) and isinstance(b, int)):
        return rgbtohex(int(r), int(g), int(b))
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

win = Tk()
win.geometry("500x1000")
canvas = Canvas(win, width=500, height=1000)
canvas.configure(bg="black")
canvas.pack()
win.resizable(width=0, height=0)
win.winfo_toplevel().title("Sticktris")

# upleft is same x, up right is one more x
# when defining pieces, 0,0 is the point which the piece rotates around
# each tuple has (beginningx, beginningy,  endingx, endingy)
pieces = [[(0, 0, 0, -1), (0, 0, 0, 1)], [(0, 0, 1, 0), (0, 0, 0, -1)], [(0, 0, 0, 1)]]
piececount = len(pieces)
# board coordinates top left 0,0

# fix line clearing piece interaction

class sticktris:  # 0 represented an empty spot

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []  # y increases down, x increases right
        self.score = 0
        self.linescleared = 0
        self.level = 1
        for i in range(height * 2 + 1):
            self.grid.append((width + i % 2) * [0])

    def lineposition(
        self, coordinatepair
    ):  # takes in line starting/end positions and returns the actual grid index used to access that
        # these must be positive
        ychange = coordinatepair[3] - coordinatepair[1]
        if ychange == 0:  # horizontal line
            return (
                coordinatepair[1] * 2,
                coordinatepair[0],
            )  # in order they are accessed
        else:  # vertical line
            return (coordinatepair[1] * 2 + 1, coordinatepair[0])

    def piececoordinates(self):
        allcoordinates = []
        for p in pieces[self.piecetype]:
            allcoordinates.append(
                self.lineposition(
                    (
                        p[0] + self.piecepos[0],
                        p[1] + self.piecepos[1],
                        p[2] + self.piecepos[0],
                        p[3] + self.piecepos[1],
                    )
                )
            )
        return allcoordinates

    def rotatepiece(self, cw=True):
        originaltype = self.piecetype
        self.setpiece()
        if cw:
            self.piecetype = (self.piecetype - piececount) % len(pieces)
        else:
            self.piecetype = (self.piecetype + piececount) % len(pieces)
        isvalid = self.checkvalid()
        if not isvalid:
            self.piecetype = originaltype
        self.setpiece(self.piecetype+1)

    def checkvalid(self):
        coordinates = self.piececoordinates()

        for coord in coordinates:
            if coord[0] >= len(self.grid) or coord[0] < 0:
                return False
            if coord[1] >= len(self.grid[coord[0]]) or coord[1] < 0:
                return False
            if self.grid[coord[0]][coord[1]] != 0:
                return False
        return True

    def movepiece(self, dx=0, dy=0):
        self.setpiece()
        self.piecepos = (self.piecepos[0] + dx, self.piecepos[1] + dy)

        isvalid = self.checkvalid()
        if not isvalid:
            self.piecepos = (self.piecepos[0] - dx, self.piecepos[1] - dy)
        self.setpiece(self.piecetype+1)
        if dx == 0 and not isvalid:
            self.addpiece()
            return True
        return False
    

    def lineclears(self):
        clearcount = 0
        piececoords = self.piececoordinates()
        line = 0
        while line < self.height:
            hasempty = (0 in self.grid[line * 2 + 1]) or (0 in self.grid[line * 2 + 2])
            if not hasempty:
                clearcount += 1
                for i in range(line * 2, -1, -1):
                    for j in range(len(self.grid[i])):
                        if (i, j) not in piececoords:
                            self.grid[i + 2][j] = self.grid[i][j]

            line += 1
        self.linescleared += clearcount
        self.score += 40*self.level*4**clearcount
        self.level = self.linescleared//10+1
        

    def valuetocolor(self, value):
        color = colorsys.hls_to_rgb(value/piececount, 0.5, 1, )
        return rgbtohex(color[0] * 255, color[1] * 255, color[2] * 255)
    


    def addpiece(self):
        self.piecepos = (self.width // 2, 2)
        self.piecetype = randint(0, piececount)
        self.setpiece(self.piecetype+1)

    def setpiece(self, value=0):  # backend thing
        coordinates = self.piececoordinates()
        for coord in coordinates:
            self.grid[coord[0]][coord[1]] = value

    def renderboard(self, xmin, ymin, xwidth, ywidth):
        canvas.delete("all")
        #vertical lines
        for i in range(self.width+1):
            canvas.create_line(xmin+i*xwidth/self.width, ymin, xmin+i*xwidth/self.width, ymin+ywidth, fill = "gray20", width = 1)
        for i in range(self.height+1):
            canvas.create_line(xmin, ymin+i*ywidth/self.height, xmin+xwidth, ymin+i*ywidth/self.height, fill = "gray20", width = 1)
        #change it so order is grey, background, white
       
       
        for y in range(1, self.height+1):
            for x in range(self.width):
                bottom = self.grid[y*2][x]
                left = self.grid[y*2-1][x]
                right = self.grid[y*2-1][x+1]
                if bottom*left*right>0:
                    canvas.create_rectangle(xmin+x*xwidth/self.width, ymin+(y-1)*ywidth/self.height, xmin+(x+1)*xwidth/self.width, ymin+(y)*ywidth/self.height, fill = "grey50")
       
        for y in range(self.height + 1):
            for x in range(self.width + 1):
                if x != self.width:
                    value = self.grid[y * 2][x]
                    if value != 0:
                        canvas.create_line(
                            xmin + x * xwidth / self.width-1,
                            ymin + y * ywidth / self.height,
                            xmin + (x + 1) * xwidth / self.width+1,
                            ymin + y * ywidth / self.height,
                            fill=self.valuetocolor(value),
                            width=4,
                        )
                if y != self.height:
                    value = self.grid[y * 2 + 1][x]
                    if value != 0:  
                        canvas.create_line(
                            xmin + x * xwidth / self.width,
                            ymin + y * ywidth / self.height-1,
                            xmin + x * xwidth / self.width,
                            ymin + (y + 1) * ywidth / self.height+1,
                            fill=self.valuetocolor(value),
                            width=4,
                        )


# piece preprocessing


def rotatecoord(x, y, x1, y1, cw=True):
    return (y, -x, y1, -x1) if cw else (-y, x, -y1, x1)


l = len(pieces)
for i in range(3):
    for j in range(l):
        piece = pieces[len(pieces) - l]
        newpiece = []
        for k in range(len(piece)):
            newpiece.append(rotatecoord(*piece[k]))
        pieces.append(newpiece)


for i in range(len(pieces)):
    for j in range(len(pieces[i])):
        k = pieces[i][j]
        swap = False
        if k[0] == k[2]:
            swap = k[1] > k[3]
        else:
            swap = k[0] > k[2]
        if swap:
            pieces[i][j] = (k[2], k[3], k[0], k[1])


def leftarrow(e):
    game.movepiece(-1, 0)


def rightarrow(e):
    game.movepiece(1, 0)


def uparrow(e):
    game.rotatepiece()


def downarrow(e):
    game.movepiece(0, 1)


canvas.focus_set()
canvas.bind("<Left>", leftarrow)
canvas.bind("<Right>", rightarrow)
canvas.bind("<Up>", uparrow)
canvas.bind("<Down>", downarrow)
game = sticktris(8, 16)
game.addpiece()
game.renderboard(50, 100, 400, 800)

counter = 0


def gameloop():
    global counter
    counter += 1
    
    
    game.renderboard(50, 100, 400, 800)
    win.after(30, gameloop)
    if counter % 10 == 0:
        if game.movepiece(0, 1):
            sleep(0.01)
            game.lineclears()
    
    
    


win.after(500, gameloop)
win.mainloop()
