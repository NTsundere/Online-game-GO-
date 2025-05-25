import socket
import threading
from game_logic import GoGame

class GoServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = []
        self.scores = 0
        self.game = GoGame(9)
        self.colors = ['black', 'white']
        print(f"Server listening on {host}:{port}")

    def broadcast(self, message):
        for client in self.clients[:]:
            try:
                client.send(message.encode('utf-8'))
            except:
                self.clients.remove(client)
                client.close()

    def handle_client(self, client):
        color = self.colors.pop(0) if self.colors else 'observer'
        try:
            client.send(f'COLOR {color}'.encode('utf-8'))
        except:
            self.clients.remove(client)
            client.close()
            return

        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    break
                if message.startswith('MOVE'):
                    x, y = map(int, message.split()[1:3])
                    if self.game.place_stone(x, y, color):
                        self.broadcast(f'UPDATE {x} {y} {color}')
                        scores = self.game.calculate_score()
                        self.broadcast(f'SCORE {scores["black"]} {scores["white"]}')
                        
                        # Проверка на окончание игры
                        if self.game.is_game_over():
                            self.end_game()
                            
                elif message == 'PASS':
                    self.game.passes += 1
                    if self.game.passes >= 2 or self.game.is_game_over():
                        self.end_game()
                    else:
                        self.game.current_player = 'white' if self.game.current_player == 'black' else 'black'
                        self.broadcast(f'TURN {self.game.current_player}')
                        scores = self.game.calculate_score()
                        self.broadcast(f'SCORE {scores["black"]} {scores["white"]}')                  
            except:
                break

        self.clients.remove(client)
        client.close()
    def end_game(self):
        """Обработка окончания игры"""
        scores = self.game.calculate_score()
        self.broadcast(f'GAME_OVER {scores["black"]} {scores["white"]}')
        # Сброс состояния игры
        self.game = GoGame(9)
        self.passes = 0
        self.colors = ['black', 'white']
        print("New game started")
        
    def run(self):
        while True:
            client, addr = self.server.accept()
            print(f"Connected with {addr}")
            self.clients.append(client)
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = GoServer()
    server.run()