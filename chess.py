import pygame

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1024,1024))
        self.playing = True
        self.clock = pygame.time.Clock()
        self.FPS = 30
        self.board = []
        self.draging = False
        self.draged_piece = ""
        self.legal_moves = []
        self.turn = 1
        self.fen_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.pieces = {"p": "black-pawn.png",
                       "b": "black-bishop.png",
                       "n": "black-knight.png",
                       "r": "black-rook.png",
                       "q": "black-queen.png",
                       "k": "black-king.png",
                       "P": "white-pawn.png",
                       "B": "white-bishop.png",
                       "N": "white-knight.png",
                       "R": "white-rook.png",
                       "Q": "white-queen.png",
                       "K": "white-king.png"}
        pygame.init()

        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    old_mouse_x = pos[0] // 128
                    old_mouse_y = pos[1] // 128
                    if self.board[old_mouse_y][old_mouse_x] != 0 and self.turn == self.board[old_mouse_y][old_mouse_x].isupper():
                        self.draging = True
                        self.draged_piece = self.board[old_mouse_y][old_mouse_x]
                        self.board[old_mouse_y][old_mouse_x] = 0
                        self.legal_moves = self.get_legal_moves(self.draged_piece, pygame.mouse.get_pos()[0] // 128, pygame.mouse.get_pos()[1] // 128)

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.draging:
                        pos = pygame.mouse.get_pos()
                        mouse_x = pos[0] // 128
                        mouse_y = pos[1] // 128

                        if self.legal_moves is not None and (mouse_y, mouse_x) in self.legal_moves:
                            self.board[mouse_y][mouse_x] = self.draged_piece
                            self.turn = 1 - self.turn
                        else:

                            self.board[old_mouse_y][old_mouse_x] = self.draged_piece
                        self.draging = False

            pygame.display.update()
            self.draw()
            self.highlight_attacked_squares()
            self.clock.tick(self.FPS)

    def fen_to_board(self, fen):
        rows = list(fen.split("/"))
        for y, row in enumerate(rows):
            l = []
            for x, character in enumerate(row):
                if character.isdigit():
                    for _ in range(int(character)):
                        l.append(0)
                else:
                    l.append(character)
            self.board.append(l)

    def draw(self):
        # draw board
        for x in range(8):
            for y in range(8):
                color = (149,83,59) if (x + y) % 2 == 0 else (251,209,185)
                pygame.draw.rect(self.screen, color, (x * 128, y * 128, 128, 128))

        # draw figures
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece != 0:
                    image = pygame.image.load(f'pieces/{self.pieces[piece]}').convert_alpha()
                    self.screen.blit(image, (x * 128, y * 128))

        # piece draging logic
        if self.draging:
            if self.legal_moves is not None:
                for move in self.legal_moves:
                    pygame.draw.circle(self.screen, (190, 190, 190), (move[1] * 128 + 64, move[0] * 128 + 64), 10)

            image = pygame.image.load(f'pieces/{self.pieces[self.draged_piece]}').convert_alpha()
            self.screen.blit(image, (pygame.mouse.get_pos()[0] - 64, pygame.mouse.get_pos()[1] - 64))

    def highlight_attacked_squares(self):
        for square in self.get_all_attacked_squares(1):
            pygame.draw.circle(self.screen, (150, 150, 150), (square[1] * 128 + 64, square[0] * 128 + 64), 15)
        

    def get_legal_moves(self, piece, pos_x, pos_y):
        legal_moves = []
        if piece == "P":
            dy = -1
            for dx, dy in ((-1, -1), (0, -1), (1, -1), (0, -2)):
                attacked_square = self.board[pos_y + dy][pos_x + dx]
                if dx != 0 and attacked_square != 0 and attacked_square.isupper():
                    legal_moves.extend((pos_y + dy, pos_x + dx))
                elif dx == 0:
                    if attacked_square == 0:
                    legal_moves.extend((pos_y + dy, pos_x + dx))
                if pos_y == 6 and 

        if piece == "p"
        
        if piece in ["b", "B", "q", "Q"]:
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                x = pos_x + dx
                y = pos_y + dy
                while 0 <= x <= 7 and 0 <= y <= 7:
                    if self.board[y][x] == 0:
                        legal_moves.append((y, x))
                        x += dx
                        y += dy
                    else:
                        if piece.isupper() != self.board[y][x].isupper():
                            legal_moves.append((y, x))
                        break

        if piece in ["r", "R", "q", "Q"]:
            for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                x = pos_x + dx
                y = pos_y + dy
                while 0 <= x <= 7 and 0 <= y <= 7:
                    if self.board[y][x] == 0:
                        legal_moves.append((y, x))
                        x += dx
                        y += dy
                    else:
                        if piece.isupper() != self.board[y][x].isupper():
                            legal_moves.append((y, x))
                        break
        
        if piece in ["n", "N"]:
            for dx, dy in ((-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)):
                x = pos_x + dx
                y = pos_y + dy
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if self.board[y][x] == 0 or piece.isupper() != self.board[y][x].isupper():
                        legal_moves.append((y, x))

        if piece in ["k", "K"]:
            for dx, dy in ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)):
                x = pos_x + dx
                y = pos_y + dy
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if self.board[y][x] == 0 or piece.isupper() != self.board[y][x].isupper():
                        legal_moves.append((y, x))

        if len(legal_moves) > 0:
            return legal_moves
        else:
            return None

    # returns all attacked_squares for a color (color=0 -> black, color=1 -> white)
    def get_all_attacked_squares(self, color):
        attacked_squares = []
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece != 0 and self.get_legal_moves(piece, x, y) is not None:
                    if color == 0:
                        if not piece.isupper():
                            attacked_squares.extend(self.get_legal_moves(piece, x, y))
                    else:
                        if piece.isupper():
                            attacked_squares.extend(self.get_legal_moves(piece, x, y))
        return list(set(attacked_squares))

Game()

