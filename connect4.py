import tkinter as tk
from tkinter import messagebox
import math
import random
import copy

ROWS = 6
COLUMNS = 7
CELL_SIZE = 80
WINDOW_WIDTH = COLUMNS * CELL_SIZE
WINDOW_HEIGHT = ROWS * CELL_SIZE
DEPTH = 4
HUMAN = 0
AI = 1
PLAYER_COLORS = ["#E30B5C", "hot pink"]
EMPTY = None
CONNECT_COUNT = 4


class LevelSelectionWindow:
    def __init__(self, root, on_level_selected):
        self.root = root
        self.on_level_selected = on_level_selected       
        self.level_window = tk.Toplevel(self.root)       
        self.level_window.title("Select Difficulty Level")
        self.level_window.geometry("500x300")
        self.level_window.configure(bg='#FFC0CB')
        label = tk.Label(self.level_window, text="❀Select Difficulty Level❀", font=("Fixedsys", 18, "bold"),bg='pink', fg="#E30B5C")
        label.pack(pady=20)
        easy_button = tk.Button(self.level_window, text="Easy", font=("Fixedsys", 18, "bold"), fg="white",bg='#fc8eac', command=lambda: self.set_difficulty("Easy"))
        easy_button.pack(pady=7)
        medium_button = tk.Button(self.level_window, text="Medium", font=("Fixedsys", 18, "bold"), fg="white",bg='#fc8eac', command=lambda: self.set_difficulty("Medium"))
        medium_button.pack(pady=7)
        hard_button = tk.Button(self.level_window, text="Hard", font=("Fixedsys", 18, "bold"), fg="white",bg='#fc8eac',command=lambda: self.set_difficulty("Hard"))
        hard_button.pack(pady=7)

    def set_difficulty(self, difficulty):
        global DEPTH
        if difficulty == "Easy":
            DEPTH = 2
        elif difficulty == "Medium":
            DEPTH = 3
        elif difficulty == "Hard":
            DEPTH = 4
        self.level_window.destroy()
        self.on_level_selected()    


class Connect4:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 with AI")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT+30}")
        self.root.withdraw() 
        self.level_window = LevelSelectionWindow(self.root, self.start_game) 

    def start_game(self):
        self.root.deiconify()    
        self.board = [[EMPTY for cell in range(COLUMNS)] for cell in range(ROWS)]
        self.canvas_cells = [[None for cell in range(COLUMNS)] for cell in range(ROWS)]
        self.game_over = False
        self.current_player = HUMAN
        self.create_widgets()

    def create_widgets(self):
        self.buttons = []
        for col in range(COLUMNS):
            btn = tk.Button(self.root, text="▼", font=("Arial", 14),  fg="#E30B5C", bg="white", command=lambda c=col: self.human_move(c)) 
            btn.place(x=col * CELL_SIZE, y=0, width=CELL_SIZE, height=30)
            self.buttons.append(btn)

        self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="pink") 
        self.canvas.place(x=0, y=30)  
        self.draw_board()

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLUMNS):
                x1 = col * CELL_SIZE  
                y1 = row * CELL_SIZE  
                x2 = x1 + CELL_SIZE   
                y2 = y1 + CELL_SIZE   
                self.draw_flower(self.canvas, x1 + 10, y1 + 10, x2 - 10, y2 - 10, "white")
                self.canvas_cells[row][col] = (x1 + 10, y1 + 10, x2 - 10, y2 - 10)

    def draw_flower(self, canvas, x1, y1, x2, y2, color):
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        petal_radius = min(x2 - x1, y2 - y1) / 4.3  
        petal_offset = [
            (-petal_radius, -petal_radius),
            (petal_radius, -petal_radius),
            (-petal_radius, petal_radius),
            (petal_radius, petal_radius)
        ]
        for dx, dy in petal_offset:
            canvas.create_oval(cx + dx - petal_radius, cy + dy - petal_radius,
                            cx + dx + petal_radius, cy + dy + petal_radius,
                            fill=color, outline=color)
        canvas.create_oval(cx - petal_radius / 1.5, cy - petal_radius / 1.5,
                        cx + petal_radius / 1.5, cy + petal_radius / 1.5,
                        fill="white", outline="")
        
    def human_move(self, col):
        if self.game_over or self.current_player != HUMAN:
            return
        if self.make_move(col, HUMAN):
            if self.check_game_over(HUMAN):
                return
            self.current_player = AI
            self.root.after(1, self.ai_move)    

    def ai_move(self):
        if self.game_over:
            return
        col, _ = self.minimax(self.board, DEPTH, True)
        self.make_move(col, AI)
        if self.check_game_over(AI):
            return
        self.current_player = HUMAN

    def make_move(self, col, player):
        for row in reversed(range(ROWS)):
            if self.board[row][col] is EMPTY:
                self.board[row][col] = player
                color = PLAYER_COLORS[player]
                x1, y1, x2, y2 = self.canvas_cells[row][col]
                self.canvas.delete(self.canvas_cells[row][col]) 
                self.draw_flower(self.canvas, x1, y1, x2, y2, color)  
                return True
        return False

    def check_game_over(self, player):
        if self.winning_move(self.board, player):
            if player == HUMAN:
                messagebox.showinfo("🌸 Yay!", "You won! 🎉\nYou totally outsmarted the AI!")
            else:
                messagebox.showinfo("💔 Oops", "The AI won this time.\nDon't give up, try again!")
            self.game_over = True
            return True
        elif self.check_draw(self.board):
            messagebox.showinfo("Hmm...", "It's a draw! Great minds think alike?")
            self.game_over = True
            return True
        return False

    def check_draw(self, board):
        return all(board[0][col] is not EMPTY for col in range(COLUMNS))

    def winning_move(self, board, player):
        for r in range(ROWS):
            for c in range(COLUMNS - CONNECT_COUNT + 1):
                if all(board[r][c + i] == player for i in range(CONNECT_COUNT)):
                    return True
        for r in range(ROWS - CONNECT_COUNT + 1):
            for c in range(COLUMNS):
                if all(board[r + i][c] == player for i in range(CONNECT_COUNT)):
                    return True      
        for r in range(ROWS - CONNECT_COUNT + 1):
            for c in range(COLUMNS - CONNECT_COUNT + 1):
                if all(board[r + i][c + i] == player for i in range(CONNECT_COUNT)):
                    return True
        for r in range(CONNECT_COUNT - 1, ROWS):
            for c in range(COLUMNS - CONNECT_COUNT + 1):
                if all(board[r - i][c + i] == player for i in range(CONNECT_COUNT)):
                    return True
        return False

    def get_valid_locations(self, board):
        return [col for col in range(COLUMNS) if board[0][col] is EMPTY]

    def evaluate_window(self, window, player):
        score = 0
        opponent = HUMAN if player == AI else AI
        if window.count(player) == CONNECT_COUNT:
            score += 100
        elif window.count(player) == CONNECT_COUNT - 1 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(player) == CONNECT_COUNT - 2 and window.count(EMPTY) == 2:
            score += 2
        if window.count(opponent) == CONNECT_COUNT - 1 and window.count(EMPTY) == 1:
            score -= 4
        return score

    def score_position(self, board, player):
        score = 0
        center = [board[i][COLUMNS // 2] for i in range(ROWS)]
        score += center.count(player) * 3
        for r in range(ROWS):
            row_array = [board[r][c] for c in range(COLUMNS)]
            for c in range(COLUMNS - CONNECT_COUNT + 1):
                window = row_array[c:c + CONNECT_COUNT]
                score += self.evaluate_window(window, player)
        for c in range(COLUMNS):
            col_array = [board[r][c] for r in range(ROWS)]
            for r in range(ROWS - CONNECT_COUNT + 1):
                window = col_array[r:r + CONNECT_COUNT]
                score += self.evaluate_window(window, player)
        for r in range(ROWS - CONNECT_COUNT + 1):
            for c in range(COLUMNS - CONNECT_COUNT + 1):
                window = [board[r + i][c + i] for i in range(CONNECT_COUNT)]
                score += self.evaluate_window(window, player)
        for r in range(ROWS - CONNECT_COUNT + 1):
            for c in range(COLUMNS - CONNECT_COUNT + 1):
                window = [board[r + CONNECT_COUNT - 1 - i][c + i] for i in range(CONNECT_COUNT)]
                score += self.evaluate_window(window, player)
        return score

    def is_terminal_node(self, board):
        return self.winning_move(board, HUMAN) or self.winning_move(board, AI) or self.check_draw(board)

    def minimax(self, board, depth, maximizingPlayer):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, AI):
                    return (None, float("inf"))
                elif self.winning_move(board, HUMAN):
                     return (None, -float("inf"))
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(board, AI))
        if maximizingPlayer:
            value = -math.inf
            best_col = random.choice(valid_locations)
            for col in valid_locations:
                temp_board = copy.deepcopy(board)
                for row in reversed(range(ROWS)):
                    if temp_board[row][col] is EMPTY:
                        temp_board[row][col] = AI
                        break
                new_score = self.minimax(temp_board, depth - 1, False)[1]
                if new_score > value:
                    value = new_score
                    best_col = col
            return best_col, value
        else:
            value = math.inf
            best_col = random.choice(valid_locations)
            for col in valid_locations:
                temp_board = copy.deepcopy(board)
                for row in reversed(range(ROWS)):
                    if temp_board[row][col] is EMPTY:
                        temp_board[row][col] = HUMAN
                        break
                new_score = self.minimax(temp_board, depth - 1, True)[1]
                if new_score < value:
                    value = new_score
                    best_col = col
        return best_col, value

if __name__ == "__main__":
    root = tk.Tk()
    game = Connect4(root)
    root.mainloop()