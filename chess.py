import pygame
from dataclasses import dataclass

@dataclass(frozen=True)
class Move:
    frm: tuple
    to: tuple
    piece: str
    captured: str | None = None

class Game:
    TILE = 128
    BOARD_SIZE = 8
    SCREEN_SIZE = TILE * BOARD_SIZE

    def __init__(self):
        pygame.display.init()

        self.screen = pygame.display.set_mode((self.SCREEN_SIZE, self.SCREEN_SIZE))
        pygame.display.set_caption("Chess")

        self.playing = True
        self.clock = pygame.time.Clock()
        self.FPS = 30

        self.board = []
        self.dragging = False
        self.dragged_piece = ""
        self.drag_from = None  # (y, x) start square for dragging
        self.legal_moves = []  # list of (y, x)
        self.move_history = []
        self.turn = 1  # 1 = White to move, 0 = Black to move

        self.fen_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

        self.pieces = {
            "p": "black-pawn.png",
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
            "K": "white-king.png",
        }
        self.images = {}
        self.load_piece_images()

        self.run()

    # ----------------------------
    # Core loop
    # ----------------------------
    def run(self):
        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # left button
                        self.on_left_mouse_down()
                    elif event.button == 2:
                        self.undo_move() # middle button
                    elif event.button == 3: # right button
                        self.cancel_drag()

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.on_left_mouse_up()

            self.draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()

    def make_move(self, move):
        fy, fx = move.frm
        ty, tx = move.to

        self.board[fy][fx] = 0
        self.board[ty][tx] = move.piece

        self.move_history.append(move)
        self.turn = 1 - self.turn # switches the turn

    def undo_move(self):
        if not self.move_history:
            return

        move = self.move_history.pop()
        fy, fx = move.frm
        ty, tx = move.to

        self.board[ty][tx] = move.captured if move.captured is not None else 0
        self.board[fy][fx] = move.piece
        self.turn = 1 - self.turn


    def on_left_mouse_down(self):
        pos = pygame.mouse.get_pos()
        sq = self.pixel_to_square(pos)
        if sq is None:
            return

        y, x = sq
        piece = self.board[y][x]
        if piece == 0:
            return

        is_white_piece = piece.isupper()
        if self.turn == 1 and not is_white_piece:
            return
        if self.turn == 0 and is_white_piece:
            return

        self.dragging = True
        self.dragged_piece = piece
        self.drag_from = (y, x)
        self.board[y][x] = 0

        self.legal_moves = self.get_legal_moves(piece, x, y)

    def on_left_mouse_up(self):
        if not self.dragging:
            return

        pos = pygame.mouse.get_pos()
        sq = self.pixel_to_square(pos)

        if sq is None: # out out bounds
            self.snap_back()
            return

        y, x = sq

        if (y, x) in self.legal_moves:
            captured = self.board[y][x] if self.board[y][x] != 0 else None

            move = Move(
                frm=self.drag_from, # (y, x) from where we picked up
                to=(y, x),
                piece=self.dragged_piece,
                captured=captured,
            )

            self.make_move(move)
        else:
            self.snap_back()

        self.dragging = False
        self.dragged_piece = ""
        self.drag_from = None
        self.legal_moves = []


    def cancel_drag(self):
        if self.dragging:
            self.snap_back()
            self.dragging = False
            self.dragged_piece = ""
            self.drag_from = None
            self.legal_moves = []

    def snap_back(self):
        if self.drag_from is None:
            return
        oy, ox = self.drag_from
        self.board[oy][ox] = self.dragged_piece

    # ----------------------------
    # Helpers
    # ----------------------------
    def pixel_to_square(self, pos):
        px, py = pos
        x = px // self.TILE
        y = py // self.TILE
        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            return (y, x)
        return None

    # ----------------------------
    # Board setup
    # ----------------------------
    def fen_to_board(self, fen):
        self.board = []
        rows = fen.split("/")
        for row in rows:
            line = []
            for ch in row:
                if ch.isdigit():
                    line.extend([0] * int(ch))
                else:
                    line.append(ch)
            self.board.append(line)

    def load_piece_images(self):
        self.images = {}
        for piece, filename in self.pieces.items():
            img = pygame.image.load(f"pieces/{filename}").convert_alpha()
            self.images[piece] = pygame.transform.smoothscale(img, (self.TILE, self.TILE))

    # ----------------------------
    # Drawing
    # ----------------------------
    def draw(self):
        for x in range(self.BOARD_SIZE):
            for y in range(self.BOARD_SIZE):
                color = (149, 83, 59) if (x + y) % 2 == 0 else (251, 209, 185)
                pygame.draw.rect(self.screen, color, (x * self.TILE, y * self.TILE, self.TILE, self.TILE))

        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece != 0:
                    self.screen.blit(self.images[piece], (x * self.TILE, y * self.TILE))

        if self.dragging:
            for (my, mx) in self.legal_moves:
                pygame.draw.circle(
                    self.screen,
                    (190, 190, 190),
                    (mx * self.TILE + self.TILE // 2, my * self.TILE + self.TILE // 2),
                    10,
                )

            mx, my = pygame.mouse.get_pos()
            self.screen.blit(self.images[self.dragged_piece], (mx - self.TILE // 2, my - self.TILE // 2))

    # ----------------------------
    # Moves
    # ----------------------------
    def get_legal_moves(self, piece, pos_x, pos_y):
        legal_moves = []

        # White pawn
        if piece == "P":
            one_y = pos_y - 1
            two_y = pos_y - 2

            if 0 <= one_y <= 7 and self.board[one_y][pos_x] == 0:
                legal_moves.append((one_y, pos_x))
                if pos_y == 6 and 0 <= two_y <= 7 and self.board[two_y][pos_x] == 0:
                    legal_moves.append((two_y, pos_x))

            for dx in (-1, 1):
                x = pos_x + dx
                y = pos_y - 1
                if 0 <= x <= 7 and 0 <= y <= 7:
                    target = self.board[y][x]
                    if target != 0 and target.islower():
                        legal_moves.append((y, x))

        # Black pawn
        elif piece == "p":
            one_y = pos_y + 1
            two_y = pos_y + 2

            if 0 <= one_y <= 7 and self.board[one_y][pos_x] == 0:
                legal_moves.append((one_y, pos_x))
                if pos_y == 1 and 0 <= two_y <= 7 and self.board[two_y][pos_x] == 0:
                    legal_moves.append((two_y, pos_x))

            for dx in (-1, 1):
                x = pos_x + dx
                y = pos_y + 1
                if 0 <= x <= 7 and 0 <= y <= 7:
                    target = self.board[y][x]
                    if target != 0 and target.isupper():
                        legal_moves.append((y, x))

        # Bishop / Queen diagonals
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

        # Rook / Queen straight lines
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

        # Knight
        if piece in ["n", "N"]:
            for dx, dy in (
                (-2, -1),
                (-1, -2),
                (1, -2),
                (2, -1),
                (2, 1),
                (1, 2),
                (-1, 2),
                (-2, 1),
            ):
                x = pos_x + dx
                y = pos_y + dy
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if self.board[y][x] == 0 or piece.isupper() != self.board[y][x].isupper():
                        legal_moves.append((y, x))

        # King
        if piece in ["k", "K"]:
            for dx, dy in (
                (-1, -1),
                (0, -1),
                (1, -1),
                (1, 0),
                (1, 1),
                (0, 1),
                (-1, 1),
                (-1, 0),
            ):
                x = pos_x + dx
                y = pos_y + dy
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if self.board[y][x] == 0 or piece.isupper() != self.board[y][x].isupper():
                        legal_moves.append((y, x))

        return legal_moves

    # ----------------------------
    # Attacks
    # ----------------------------
    def get_attacked_squares(self, piece, pos_x, pos_y):
        attacked = []

        # Pawns: attacks are diagonals only
        if piece == "P":
            for dx in (-1, 1):
                x = pos_x + dx
                y = pos_y - 1
                if 0 <= x <= 7 and 0 <= y <= 7:
                    attacked.append((y, x))
            return attacked

        if piece == "p":
            for dx in (-1, 1):
                x = pos_x + dx
                y = pos_y + 1
                if 0 <= x <= 7 and 0 <= y <= 7:
                    attacked.append((y, x))
            return attacked

        return self.get_legal_moves(piece, pos_x, pos_y)

    # returns all attacked squares for a color (color=0 -> black, color=1 -> white)
    def get_all_attacked_squares(self, color):
        attacked_squares = []
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece == 0:
                    continue

                if color == 0 and piece.islower():
                    attacked_squares.extend(self.get_attacked_squares(piece, x, y))
                elif color == 1 and piece.isupper():
                    attacked_squares.extend(self.get_attacked_squares(piece, x, y))

        seen = set()
        unique = []
        for sq in attacked_squares:
            if sq not in seen:
                seen.add(sq)
                unique.append(sq)
        return unique


Game()
