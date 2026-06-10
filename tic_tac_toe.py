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

        grid_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        grid_frame.grid(row=2, column=0, columnspan=3, padx=20)

        for i in range(9):
            r, c = divmod(i, 3)
            cell = tk.Label(
                grid_frame, text='', font=self.COLOR_TEXT,
                width=3, height=1,
                bg=self.COLOR-CELL, fg=self.COLOR_TEXT,
                bd=0, relief='flat', cursor='hand2',
            )
            cell.grid(row=r, column=c, padx=4, pady=4, ipadx=4, ipady=4)
            cell.bind('<Button-1>', lambda e, idx=i: self._on_cell_click(idx))
            cell.bind('<Enter>', lambda e, idx=i: self._on_hover(idx, True))
            cell.bind('<Leave>', lambda e, idx=i: self._on_hover(idx, False))
            self.cells.append(cell)

        self.brain_info = tk.Label(
            self.root, text='', font=('Segoe UI', 9),
            bg=self.COLOR_BG, fg='#9090a0',
        )
        self.brain_info.grid(row=3, column=0, columnspan=3, pady=(12, 4))

        btn_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(4, 14), padx=20, sticky='ew')

        self._make_button(btn_frame, 'Partida noua', self._new_game).pack(side='left', padx=3)
        self._make_button(btn_frame, 'Antreneaza', self._train).pack(side='left', padx=3)
        self._make_button(btn_frame, 'Cine Incepe', self._toggle_first).pack(side='left', padx=3)
        self._make_button(btn_frame, 'Reseteaza AI', self._reset_brain).pack(side='left', padx=3)

        self._refresh_brain_info()

    def  _make_button(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command, font=self.BTN_FONT,
            bg='#3a3a5a', fg=self.COLOR_TEXT, activebackground = '#4a4a7a',
            activeforeground=self.COLOR_TEXT, bd=0, padx=10, pady=6, cursor='hand2',
        )
    def _refresh_brain_info(self):
        s = self.stats
        self.brain_info.config(
            text=f'Stari invatate: {len(self.ai.q)}  |  Tu: {s['w']} V / {s['l']} I / {s['d']} E'
        )

    def _on_hover(self, idx, entering):
        if self.game_over or self.board[idx] != EMPTY:
            return
        self.cells[idx].config(bg=self.COLOR_CELL_HOVER if entering else self.COLOR_CELL)

    def _render(self, win_line=None):
        for i, v in enumerate(self.board):
            cell = self.cells[i]
            if v == HUMAN:
                cell.config(text='X', fg=self.COLOR_X, bg=self.COLOR_CELL)
            elif v == AI:
                cell.config(text='O', fg=self.COLOR_O, bg=self.COLOR_CELL)
            else:
                cell.config(text='', bg=self.COLOR_CELL)
        if win_line:
            for i in win_line:
                self.cells[i].config(bg=self.COLOR_WIN)

    def _set_status(self, text):
        self.status.config(text=text)

    def _new_game(self):
        self.board = new_board()
        self.ai.reset_history()
        self.game_over = False
        self._render()
        if self.human_first:
            self._set_status('Tura ta (X) - da click pe o casuta')
        else:
            self._set_status('AI incepe...')
            self.root.after(400, self._ai_turn)
    def _toggle_first(self):
        self.human_first = not self.human_first
        who = 'Tu' if self.human_first else 'AI'
        messagebox.showinfo('Cine incepe', f'{who} incepe partida urmatoare.')

    def _on_cell_click(self, idx):
        if self.game_over or self.board[idx] != EMPTY:
            return
        self.board[idx] = HUMAN
        self._render()
        if self._check_end():
            return
        self._set_status('AI se gandeste...')
        self.root.after(350, self.ai_turn)

    def _ai_turn(self):
        if self.game_over:
            return
        move = self.ai.choose_move(self.board, training=True)
        self.board[move] = AI
        self._render()
        if self._check_end():
            return
        self._set_status('Tura ta (X)')
    def _check_end(self):
        result, line = winner(self.board)
        if result is None:
            return False
        self.game_over = True
        if result == AI:
            self.ai.learn(1.0)
            self.stats['l'] += 1
            self._set_status('AI a castigat. Apasa Partida noua.')
        elif result == HUMAN:
            self.ai.learn(-1.0)
            self.stats['w'] += 1
            self._set_status('Ai castigat! AI a invatat din asta')
        else:
            self.ai.learn(0.3)
            self.stats['d'] += 1
            self._set_status('Egal. Apasa Partida noua.')
        self._render(win_line=line)
        self.ai.save()
        self._refresh_brain_info()
        return True
    
    def _train(self):
        games = simpledialog.askinteger(
            'Antrenament',
            'Cate partide sa joace AI singur?\n(recomandat: 1000 - 10000)',
            parent=self.root, minvalue=1, maxvalue= 200_000_000, initialvalue=2000,
        )
        if not games:
            return
        
        progress = tk.Toplevel(self.root)
        progress.title('Antrenament in desfasurare')
        progress.configure(bg=self.COLOR_BG)
        progress.resizable(False, False)
        progress.transient(self.root)
        progress.grab_set()

        label = tk.Label(progress, text='Pornire...', font=self.STATUS_FONT,
                         bg=self.COLOR_BG, fg=self.COLOR_TEXT, width=42)
        label.pack(padx=20, pady=(18, 6))

        bar_bg = tk.Frame(progress, bg='#2a2a3e', width=320,height=14)
        bar_bg.pack(padx=20, pady=(0, 6))
        bar_bg.pack_propagate(False)
        bar_fill = tk.Frame(bar_bg, bg='#7dd3fc', width=0, height=14)
        bar_fill.place(x=0, y=0)

        detail = tk.Label(progress, text='', font=('Segoe UI', 9),
                          bg=self.COLOR_BG, fg='#9090a0', width = 42)
        detail.pack(padx=20,pady=(0, 16))
        
        state = {'i': 0, 'w': 0, 'l': 0, 'd': 0, 'cancelled': False}

        def on_close():
            state['cancelled'] = True
        progress.protocol('WM_DELETE_WINDOW', on_close)

        batch = min(5000, max(50, games // 100))

        def run_batch():
            if state['cancelled']:
                progress.destroy()
                return
            end = min(state['i'] + batch, games)
            
