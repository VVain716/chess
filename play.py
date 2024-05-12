from flask import Flask, request
import pygame
import threading
import pieces
import sys
from werkzeug.serving import make_server

app = Flask(__name__)

EMPTY = None
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
BLOCKSIZE = 640 // 8
LIGHT = (233, 215, 182)
DARK = (171, 136, 102)
YELLOW = (255, 218, 112)
RED = (255, 0, 0)
LIGHT_YELLOW = ((255 * 2 + 233) // 3, (218 * 2 + 215) // 3, (112 * 2 + 182) // 3)
DARK_YELLOW = ((255 * 2 + 171) // 3, (218 * 2 + 136) // 3, (112 * 2 + 102) // 3)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


@app.route('/send_text', methods=['POST'])
def receive_text():
    text = request.form['text']
    print("Received Text:", text)
    # Process the text as needed
    return 'Text received successfully!'


def draw_piece(piece):
    rect = piece.img.get_rect()
    rect.center = (piece.y * BLOCKSIZE + BLOCKSIZE // 2, piece.x * BLOCKSIZE + BLOCKSIZE // 2)
    screen.blit(piece.img, rect)


def draw_grid():
    for i in range(0, SCREEN_WIDTH, BLOCKSIZE):
        for j in range(0, SCREEN_HEIGHT, BLOCKSIZE):
            rect = pygame.rect.Rect(i, j, BLOCKSIZE, BLOCKSIZE)
            if ((i + j) // BLOCKSIZE) % 2 == 0:
                pygame.draw.rect(screen, LIGHT, rect)
            else:
                pygame.draw.rect(screen, DARK, rect)


def draw_board(board):
    for i in range(8):
        for j in range(8):
            if board[i][j] is not EMPTY:
                draw_piece(board[i][j])


def show_legal_moves(legal_moves):
    for legal_move in legal_moves:
        rect = pygame.rect.Rect(legal_move[1] * BLOCKSIZE, legal_move[0] * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE)
        pygame.draw.rect(screen, (LIGHT_YELLOW if (legal_move[0] + legal_move[1]) % 2 == 0 else DARK_YELLOW), rect)


def main(server):
    white_player = True
    board_class = pieces.Board()
    piece_clicked = None
    legal_moves = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()  # Cleanly quit Pygame
                server.shutdown()   # Call the function to stop the Flask server
                sys.exit(0)  # Exit the Python interpreter
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                x, y = pos[0] // BLOCKSIZE, pos[1] // BLOCKSIZE
                if legal_moves and (y, x) in legal_moves:
                    if isinstance(board_class.board[piece_clicked[1]][piece_clicked[0]], pieces.King) and \
                            board_class.board[piece_clicked[1]][piece_clicked[0]].is_castle(y, x):
                        board_class.board = pieces.castle(board_class.board, x, y, True)
                    else:
                        board_class.board = pieces.make_move(board_class.board, (x, y),
                                                             (piece_clicked[1], piece_clicked[0]))
                    piece_clicked = None
                    legal_moves = None
                    if white_player:
                        white_player = False
                    else:
                        white_player = True
                elif board_class.board[y][x] is not EMPTY and board_class.board[y][x].white == white_player:
                    piece_clicked = x, y
                    legal_moves = board_class.board[piece_clicked[1]][piece_clicked[0]].get_legal_moves(
                        board_class.board)
                    moves_to_remove = []
                    for move in legal_moves:
                        if not pieces.is_check_resolved(board_class.board, (move[1], move[0]),
                                                        (piece_clicked[1], piece_clicked[0]),
                                                        is_white=white_player):
                            moves_to_remove.append(move)

                    for move in moves_to_remove:
                        legal_moves.remove(move)

        screen.fill('black')
        draw_grid()
        if piece_clicked:
            clicked_rect = pygame.rect.Rect(piece_clicked[0] * BLOCKSIZE, piece_clicked[1] * BLOCKSIZE, BLOCKSIZE,
                                            BLOCKSIZE)
            if (piece_clicked[0] + piece_clicked[1]) % 2 == 0:
                color = LIGHT_YELLOW
            else:
                color = DARK_YELLOW
            pygame.draw.rect(screen, color, clicked_rect)
            show_legal_moves(legal_moves)
        white_king_pos = pieces.get_king_position(board_class.board)
        black_king_pos = pieces.get_king_position(board_class.board, False)
        white_king_in_check = pieces.in_check(board_class.board, white_king_pos[0], white_king_pos[1], True)
        if white_king_in_check:
            rect = pygame.rect.Rect(white_king_pos[1] * BLOCKSIZE, white_king_pos[0] * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE)
            pygame.draw.rect(screen, RED, rect)
        black_king_in_check = pieces.in_check(board_class.board, black_king_pos[0], black_king_pos[1], False)
        if black_king_in_check:
            rect = pygame.rect.Rect(black_king_pos[1] * BLOCKSIZE, black_king_pos[0] * BLOCKSIZE, BLOCKSIZE, BLOCKSIZE)
            pygame.draw.rect(screen, RED, rect)
        if pieces.checkmate(board_class.board, white_king_pos[0], white_king_pos[1], True):
            print("WHITE IS IN CHECKMATE")
        draw_board(board_class.board)
        pygame.display.update()
        pygame.time.Clock().tick(60)


def run_flask():
    server = make_server('0.0.0.0', 4444, app)
    flask_thread = threading.Thread(target=server.serve_forever)
    flask_thread.start()
    main(server)


if __name__ == '__main__':
    run_flask()
