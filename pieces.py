import pygame
import copy
pygame.init()


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

    return new_board


def is_check_resolved(board: list[list], future_pos: tuple, curr_pos: tuple, is_white: bool) -> bool:
    # Make a copy of the board
    new_board = make_move(board, future_pos, curr_pos)

    # Get the position of the king
    king_x, king_y = get_king_position(new_board, is_white)

    # Check if the king is still in check
    return not in_check(new_board, king_x, king_y, is_white)


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
                if type(piece) is Pawn:
                    legal_moves = piece.get_legal_moves(board, check_king=True)
                else:
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

    def get_legal_moves(self, board, check_king=False):
        legal_moves = []
        if self.white:
            white_king = get_king_position(board)
            if self.x > 0 and board[self.x - 1][self.y] is None:
                legal_moves.append((self.x - 1, self.y))
            if self.x == 6 and board[self.x - 2][self.y] is None and board[self.x - 1][self.y] is None:
                legal_moves.append((self.x - 2, self.y))
            if check_king or self.x > 0 and self.y > 0 and board[self.x - 1][self.y - 1] is not None and board[self.x - 1][self.y - 1].white != self.white:
                legal_moves.append((self.x - 1, self.y - 1))
            if check_king or self.x > 0 and self.y < 7 and board[self.x - 1][self.y + 1] is not None and board[self.x - 1][self.y + 1].white != self.white:
                legal_moves.append((self.x - 1, self.y + 1))
        else:
            if self.x < 7 and board[self.x + 1][self.y] is None:
                legal_moves.append((self.x + 1, self.y))
            if self.x == 1 and board[self.x + 2][self.y] is None and board[self.x + 1][self.y] is None:
                legal_moves.append((self.x + 2, self.y))
            if check_king or self.x < 7 and self.y > 0 and board[self.x + 1][self.y - 1] is not None and board[self.x + 1][self.y - 1].white != self.white:
                legal_moves.append((self.x + 1, self.y - 1))
            if check_king or self.x < 7 and self.y < 7 and board[self.x + 1][self.y + 1] is not None and board[self.x + 1][self.y + 1].white != self.white:
                legal_moves.append((self.x + 1, self.y + 1))

        return legal_moves


class Rook:
    def __init__(self, x, y, white=True):
        self.x = x
        self.y = y
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
                        tmp = board[self.x][self.y]
                        board[self.x][self.y] = None
                        if not in_check(board, self.x + i, self.y + j, self.white):
                            legal_moves.append((self.x + i, self.y + j))
                        board[self.x][self.y] = tmp
        return legal_moves


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