import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
from boggle_utils import *
import sys
from boggle_board_randomizer import *

TIMER_SECONDS = 300
FONT_SIZE = 12
BUTTON_STYLE = {"height": 93, "width": 93, "borderwidth": 1,
                "relief": tk.FLAT}


class BoggleModel:
    """Logic class of Boggle! Deals with backend calculations."""
    def __init__(self):
        """A method that initializes instance variables."""
        self._board = randomize_board(LETTERS)
        self._path = []
        self._words = load_words_dict(file_path="boggle_dict.txt")
        self._guessed_words = []
        self.points = 0
        self.message = ""

    def get_board(self):
        """A getter method for self._board"""
        return self._board

    def get_guessed_words(self):
        """A getter method for self._guessed_words"""
        guessed_words_str = ""
        for word in self._guessed_words:
            guessed_words_str += f"\n{word.upper()}"
        return guessed_words_str

    def get_path(self):
        """A getter method for self._path"""
        return self._path

    def set_path(self, path):
        """A setter method for self._path"""
        self._path = path

    def submit_is_pressed(self):
        """A method that performs actions if the submit button is pressed."""
        # If not enough letters are entered:
        if len(self._path) < 3:
            self._show_message("Not enough letters entered")
            return
        # When enough letters are entered:
        word = is_valid_path(self._board, self._path, self._words)
        # If the word is not a valid word:
        if word is None:
            self._show_message("Word is incorrect")
            self._path = []
            return
        # If the word was already chosen
        if word in self._guessed_words:
            self._show_message("Word has already been chosen")
            self._path = []
            return
        # When a new word found in the dictionary, 3-16 letters long, with a valid path on the board is chosen.
        else:
            self._add_points(word)
            self._add_word_to_wordlist(word)
            self._show_message("Word is correct!")
            self._path = []

    def _add_points(self, word):
        """A helper method that calculates the number of points to be awarded."""
        self.points += len(word)**2
        return self.points

    def _add_word_to_wordlist(self, word):
        """A helper method that adds a correct word to the guessed word list."""
        self._guessed_words.append(word)
        return self._guessed_words

    def _show_message(self, msg):
        """A helper method that returns a relevant message."""
        self.message = msg
        return self.message

    def get_hint(self):
        """A method that returns a random valid word on the board that has yet been found."""
        length_of_word = random.randint(3,16)
        words_and_coords = find_length_n_words(length_of_word, self._board, self._words)  # returns a list of tuples
        words = self._get_words(words_and_coords)  # retrieves the words from each tuple
        words = self._loop_until_words_found(words)
        word = random.choice(words)
        word = self._loop_until_new_word(word, words)
        return word

    def _get_words(self, words_and_coords):
        """A helper method that extracts only the words from the word/coordinate tuple-list."""
        words = []
        for word_and_coord in words_and_coords:
            words.append(word_and_coord[0])
        return words

    def _loop_until_words_found(self, words):
        """A helper method that runs until a list of at least one word of a randomized length had been found."""
        while not words:
            length_of_word = random.randint(3, 16)
            words_and_coords = find_length_n_words(length_of_word, self._board, self._words)
            words = self._get_words(words_and_coords)
        return words

    def _loop_until_new_word(self, word, words):
        """A helper method that runs until the hint-word has yet been chosen."""
        while word in self._guessed_words:
            word = random.choice(words)
        return word


class BoggleGui:
    """Graphic class of Boggle! Deals with front end design."""
    _dice_number_to_object = {}
    _dice_letter_to_image = {}

    def __init__(self):
        """A method that initializes instance variables."""
        root = tk.Tk()
        root.title("Boggle!")
        root.resizable(False, False)
        root.iconbitmap("icon.ico")
        self.__main_window = root

        # 'new game' widget area
        self.newgame_frame = tk.Frame(self.__main_window, bg="#dfdfdf")

        self.new_game = tk.Button(self.newgame_frame, font=FONT_SIZE, text="New Game", width=10, bg="#dfdfdf", relief="flat")
        self.new_game.pack(side=tk.TOP)

        # 'guessed words' area
        self.guessed_words_frame = tk.Frame(self.__main_window, width=150, height=150, bg="#ababab")

        self.words_list = tk.Label(self.guessed_words_frame, font=FONT_SIZE, text="Guessed Words", width=25,
                                   background="#ababab")
        self.words_list.pack(side=tk.TOP, pady=10)

        # hint, timer and points area
        self.widget_frame = tk.Frame(self.__main_window, bg="#dfdfdf")

        self.hint = tk.Button(self.widget_frame, font=FONT_SIZE, text="Hint", bg="#dfdfdf", relief="flat", width=5)
        self.hint.pack(side=tk.LEFT, padx=30)
        self.timer = tk.Label(self.widget_frame, font=FONT_SIZE, text="Time", bg="#dfdfdf", width=12)
        self.timer.pack(side=tk.LEFT, padx=50)
        self.points = tk.Label(self.widget_frame, font=FONT_SIZE, text="Points", bg="#dfdfdf", width=15)
        self.points.pack(side=tk.LEFT, padx=0)

        # message display area
        self.message_display_frame = tk.Frame(self.__main_window)
        self.message_display = tk.Label(self.message_display_frame, font=FONT_SIZE, text="",
                                        bg="#dfdfdf", width=50)
        self.message_display.pack(pady=10)

        # board area
        self.board_frame = tk.Frame(self.__main_window, width=400, height=400,
                                    background="#ffffff", highlightthickness=50)
        # dice grid
        for i in range(4):
            tk.Grid.columnconfigure(self.board_frame, i, weight=1)
            tk.Grid.rowconfigure(self.board_frame, i, weight=1)

        # dice images
        for i in range(26):
            self._dice_letter_to_image[str(chr(ord('A') + i))] = \
                ImageTk.PhotoImage(Image.open(f"dice_{chr(ord('a') + i)}.png"))
        self.blank_dice = ImageTk.PhotoImage(Image.open("dice_blank.png"))

        # make pre-game board
        for i in range(4):
            for j in range(4):
                die_label = tk.Label(self.board_frame, image=self.blank_dice)
                die_label.grid(row=i, column=j, rowspan=1, columnspan=1, padx=1, pady=7)

        # submit area
        self.submit_frame = tk.Frame(self.__main_window)
        self.submit_label = tk.Label(self.submit_frame, font=FONT_SIZE, text="", bg="#dfdfdf", width=20)
        self.submit_button = tk.Button(self.submit_frame, font=FONT_SIZE, text="Submit Word", bg="#dfdfdf",
                                       relief="flat", width=12)
        self.submit_button.pack(side=tk.BOTTOM, pady=10)
        self.submit_label.pack(side=tk.TOP)

        # instructions area
        self.instructions = self.load_instructions("instructions.txt")
        self.instructions_frame = tk.Frame(self.__main_window)
        self.status = tk.Label(self.instructions_frame, text="Click here for instructions")
        self.status.pack(side=tk.RIGHT, padx=208)
        self.status.bind("<Button-1>", lambda event: messagebox.showinfo("Instructions", self.instructions))

        # initialize main window grid
        self.newgame_frame.grid(row=0, column=0, sticky="ew")
        self.widget_frame.grid(row=0, column=1, sticky="ew")
        self.guessed_words_frame.grid(row=1, column=0, rowspan=3, sticky="nsew")
        self.message_display_frame.grid(row=1, column=1, columnspan=1, sticky="ew")
        self.board_frame.grid(row=2, column=1, sticky="nsew")
        self.submit_frame.grid(row=3,column=1, sticky="ew")
        self.instructions_frame.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.__main_window.grid_rowconfigure(1, weight=1)
        self.__main_window.grid_columnconfigure(1, weight=1)

    def create_board(self, board):
        """A method that creates the game board. Initialized when newgame button is pressed."""
        for i in range(4):
            for j in range(4):
                letter = board[i][j]
                if letter == 'QU': letter = 'Q'
                self._make_dice_button(self._dice_letter_to_image[letter], i, j, dice_number=i * 4 + j)

    def _make_dice_button(self, button_img, row, col, dice_number, rowspan=1, columnspan=1):
        """A helper method that initializes each dice button. Dictionary that ties dice number to object is updated."""
        die_button = tk.Button(self.board_frame, image=button_img, **BUTTON_STYLE)
        die_button.grid(row=row, column=col, rowspan=rowspan, columnspan=columnspan, padx=1, pady=7)
        self._dice_number_to_object[dice_number] = die_button
        return die_button

    def get_dice_dict(self):
        """A getter method for the 'dice number to object' dictionary."""
        return self._dice_number_to_object

    def load_instructions(self, file_path):
        """A method that reads the instructions text file and converts it to a string.
        Accounts for empty lines in file."""
        with open(file_path) as data_file:
            instructions_text = ""
            for line in data_file:
                if line == "":
                    instructions_text += '\n'
                instructions_text += line
            return instructions_text

    def set_newgame_button_command(self, cmd):
        """A method that sets the newgame button command. Used by controller."""
        self.new_game["command"] = cmd

    def set_submit_button_command(self, cmd):
        """A method that sets the newgame button command. Used by controller."""
        self.submit_button["command"] = cmd

    def set_hint_button_command(self, cmd):
        """A method that sets the newgame button command. Used by controller."""
        self.hint["command"] = cmd

    def get_display(self, guessed_words, points, message):
        """A method that gets new variable value from the Model class (via the controller) and displays them."""
        self.words_list["text"] = f"Guessed Words {guessed_words}"
        self.points["text"] = f"Points: {points}"
        self.message_display["text"] = f"{message}"

    def countdown_timer(self, count):
        """A method responsible for creating the countdown timer."""
        time_display = time.strftime("%M:%S", time.gmtime(count))
        self.timer.configure(text=f"Timer: {time_display}")
        self._has_timer_ended(count)

    def _has_timer_ended(self, count):
        """A helper method that checks if timer has ended and if it has, executes the endgame screen."""
        if count > 0:
            self.__main_window.after(1000, self.countdown_timer, count - 1)
        else:
            answer = messagebox.askyesno("Game Over", "    Your time has run out \nDo you want to play again?")
            if answer:
                self.__main_window.destroy()
                main()
            else:
                sys.exit()

    def run(self):
        """A method that runs the game's mainloop."""
        self.__main_window.mainloop()


class BoggleController:
    """Controller class that bridges the gap between back-end and front-end."""
    def __init__(self):
        """A method that initializes instance variables."""
        self._gui = BoggleGui()
        self._model = BoggleModel()
        self._gui.set_newgame_button_command(lambda: self.start_new_game(self._model.get_board()))
        self._gui.set_submit_button_command(self.set_display)
        self._gui.set_hint_button_command(self.hint_is_pressed)
        self.newgame_wasnt_pressed = True

    def start_new_game(self, board):
        """A method that is called when the new_game button is pressed.
        (1) Board with letters is created and displayed, (2) Buttons are bound to the the dice is pressed method and
        (3) Button is deactivated and disappears."""
        if self.newgame_wasnt_pressed:
            self._gui.create_board(board)
            self._gui.countdown_timer(TIMER_SECONDS)
            self.set_dice_command()
            self._gui.new_game["text"] = ""
            self.newgame_wasnt_pressed = False

    def set_dice_command(self):
        """A method that sets the 'dice_is_pressed' function to each dice button."""
        for dice_num, dice in self._gui.get_dice_dict().items():
            dice.bind("<Button-1>", lambda event, index=dice_num: self.dice_is_pressed(index))

    def set_display(self):
        """A method that is called when the submit button is pressed.
        (1) Submit function in Model class is called and (2) guessed words, points and message data are collected
        and displayed."""
        self._model.submit_is_pressed()
        guessed_words = self._model.get_guessed_words()
        points = self._model.points
        message = self._model.message
        self._gui.get_display(guessed_words, points, message)
        self._gui.submit_label["text"] = ""

    def dice_is_pressed(self, dice_number):
        """A method that is called when a dice button is pressed.
        (1) Dice coordinates are found, (2) Dice letter is displayed and (3) Path is built."""
        x = dice_number//4
        y = dice_number%4
        letter = self._model.get_board()[x][y]
        self._gui.submit_label["text"] += letter
        letter_coord = [(x, y)]
        path = self._model.get_path()
        path += letter_coord
        return self._model.set_path(path)

    def hint_is_pressed(self):
        """A method that is called when the hint button is pressed.
        (1) Hint is displayed in message box. (2) 30-point deduction is displayed."""
        message = self._model.get_hint()
        guessed_words = self._model.get_guessed_words()
        self._model.points -= 30
        self._gui.get_display(guessed_words, self._model.points, message)

    def run(self):
        """A method that calls the run method of the Gui."""
        self._gui.run()


def main():
    """A function that creates a controller and runs the game."""
    game = BoggleController()
    game.run()


if __name__ == '__main__':
    main()







