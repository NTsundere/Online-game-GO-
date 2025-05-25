import tkinter as tk
from tkinter import messagebox

class GoGUI:
    def __init__(self, client, board_size=9):
        self.client = client
        self.board_size = board_size
        self.cell_size = 40
        self.stone_radius = self.cell_size // 2 - 2
        
        self.window = tk.Tk()
        self.window.title("Go Game")
        
        # Основной холст
        self.canvas = tk.Canvas(self.window, 
                              width=self.cell_size*(board_size+1),
                              height=self.cell_size*(board_size+1),
                              bg='#DEB887')
        self.canvas.pack(pady=20)
        
        # Панель информации
        self.info_frame = tk.Frame(self.window)
        self.info_frame.pack(fill=tk.X, padx=20)
        
        self.current_player_label = tk.Label(
            self.info_frame, 
            text="Current Player: Black",
            font=('Helvetica', 12, 'bold'))
        self.current_player_label.pack(side=tk.LEFT)
        
        self.score_label = tk.Label(
            self.info_frame,
            text="Black: 0 | White: 0",
            font=('Helvetica', 12)
        )
        self.score_label.pack(side=tk.RIGHT)
        
        # Кнопки управления
        self.control_frame = tk.Frame(self.window)
        self.control_frame.pack(pady=10)
        
        self.pass_button = tk.Button(
            self.control_frame,
            text="Pass Turn",
            command=self.pass_turn,
            bg='#4CAF50',
            fg='white'
        )
        self.pass_button.pack(side=tk.LEFT, padx=5)
        
        # Инициализация доски
        self.draw_board()
        self.preview_stone = None
        self.canvas.bind("<Motion>", self.show_preview)
        self.canvas.bind("<Leave>", self.hide_preview)
        self.canvas.bind("<Button-1>", self.handle_click)
        
        self.rules_button = tk.Button(
            self.control_frame,
            text="Правила",
            command=self.show_rules,
            bg='#2196F3',
            fg='white'
        )
        self.rules_button.pack(side=tk.LEFT, padx=5)

    def show_rules(self):
        rules_window = tk.Toplevel(self.window)
        rules_window.title("Правила игры Го")
        
        rules_text = """Основные правила Го:
1. Играют два игрока черными и белыми камнями
2. Камни ставятся на пересечения линий
3. Камни не могут быть перемещены после установки
4. Камни захватываются, когда теряют все свободы
5. Игрок может пасовать, пропуская ход
6. Игра заканчивается при двух последовательных пасах
7. Побеждает игрок с большей территорией + захваченные камни"""
        
        rules_label = tk.Label(rules_window, text=rules_text, justify=tk.LEFT, padx=20, pady=20)
        rules_label.pack()

    def draw_board(self):
        # Отрисовка линий
        for i in range(self.board_size):
            x = self.cell_size * (i + 1)
            self.canvas.create_line(
                x, self.cell_size, 
                x, self.cell_size*self.board_size,
                width=2, fill='black'
            )
            self.canvas.create_line(
                self.cell_size, x,
                self.cell_size*self.board_size, x,
                width=2, fill='black'
            )
            
        # Звездные точки
        star_points = [(2,2), (2,6), (6,2), (6,6), (4,4)]
        for x, y in star_points:
            center_x = (x + 1) * self.cell_size
            center_y = (y + 1) * self.cell_size
            self.canvas.create_oval(
                center_x - 3, center_y - 3,
                center_x + 3, center_y + 3,
                fill='black'
            )
            
    def show_preview(self, event):
        if self.client.color != self.client.current_turn:
            return

        x, y = self.get_grid_coords(event)
        if x is not None:
            # Удаляем предыдущий предварительный камень, если он существует
            if self.preview_stone:
                self.canvas.delete(self.preview_stone)
        
            # Отрисовка нового предварительного камня
            color = '#888888' if self.client.color == 'black' else '#DDDDDD'
            self.preview_stone = self.draw_stone(x, y, color)
            
    def hide_preview(self, event):
        if self.preview_stone:
            self.canvas.delete(self.preview_stone)
            self.preview_stone = None
                
    def handle_click(self, event):
        try:
            x, y = self.get_grid_coords(event)
            if x is not None:
                self.client.send_move(x, y)
        except Exception as e:
            self.show_error(str(e))
            
    def get_grid_coords(self, event):
        grid_x = round((event.x - self.cell_size)/self.cell_size)
        grid_y = round((event.y - self.cell_size)/self.cell_size)
        if 0 <= grid_x < self.board_size and 0 <= grid_y < self.board_size:
            return (grid_x, grid_y)
        return (None, None)
        
    def draw_stone(self, x, y, color):
        x_pixel = (x + 1) * self.cell_size
        y_pixel = (y + 1) * self.cell_size
        return self.canvas.create_oval(
            x_pixel - self.stone_radius,
            y_pixel - self.stone_radius,
            x_pixel + self.stone_radius,
            y_pixel + self.stone_radius,
            fill=color,
            outline='black' if color != 'white' else '#666666'
        )
        
    def update_board(self, x, y, color):
        stone_color = 'black' if color == 'black' else 'white'
        self.draw_stone(x, y, stone_color)
        
    def update_info(self, current_player, scores):
        """Обновляет информацию о текущем игроке и счете"""
        # Обновляем счет
        score_text = f"Black: {scores.get('black', 0)} | White: {scores.get('white', 0)}"
        self.score_label.config(text=score_text)
        
        # Обновляем текущего игрока
        if current_player:
            player_text = f"Current Player: {current_player.capitalize()}"
            self.current_player_label.config(text=player_text)
        
    def pass_turn(self):
        self.client.send_pass()
        
    def run(self):
        self.window.mainloop()

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_game_over(self, scores):
        # Убираем предыдущее окно если есть
        if hasattr(self, 'game_over_window'):
            self.game_over_window.destroy()
            
        self.game_over_window = tk.Toplevel(self.window)
        self.game_over_window.title("Игра окончена!")
        
        winner = 'Black' if scores['black'] > scores['white'] else 'White'
        result_text = (
            f"Победитель: {winner}\n\n"
            f"Очки Black: {scores['black']}\n"
            f"Очки White: {scores['white']}"
        )
        
        label = tk.Label(self.game_over_window, text=result_text, padx=20, pady=20)
        label.pack()
        
        new_game_button = tk.Button(
            self.game_over_window,
            text="Новая игра",
            command=self.restart_game,
            bg='#4CAF50',
            fg='white'
        )
        new_game_button.pack(pady=10)

    def restart_game(self):
        """Обработчик кнопки новой игры"""
        self.game_over_window.destroy()