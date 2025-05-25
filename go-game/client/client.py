import socket
import threading
from gui import GoGUI

class GoClient:
    def __init__(self, server_ip='127.0.0.1', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_ip, port))
        self.gui = GoGUI(self)
        self.color = None
        self.current_turn = 'black'  # Initialize current_turn
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()
        self.running = True
        self.gui.run()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message.startswith('TURN'):
                    self.current_turn = message.split()[1]
                    # Исправлено: передаем текущий счет (по умолчанию 0:0)
                    self.gui.update_info(self.current_turn, {'black': 0, 'white': 0})
                elif message.startswith('COLOR'):
                    self.color = message.split()[1]
                    self.gui.update_info(self.color, {'black': 0, 'white': 0})
                elif message.startswith('UPDATE'):
                    x, y, color = message.split()[1:]
                    self.gui.update_board(int(x), int(y), color)
                    self.current_turn = 'white' if color == 'black' else 'black'
                    # Добавляем передачу счета при обновлении доски
                    self.gui.update_info(self.current_turn, {'black': 0, 'white': 0})
                elif message.startswith('PASS'):
                    color = message.split()[1]
                    self.current_turn = 'white' if color == 'black' else 'black'
                    self.gui.update_info(self.current_turn, {})  # Обновить текущего игрока
                elif message.startswith('SCORE'):
                    black, white = message.split()[1:]
                    self.gui.update_info(self.current_turn, {'black': black, 'white': white})
                elif message.startswith('GAME_OVER'):
                    _, black_score, white_score = message.split()
                    self.gui.show_game_over({
                        'black': float(black_score),
                        'white': float(white_score)
                    })
            except ConnectionAbortedError:
                self.gui.show_error("Connection lost")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

    def send_move(self, x, y):
        if self.color and self.running:
            try:
                self.client.send(f'MOVE {x} {y}'.encode('utf-8'))
            except Exception as e:
                print("Send failed:", e)
                self.running = False
                self.client.close()

    def send_pass(self):
        if self.color:
            self.client.send('PASS'.encode('utf-8'))
    
if __name__ == "__main__":
    client = GoClient()