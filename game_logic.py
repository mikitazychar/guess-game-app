import random
import sqlite3
from datetime import datetime


class GuessGameLogic:
    def __init__(self):
        self.secret_number = 0
        self.attempts_left = 0
        self.difficulty_multiplier = 1
        self._setup_db()

    def _setup_db(self):
        with sqlite3.connect('scores.db') as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS scores
                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date TEXT, score INTEGER, difficulty TEXT)''')

    def start_new_game(self, max_range, attempts):
        self.secret_number = random.randint(1, max_range)
        self.attempts_left = attempts
        self.difficulty_multiplier = 10 if max_range > 10 else 1
        return f"Угадай число от 1 до {max_range}"

    def check_guess(self, guess):
        self.attempts_left -= 1
        if guess == self.secret_number:
            score = (self.attempts_left + 1) * self.difficulty_multiplier
            return "win", score
        if self.attempts_left <= 0:
            return "lose", f"ПРОИГРЫШ\nЭто было {self.secret_number}"

        hint = "Больше" if guess < self.secret_number else "Меньше"
        return "continue", f"{hint}!\nПопыток: {self.attempts_left}"

    def save_score(self, score, diff_name):
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        with sqlite3.connect('scores.db') as conn:
            conn.execute('INSERT INTO scores (date, score, difficulty) VALUES (?, ?, ?)',
                         (date_str, score, diff_name))

    def get_top_scores(self):
        with sqlite3.connect('scores.db') as conn:
            cursor = conn.execute('SELECT date, score, difficulty FROM scores ORDER BY score DESC LIMIT 5')
            return cursor.fetchall()
