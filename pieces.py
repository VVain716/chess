import pygame
import copy

pygame.init()


def promote_pawn(board, x, y, is_white):
    board[x][y] = Queen(x, y, is_white)

    return board


def castle(board, x, y, is_white):
    if (x, y) == (6, 7):
        board = make_move(board, (6, 7), (7, 4))
        board = make_move(board, (5, 7), (7, 7))
    elif (x, y) == (2, 7):
        board = make_move(board, (2, 7), (7, 4))
        board = make_move(board, (3, 7), (0, 7))
    elif (x, y) == (6, 0):
        board = make_move(board, (6, 0), (0, 4))
        board = make_move(board, (5, 0), (0, 7))
    else:
        board = make_move(board, (2, 0), (0, 4))
        board = make_move(board, (3, 0), (0, 0))

    return board


def make_move(board: list[list], future_pos: tuple, curr_pos: tuple):
    new_board = [row[:] for row in board]  # Shallow copy of the board

    x, y = future_pos
    b, a = curr_pos
    # Create a new instance of the piece at the future position
    new_board[y][x] = type(board[b][a])(x, y, board[b][a].white)

    # Set the position of the new piece
    new_board[y][x].x = y
    new_board[y][x].y = x
    # Remove the piece from its current position
    new_board[b][a] = None
    if isinstance(new_board[y][x], Pawn) and (y == 0 or y == 7):
        # Perform pawn promotion
        new_board = promote_pawn(new_board, y, x, new_board[y][x].white)

    # Check if the piece is a king or a rook and update has_moved accordingly
    if isinstance(new_board[y][x], King):
        new_board[y][x].has_moved = True
    elif isinstance(new_board[y][x], Rook):
        new_board[y][x].has_moved = True

    return new_board



def is_check_resolved(board: list[list], future_pos: tuple, curr_pos: tuple, is_white: bool) -> bool:
    # Make a copy of the board
    new_board = make_move(board, future_pos, curr_pos)
    # Get the position of the king
    king_x, king_y = get_king_position(new_board, is_white)
    # Check if the king is still in check
    return not in_check(new_board, king_x, king_y, is_white)


def print_board(board: list[list]):
    for row in board:
        for item in row:
            print(type(item), end=' ')
        print()


def get_king_position(board: list[list], is_white=True):
    for i in range(8):
        for j in range(8):
            if type(board[i][j]) is King and board[i][j].white == is_white:
                return i, j


def in_check(board, king_x, king_y, is_white):
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece and piece.white != is_white and type(piece) is not King:
                legal_moves = piece.get_legal_moves(board)
                if (king_x, king_y) in legal_moves:
                    return True

    return False


def checkmate(board, king_x, king_y, is_white):
    if not in_check(board, king_x, king_y, is_white):
        return False

    if len(board[king_x][king_y].get_legal_moves(board)) != 0:
        return False

    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece and piece.white == is_white:
                legal_moves = piece.get_legal_moves(board)
                for move in legal_moves:
                    temp_board = [row[:] for row in board]
                    temp_board[i][j], temp_board[move[0]][move[1]] = temp_board[move[0]][move[1]], temp_board[i][j]
                    if not in_check(temp_board, king_x, king_y, is_white):
                        return False
    return True


class Pawn:
    def __init__(self, x, y, white=True):
        self.x = x
        self.y = y
        self.clicked = False
        self.white = white
        if white:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/white-pawn.png'), (80, 80))
        else:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/black-pawn.png'), (80, 80))

    def get_legal_moves(self, board):
        legal_moves = []
        if self.white:
            white_king = get_king_position(board)
            if self.x > 0 and board[self.x - 1][self.y] is None:
                legal_moves.append((self.x - 1, self.y))
            if self.x == 6 and board[self.x - 2][self.y] is None and board[self.x - 1][self.y] is None:
                legal_moves.append((self.x - 2, self.y))
            if self.x > 0 and self.y > 0 and board[self.x - 1][self.y - 1] is not None and board[self.x - 1][
                self.y - 1].white != self.white:
                legal_moves.append((self.x - 1, self.y - 1))
            if self.x > 0 and self.y < 7 and board[self.x - 1][self.y + 1] is not None and board[self.x - 1][
                self.y + 1].white != self.white:
                legal_moves.append((self.x - 1, self.y + 1))
        else:
            if self.x < 7 and board[self.x + 1][self.y] is None:
                legal_moves.append((self.x + 1, self.y))
            if self.x == 1 and board[self.x + 2][self.y] is None and board[self.x + 1][self.y] is None:
                legal_moves.append((self.x + 2, self.y))
            if self.x < 7 and self.y > 0 and board[self.x + 1][self.y - 1] is not None and board[self.x + 1][
                self.y - 1].white != self.white:
                legal_moves.append((self.x + 1, self.y - 1))
            if self.x < 7 and self.y < 7 and board[self.x + 1][self.y + 1] is not None and board[self.x + 1][
                self.y + 1].white != self.white:
                legal_moves.append((self.x + 1, self.y + 1))

        return legal_moves


class Rook:
    def __init__(self, x, y, white=True):
        self.x = x
        self.y = y
        self.has_moved = False
        self.clicked = False
        self.white = white
        if white:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/white-rook.png'), (80, 80))
        else:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/black-rook.png'), (80, 80))

    def get_legal_moves(self, board):
        legal_moves = []
        # Horizontal movement
        for i in range(self.x - 1, -1, -1):
            if board[i][self.y] is not None:
                if board[i][self.y].white != self.white:
                    legal_moves.append((i, self.y))
                break
            legal_moves.append((i, self.y))
        for i in range(self.x + 1, 8):
            if board[i][self.y] is not None:
                if board[i][self.y].white != self.white:
                    legal_moves.append((i, self.y))
                break
            legal_moves.append((i, self.y))
        # Vertical movement
        for j in range(self.y - 1, -1, -1):
            if board[self.x][j] is not None:
                if board[self.x][j].white != self.white:
                    legal_moves.append((self.x, j))
                break
            legal_moves.append((self.x, j))
        for j in range(self.y + 1, 8):
            if board[self.x][j] is not None:
                if board[self.x][j].white != self.white:
                    legal_moves.append((self.x, j))
                break
            legal_moves.append((self.x, j))
        return legal_moves


class Queen:
    def __init__(self, x, y, white=True):
        self.x = x
        self.y = y
        self.clicked = False
        self.white = white
        if white:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/white-queen.png'), (80, 80))
        else:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/black-queen.png'), (80, 80))

    def get_legal_moves(self, board):
        legal_moves = []
        # Horizontal movement
        for i in range(self.x - 1, -1, -1):
            if board[i][self.y] is not None:
                if board[i][self.y].white != self.white:
                    legal_moves.append((i, self.y))
                break
            legal_moves.append((i, self.y))
        for i in range(self.x + 1, 8):
            if board[i][self.y] is not None:
                if board[i][self.y].white != self.white:
                    legal_moves.append((i, self.y))
                break
            legal_moves.append((i, self.y))
        # Vertical movement
        for j in range(self.y - 1, -1, -1):
            if board[self.x][j] is not None:
                if board[self.x][j].white != self.white:
                    legal_moves.append((self.x, j))
                break
            legal_moves.append((self.x, j))
        for j in range(self.y + 1, 8):
            if board[self.x][j] is not None:
                if board[self.x][j].white != self.white:
                    legal_moves.append((self.x, j))
                break
            legal_moves.append((self.x, j))
        # Diagonal movement
        for i in range(1, 8):
            if 0 <= self.x - i < 8 and 0 <= self.y - i < 8:
                if board[self.x - i][self.y - i] is not None:
                    if board[self.x - i][self.y - i].white != self.white:
                        legal_moves.append((self.x - i, self.y - i))
                    break
                legal_moves.append((self.x - i, self.y - i))
        for i in range(1, 8):
            if 0 <= self.x + i < 8 and 0 <= self.y - i < 8:
                if board[self.x + i][self.y - i] is not None:
                    if board[self.x + i][self.y - i].white != self.white:
                        legal_moves.append((self.x + i, self.y - i))
                    break
                legal_moves.append((self.x + i, self.y - i))
        for i in range(1, 8):
            if 0 <= self.x - i < 8 and 0 <= self.y + i < 8:
                if board[self.x - i][self.y + i] is not None:
                    if board[self.x - i][self.y + i].white != self.white:
                        legal_moves.append((self.x - i, self.y + i))
                    break
                legal_moves.append((self.x - i, self.y + i))
        for i in range(1, 8):
            if 0 <= self.x + i < 8 and 0 <= self.y + i < 8:
                if board[self.x + i][self.y + i] is not None:
                    if board[self.x + i][self.y + i].white != self.white:
                        legal_moves.append((self.x + i, self.y + i))
                    break
                legal_moves.append((self.x + i, self.y + i))
        return legal_moves


class King:
    def __init__(self, x, y, white=True):
        self.x = x
        self.y = y
        self.clicked = False
        self.has_moved = False
        self.white = white
        if white:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/white-king.png'), (80, 80))
        else:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/black-king.png'), (80, 80))

    def get_legal_moves(self, board):
        legal_moves = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if 0 <= self.x + i < 8 and 0 <= self.y + j < 8:
                    if board[self.x + i][self.y + j] is None or board[self.x + i][self.y + j].white != self.white:
                        tmp_board = make_move(board, (self.x + i, self.y + j), (self.x, self.y))
                        if not in_check(tmp_board, self.x + i, self.y + j, self.white):
                            legal_moves.append((self.x + i, self.y + j))

        #Check for castling

        if not self.has_moved:
            if self.white:
                if board[7][5] is None and board[7][6] is None and type(board[7][7]) is Rook:
                    legal_moves.append((7, 6))
                if board[7][3] is None and board[7][2] is None and board[7][1] is None and type(board[7][0]) is Rook:
                    legal_moves.append((7, 2))
            else:
                if board[0][5] is None and board[0][6] is None and type(board[0][7]) is Rook:
                    legal_moves.append((0, 6))
                if board[0][3] is None and board[0][2] is None and board[0][1] is None and type(board[0][0]) is Rook:
                    legal_moves.append((0, 2))

        return legal_moves

    def is_castle(self, future_x, future_y):
        if self.has_moved:
            return False

        if future_x == 7 and future_y == 6:  # Castling kingside
            return True
        elif future_x == 7 and future_y == 2:  # Castling queenside
            return True
        elif future_x == 0 and future_y == 6:  # Castling kingside (black)
            return True
        elif future_x == 0 and future_y == 2:  # Castling queenside (black)
            return True

        return False

class Bishop:
    def __init__(self, x, y, white=True):
        self.x = x
        self.y = y
        self.clicked = False
        self.white = white
        if white:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/white-bishop.png'), (80, 80))
        else:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/black-bishop.png'), (80, 80))

    def get_legal_moves(self, board):
        legal_moves = []
        # Diagonal movement
        # Top-left diagonal
        for i in range(1, min(self.x, self.y) + 1):
            if board[self.x - i][self.y - i] is None:
                legal_moves.append((self.x - i, self.y - i))
            elif board[self.x - i][self.y - i].white != self.white:
                legal_moves.append((self.x - i, self.y - i))
                break
            else:
                break
        # Top-right diagonal
        for i in range(1, min(self.x, 7 - self.y) + 1):
            if board[self.x - i][self.y + i] is None:
                legal_moves.append((self.x - i, self.y + i))
            elif board[self.x - i][self.y + i].white != self.white:
                legal_moves.append((self.x - i, self.y + i))
                break
            else:
                break
        # Bottom-left diagonal
        for i in range(1, min(7 - self.x, self.y) + 1):
            if board[self.x + i][self.y - i] is None:
                legal_moves.append((self.x + i, self.y - i))
            elif board[self.x + i][self.y - i].white != self.white:
                legal_moves.append((self.x + i, self.y - i))
                break
            else:
                break
        # Bottom-right diagonal
        for i in range(1, min(7 - self.x, 7 - self.y) + 1):
            if board[self.x + i][self.y + i] is None:
                legal_moves.append((self.x + i, self.y + i))
            elif board[self.x + i][self.y + i].white != self.white:
                legal_moves.append((self.x + i, self.y + i))
                break
            else:
                break
        return legal_moves


class Knight:
    def __init__(self, x, y, white=True):
        self.x = x
        self.y = y
        self.clicked = False
        self.white = white
        if white:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/white-knight.png'), (80, 80))
        else:
            self.img = pygame.transform.smoothscale(pygame.image.load('pieces-basic-png/black-knight.png'), (80, 80))

    def get_legal_moves(self, board):
        legal_moves = []
        # Knight movement pattern
        moves = [
            (self.x - 1, self.y - 2), (self.x + 1, self.y - 2),
            (self.x - 2, self.y - 1), (self.x + 2, self.y - 1),
            (self.x - 2, self.y + 1), (self.x + 2, self.y + 1),
            (self.x - 1, self.y + 2), (self.x + 1, self.y + 2)
        ]
        # Filter out moves outside the board
        for x, y in moves:
            if 0 <= x < 8 and 0 <= y < 8:
                if board[x][y] is None or board[x][y].white != self.white:
                    legal_moves.append((x, y))
        return legal_moves


class Board:
    def __init__(self):
        self.board = [
            [Rook(0, 0, False), Knight(0, 1, False), Bishop(0, 2, False), Queen(0, 3, False), King(0, 4, False),
             Bishop(0, 5, False), Knight(0, 6, False), Rook(0, 7, False)],
            [Pawn(1, 0, False), Pawn(1, 1, False), Pawn(1, 2, False), Pawn(1, 3, False), Pawn(1, 4, False),
             Pawn(1, 5, False), Pawn(1, 6, False), Pawn(1, 7, False)],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [Pawn(6, 0, True), Pawn(6, 1, True), Pawn(6, 2, True), Pawn(6, 3, True), Pawn(6, 4, True), Pawn(6, 5, True),
             Pawn(6, 6, True), Pawn(6, 7, True)],
            [Rook(7, 0, True), Knight(7, 1, True), Bishop(7, 2, True), Queen(7, 3, True), King(7, 4, True),
             Bishop(7, 5, True), Knight(7, 6, True), Rook(7, 7, True)]
        ]
