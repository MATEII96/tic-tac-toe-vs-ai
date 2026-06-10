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