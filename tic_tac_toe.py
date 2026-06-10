import json
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path

BRAIN_FILE = Path(__file__).parent / 'ai_brain.json'

EMPTY = '.'
HUMAN = 'X'
AI = 'O'

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),   
]

def new_board():
    return [EMPTY] * 9

def board_key(board):
    return ''.join(board)

def winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
        if EMPTY not in board:
            return 'draw', None
        return None, None
    
def available_moves(board):
    return [i for i, v in enumerate(board) if v == EMPTY]

def find_immediate(board, player):
    for m in available_moves(board):
        test = board.copy()
        test[m] = player
        w, _ = winner(test)
        if w == player:
            return m
    return None

class QLearningAI:
    def __init__(self, alpha=0.3, gamma=0.9, epsilon=0.15):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q = {}
        self.history = []
        self.load()

    def load(self):
        if BRAIN_FILE.exists():
            try:
                with open(BRAIN_FILE, 'r', encoding = 'utf-8') as f:
                    raw = json.load(f)
                self.q = {s: {int(k): v for k, v in moves.items()}
                          for s, moves in raw.items()}
            except (json.JSONDecodeError, ValueError):
                self.q = {}

    def save(self):
        with open(BRAIN_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.q, f)

    def get_q(self, state, move):
        return self.q.get(state, {}).get(move, 0.0)
    
    def set_q(self, state, move, value):
        if state not in self.q:
            self.q[state] = {}
            self.q[state][move] = value

    def choose_move(self, board, training=False):
        state = board_key(board)
        moves = available_moves(board)

        if training and random.random() < self.epsilon:
            move = random.choice(moves)
        else:
            best_value - -float('inf')
            best_moves = []
            for m in moves:
                v = self.get_q(state, m)
                if v > best_value:
                    best_value = v
                    best_moves = [m]
                elif v == best_value:
                    best_moves.append(m)
            move = random.choice(best_moves)

        self.history.append((state, move))
        return move
    
    def learn(self):
        self.history = []

def smart_opponent_move(board, me, opp, randomness):
    win_now = find_immediate(board, me)
    if win_now is not None:
        return win_now
    block = find_immediate(board, opp)
    if block is not None and random.random() > randomness:
        return block
    if random.random() < randomness:
        return random.choice(available_moves(board))
    for pref in (4, 0, 2, 6, 8, 1, 3, 5, 7):
        if board[pref] == EMPTY:
            return pref
    return random.choice(available_moves(board))
    
class TicTacToeApp:
    CELL_FONT = ('Segoe UI', 36, 'bold')
    STATUS_FONT = ('Segoe UI', 13)
    BTN_FONT = ('Segoe UI', 10)

    COLOR_BG = '#1e1e2e'
    COLOR_CELL = '#2a2a3e'
    COLOR_CELL_HOVER = '#363650'
    COLOR_X = '#7dd3fc'
    COLOR_O = '#f9a8d4'
    COLOR_WIN = '#fde047'
    COLOR_TEXT = '#e4e4e7'

    def __init__(self, root):
        self.root = root
        self.root.title('Tic-Tac-Toe AI')
        self.root.configure(bg=self.COLOR_BG)
        self.root.resizable(False, False)

        self.ai = QLearningAI()
        self.board = new_board()
        self.human_first = True
        self.game_over = True
        self.cells = []
        self.stats = {'w': 0, 'l': 0, 'd': 0}

        self._build_ui()
        self._new_game()

    def _build_ui(self):
        title = tk.Label(
            self.root, text = 'Tic-Tac-Toe AI', font = ('Segoe UI', 18, 'bold'),
            bg=self.COLOR_BG, fg=self.COLOR_TEXT,
        )
        title.grid(row=0, column=0, columnspan=3, pady=(14,4))

        self.status = tk.Label(
            self.root, text='', font=self.STATUS_FONT,
            bg=self.COLOR_BG, fg=self.COLOR_TEXT,
        )
        self.status.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
