class GoGame:
    def __init__(self, size=9):
        self.size = size
        self.board = [[None]*size for _ in range(size)]
        self.current_player = 'black'
        self.captured = {'black': 0, 'white': 0}
        self.previous_states = []
        self.passes = 0
        self.ko = None

    def is_valid_move(self, x, y, color):
        if self.board[y][x] is not None or color != self.current_player:
            return False
        
        # Проверка правила ко
        temp_board = [row.copy() for row in self.board]
        temp_board[y][x] = color
        if self.ko and temp_board == self.ko:
            return False
            
        # Проверка самоубийственного хода
        if not self.check_liberty(x, y, temp_board):
            return False
            
        return True

    def check_liberty(self, x, y, board):
        visited = set()
        stack = [(x, y)]
        color = board[y][x]
        
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if board[ny][nx] is None:
                        return True
                    elif board[ny][nx] == color and (nx, ny) not in visited:
                        stack.append((nx, ny))
        return False

    def place_stone(self, x, y, color):
        if not self.is_valid_move(x, y, color):
            return False
            
        self.board[y][x] = color
        self.capture_stones(x, y, color)  # Захват камней
        self.update_ko()
        self.current_player = 'white' if color == 'black' else 'black'
        return True

    def capture_stones(self, x, y, color):
        opponent = 'white' if color == 'black' else 'black'
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if self.board[ny][nx] == opponent:
                    group = self.get_group(nx, ny)
                    if not self.has_liberties(group):
                        self.remove_group(group)
                        self.captured[color] += len(group)

    def get_group(self, x, y):
        color = self.board[y][x]
        visited = set()
        stack = [(x, y)]
        group = []
        
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            group.append((cx, cy))
            
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.board[ny][nx] == color and (nx, ny) not in visited:
                        stack.append((nx, ny))
        return group

    def has_liberties(self, group):
        for (x, y) in group:
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.board[ny][nx] is None:
                        return True
        return False

    def remove_group(self, group):
        for x, y in group:
            self.board[y][x] = None

    def update_ko(self):
        self.ko = [row.copy() for row in self.board]

    def calculate_score(self):
        return {
            'black': self.captured['black'] + 6.5,
            'white': self.captured['white']
        }
    
    def has_valid_moves(self, color):
        """Проверяет наличие допустимых ходов для указанного цвета"""
        if color != self.current_player:
            return False
            
        for y in range(self.size):
            for x in range(self.size):
                if self.is_valid_move(x, y, color):
                    return True
        return False

    def is_game_over(self):
        """Проверяет условия окончания игры"""
        # Если оба игрока не имеют допустимых ходов
        return not self.has_valid_moves('black') and not self.has_valid_moves('white')