import random, time
from tkinter import *

CONTROLS = {"DOWN": "s",
            "RIGHT": "d",
            "LEFT": "a",
            "ROTATE": "r",
            "PAUSE": "p"}
MAPSIZE = [15, 10]
SPACESIZE = 40
SPEED = 1000
SPEED_INCREASE = 0.9
COLORS = {"RED": "#FF0000",
          "BLUE": "#0000FF",
          "YELLOW": "#FFFF00",
          "GREEN": "#00FF00",
          "PINK": "#FF00FF",
          "CYAN": "#00FFFF"}


class Block:
    def __init__(self, coords, world):
        self.coords = coords["coords"]
        self.world = world
        self.color = coords["color"]
        sRow, sCol = self.world.startPos
        self.location = [(row + sRow, col + sCol) for row, col in self.coords]
        if not self.checkCollision(self.location):
            for coord in self.location:
                self.world.coords[coord] = ["@", self.color]
        else:
            print("END")
            exit()

    def moveModel(self, direction):
        print(direction)
        if direction not in CONTROLS.values():
            return
        newLocation = self.location.copy()
        for i, coord in enumerate(newLocation):
            row, col = coord
            if direction == CONTROLS["RIGHT"]:
                newLocation[i] = (row, col + 1)
            elif direction == CONTROLS["LEFT"]:
                newLocation[i] = (row, col - 1)
            elif direction == CONTROLS["DOWN"]:
                newLocation[i] = (row + 1, col)

        if not self.checkCollision(newLocation):
            self.removeFromWorld()
            self.location = newLocation
            self.addToWorld()
        else:
            if direction == CONTROLS["DOWN"]:
                return self.embedToWorld()

    def rotateModel(self):
        # adds model to rectangle grid
        rows = max([x[0] for x in self.coords]) + 1
        cols = max([x[1] for x in self.coords]) + 1
        drawing = [[0 for _ in range(cols)] for _ in range(rows)]
        for coord in self.coords:
            row, col = coord
            drawing[row][col] = 1

        # rotates rectangle and extracts model coords
        newCoords = []
        newLocation = []
        for r, row in enumerate(drawing):
            for c, col in enumerate(row):
                if col == 1:
                    newCoords.append((c, len(drawing) - 1 - r))

        # creates new location from new coords
        rows = min([row for row, col in self.location])
        cols = min([col for row, col in self.location])
        for coords in newCoords:
            row, col = coords
            newLocation.append((row + rows, col + cols))

        # replaces model in world if no collision
        if not self.checkCollision(newLocation):
            self.removeFromWorld()
            self.coords = newCoords
            self.location = newLocation
            self.addToWorld()

    def checkCollision(self, newLocation):
        print("check collision")
        for coord in newLocation:
            if self.world.coords[coord][0] != " " and self.world.coords[coord][0] != "@":
                return True
        return False

    def addToWorld(self):
        for coord in self.location:
            self.world.coords[coord] = ["@", self.color]

    def embedToWorld(self):
        print("embed")
        for coord in self.location:
            self.world.coords[coord][0] = "X"
        self.world.checkRows()
        self.world.draw()
        return "Bottom"

    def removeFromWorld(self):
        for position in self.location:
            self.world.coords[position] = [" ", None]


class GameSpace:
    def __init__(self):
        self.rows, self.cols = MAPSIZE
        self.score = 0
        self.startPos = (1, self.cols // 2)
        self.coords = {}
        self.speed = SPEED
        self.borderColor = "#FFFFFF"
        for col in range(self.cols):
            for row in range(self.rows):
                if row == 0 or row == self.rows - 1 or col == 0 or col == self.cols - 1:
                    self.coords[(row, col)] = ["O", self.borderColor]
                else:
                    self.coords[(row, col)] = [" ", None]

    def draw(self):
        canvas.delete(ALL)
        for row in range(self.rows):
            print()
            for col in range(self.cols):
                space, color = self.coords[(row, col)]
                x, y = col * SPACESIZE, row * SPACESIZE
                if space == "@":
                    canvas.create_rectangle(x, y, x + SPACESIZE - 1, y + SPACESIZE - 1, fill=color)
                elif space == "X":
                    canvas.create_rectangle(x, y, x + SPACESIZE - 1, y + SPACESIZE - 1, fill=color)
                elif space == "O":
                    canvas.create_rectangle(x, y, x + SPACESIZE - 1, y + SPACESIZE, fill=color)
                print(space, end="  ")
        print()

    def checkRows(self):
        for row in range(1, self.rows - 1):
            for col in range(1, self.cols - 1):
                if self.coords[(row, col)][0] == " ":
                    break
            else:
                self.score += 1
                self.speed = int(self.speed*SPEED_INCREASE)
                label.config(text="Score:{}".format(self.score))
                for col in range(1, self.cols - 1):
                    self.coords[(row, col)] = [" ", None]
                for row2 in range(row, 1, -1):
                    for col2 in range(1, self.cols - 1):
                        if self.coords[(row2 - 1, col2)][0] != " ":
                            self.coords[(row2, col2)] = self.coords[(row2 - 1, col2)]
                            self.coords[(row2 - 1, col2)] = [" ", None]


class GameLoop:
    def __init__(self):
        self.world = GameSpace()
        self.block = Block(random.choice(blocks), self.world)
        self.pause = False

    def loop(self, key):
        if self.pause:
            if key == CONTROLS["PAUSE"]:
                self.pause = False
            time.sleep(0.1)
        elif key == CONTROLS["PAUSE"]:
            self.pause = True
        elif key == CONTROLS["ROTATE"]:
            self.block.rotateModel()
        elif self.block.moveModel(key) == "Bottom":
            self.block = Block(random.choice(blocks), self.world)
        self.world.draw()


def moveDown():
    game.loop(CONTROLS["DOWN"])
    base.after(game.world.speed, moveDown)


blocks = [{"coords": [(0, 0), (1, 0), (2, 0), (2, 1)], "color": COLORS["RED"]},
          {"coords": [(0, 1), (1, 1), (2, 1), (2, 0)], "color": COLORS["BLUE"]},
          {"coords": [(0, 0), (0, 1), (1, 0), (1, 1)], "color": COLORS["YELLOW"]},
          {"coords": [(0, 0), (0, 1), (1, 1), (1, 2)], "color": COLORS["GREEN"]},
          {"coords": [(0, 0), (1, 0), (2, 0), (3, 0)], "color": COLORS["PINK"]},
          {"coords": [(0, 0), (1, 0), (1, 1), (2, 0)], "color": COLORS["CYAN"]}
          ]
game = GameLoop()

base = Tk()
base.geometry("{}x{}".format(game.world.cols * SPACESIZE, game.world.rows * SPACESIZE + SPACESIZE + 20))

label = Label(base, text="Score:{}".format(game.world.score), font=('consolas', 40))
label.pack()
canvas = Canvas(base, bg="#000000", height=game.world.rows * SPACESIZE, width=game.world.cols * SPACESIZE)
canvas.pack()
base.bind("<KeyPress>", lambda x: game.loop(x.char))
base.after(game.world.speed, moveDown)

base.mainloop()
