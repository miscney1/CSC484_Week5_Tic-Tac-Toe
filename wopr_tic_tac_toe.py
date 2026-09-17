"""
CSC 484 - Module 5
Tic-Tac-Toe with NumPy, Inheritance, and Polymorphism

This program uses:
1. NumPy to store and evaluate a 3x3 tic-tac-toe board.
2. Tkinter to create a point-and-click graphical user interface.
3. Inheritance through a shared Player parent class.
4. Polymorphism because HumanPlayer and WOPRPlayer both implement
   choose_move() differently.
5. A main application class to keep the game state and GUI together.

The game intentionally favors readable coursework over highly compressed code.
A few sections take a longer, very explicit route so the logic is easy to
follow and still leaves room for later refactoring as more Python is learned.
"""

# -----------------------------------------------------------------------------
# SECTION 1 - IMPORTS
# -----------------------------------------------------------------------------
import tkinter as tk
from tkinter import messagebox
import numpy as np


# -----------------------------------------------------------------------------
# SECTION 2 - PLAYER CLASSES: INHERITANCE AND POLYMORPHISM
# -----------------------------------------------------------------------------
class Player:
    """Parent class containing information shared by every player type."""

    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    def choose_move(self, board, row=None, column=None):
        """Subclasses provide their own version of how a move is selected."""
        raise NotImplementedError("Subclasses must define choose_move().")


class HumanPlayer(Player):
    """Represents Dr. Falken, who chooses a move by clicking the GUI."""

    def choose_move(self, board, row=None, column=None):
        # The human move already comes from a GUI click.  This method simply
        # validates the selected NumPy position and returns it if it is legal.
        if row is None or column is None:
            return None

        if board[row, column] == " ":
            return row, column

        return None


class WOPRPlayer(Player):
    """Represents the computer opponent and selects its own NumPy position."""

    def choose_move(self, board, row=None, column=None):
        # WOPR follows a simple strategy rather than choosing a random square.
        # The steps are intentionally written out so each decision is visible.

        # Step 1: If WOPR can win immediately, take that move.
        winning_move = self.find_winning_move(board, self.symbol)
        if winning_move is not None:
            return winning_move

        # Step 2: If the human can win next turn, block that square.
        blocking_move = self.find_winning_move(board, "X")
        if blocking_move is not None:
            return blocking_move

        # Step 3: Prefer the center when it is available.
        if board[1, 1] == " ":
            return 1, 1

        # Step 4: If the human owns a corner and the opposite corner is open,
        # WOPR takes the opposite corner.  This helps reduce simple fork setups.
        opposite_corner_pairs = [
            ((0, 0), (2, 2)),
            ((2, 2), (0, 0)),
            ((0, 2), (2, 0)),
            ((2, 0), (0, 2))
        ]

        for human_corner, opposite_corner in opposite_corner_pairs:
            human_row, human_column = human_corner
            opposite_row, opposite_column = opposite_corner

            if board[human_row, human_column] == "X":
                if board[opposite_row, opposite_column] == " ":
                    return opposite_row, opposite_column

        # Step 5: Try each corner in a fixed order.
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]

        for corner in corners:
            corner_row, corner_column = corner
            if board[corner_row, corner_column] == " ":
                return corner_row, corner_column

        # Step 6: If no corner is open, try the edge squares.
        edges = [(0, 1), (1, 0), (1, 2), (2, 1)]

        for edge in edges:
            edge_row, edge_column = edge
            if board[edge_row, edge_column] == " ":
                return edge_row, edge_column

        # If no squares remain, there is no legal move.
        return None

    def find_winning_move(self, board, symbol):
        """Return a move that makes three in a row, or None if none exists."""

        # We test each empty square by temporarily placing the supplied symbol.
        # A tighter implementation could reduce some repetition, but the longer
        # version makes the trial-and-restore process straightforward to trace.
        for row in range(3):
            for column in range(3):
                if board[row, column] == " ":
                    board[row, column] = symbol

                    if self.board_has_winner(board, symbol):
                        board[row, column] = " "
                        return row, column

                    board[row, column] = " "

        return None

    def board_has_winner(self, board, symbol):
        """Small helper used only while WOPR evaluates possible moves."""

        for row in range(3):
            if np.all(board[row, :] == symbol):
                return True

        for column in range(3):
            if np.all(board[:, column] == symbol):
                return True

        first_diagonal = np.array([
            board[0, 0],
            board[1, 1],
            board[2, 2]
        ])

        if np.all(first_diagonal == symbol):
            return True

        second_diagonal = np.array([
            board[0, 2],
            board[1, 1],
            board[2, 0]
        ])

        if np.all(second_diagonal == symbol):
            return True

        return False


# -----------------------------------------------------------------------------
# SECTION 3 - MAIN APPLICATION CLASS
# -----------------------------------------------------------------------------
class WOPRTicTacToe:
    """Controls the WOPR-style Tic-Tac-Toe game and Tkinter interface."""

    def __init__(self, root):
        """Set up the main window, players, and first program state."""

        self.root = root
        self.root.title("WOPR Tic-Tac-Toe")
        self.root.geometry("560x610")
        self.root.resizable(False, False)

        self.win95_gray = "#C0C0C0"
        self.root.configure(bg=self.win95_gray)

        # The assignment's game board is a real 3x3 NumPy array.
        self.board = np.full((3, 3), " ", dtype="<U1")

        # The two subclasses inherit name and symbol from Player, but each has
        # its own choose_move() behavior.  This is the polymorphism example.
        self.human_player = HumanPlayer("Dr. Falken", "X")
        self.wopr_player = WOPRPlayer("WOPR", "O")

        # Dr. Falken always begins each round.  WOPR is always Player O.
        self.current_player = self.human_player

        self.consecutive_draws = 0
        self.game_over = False
        self.wopr_thinking = False

        self.square_buttons = [[None for _ in range(3)] for _ in range(3)]
        self.main_frame = None

        self.create_menu_bar()
        self.show_start_screen()

    # -------------------------------------------------------------------------
    # SECTION 4 - WINDOWS 95 STYLE MENU AND STARTUP SCREEN
    # -------------------------------------------------------------------------
    def create_menu_bar(self):
        """Create a small Windows 95-style menu at the top of the window."""

        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Tic-Tac-Toe Game", command=self.start_new_game)
        game_menu.add_command(label="Return to Game Menu", command=self.show_start_screen)
        menu_bar.add_cascade(label="Game", menu=game_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_message)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def clear_main_frame(self):
        """Remove the current screen before drawing a different one."""

        if self.main_frame is not None:
            self.main_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg=self.win95_gray)
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=12)

    def show_start_screen(self):
        """Display the WOPR opening screen and game choices."""

        self.clear_main_frame()

        terminal_frame = tk.Frame(
            self.main_frame,
            bg="black",
            bd=4,
            relief="sunken"
        )
        terminal_frame.pack(fill="both", expand=True, padx=18, pady=18)

        title_label = tk.Label(
            terminal_frame,
            text="WOPR GAME SYSTEM",
            bg="black",
            fg="#00FF66",
            font=("Courier", 18, "bold")
        )
        title_label.pack(pady=(40, 30))

        hello_label = tk.Label(
            terminal_frame,
            text="Hello, Dr. Falken.",
            bg="black",
            fg="#00FF66",
            font=("Courier", 14)
        )
        hello_label.pack(pady=8)

        question_label = tk.Label(
            terminal_frame,
            text="Would you like to play a game?",
            bg="black",
            fg="#00FF66",
            font=("Courier", 14)
        )
        question_label.pack(pady=(0, 30))

        tic_tac_toe_button = tk.Button(
            terminal_frame,
            text="TIC-TAC-TOE",
            command=self.start_new_game,
            width=24,
            bg=self.win95_gray,
            activebackground="#D4D0C8",
            relief="raised",
            bd=4,
            font=("Arial", 10, "bold")
        )
        tic_tac_toe_button.pack(pady=10)

        thermo_button = tk.Button(
            terminal_frame,
            text="THERMO-NUCLEAR WAR",
            command=self.show_thermonuclear_warning,
            width=24,
            bg=self.win95_gray,
            fg="red",
            activebackground="#D4D0C8",
            relief="raised",
            bd=4,
            font=("Arial", 10, "bold", "overstrike")
        )
        thermo_button.pack(pady=10)

        exit_button = tk.Button(
            terminal_frame,
            text="EXIT",
            command=self.root.destroy,
            width=12,
            bg=self.win95_gray,
            relief="raised",
            bd=4
        )
        exit_button.pack(pady=(30, 10))

    def show_thermonuclear_warning(self):
        """Show the warning attached to the crossed-out game choice."""

        messagebox.showwarning(
            "WOPR Warning",
            "This game is no longer playable as it is a 0 sum game with no discernable winner."
        )

    def show_about_message(self):
        """Display a short description of the program."""

        messagebox.showinfo(
            "About WOPR Tic-Tac-Toe",
            "CSC 484 Module 5\n\n"
            "A point-and-click Tic-Tac-Toe game using NumPy, inheritance, "
            "and polymorphism."
        )

    # -------------------------------------------------------------------------
    # SECTION 5 - BUILDING AND RESETTING THE GAME BOARD
    # -------------------------------------------------------------------------
    def start_new_game(self):
        """Create a fresh NumPy board and draw a new 3x3 GUI game board."""

        self.board = np.full((3, 3), " ", dtype="<U1")
        self.current_player = self.human_player
        self.game_over = False
        self.wopr_thinking = False

        self.clear_main_frame()

        game_title = tk.Label(
            self.main_frame,
            text="WOPR TIC-TAC-TOE",
            bg=self.win95_gray,
            font=("Arial", 18, "bold")
        )
        game_title.pack(pady=(10, 5))

        self.status_label = tk.Label(
            self.main_frame,
            text="Dr. Falken (X): Select a square",
            bg=self.win95_gray,
            font=("Arial", 11, "bold"),
            relief="sunken",
            bd=2,
            anchor="w",
            padx=8
        )
        self.status_label.pack(fill="x", padx=20, pady=(5, 15))

        board_frame = tk.Frame(self.main_frame, bg=self.win95_gray)
        board_frame.pack(pady=5)

        for row in range(3):
            for column in range(3):
                square_button = tk.Button(
                    board_frame,
                    text="",
                    width=7,
                    height=3,
                    bg=self.win95_gray,
                    activebackground="#D4D0C8",
                    relief="raised",
                    bd=6,
                    font=("Arial", 26, "bold"),
                    command=lambda r=row, c=column: self.handle_human_click(r, c)
                )

                square_button.grid(row=row, column=column, padx=2, pady=2)
                self.square_buttons[row][column] = square_button

        self.coordinate_label = tk.Label(
            self.main_frame,
            text="Selected position: [--, --]",
            bg=self.win95_gray,
            font=("Courier", 11)
        )
        self.coordinate_label.pack(pady=(14, 4))

        control_frame = tk.Frame(self.main_frame, bg=self.win95_gray)
        control_frame.pack(pady=12)

        new_game_button = tk.Button(
            control_frame,
            text="New Game",
            command=self.start_new_game,
            width=12,
            relief="raised",
            bd=4,
            bg=self.win95_gray
        )
        new_game_button.grid(row=0, column=0, padx=8)

        menu_button = tk.Button(
            control_frame,
            text="Game Menu",
            command=self.show_start_screen,
            width=12,
            relief="raised",
            bd=4,
            bg=self.win95_gray
        )
        menu_button.grid(row=0, column=1, padx=8)

        exit_button = tk.Button(
            control_frame,
            text="Exit",
            command=self.root.destroy,
            width=12,
            relief="raised",
            bd=4,
            bg=self.win95_gray
        )
        exit_button.grid(row=0, column=2, padx=8)

    # -------------------------------------------------------------------------
    # SECTION 6 - HUMAN AND WOPR MOVES
    # -------------------------------------------------------------------------
    def handle_human_click(self, row, column):
        """Process Dr. Falken's GUI click and then give WOPR its turn."""

        if self.game_over or self.wopr_thinking:
            return

        # The HumanPlayer subclass handles the human version of choose_move().
        selected_move = self.human_player.choose_move(self.board, row, column)

        if selected_move is None:
            self.status_label.config(
                text=f"Square [{row}, {column}] is already occupied. Choose another square."
            )
            return

        selected_row, selected_column = selected_move
        self.apply_move(self.human_player, selected_row, selected_column)

        if self.check_for_winner(self.human_player.symbol):
            self.finish_with_winner(self.human_player)
            return

        if self.check_for_draw():
            self.finish_with_draw()
            return

        # Prevent another click while WOPR is selecting its response.
        self.wopr_thinking = True
        self.status_label.config(text="WOPR (O): Evaluating board...")
        self.disable_open_squares()

        # after() creates a short pause so the computer move feels deliberate
        # and keeps the interface responsive while we wait.
        self.root.after(650, self.make_wopr_move)

    def make_wopr_move(self):
        """Ask the WOPRPlayer subclass to choose and perform its move."""

        if self.game_over:
            return

        # Same method name as HumanPlayer, different behavior.  WOPR receives
        # the board and determines its own row and column automatically.
        selected_move = self.wopr_player.choose_move(self.board)

        if selected_move is None:
            # This should normally mean the board is full, but the explicit
            # check makes the program safer and easier to follow.
            if self.check_for_draw():
                self.finish_with_draw()
            return

        selected_row, selected_column = selected_move
        self.apply_move(self.wopr_player, selected_row, selected_column)

        if self.check_for_winner(self.wopr_player.symbol):
            self.finish_with_winner(self.wopr_player)
            return

        if self.check_for_draw():
            self.finish_with_draw()
            return

        self.wopr_thinking = False
        self.enable_open_squares()
        self.status_label.config(text="Dr. Falken (X): Select a square")

    def apply_move(self, player, row, column):
        """Store one player's move in NumPy and update the matching GUI button."""

        self.board[row, column] = player.symbol

        self.square_buttons[row][column].config(
            text=player.symbol,
            relief="sunken",
            state="disabled",
            disabledforeground="black"
        )

        self.coordinate_label.config(
            text=f"{player.name} selected position: [{row}, {column}]"
        )

    # -------------------------------------------------------------------------
    # SECTION 7 - WIN AND DRAW CHECKS USING NUMPY
    # -------------------------------------------------------------------------
    def check_for_winner(self, symbol):
        """Return True when the supplied symbol has three matching squares."""

        # Check the three horizontal rows.
        for row in range(3):
            row_values = self.board[row, :]

            if np.all(row_values == symbol):
                return True

        # Check the three vertical columns.
        for column in range(3):
            column_values = self.board[:, column]

            if np.all(column_values == symbol):
                return True

        # The diagonal checks intentionally spell out the coordinates rather
        # than using the shorter np.diag() approach.  It is still correct, but
        # it leaves an obvious future refactoring opportunity.
        first_diagonal = np.array([
            self.board[0, 0],
            self.board[1, 1],
            self.board[2, 2]
        ])

        if np.all(first_diagonal == symbol):
            return True

        second_diagonal = np.array([
            self.board[0, 2],
            self.board[1, 1],
            self.board[2, 0]
        ])

        if np.all(second_diagonal == symbol):
            return True

        return False

    def check_for_draw(self):
        """Return True only when every NumPy square is filled without a win."""

        board_is_full = np.all(self.board != " ")

        if board_is_full:
            return True
        else:
            return False

    # -------------------------------------------------------------------------
    # SECTION 8 - NORMAL GAME ENDINGS AND BUTTON CONTROL
    # -------------------------------------------------------------------------
    def finish_with_winner(self, player):
        """Stop the round, announce the winner, and reset the draw streak."""

        self.game_over = True
        self.wopr_thinking = False
        self.consecutive_draws = 0
        self.disable_all_squares()

        if player is self.human_player:
            winner_message = "Dr. Falken wins."
        else:
            winner_message = "WOPR wins."

        self.status_label.config(text=winner_message)
        messagebox.showinfo("Game Complete", winner_message)

    def finish_with_draw(self):
        """Handle a draw and start the WOPR analysis after three in a row."""

        self.game_over = True
        self.wopr_thinking = False
        self.consecutive_draws = self.consecutive_draws + 1

        self.status_label.config(
            text=f"Draw. Consecutive draws: {self.consecutive_draws}"
        )
        self.disable_all_squares()

        if self.consecutive_draws < 3:
            messagebox.showinfo(
                "Draw",
                f"The game is a draw.\n\nConsecutive draws: {self.consecutive_draws}"
            )
            self.start_new_game()
        else:
            self.root.after(700, self.start_wopr_analysis)

    def disable_all_squares(self):
        """Disable every square after a round ends."""

        for row in range(3):
            for column in range(3):
                self.square_buttons[row][column].config(state="disabled")

    def disable_open_squares(self):
        """Temporarily disable open squares while WOPR is thinking."""

        for row in range(3):
            for column in range(3):
                if self.board[row, column] == " ":
                    self.square_buttons[row][column].config(state="disabled")

    def enable_open_squares(self):
        """Re-enable only squares that are still empty after WOPR's turn."""

        for row in range(3):
            for column in range(3):
                if self.board[row, column] == " ":
                    self.square_buttons[row][column].config(state="normal")

    # -------------------------------------------------------------------------
    # SECTION 9 - THREE-DRAW WOPR ANALYSIS SEQUENCE
    # -------------------------------------------------------------------------
    def start_wopr_analysis(self):
        """Display a deliberately simple line-by-line WOPR learning sequence."""

        self.clear_main_frame()

        analysis_frame = tk.Frame(
            self.main_frame,
            bg="black",
            bd=4,
            relief="sunken"
        )
        analysis_frame.pack(fill="both", expand=True, padx=10, pady=10)

        analysis_title = tk.Label(
            analysis_frame,
            text="WOPR STRATEGIC GAME ANALYSIS",
            bg="black",
            fg="#00FF66",
            font=("Courier", 14, "bold")
        )
        analysis_title.pack(pady=(16, 8))

        self.analysis_text = tk.Text(
            analysis_frame,
            width=58,
            height=24,
            bg="black",
            fg="#00FF66",
            insertbackground="#00FF66",
            font=("Courier", 10),
            relief="flat",
            wrap="word"
        )
        self.analysis_text.pack(padx=14, pady=8)
        self.analysis_text.config(state="disabled")

        self.analysis_lines = [
            "ACCESSING RECENT GAME HISTORY...",
            "GAME 1 RESULT: DRAW",
            "GAME 2 RESULT: DRAW",
            "GAME 3 RESULT: DRAW",
            "",
            "BEGINNING STRATEGIC REVIEW...",
            "REPLAYING HUMAN OPENING MOVES...",
            "REPLAYING WOPR RESPONSE PATTERNS...",
            "TESTING CENTER CONTROL...",
            "RESULT: NO FORCED WIN FOUND",
            "TESTING CORNER CONTROL...",
            "RESULT: NO FORCED WIN FOUND",
            "TESTING EDGE CONTROL...",
            "RESULT: NO FORCED WIN FOUND",
            "",
            "COMPARING RESPONSE PATTERNS...",
            "CHECKING OFFENSIVE PATHS...",
            "CHECKING DEFENSIVE PATHS...",
            "CHECKING BLOCKING PATHS...",
            "CHECKING REPEATED OUTCOMES...",
            "",
            "NO DECISIVE ADVANTAGE DETECTED.",
            "NO RELIABLE WINNING PATH DETECTED.",
            "",
            "CONCLUSION:",
            "Dr. Falken, this game is much like Thermo-Nuclear War...",
            "There is no winner."
        ]

        self.analysis_line_number = 0
        self.write_next_analysis_line()

    def write_next_analysis_line(self):
        """Write one analysis line, then schedule the next line."""

        if self.analysis_line_number < len(self.analysis_lines):
            line_to_write = self.analysis_lines[self.analysis_line_number]

            self.analysis_text.config(state="normal")
            self.analysis_text.insert("end", line_to_write + "\n")
            self.analysis_text.see("end")
            self.analysis_text.config(state="disabled")

            self.analysis_line_number = self.analysis_line_number + 1

            # This could be replaced by a timing dictionary or a more general
            # animation helper.  The longer if/elif version remains readable
            # and shows exactly why different lines pause for different times.
            if line_to_write == "":
                delay = 250
            elif "ACCESSING" in line_to_write:
                delay = 700
            elif "BEGINNING" in line_to_write:
                delay = 700
            elif "REPLAYING" in line_to_write:
                delay = 600
            elif "CONCLUSION" in line_to_write:
                delay = 900
            elif "Dr. Falken" in line_to_write:
                delay = 1000
            elif line_to_write == "There is no winner.":
                delay = 1200
            else:
                delay = 550

            self.root.after(delay, self.write_next_analysis_line)
        else:
            self.show_analysis_return_button()

    def show_analysis_return_button(self):
        """Add the final return button after the analysis crawl finishes."""

        return_button = tk.Button(
            self.main_frame,
            text="Return to Game Menu",
            command=self.return_from_analysis,
            width=22,
            bg=self.win95_gray,
            relief="raised",
            bd=4
        )
        return_button.pack(pady=(0, 10))

    def return_from_analysis(self):
        """Reset the draw streak and return to the startup screen."""

        self.consecutive_draws = 0
        self.show_start_screen()


# -----------------------------------------------------------------------------
# SECTION 10 - PROGRAM START
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = WOPRTicTacToe(root)
    root.mainloop()
