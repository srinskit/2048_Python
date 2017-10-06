from tkinter import *
import random
import time
import threading


class Matrix:
    # class to handle core game
    def __init__(self, frame, order):
        # implements contructor
        # logical 2048 matrix
        self.order = order
        self.labelWidth = self.frameMat = self.labelMat = None
        self.mat = [[0 for _ in range(self.order)] for _ in range(self.order)]
        self.target = 2048
        # main frame of matrix
        self.frame = frame
        self.make_gui()
        self.gen_new()
        # game status indicator
        self.gameStatus = 0

    def make_gui(self):
        # implements GUI
        # get width of tile from main frame width
        self.frame.update()
        self.labelWidth = min(self.frame.winfo_width(), self.frame.winfo_height()) // self.order
        # create and arrange tile frames
        self.frameMat = [
            [Frame(self.frame, width=self.labelWidth, height=self.labelWidth) for _ in range(self.order)]
            for _ in range(self.order)]
        for x in range(self.order):
            for y in range(self.order):
                self.frameMat[x][y].pack_propagate(False)
                self.frameMat[x][y].grid(row=x, column=y, padx=2, pady=2)
        # create label and fill in each tile frame
        self.labelMat = [
            [Label(self.frameMat[x][y], text="", font=("Helvetica", 24, "bold"), fg="black", bg="lightgrey") for y in
             range(self.order)]
            for x in range(self.order)]
        for x in range(self.order):
            for y in range(self.order):
                self.labelMat[x][y].pack(fill=BOTH, expand=1)

    def gen_new(self):
        # implements generation of new tile
        # convert a zero to non-zero tile
        zero = []
        for x in range(self.order):
            for y in range(self.order):
                if self.mat[x][y] == 0:
                    zero.append([x, y])
        if len(zero) != 0:
            i = random.randint(0, len(zero) - 1)
            x = zero[i][0]
            y = zero[i][1]
            self.mat[x][y] = 2
            # sync generation
            self.labelMat[x][y].config(text=str(self.mat[x][y]))

    def game_finished(self):
        for x in range(self.order):
            for y in range(self.order):
                if self.mat[x][y] >= self.target:
                    return True
        return False

    def up_game_status(self):
        # implements game-over check
        if self.game_finished():
            self.gameStatus = 2
        movement = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for x in range(self.order):
            for y in range(self.order):
                # zero tile
                if self.mat[x][y] == 0:
                    return
                # neighbour is equal to tile
                for i in range(4):
                    nex = x + movement[i][0]
                    ney = y + movement[i][1]
                    if 0 <= nex < self.order and 0 <= ney < self.order and self.mat[x][y] == \
                            self.mat[nex][ney]:
                        return
        self.gameStatus = 1

    def sync_mat(self):
        # implements sync between logical and graphics matrix
        for x in range(self.order):
            for y in range(self.order):
                self.labelMat[x][y].config(text=str(self.mat[x][y]) if self.mat[x][y] != 0 else "")

    def rotate_c(self):
        # implements clockwise rotation of logical matrix
        self.mat = list(map(list, zip(*self.mat[::-1])))

    def rotate_a(self):
        # implements anticlockwise rotation of logical matrix
        self.mat = list(map(list, zip(*self.mat)))[::-1]

    def rotate_push(self, rotate):
        # implements pushing of matrix
        # translate to left push
        if rotate > 0:
            for i in range(0, rotate, 1):
                self.rotate_c()
        elif rotate < 0:
            for i in range(rotate, 0, 1):
                self.rotate_a()
        # push left
        changed = False
        for x in range(self.order):
            y = 0
            while y < self.order - 1:
                # find non-zero from y+1
                i = y + 1
                while i < self.order:
                    if self.mat[x][i] != 0:
                        break
                    i = i + 1
                else:
                    break
                # if nonzero matches y tile
                if self.mat[x][i] == self.mat[x][y]:
                    self.mat[x][y] *= 2
                    self.mat[x][i] = 0
                    y = y + 1
                    changed = True
                # if y was zero simply copy
                elif self.mat[x][y] == 0:
                    self.mat[x][y] = self.mat[x][i]
                    self.mat[x][i] = 0
                    changed = True
                else:
                    y = y + 1
        # revert translation
        if rotate > 0:
            for i in range(0, rotate, 1):
                self.rotate_a()
        elif rotate < 0:
            for i in range(rotate, 0, 1):
                self.rotate_c()
        # sync, generate new and check for gameover
        if changed:
            self.sync_mat()
            self.gen_new()
        self.up_game_status()

    def reset(self):
        # implements handler for retry
        for x in range(self.order):
            for y in range(self.order):
                self.mat[x][y] = 0
        self.gameStatus = 0
        self.sync_mat()
        self.gen_new()


class App:
    width = 600
    height = 650

    def __init__(self):
        # create window
        self.window = Tk()
        self.window.title('2048 - SrinSxit')
        # create three main frames and stack them
        self.homeFrame = self.paused = self.timeLabel = self.statusFrame = None
        self.playButton = self.playFrame = self.gameFrame = self.mat = None

        self.make_play_frame()
        self.make_home_frame()
        self.pause_game()
        # start a deamon to handle time

        class Thread(threading.Thread):
            def __init__(self, app_ptr):
                threading.Thread.__init__(self)
                self.app_ptr = app_ptr
                self.onTime = 0

            def run(self):
                dt = 0.25
                while True:
                    time.sleep(dt)
                    if not self.app_ptr.paused:
                        self.onTime = self.onTime + dt
                        if self.app_ptr.mat.gameStatus != 0:
                            self.app_ptr.paused = True
                            if self.app_ptr.mat.gameStatus == 2:
                                self.app_ptr.timeLabel.config(text="You Win!Your time : " + str(self.onTime))
                            else:
                                self.app_ptr.timeLabel.config(text="Game Over")
                        else:
                            self.app_ptr.timeLabel.config(text=str(int(self.onTime)))

            def reset(self):
                self.onTime = 0

        self.timeThread = Thread(self)
        self.timeThread.setDaemon(True)
        self.timeThread.start()

    def key_pressed(self, direction):
        if not self.paused:
            if direction == 'L':
                self.mat.rotate_push(0)
            elif direction == 'R':
                self.mat.rotate_push(2)
            elif direction == 'D':
                self.mat.rotate_push(1)
            elif direction == 'U':
                self.mat.rotate_push(-1)

    def make_home_frame(self):
        # add widgets of home frame
        self.homeFrame = Frame(self.window, width=App.width, height=App.height)
        self.homeFrame.pack_propagate(0)
        self.homeFrame.grid(row=0, column=0, sticky="nsew")
        self.playButton = Button(self.homeFrame, text="Play", command=self.resume_game)
        self.playButton.place(relx=0.5, rely=0.5, anchor=CENTER)

    def make_play_frame(self):
        # add widgets of play frame
        self.playFrame = Frame(self.window, width=App.width, height=App.height)
        self.playFrame.pack_propagate(0)
        self.playFrame.grid(row=0, column=0, sticky="nsew")
        # children of main game frame
        self.make_status_frame()
        self.gameFrame = Frame(self.playFrame, width=App.width, height=App.width)
        self.gameFrame.pack_propagate(0)
        self.gameFrame.pack()
        self.mat = Matrix(self.gameFrame, 3)
        # bind keypresses
        self.mat.frame.bind("<Left>", lambda e: self.key_pressed('L'))
        self.mat.frame.bind("<Right>", lambda e: self.key_pressed('R'))
        self.mat.frame.bind("<Down>", lambda e: self.key_pressed('D'))
        self.mat.frame.bind("<Up>", lambda e: self.key_pressed('U'))

    def make_status_frame(self):
        self.statusFrame = Frame(self.playFrame, width=App.width, height=App.height - App.width)
        self.statusFrame.pack()
        self.statusFrame.grid_propagate(False)
        Grid.rowconfigure(self.statusFrame, index=0, weight=1)
        Grid.columnconfigure(self.statusFrame, index=0, weight=1)
        Grid.columnconfigure(self.statusFrame, index=1, weight=1)
        Grid.columnconfigure(self.statusFrame, index=2, weight=1)
        Button(self.statusFrame, text="Home", command=self.reset_game).grid(row=0, column=0, sticky="wens")
        self.timeLabel = Label(self.statusFrame)
        self.timeLabel.grid(row=0, column=1, sticky="wens")
        Button(self.statusFrame, text="Pause", command=self.pause_game).grid(row=0, column=2, sticky="wens")

    def display_home(self):
        self.homeFrame.lift()
        self.homeFrame.focus()

    def display_play(self):
        self.playFrame.lift()
        self.gameFrame.focus()

    def pause_game(self):
        self.paused = True
        self.display_home()

    def resume_game(self):
        self.paused = False
        self.display_play()

    def reset_game(self):
        self.pause_game()
        self.timeThread.reset()
        self.mat.reset()
        self.mat.gameStatus = 0


foo = App()
foo.window.mainloop()
