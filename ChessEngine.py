import pygame as p
from Board import Board
from ChessAi import ChessAi
from Move import Move
from Piece import Piece
from multiprocessing import Process, Queue

p.init()
BOARD_WIDTH = BOARD_HEIGHT = 400
#MOVE_LOG_PANEL_WIDTH = 250
#MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
undoEnabled = True


def loadImages():
    pieces = ["bB", "bK", "bN", "bp", "bQ", "bR",
              "wB", "wK", "wN", "wp", "wQ", "wR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def drawEndGameText(screen, text: str):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation.move(1, 1))

def main():
    board = Board()
    #screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    screen = p.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    loadImages()
    running = True
    gameOver = False

    validMoves = board.currentValidMoves
    moveMade = False

    squareSelected = ()  # at start, no square selected
    playerClicks = []  # list of squares

    playerOne = False # true if white player is human
    playerTwo = False # true if black player is human

    aiDepth = 3
    aiThinking = False # true if ai is still thinking

    moveFinderProcess = None
    shouldDrawGameState = True

    chessAiWhite = ChessAi(aiDepth, board)  # add your chess engine here for white
    chessAiBlack = ChessAi(aiDepth, board)  # add your chess engine here for black


    #moveLogFont = p.font.SysFont("Arial", 12, False, False)

    drawGameState(screen, board, playerClicks)
    while running:
        humanTurn = ((board.whiteToPlay and playerOne) or (not board.whiteToPlay and playerTwo))
        #time.sleep(0.5)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN: #mouse handler
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) values
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if squareSelected == (row, col) or col >= 8: # same space, deselect
                        squareSelected = ()
                        playerClicks = []
                        #drawGameState(screen, board, playerClicks)
                        shouldDrawGameState = True
                        board.alreadyDrawnValidMoves = False
                    else:
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                        drawGameState(screen, board, playerClicks)
                        if len(playerClicks) == 1:
                            startPiece = board.getPiece(playerClicks[0][0], playerClicks[0][1])
                            if startPiece == 0:  # if 1st click was on empty square
                                playerClicks = []
                                squareSelected = ()
                                shouldDrawGameState = True
                                #drawGameState(screen, board, playerClicks)
                                board.alreadyDrawnValidMoves = False
                        elif len(playerClicks) == 2 : #2nd click
                            move = Move(playerClicks[0], playerClicks[1], board)
                            if humanTurn and move.isPawnPromotion:
                                color = Piece.getPieceColor(move.pieceStart)

                                pieceNameMap = {"Q": Piece.QUEEN, "R": Piece.ROOK, "B": Piece.BISHOP,
                                                'K': Piece.KNIGHT}

                                promotedPiece = Piece.NO_PIECE
                                correctPiece = False
                                while correctPiece is False:
                                    promotedPieceName = input(
                                        "Promote to Q, R, B, or K (type the letter to select which piece)")
                                    try:
                                        promotedPiece = pieceNameMap[promotedPieceName]
                                        correctPiece = True
                                    except KeyError as error:
                                        correctPiece = False

                                newPiece = color | promotedPiece
                                move.promotePiece = newPiece

                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    board.makeMove(validMoves[i])
                                    print(validMoves[i])
                                    moveMade = True
                                    shouldDrawGameState = True
                                    #drawGameState(screen, board, playerClicks)

                            squareSelected = ()
                            playerClicks = []
                            board.alreadyDrawnValidMoves = False
                            shouldDrawGameState = True
                            #drawGameState(screen, board, playerClicks)


            elif e.type == p.KEYDOWN and undoEnabled is True:
                if e.key == p.K_LEFT and not aiThinking: # left arrow, to undo move
                    if not playerOne or not playerTwo:
                        board.undoMove() #undoing 1 extra time if computer is present

                    board.undoMove()
                    moveMade = True
                    gameOver = False
                    shouldDrawGameState = True
                if e.key == p.K_r and not aiThinking: # r, to restart board
                    board = Board()
                    validMoves = board.currentValidMoves
                    moveMade = False
                    gameOver = False
                    playerClicks = []
                    squareSelected = ()
                    chessAiWhite.board = board
                    chessAiBlack.board = board
                    shouldDrawGameState = True

        # AI move logic
        if not gameOver and not humanTurn:
            if not aiThinking:
                if board.whiteToPlay:
                    aiThinking = True
                    returnQueue = Queue()  # used to share data between threads
                    validMovesCopy = validMoves[:]
                    moveFinderProcess = Process(target=chessAiWhite.getBestMove, args=(validMovesCopy, board.whiteToPlay, returnQueue))
                    moveFinderProcess.start()

                else:
                    aiThinking = True
                    returnQueue = Queue() # used to share data between threads
                    validMovesCopy = validMoves[:]
                    moveFinderProcess = Process(target= chessAiBlack.getBestMove, args=(validMovesCopy, board.whiteToPlay, returnQueue))
                    moveFinderProcess.start()


            if not moveFinderProcess.is_alive():
                if not returnQueue.empty():
                    aiMove = returnQueue.get()
                if aiMove is not None:
                    if aiMove not in validMovesCopy:
                        aiMove = validMovesCopy[0]
                else:
                    aiMove = board.currentValidMoves[0]

                board.makeMove(aiMove)
                print(aiMove)
                moveMade = True
                shouldDrawGameState = True
                #drawGameState(screen, board, playerClicks)
                aiThinking = False

        if shouldDrawGameState:
            shouldDrawGameState = False
            drawGameState(screen, board, playerClicks)

        if moveMade:
            validMoves = board.currentValidMoves
            moveMade = False
            if len(validMoves) == 0 and board.inCheck:
                if board.whiteToPlay:
                    drawEndGameText(screen, "Checkmate, black wins.")
                    gameOver = True
                else:
                    drawEndGameText(screen, "Checkmate, white wins.")
                    gameOver = True
            elif len(validMoves) == 0 and not board.inCheck:
                drawEndGameText(screen, "Stalemate")
                gameOver = True

        clock.tick(MAX_FPS)
        p.display.flip()


def drawSquares(screen):
    colors = [p.Color("white"), p.Color("gray")]  # order here matters
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[(i + j) % 2]
            p.draw.rect(screen, color, p.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawSelectedSquare(screen, playerClicks, board):
    if len(playerClicks) == 1:
        click = playerClicks[0]

        i = click[0]
        j = click[1]
        piece = board.getPiece(i, j)

        if piece != -1 and ((Piece.isPieceWhite(piece) and board.whiteToPlay) or ((Piece.isPieceBlack(piece) and not board.whiteToPlay))):
            color = p.Color(255,255,0)
            p.draw.rect(screen, color, p.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawLegalMovesOfSelectedPiece(screen, playerClicks, board):
    if len(playerClicks) == 1 and board.alreadyDrawnValidMoves is False:
        click = playerClicks[0]

        i = click[0]
        j = click[1]
        piece = board.getPiece(i, j)
        if piece != -1 and ((Piece.isPieceWhite(piece) and board.whiteToPlay) or ((Piece.isPieceBlack(piece) and not board.whiteToPlay))):
            board.alreadyDrawnValidMoves = True
            validMoves = board.currentValidMoves
            for move in validMoves:

                if move.startRow == i and move.startColumn == j:
                    endPiece = move.pieceEnd

                    if endPiece == Piece.NO_PIECE: # filling empty squares
                        color2 = p.Color(30, 70, 90, 20)
                        p.draw.circle(screen,color2, (move.endColumn * SQUARE_SIZE + SQUARE_SIZE/2 , move.endRow * SQUARE_SIZE + SQUARE_SIZE/2), SQUARE_SIZE/8)
                    elif (Piece.isPieceWhite(piece) and Piece.isPieceBlack(endPiece)) or (Piece.isPieceBlack(piece) and Piece.isPieceWhite(endPiece)): # filling captures
                        color3 = p.Color(20, 20, 20, 200)
                        p.draw.circle(screen,color3, (move.endColumn * SQUARE_SIZE + SQUARE_SIZE/2 + 1, move.endRow * SQUARE_SIZE + SQUARE_SIZE/2), SQUARE_SIZE/2, 2)



def drawPieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board.squares[i * DIMENSION + j]
            if piece > 0:
                pieceName = Piece.getPieceImageName(piece)
                screen.blit(IMAGES[pieceName], p.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawGameState(screen, board: Board, playerClicks):
    drawSquares(screen)
    drawHighlightedLastMove(screen, board)
    drawSelectedSquare(screen, playerClicks, board)
    drawPieces(screen, board)
    drawLegalMovesOfSelectedPiece(screen, playerClicks, board)


def drawHighlightedLastMove(screen , board: Board):
    if not board.currentLastMove is None:
        color = p.Color(253, 230, 179)
        p.draw.rect(screen, color, p.Rect(board.currentLastMove[1] * SQUARE_SIZE, board.currentLastMove[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))  # highlight start move
        p.draw.rect(screen, color,p.Rect(board.currentLastMove[3] * SQUARE_SIZE, board.currentLastMove[2] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))  # highlight end move


if __name__ == "__main__":
    main()
