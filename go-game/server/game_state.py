class GameState:
    def __init__(self, size):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.current_player = 'black'

    def make_move(self, x, y, color):
        if color != self.current_player:
            return False
        if self.board[y][x] is None:
            self.board[y][x] = color
            self.capture_stones(x, y, color)
            self.current_player = 'white' if color == 'black' else 'black'
            return True
        return False
    
    def place_stone(self, x, y, color):
        if not self.is_valid_move(x, y, color):
            return False
            
        self.board[y][x] = color
        self.capture_stones(x, y, color)  
        self.update_ko()
        self.current_player = 'white' if color == 'black' else 'black'
        return True