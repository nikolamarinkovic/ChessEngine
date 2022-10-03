import random
import time
from multiprocessing import Queue
import chess.pgn
import numpy as np
from chess import square_file, square_rank
import time

from AiOpponent import AiOpponent
from Board import Board
from Move import Move
from Piece import Piece

NUMBER_OF_FILES_IN_OPENING_DATABASE = 1


class ChessAi(AiOpponent):

    CHECKMATE = 1000
    STALEMATE = 0

    nextMoveMinimax = None
    nextMoveNegamax = None
    nextMoveNegamaxAlphaBeta = None

    POSITIONAL_WEIGHT = 0.01
    DOUBLE_PAWN_WEIGHT = 0.02
    ISOLATED_PAWN_WEIGHT = 0.05
    MOBILITY_WEIGHT = 0.25


    whitePawnMap = [[90, 90, 90,  90,  90,  90,  90, 90],
                    [50, 50, 50,  50,  50,  50,  50, 50],
                    [10, 10, 20,  30,  30,  20,  10, 10],
                    [5,  5,  10,  25,  25,  10,  5,  5],
                    [0,  0,  0,   20,  20,  0,   0,  0],
                    [5,  -5, -10, 10,  10,  -10, -5, 5],
                    [0,  10, 10,  -20, -20, 10,  10, 0],
                    [0,  0,  0,   0,   0,   0,   0,  0]]


    blackPawnMap = []
    i = 7
    while i >= 0:
        blackPawnMap.append(whitePawnMap[i])
        i -= 1

    knightMap = [[-50, -40, -30, -30, -30, -30, -40, -50],
                 [-40, -20, 0,   15,  15,   0,  -20, -40],
                 [-30, 5,   30,  10,  10,  30,  0,   -30],
                 [-30, 0,   15,  40,  40,  15,  5,   -30],
                 [-30, 0,   15,  40,  40,  15,  0,   -30],
                 [-30, 5,   30,  10,  10,  30,  5,   -30],
                 [-40, -20, 0,   15,  15,   0,  -20, -40],
                 [-50, -40, -30, -30, -30, -30, -40, -50]]

    whiteBishopMap =[[-20, -10, -10, -10, -10, -10, -10, -20],
                     [-10, 0,   0,   0,   0,   0,   0,   -10],
                     [-10, 0,   0,   0,   0,   5,   0,   -10],
                     [-10, 20,  5,   10,  10,  5,   20,  -10],
                     [-10, 0,   15,  10,  10,  15,  0,   -10],
                     [-10, 20,  20,  5,   5,   20,  20,  -10],
                     [-10, 15,   0,   0,   0,   0,  15,   -10],
                     [-20, -10, -10, -10, -10, -10, -10, -20]]

    blackBishopMap = []
    i = 7
    while i >= 0:
        blackBishopMap.append(whiteBishopMap[i])
        i -= 1

    whiteRookMap = [[0, 0, 0, 0, 0, 0, 0, 0],
                    [5, 10, 10, 10, 10, 10, 10, 5],
                    [-5, 0, 0, 0, 0, 0, 0, -5],
                    [-5, 0, 0, 0, 0, 0, 0, -5],
                    [-5, 0, 0, 0, 0, 0, 0, -5],
                    [-5, 0, 0, 0, 0, 0, 0, -5],
                    [-5, 0, 0, 0, 0, 0, 0, -5],
                    [0, 0, 0, 5, 5, 0, 0, 0]]

    blackRookMap = []
    i = 7
    while i >= 0:
        blackRookMap.append(whiteRookMap[i])
        i -= 1


    queenMap = [[-20, -10, -10, -5, -5, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 5, 5, 5, 0, -10],
                [-5, 0, 5, 5, 5, 5, 0, -5],
                [0, 0, 5, 5, 5, 5, 0, -5],
                [-10, 5, 5, 5, 5, 5, 0, -10],
                [-10, 0, 5, 0, 0, 0, 0, -10],
                [-20, -10, -10, -5, -5, -10, -10, -20]]

    whiteKingMap = [[-30, -40, -40, -50, -50, -40, -40, -30],
                    [-30, -40, -40, -50, -50, -40, -40, -30],
                    [-30, -40, -40, -50, -50, -40, -40, -30],
                    [-30, -40, -40, -50, -50, -40, -40, -30],
                    [-20, -30, -30, -40, -40, -30, -30, -20],
                    [-10, -20, -20, -20, -20, -20, -20, -10],
                    [10,  10,  0,   0,   0,   0,   10,  10],
                    [30,  50,  40,  0,   0,   20,  50,  40]]

    blackKingMap = []
    i = 7
    while i >= 0:
        blackKingMap.append(whiteKingMap[i])
        i -= 1

    piecePositionScores = {Piece.PAWN | Piece.WHITE: whitePawnMap,
                           Piece.PAWN | Piece.BLACK: blackPawnMap,
                           Piece.KNIGHT: knightMap,
                           Piece.BISHOP | Piece.WHITE: whiteBishopMap,
                           Piece.BISHOP | Piece.BLACK: blackBishopMap,
                           Piece.ROOK | Piece.WHITE: whiteRookMap,
                           Piece.ROOK | Piece.BLACK: blackRookMap,
                           Piece.QUEEN: queenMap,
                           Piece.KING | Piece.WHITE: whiteKingMap,
                           Piece.KING | Piece.BLACK: blackKingMap}




    def __init__(self, depth: int, board: Board):
        self.depth = depth
        self.board = board

        self.openingBook = self.initOpeningBook()

        self.cnt = 0


    def getRandomMove(self, moves):
        return moves[random.randint(0, len(moves) - 1)]


    def getBestMoveFirstTry(self, moves):
        if self.board.whiteToPlay:
            maxScore = ChessAi.CHECKMATE
            bestMove = None
            for playerMove in moves:
                self.board.makeMove()
                opponentMoves = self.board.currentValidMoves
                for opponentMove in opponentMoves:
                    self.board.makeMove(opponentMove)
                    score = -self.getEvaluation()
                    if score > maxScore:
                        maxScore = score
                        bestMove = playerMove
                    self.board.undoMove()
                self.board.undoMove()
            return bestMove

        else:
            maxScore = ChessAi.CHECKMATE
            bestMove = None
            for playerMove in moves:
                self.board.makeMove(playerMove)
                score = self.getEvaluation()
                #print(score)
                self.board.undoMove()
                if score < maxScore:
                    maxScore = score
                    bestMove = playerMove
            return bestMove


    def getBestMoveMinMax(self, moves, maxDepth, whiteToMove):
        self.nextMove = None
        self.getMoveMinMax(moves, whiteToMove, maxDepth, maxDepth)
        return self.nextMove

    def getMoveMinMax(self, moves,  whiteToMove: bool, maxDepth: int, currDepth: int):
        if currDepth == 0:
            return self.getEvaluation()

        if whiteToMove:
            maxScore = -ChessAi.CHECKMATE
            for move in moves:
                self.board.makeMove(move)
                nextMoves = self.board.currentValidMoves
                score = self.getMoveMinMax(nextMoves, False, maxDepth, currDepth-1)
                if score > maxScore:
                    maxScore = score
                    if currDepth == maxDepth:
                        self.nextMoveMinimax = move

                self.board.undoMove()
            return maxScore
        else:
            minScore = ChessAi.CHECKMATE
            for move in moves:
                self.board.makeMove(move)
                nextMoves = self.board.currentValidMoves
                score = self.getMoveMinMax(nextMoves, True, maxDepth, currDepth - 1)
                if score < minScore:
                    minScore = score
                    if currDepth == maxDepth:
                        self.nextMoveMinimax = move
                self.board.undoMove()
            return minScore


    def getBestMoveNegaMax(self, moves, maxDepth: int, whiteToPlay: bool, returnQue: Queue):

        if self.board.numberOfMovesPlayed <= 9:
            moveFromOpeningBook = self.getMoveFromOpeningBook(moves, whiteToPlay, returnQue)
            #print(moveFromOpeningBook)
            if moveFromOpeningBook is not None:
                time.sleep(random.randint(1, 5) / 5)
                returnQue.put(moveFromOpeningBook)
                return
            else:
                self.nextMoveNegamaxAlphaBeta = None
                mult = 1 if whiteToPlay else -1
                self.cnt = 0
                start = time.time()
                self.getMoveNegaMax(moves, mult, maxDepth, maxDepth)
                end = time.time()
                print(self.cnt)
                elapsed = end - start
                print("Time elapsed:" + str(elapsed))


                returnQue.put(self.nextMoveNegamax)
        else:

            self.nextMoveNegamax = None
            mult = 1 if whiteToPlay else -1
            self.cnt = 0
            start = time.time()
            self.getMoveNegaMax(moves, mult, maxDepth, maxDepth )
            end = time.time()
            print(self.cnt)
            elapsed = end - start
            print("Time elapsed:" + str(elapsed))

            returnQue.put(self.nextMoveNegamax)


    def getMoveNegaMax(self, moves,  turnMultiplier: int, maxDepth: int, currDepth: int):
        self.cnt += 1

        if currDepth == 0:
            return turnMultiplier * self.getEvaluation()

        maxScore = -ChessAi.CHECKMATE
        for move in moves:
            self.board.makeMove(move)
            nextMoves = self.board.currentValidMoves
            score = -self.getMoveNegaMax(nextMoves, -turnMultiplier, maxDepth, currDepth - 1)
            if score > maxScore:
                maxScore = score
                if currDepth == maxDepth:
                    self.nextMoveNegamax = move

            self.board.undoMove()
        return maxScore



    def getBestMoveNegaMaxAlphaBeta(self, moves, maxDepth: int, whiteToPlay: bool, returnQue: Queue):
        if self.board.numberOfMovesPlayed <= 9:
            moveFromOpeningBook = self.getMoveFromOpeningBook(moves, whiteToPlay, returnQue)
            #print(moveFromOpeningBook)
            if moveFromOpeningBook is not None:
                time.sleep(random.randint(1, 5) / 5)
                returnQue.put(moveFromOpeningBook)
                return
            else:
                self.nextMoveNegamaxAlphaBeta = None
                mult = 1 if whiteToPlay else -1
                self.cnt = 0
                start = time.time()
                self.getMoveNegaMaxAlphaBeta(moves, mult, maxDepth, maxDepth, -ChessAi.CHECKMATE, ChessAi.CHECKMATE)
                end = time.time()
                print(self.cnt)
                elapsed = end - start
                print("Time elapsed:" + str(elapsed))
                returnQue.put(self.nextMoveNegamaxAlphaBeta)
        else:

            self.nextMoveNegamaxAlphaBeta = None
            mult = 1 if whiteToPlay else -1
            self.cnt = 0
            start = time.time()
            self.getMoveNegaMaxAlphaBeta(moves, mult, maxDepth, maxDepth, -ChessAi.CHECKMATE, ChessAi.CHECKMATE)
            end = time.time()
            print(self.cnt)
            elapsed = end - start
            print("Time elapsed:" + str(elapsed))
            returnQue.put(self.nextMoveNegamaxAlphaBeta)

    def getMoveNegaMaxAlphaBeta(self, moves,  turnMultiplier: int, maxDepth: int, currDepth: int, alpha:float, beta: float):
        self.cnt += 1

        if currDepth == 0:
            return turnMultiplier * self.getEvaluation()

        #orderedMoves = moves
        orderedMoves = self.orderMoves(moves)

        maxScore = -ChessAi.CHECKMATE
        for move in orderedMoves:
            self.board.makeMove(move)
            nextMoves = self.board.currentValidMoves
            score = -self.getMoveNegaMaxAlphaBeta(nextMoves, -turnMultiplier, maxDepth, currDepth - 1, -beta, -alpha)
            if score > maxScore:
                maxScore = score
                if currDepth == maxDepth:
                    self.nextMoveNegamaxAlphaBeta = move

            self.board.undoMove()

            # pruning
            if maxScore > alpha:
                alpha = maxScore
            if alpha >= beta:
                break

        return maxScore

    # overriding interface method
    def getBestMove(self, validMoves, whiteToPlay, returnQueue):
        self.getBestMoveNegaMaxAlphaBeta(validMoves, self.depth, whiteToPlay, returnQueue)

    def getEvaluation(self):
        # game evaluation
        validMoves = self.board.currentValidMoves
        if len(validMoves) == 0 and self.board.inCheck:
            return ChessAi.CHECKMATE
        elif len(validMoves) == 0 and self.board.inCheck:
            return ChessAi.STALEMATE

        # material and positional evaluation
        s = 0
        for i in range(8):
            for j in range(8):
                piece = self.board.getPiece(i , j)

                if piece != Piece.NO_PIECE and piece != Piece.INVALID:
                    #score positionaly

                    piecePositionScore = self.getPiecePositionScore(piece, i , j)

                    s += Piece.getPieceValue(piece) + piecePositionScore * ChessAi.POSITIONAL_WEIGHT


        whitePawnsInFiles, blackPawnsInFiles = self.initPawnsInFilesArray()


        # number of isolated pawns
        isolatedPawnsWhite = self.getNumOfIsolatedPawnsFromArray(whitePawnsInFiles)
        isolatedPawnsBlack = self.getNumOfIsolatedPawnsFromArray(blackPawnsInFiles)

        # number of doubled pawns
        doubledPawnsWhite = self.getNumOfDoubledPawnsFromArray(whitePawnsInFiles)
        doubledPawnsBlack = self.getNumOfDoubledPawnsFromArray(blackPawnsInFiles)

        s = s + (isolatedPawnsBlack - isolatedPawnsWhite) * ChessAi.ISOLATED_PAWN_WEIGHT - (doubledPawnsBlack - doubledPawnsWhite) * ChessAi.DOUBLE_PAWN_WEIGHT


        #s += self.getLegalMoveNumberDifference() * ChessAi.MOBILITY_WEIGHT




        return s


    def getPiecePositionScore(self, piece, i, j) -> int:
        piecePositionScore = 0
        if Piece.isPiecePawn(piece):
            if Piece.isPieceWhite(piece):
                color = Piece.WHITE
            else:
                color = Piece.BLACK

            piecePositionScore = ChessAi.piecePositionScores[Piece.PAWN | color][i][j]

        elif Piece.isPieceKnight(piece):
            piecePositionScore = ChessAi.piecePositionScores[Piece.KNIGHT][i][j]

        elif Piece.isPieceBishop(piece):
            if Piece.isPieceWhite(piece):
                color = Piece.WHITE
            else:
                color = Piece.BLACK

            piecePositionScore = ChessAi.piecePositionScores[Piece.BISHOP | color][i][j]

        elif Piece.isPieceRook(piece):
            if Piece.isPieceWhite(piece):
                color = Piece.WHITE
            else:
                color = Piece.BLACK

            piecePositionScore = ChessAi.piecePositionScores[Piece.ROOK | color][i][j]

        elif Piece.isPieceQueen(piece):
            piecePositionScore = ChessAi.piecePositionScores[Piece.QUEEN][i][j]

        else:  # king
            if Piece.isPieceWhite(piece):
                color = Piece.WHITE
            else:
                color = Piece.BLACK

            piecePositionScore = ChessAi.piecePositionScores[Piece.KING | color][i][j]

        if not Piece.isPieceWhite(piece):  # if black we invert bonus to be negative
            piecePositionScore = - piecePositionScore


        return piecePositionScore


    def initOpeningBook(self):
        openingFile = open("masterGames.txt", "r")

        openingBook = []
        for line in openingFile.readlines():
            openingBook.append(line.split())

        openingFile.close()

        return openingBook

    def getMoveFromOpeningBook(self, moves, whiteToPlay, returnQue):

        index = len(self.board.chessNotationMoveHistoryLog)
        lines = self.getAllGamesWithStartingMovesAtCurrentPosition()

        movesStr = [str(move) for move in moves]
        random.shuffle(lines)
        for line in lines:
            move = line[index]
            if move in movesStr:
                return moves[movesStr.index(move)]

        return None


    # based on board move history, find all lines in opening databook that start that way
    def getAllGamesWithStartingMovesAtCurrentPosition(self):
        ret = []

        gameLog = self.board.chessNotationMoveHistoryLog

        if len(gameLog) == 0:
            return self.openingBook


        for line in self.openingBook:
            i = 0
            followingMoves = True
            while i < len(gameLog):
                if line[i] != gameLog[i]:
                    followingMoves = False
                    break
                i += 1

            if followingMoves:
                ret.append(line)

        return ret


    def orderMoves(self, moves):
        orderedMoves = []
        movesCopy = moves[:]


        i = len(movesCopy) - 1
        while i >= 0: # checkmate moves
            move = movesCopy[i]
            if move.isCheckmate:
                movesCopy.remove(move)
                orderedMoves.append(move)
            i -= 1

        i = len(movesCopy) - 1
        while i >= 0:  # stalemate moves
            move = movesCopy[i]
            if move.isStalemate:
                movesCopy.remove(move)
                orderedMoves.append(move)
            i -= 1

        i = len(movesCopy) - 1
        while i >= 0:  # check moves
            move = movesCopy[i]
            if move.isCheck:
                movesCopy.remove(move)
                orderedMoves.append(move)
            i -= 1

        i = len(movesCopy) - 1
        while i >= 0:  # capture moves
            move = movesCopy[i]
            if move.isCapture:
                movesCopy.remove(move)
                orderedMoves.append(move)
            i -= 1

        i = len(movesCopy) - 1
        while i >= 0: # promotion moves
            move = movesCopy[i]
            if move.isPawnPromotion:
                movesCopy.remove(move)
                orderedMoves.append(move)
            i -= 1

        for move in movesCopy: #putting the rest of the moves here
            orderedMoves.append(move)

        return orderedMoves

    # returns 1 if pawn in file is isolated, 0 otherwise
    def isPawnInFileIsolatedIn(self, pawnsInFiles, i) -> int:

        if i < 7:
            if pawnsInFiles[i + 1] > 0:
                # we have right neighbour pawn
                return 1

        if i > 0:
            if pawnsInFiles[i - 1] > 0:
                # we have left neighbour pawn
                return 1

        #no neighbours found
        return 0


    # returns 2 arrays with of number of pawns in file for each side
    def initPawnsInFilesArray(self):
        # evaluate double and isolated pawns
        whitePawnsInFiles = np.zeros(8,dtype=np.int)  # used for determining white's isolated (pawns with no neighbours) and double(2 or more pawns in same file) pawns
        blackPawnsInFiles = np.zeros(8,dtype=np.int)  # used for determining black's isolated (pawns with no neighbours) and double(2 or more pawns in same file) pawns
        for i in range(8):
            for j in range(8):
                piece = self.board.getPiece(i, j)
                if Piece.isPiecePawn(piece) and Piece.isPieceWhite(piece):
                    whitePawnsInFiles[i] += 1
                elif Piece.isPiecePawn(piece) and Piece.isPieceBlack(piece):
                    blackPawnsInFiles[i] += 1

        return whitePawnsInFiles, blackPawnsInFiles



    def getNumOfIsolatedPawnsFromArray(self, pawnsInFiles) -> int:
        numOfIsolatedPawns = 0
        for i in range(8):

            numOfIsolatedPawns += self.isPawnInFileIsolatedIn(pawnsInFiles, i)

        return numOfIsolatedPawns


    def getNumOfDoubledPawnsFromArray(self, pawnsInFiles):
        numOfDoubledPawns = 0
        for i in range(8):

            if pawnsInFiles[i] > 1:
                numOfDoubledPawns += 1

        return numOfDoubledPawns

    # returns the difference between number of white legal moves and black legal moves
    def getLegalMoveNumberDifference(self) -> float:
        # save old values
        oldInCheck = self.board.inCheck
        oldPins = self.board.pins[:]
        oldChecks = self.board.checks[:]

        if self.board.whiteToPlay:
            numOfLegalMovesWhite = len(self.board.currentValidMoves)
            self.board.whiteToPlay = False # setting black to move
            numOfLegalMovesBlack = len(self.board.getValidMoves())
            self.board.whiteToPlay = True

        else:
            numOfLegalMovesBlack = len(self.board.currentValidMoves)
            self.board.whiteToPlay = False  # setting black to move
            numOfLegalMovesWhite = len(self.board.getValidMoves())
            self.board.whiteToPlay = True

            # returning old board values

        self.board.inCheck = oldInCheck
        self.board.pins = oldPins[:]
        self.board.checks = oldChecks[:]

        return numOfLegalMovesWhite - numOfLegalMovesBlack
