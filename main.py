import sys
import sqlite3
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QGridLayout, QWidget,
    QMessageBox, QVBoxLayout, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QComboBox
)
from PyQt6.QtCore import QSize, Qt


class TicTacToeApp(QMainWindow):
    def __init__(self):
        """
        Инициализирует главное окно приложения, устанавливает соединение с базами данных
        создает необходимые таблицы и открывает главное меню
        """
        super().__init__()
        self.setStyleSheet("background-image:url(\"background_2.png\"); background-position: center;")
        self.setWindowTitle("Крестики-нолики")
        self.setFixedSize(QSize(400, 500))
        self.username = None
        self.user_id = None
        self.ai_difficulty = 'medium'
        try:
            self.conn = sqlite3.connect("leaderboard.db")
            self.conn2 = sqlite3.connect("player_stats.db")
            self.create_tables()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "База данных", f"Ошибка подключения к базе данных: {e}")
            sys.exit(1)
        self.main_menu()

    def create_tables(self):
        """
        Создает таблицы в базах данных, если они не существуют
        В player_stats.db создается таблица users
        В leaderboard.db создается таблица stats
        """
        try:
            with self.conn2:
                self.conn2.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                    )
                """)
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        wins INTEGER DEFAULT 0,
                        losses INTEGER DEFAULT 0
                    )
                """)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "База данных", f"Ошибка создания таблиц: {e}")
            sys.exit(1)

    def main_menu(self):
        """
        Отображает главное меню приложения
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        title = QLabel("Крестики-нолики")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")

        register_button = QPushButton("Регистрация")
        register_button.setStyleSheet("font-size: 18px; padding: 10px; background: rgb(0, 191, 255); color: rgb(255, 255, 255);")
        register_button.clicked.connect(self.register_user)

        login_button = QPushButton("Авторизация")
        login_button.setStyleSheet("font-size: 18px; padding: 10px; background: rgb(0, 191, 255); color: rgb(255, 255, 255);")
        login_button.clicked.connect(self.login_user)

        play_with_friend_button = QPushButton("Играть с другом")
        play_with_friend_button.setStyleSheet("font-size: 18px; padding: 10px; background: rgb(0, 191, 255); color: rgb(255, 255, 255);")
        play_with_friend_button.clicked.connect(lambda: self.start_game("friend"))

        play_with_ai_button = QPushButton("Играть с ИИ")
        play_with_ai_button.setStyleSheet("font-size: 18px; padding: 10px; background: rgb(0, 191, 255); color: rgb(255, 255, 255);")
        play_with_ai_button.clicked.connect(self.select_difficulty)

        leaderboard_button = QPushButton("Таблица лидеров")
        leaderboard_button.setStyleSheet("font-size: 18px; padding: 10px; background: rgb(0, 191, 255); color: rgb(255, 255, 255);")
        leaderboard_button.clicked.connect(self.show_leaderboard)

        layout.addWidget(title)
        layout.addWidget(register_button)
        layout.addWidget(login_button)
        layout.addWidget(play_with_friend_button)
        layout.addWidget(play_with_ai_button)
        layout.addWidget(leaderboard_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_widget.setLayout(layout)

    def select_difficulty(self):
        """
        Отображает окно выбора сложности ИИ и порядка хода перед началом игры с ИИ
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        title = QLabel("Настройки игры с ИИ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")

        difficulty_label = QLabel("Выберите сложность ИИ")
        difficulty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        difficulty_label.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Лёгкий", "Средний", "Сложный"])
        self.difficulty_combo.setStyleSheet("font-size: 14px; padding: 5px;")

        order_label = QLabel("Кто ходит первым?")
        order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        order_label.setStyleSheet("font-size: 16px; margin-top: 15px; margin-bottom: 5px;")
        self.order_combo = QComboBox()
        self.order_combo.addItems(["Игрок", "ИИ"])
        self.order_combo.setStyleSheet("font-size: 14px; padding: 5px;")

        start_button = QPushButton("Начать игру с ИИ")
        start_button.setStyleSheet("font-size: 16px; padding: 10px;")
        start_button.clicked.connect(self.set_difficulty_and_start)

        back_button = QPushButton("Назад")
        back_button.setStyleSheet("font-size: 16px; padding: 10px;")
        back_button.clicked.connect(self.main_menu)

        layout.addWidget(title)
        layout.addWidget(difficulty_label)
        layout.addWidget(self.difficulty_combo)
        layout.addWidget(order_label)
        layout.addWidget(self.order_combo)
        layout.addWidget(start_button)
        layout.addWidget(back_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_widget.setLayout(layout)

    def set_difficulty_and_start(self):
        """
        Устанавливает выбранную сложность ИИ и порядок хода, зтем начинает игру
        """
        difficulty_text = self.difficulty_combo.currentText()
        order_text = self.order_combo.currentText()

        if difficulty_text == "Лёгкий":
            self.ai_difficulty = "easy"
        elif difficulty_text == "Средний":
            self.ai_difficulty = "medium"
        else:
            self.ai_difficulty = "hard"

        if order_text == "Игрок":
            mode = "ai_second"
        else:
            mode = "ai_first"

        self.start_game(mode)

    def register_user(self):
        """
        Отображает окно регистрации нового пользователя
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        title = QLabel("Регистрация")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; margin-bottom: 10px;")

        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText("Имя пользователя")
        self.reg_username_input.setStyleSheet("font-size: 16px; padding: 5px;")

        self.reg_password_input = QLineEdit()
        self.reg_password_input.setPlaceholderText("Пароль")
        self.reg_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password_input.setStyleSheet("font-size: 16px; padding: 5px;")

        submit_button = QPushButton("Зарегистрироваться")
        submit_button.setStyleSheet("font-size: 18px; padding: 10px;")
        submit_button.clicked.connect(self.save_new_user)

        back_button = QPushButton("Назад")
        back_button.setStyleSheet("font-size: 18px; padding: 10px;")
        back_button.clicked.connect(self.main_menu)

        layout.addWidget(title)
        layout.addWidget(self.reg_username_input)
        layout.addWidget(self.reg_password_input)
        layout.addWidget(submit_button)
        layout.addWidget(back_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_widget.setLayout(layout)

    def save_new_user(self):
        """
        Сохраняет нового пользователя в базу данных, проверяя уникальность имени пользователя
        """
        username = self.reg_username_input.text().strip()
        password = self.reg_password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя и пароль не могут быть пустыми.")
            return

        try:
            with self.conn2:
                result = self.conn2.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
                if result:
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует.")
                    return
                else:
                    self.conn2.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    user_id = self.conn2.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()[0]

            with self.conn:
                self.conn.execute("INSERT INTO stats (user_id, wins, losses) VALUES (?, 0, 0)", (user_id,))

            QMessageBox.information(self, "Успех", f"Пользователь {username} успешно зарегистрирован!")
            self.username = username
            self.user_id = user_id

            try:
                with open("player_data.txt", "a", encoding="utf-8") as f:
                    f.write(f"Username: {username}, Password: {password}\n")
            except Exception as e:
                QMessageBox.warning(self, "Файл", f"Не удалось записать данные в файл: {e}")

            self.main_menu()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "База данных", f"Ошибка при регистрации пользователя: {e}")

    def login_user(self):
        """
        Отображает окно авторизации пользователя
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        title = QLabel("Авторизация")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; margin-bottom: 10px;")

        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText("Имя пользователя")
        self.login_username_input.setStyleSheet("font-size: 16px; padding: 5px;")

        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText("Пароль")
        self.login_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password_input.setStyleSheet("font-size: 16px; padding: 5px;")

        submit_button = QPushButton("Войти")
        submit_button.setStyleSheet("font-size: 18px; padding: 10px;")
        submit_button.clicked.connect(self.check_credentials)

        back_button = QPushButton("Назад")
        back_button.setStyleSheet("font-size: 18px; padding: 10px;")
        back_button.clicked.connect(self.main_menu)

        layout.addWidget(title)
        layout.addWidget(self.login_username_input)
        layout.addWidget(self.login_password_input)
        layout.addWidget(submit_button)
        layout.addWidget(back_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_widget.setLayout(layout)

    def check_credentials(self):
        """
        Проверяет введенные учетные данные пользователя в базе данных
        При успешной авторизации сохраняет данные о пользователе и возвращается в главное меню
        """
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя и пароль не могут быть пустыми.")
            return

        try:
            with self.conn2:
                result = self.conn2.execute("SELECT id, username FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
                if result:
                    self.user_id = result[0]
                    self.username = result[1]
                    QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
                    self.main_menu()
                else:
                    QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "База данных", f"Ошибка при проверке учетных данных: {e}")

    def start_game(self, mode):
        """
        Запускает игровое поле. Если пользователь не авторизован, выдает предупреждение
        """
        if not self.username:
            QMessageBox.warning(self, "Ошибка", "Сначала авторизуйтесь или зарегистрируйтесь, прежде чем играть.")
            return
        self.game_window = TicTacToe(self, mode, self.username, self.user_id, self.ai_difficulty)
        self.setCentralWidget(self.game_window)

    def show_leaderboard(self):
        """
        Отображает таблицу лидеров, получая данные о победах и поражениях из базы данных
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        title = QLabel("Таблица лидеров")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")

        leaderboard_table = QTableWidget()
        leaderboard_table.setColumnCount(3)
        leaderboard_table.setHorizontalHeaderLabels(["Имя пользователя", "Победы", "Поражения"])
        leaderboard_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        leaderboard_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        leaderboard_table.horizontalHeader().setStretchLastSection(True)
        leaderboard_table.verticalHeader().setVisible(False)

        try:
            with self.conn:
                stats_data = self.conn.execute("SELECT user_id, wins, losses FROM stats ORDER BY wins DESC").fetchall()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "База данных", f"Ошибка при получении данных таблицы лидеров: {e}")
            stats_data = []

        leaderboard = []
        try:
            with self.conn2:
                for row in stats_data:
                    user_id, wins, losses = row
                    user_row = self.conn2.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
                    if user_row:
                        username = user_row[0]
                        leaderboard.append((username, wins, losses))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "База данных", f"Ошибка при получении данных пользователей: {e}")

        leaderboard_table.setRowCount(len(leaderboard))
        for i, (username, wins, losses) in enumerate(leaderboard):
            leaderboard_table.setItem(i, 0, QTableWidgetItem(str(username)))
            leaderboard_table.setItem(i, 1, QTableWidgetItem(str(wins)))
            leaderboard_table.setItem(i, 2, QTableWidgetItem(str(losses)))

        back_button = QPushButton("Назад")
        back_button.setStyleSheet("font-size: 18px; padding: 10px;")
        back_button.clicked.connect(self.main_menu)

        layout.addWidget(title)
        layout.addWidget(leaderboard_table)
        layout.addWidget(back_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_widget.setLayout(layout)


class TicTacToe(QWidget):
    def __init__(self, parent, mode, username, user_id, ai_difficulty):
        """
        Инициализирует игровое поле, задает текущего игрока, созжает кнопки для поля,
        определяет режим игры
        """
        super().__init__()
        self.parent = parent
        self.mode = mode
        self.username = username
        self.user_id = user_id
        self.ai_difficulty = ai_difficulty
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                button = QPushButton("")
                button.setFixedSize(100, 100)
                button.setStyleSheet("font-size: 24px;")
                button.clicked.connect(lambda x, r=row, c=col: self.make_move(r, c))
                self.layout.addWidget(button, row, col)
                self.buttons[row][col] = button

        back_button = QPushButton("Назад")
        back_button.setStyleSheet("font-size: 18px; padding: 10px;")
        back_button.clicked.connect(self.parent.main_menu)
        self.layout.addWidget(back_button, 3, 0, 1, 3)

        if self.mode == "ai_first":
            self.current_player = "O"
            self.ai_move()

    def make_move(self, row, col):
        """
        Обрабатывает ход текущего игрока, обновляет поле, проверяет победу или ничью
        Если игра продолжается и следующий ход ИИ, делает ход ИИ
        """
        if self.board[row][col] == "":
            self.board[row][col] = self.current_player
            self.buttons[row][col].setText(self.current_player)

            if self.check_winner(self.current_player):
                if self.current_player == "X":
                    QMessageBox.information(self, "Игра завершена", f"Игрок {self.current_player} победил!")
                else:
                    QMessageBox.information(self, "Игра завершена", f"ИИ ({self.current_player}) победил!")
                self.update_leaderboard(self.current_player)
                self.reset_game()
                return

            if self.check_draw():
                QMessageBox.information(self, "Игра завершена", "Ничья!")
                self.reset_game()
                return

            self.current_player = "O" if self.current_player == "X" else "X"

            if self.mode.startswith("ai") and self.current_player == "O":
                self.ai_move()

    def ai_move(self):
        """
        Определяет ход ИИ в зависимости от выбранной сложности
        """
        if self.ai_difficulty == 'easy':
            self.ai_move_easy()
        elif self.ai_difficulty == 'medium':
            self.ai_move_medium()
        elif self.ai_difficulty == 'hard':
            self.ai_move_hard()

    def ai_move_easy(self):
        """
        Ход ИИ на легком уровне — выбирает случайную пустую клетку
        """
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty_cells:
            row, col = random.choice(empty_cells)
            self.board[row][col] = "O"
            self.buttons[row][col].setText("O")
            if self.check_winner("O"):
                QMessageBox.information(self, "Игра завершена", "ИИ победил!")
                self.update_leaderboard("O")
                self.reset_game()
                return
            if self.check_draw():
                QMessageBox.information(self, "Игра завершена", "Ничья!")
                self.reset_game()
                return
            self.current_player = "X"

    def ai_move_medium(self):
        """
        Ход ИИ на среднем уровне — пытается выиграть или помешать игроку выиграть
        Если нет очевидного хода, выбирает случайную пустую клетку
        """
        for player in ["O", "X"]:
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == "":
                        self.board[row][col] = player
                        if self.check_winner(player):
                            if player == "O":
                                self.buttons[row][col].setText("O")
                                QMessageBox.information(self, "Игра завершена", "ИИ победил!")
                                self.update_leaderboard("O")
                                self.reset_game()
                                return
                            else:
                                self.board[row][col] = "O"
                                self.buttons[row][col].setText("O")
                                if self.check_winner("O"):
                                    QMessageBox.information(self, "Игра завершена", "ИИ победил!")
                                    self.update_leaderboard("O")
                                    self.reset_game()
                                    return
                                if self.check_draw():
                                    QMessageBox.information(self, "Игра завершена", "Ничья!")
                                    self.reset_game()
                                    return
                                self.current_player = "X"
                                return
                        self.board[row][col] = ""

        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty_cells:
            row, col = random.choice(empty_cells)
            self.board[row][col] = "O"
            self.buttons[row][col].setText("O")
            if self.check_winner("O"):
                QMessageBox.information(self, "Игра завершена", "ИИ победил!")
                self.update_leaderboard("O")
                self.reset_game()
                return
            if self.check_draw():
                QMessageBox.information(self, "Игра завершена", "Ничья!")
                self.reset_game()
                return
            self.current_player = "X"

    def ai_move_hard(self):
        """
        Ход ИИ на сложном уровне — использует алгоритм минимакс для выбора оптимального хода
        """
        best_score = -float('inf')
        best_move = None
        if self.board == [["", "", ""],
                          ["", "", ""],
                          ["", "", ""]]:
            best_move = (1, 1)
        else:
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == "":
                        self.board[r][c] = "O"
                        score = self.get_best_move(False, 0)
                        self.board[r][c] = ""
                        if score > best_score:
                            best_score = score
                            best_move = (r, c)

        if best_move is not None:
            r, c = best_move
            self.board[r][c] = "O"
            self.buttons[r][c].setText("O")

            if self.check_winner("O"):
                QMessageBox.information(self, "Игра завершена", "ИИ победил!")
                self.update_leaderboard("O")
                self.reset_game()
                return

            if self.check_draw():
                QMessageBox.information(self, "Игра завершена", "Ничья!")
                self.reset_game()
                return

            self.current_player = "X"

    def get_best_move(self, is_maximizing, depth):
        """
        Рекурсивный метод для оценки хода на сложном уровн
        """
        if self.check_winner("O"):
            return 10 - depth
        if self.check_winner("X"):
            return -10 + depth
        if self.check_draw():
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == "":
                        self.board[r][c] = "O"
                        score = self.get_best_move(False, depth + 1)
                        self.board[r][c] = ""
                        best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == "":
                        self.board[r][c] = "X"
                        score = self.get_best_move(True, depth + 1)
                        self.board[r][c] = ""
                        best_score = min(best_score, score)
            return best_score

    def check_winner(self, player):
        """
        Проверяет, достиг ли игрок победы
        Возвращает True, если есть победа, иначе False
        """
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)) or \
               all(self.board[j][i] == player for j in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)) or \
           all(self.board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def check_draw(self):
        """
        Проверяет, остались ли пустые клетки
        Если пустых клеток нет и нет победителя, возвращает True, иначе False
        """
        return all(self.board[row][col] != "" for row in range(3) for col in range(3))

    def update_leaderboard(self, winner):
        """
        Обновляет статистику побед и поражений в таблице лидеров для текущего пользователя
        """
        try:
            with self.parent.conn:
                stats = self.parent.conn.execute("SELECT wins, losses FROM stats WHERE user_id = ?", (self.user_id,)).fetchone()
                if not stats:
                    self.parent.conn.execute("INSERT INTO stats (user_id, wins, losses) VALUES (?, 0, 0)", (self.user_id,))
                    stats = (0, 0)
                wins, losses = stats

                if self.mode.startswith("ai") and self.ai_difficulty == 'hard':
                    if winner == "X":
                        wins += 1
                    elif winner == "O":
                        losses += 1
                    self.parent.conn.execute("UPDATE stats SET wins = ?, losses = ? WHERE user_id = ?", (wins, losses, self.user_id))
        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "База данных", f"Ошибка при обновлении статистики: {e}")

    def reset_game(self):
        """
        Сбрасывает состояние игры, очщает поле. Если ИИ должен ходить первым, делает первый ход
        """
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].setText("")

        if self.mode == "ai_first":
            self.current_player = "O"
            self.ai_move()
        else:
            self.current_player = "X"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicTacToeApp()
    window.show()
    sys.exit(app.exec())