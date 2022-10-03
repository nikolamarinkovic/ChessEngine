import numpy as np
from numpy import ndarray

from CastlingRights import CastlingRights
from Move import Move
from Piece import Piece


class Board:
    squares: ndarray

    def __init__(self):
        self.squares = np.zeros(64, dtype=np.int)
        self.initPieces()

        self.whiteToPlay = True  # 1 - white, 0 black

        self.playedMoves = []

        self.whiteKing = (7, 4)
        self.blackKing = (0, 4)

        self.inCheck = False
        self.pins = []
        self.checks = []

        self.alreadyDrawnValidMoves = False # for not drawing more than needed, and for not calling getValidMoves() more than necessary
        self.numberOfMovesPlayed = 0

        # for en passant
        self.enpassantPossible = () # square where en passant is possible
        self.enPassantPossibleLog = [self.enpassantPossible]
        # for castling
        self.currentCastlingRight = CastlingRights(whiteKingSide=True, whiteQueenSide=True, blackKingSide=True, blackQueenSide=True)
        self.castlingRightsLog = [CastlingRights(self.currentCastlingRight.whiteKingSide,
                                                 self.currentCastlingRight.blackKingSide,
                                                 self.currentCastlingRight.whiteQueenSide,
                                                 self.currentCastlingRight.blackQueenSide)]

        # for highlighting last move
        self.highlightLastMoveLog = []
        self.currentLastMove = None

        self.chessNotationMoveHistoryLog = []

        self.currentValidMoves = self.getValidMoves()
        self.validMovesLog = []

        self.oldPositionLog  = [] # for keeping track of threefold repetition

        self.currentDrawCounter = 0 # for keeping track of 50 move draw
        self.drawCounterLog = []


        #self.validMovesLog.append(self.currentValidMoves)

        """
        newValidMoves = []
        for move in self.validMoves: #copy moves, todo: check if we can add the currentValidMoves
            newMove = Move((move.startRow, move.startColumn), (move.endRow, move.endColumn), enPassantMove=move.isEnPassantMove, isCastleMove=move.isCastleMove, promotePiece= move.promotePiece)
            newValidMoves.append(newMove)

        newValidMoves.append(newValidMoves)
        """



    def initPieces(self):

        blackRook = Piece.BLACK | Piece.ROOK
        blackKnight = Piece.BLACK | Piece.KNIGHT
        blackBishop = Piece.BLACK | Piece.BISHOP
        blackQueen = Piece.BLACK | Piece.QUEEN
        blackKing = Piece.BLACK | Piece.KING
        blackPawn = Piece.BLACK | Piece.PAWN

        whiteRook = Piece.WHITE | Piece.ROOK
        whiteKnight = Piece.WHITE | Piece.KNIGHT
        whiteBishop = Piece.WHITE | Piece.BISHOP
        whiteQueen = Piece.WHITE | Piece.QUEEN
        whiteKing = Piece.WHITE | Piece.KING
        whitePawn = Piece.WHITE | Piece.PAWN


        self.squares[0] = blackRook
        self.squares[1] = blackKnight
        self.squares[2] = blackBishop
        self.squares[3] = blackQueen
        self.squares[4] = blackKing
        self.squares[5] = blackBishop
        self.squares[6] = blackKnight
        self.squares[7] = blackRook

        self.squares[8] = blackPawn
        self.squares[9] = blackPawn
        self.squares[10] = blackPawn
        self.squares[11] = blackPawn
        self.squares[12] = blackPawn
        self.squares[13] = blackPawn
        self.squares[14] = blackPawn
        self.squares[15] = blackPawn

        self.squares[48] = whitePawn
        self.squares[49] = whitePawn
        self.squares[50] = whitePawn
        self.squares[51] = whitePawn
        self.squares[52] = whitePawn
        self.squares[53] = whitePawn
        self.squares[54] = whitePawn
        self.squares[55] = whitePawn

        self.squares[56] = whiteRook
        self.squares[57] = whiteKnight
        self.squares[58] = whiteBishop
        self.squares[59] = whiteQueen
        self.squares[60] = whiteKing
        self.squares[61] = whiteBishop
        self.squares[62] = whiteKnight
        self.squares[63] = whiteRook

    def printBoard(self):
        j: int = 0
        while j < 8:
            i: int = 0
            while i < 8:
                print(self.squares[j * 8 + i], end=' ')
                i = i + 1
            print('')
            j = j + 1

    def makeMove(self, move: Move):  # doesn't work for castling, en passant, promotion

        #print(move)
        self.numberOfMovesPlayed += 1

        # setting move to be highlighted
        self.currentLastMove = (move.startRow, move.startColumn, move.endRow, move.endColumn)
        self.highlightLastMoveLog.append(self.currentLastMove)

        # setting startPiece to endPosition
        self.setPiece(move.startRow, move.startColumn, Piece.NO_PIECE)
        self.setPiece(move.endRow, move.endColumn, move.pieceStart)
        self.playedMoves.append(move)

        self.whiteToPlay = not self.whiteToPlay  # swapping turns

        # updating kings position
        if Piece.isPieceKing(move.pieceStart) and Piece.isPieceWhite(move.pieceStart):
            self.whiteKing = (move.endRow, move.endColumn)
        if Piece.isPieceKing(move.pieceStart) and Piece.isPieceBlack(move.pieceStart):
            self.blackKing = (move.endRow, move.endColumn)

        if move.isPawnPromotion:
            self.setPiece(move.endRow, move.endColumn, move.promotePiece)


        #enpassant move
        if move.isEnPassantMove:
            self.setPiece(move.startRow, move.endColumn, Piece.NO_PIECE)

        #update enpassantPossible
        if Piece.isPiecePawn(move.pieceStart) and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startColumn)
        else:
            self.enpassantPossible = ()

        self.enPassantPossibleLog.append(self.enpassantPossible)

        #caslting

        if move.isCastleMove:
            if move.endColumn - move.startColumn == 2: # king side castle
                rook = self.getPiece(move.endRow, move.endColumn + 1)
                self.setPiece(move.endRow, move.endColumn - 1, rook)
                self.setPiece(move.endRow, move.endColumn + 1, Piece.NO_PIECE)
            else: # queen side castle
                rook = self.getPiece(move.endRow, move.endColumn - 2)
                self.setPiece(move.endRow, move.endColumn + 1, rook)
                self.setPiece(move.endRow, move.endColumn - 2, Piece.NO_PIECE)



        #update castling rights for rook and king moves
        self.updateCastlingRights(move)
        self.castlingRightsLog.append(CastlingRights(self.currentCastlingRight.whiteKingSide,
                                                     self.currentCastlingRight.blackKingSide,
                                                     self.currentCastlingRight.whiteQueenSide,
                                                     self.currentCastlingRight.blackQueenSide))


        newValidMoves = self.currentValidMoves[:] #copy moves

        self.validMovesLog.append(newValidMoves)

        self.currentValidMoves = self.getValidMoves()

        if len(self.currentValidMoves) > 0 and self.inCheck:
            move.isCheck = True
        elif len(self.currentValidMoves) == 0 and self.inCheck:
            move.isCheckmate = True
        if len(self.currentValidMoves) == 0 and not self.inCheck:
            move.isStalemate = True

        self.chessNotationMoveHistoryLog.append(str(move))
        #print(self.chessNotationMoveHistoryLog)

    def updateCastlingRights(self, move):
        piece = move.pieceStart
        startI = move.startRow
        startJ = move.startColumn
        #white king moving
        if Piece.isPieceWhite(piece) and Piece.isPieceKing(piece):
            self.currentCastlingRight.whiteKingSide = False
            self.currentCastlingRight.whiteQueenSide = False
        #black king moving
        elif Piece.isPieceBlack(piece) and Piece.isPieceKing(piece):
            self.currentCastlingRight.blackKingSide = False
            self.currentCastlingRight.blackQueenSide = False
        #white rook moving
        elif Piece.isPieceWhite(piece) and Piece.isPieceRook(piece):
            if startI == 7 and startJ == 0: #white left rook
                self.currentCastlingRight.whiteQueenSide = False
            elif startI == 7 and startJ == 7: #white right rook
                self.currentCastlingRight.whiteKingSide = False
        # black rook moving
        elif Piece.isPieceBlack(piece) and Piece.isPieceRook(piece):
            if startI == 0 and startJ == 0:  # black left rook
                self.currentCastlingRight.blackQueenSide = False
            elif startI == 0 and startJ == 7:  # black right rook
                self.currentCastlingRight.blackKingSide = False

        #fixing a bug where the king can castle, with rook on opposite side (castling with queens rook on kingside and vice verse) under these conditions:
            #1: king has castling privileges
            #2 rook on that side was captured without moving
            #3 rook from opposite side comes to that rooks position (eg. queens rook comes to kings rook position)
        # solution: as soon as any piece lands on the rook starting squares, immediately invalidate the kings right to castle that way

        if move.endRow == 0 and move.endColumn == 0: #upper left rook, black queen side rook
            self.currentCastlingRight.blackQueenSide = False
        if move.endRow == 0 and move.endColumn == 7: #upper right rook, black king side
            self.currentCastlingRight.blackKingSide = False
        if move.endRow == 7 and move.endColumn == 0: #lower left rook, white queen side rook
            self.currentCastlingRight.whiteQueenSide = False
        if move.endRow == 7 and move.endColumn == 7: #lower right rook, white king side
            self.currentCastlingRight.whiteKingSide = False


    def undoMove(self):
        if len(self.playedMoves) > 0:

            self.numberOfMovesPlayed -= 1

            if len(self.highlightLastMoveLog) > 0:
                self.highlightLastMoveLog.pop()
                if len(self.highlightLastMoveLog) > 0:
                    self.currentLastMove = self.highlightLastMoveLog[-1]
                else:
                    self.currentLastMove = None

            move = self.playedMoves.pop()  # returns last move
            self.setPiece(move.startRow, move.startColumn, move.pieceStart)
            self.setPiece(move.endRow, move.endColumn, move.pieceEnd)
            self.whiteToPlay = not self.whiteToPlay  # swap

            # update kings position
            if Piece.isPieceKing(move.pieceStart) and Piece.isPieceWhite(move.pieceStart):
                self.whiteKing = (move.startRow, move.startColumn)
            if Piece.isPieceKing(move.pieceStart) and Piece.isPieceBlack(move.pieceStart):
                self.blackKing = (move.startRow, move.startColumn)

            # undo en passant
            if move.isEnPassantMove:
                self.setPiece(move.endRow, move.endColumn, Piece.NO_PIECE)#returning empty piece
                self.setPiece(move.startRow, move.endColumn, move.pieceEnd)#returning opponent pawn


            self.enPassantPossibleLog.pop()
            self.enpassantPossible = self.enPassantPossibleLog[-1]

            self.chessNotationMoveHistoryLog.pop()

            #undo castling rights
            self.castlingRightsLog.pop()
            newCastlingRights = self.castlingRightsLog[-1]
            self.currentCastlingRight = CastlingRights(newCastlingRights.whiteKingSide, newCastlingRights.blackKingSide, newCastlingRights.whiteQueenSide, newCastlingRights.blackQueenSide)

            #undo castling move
            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2: #kingside
                    rook = self.getPiece(move.endRow, move.endColumn-1)
                    self.setPiece(move.endRow, move.endColumn + 1, rook)
                    self.setPiece(move.endRow, move.endColumn - 1, Piece.NO_PIECE)
                else:
                    rook = self.getPiece(move.endRow, move.endColumn + 1)
                    self.setPiece(move.endRow, move.endColumn - 2, rook)
                    self.setPiece(move.endRow, move.endColumn + 1, Piece.NO_PIECE)

            #pop validMoveLog into currentValidMoves

            self.currentValidMoves = self.validMovesLog.pop()


    # detects if enemy can attack a square
    def squareUnderAttack(self, i, j):
        self.whiteToPlay = not self.whiteToPlay
        opponentMoves = self.getAllPossibleMoves()
        self.whiteToPlay = not self.whiteToPlay
        for move in opponentMoves:
            if move.endRow == i and move.endColumn == j:
                return True

        return False

    def getValidMoves(self):  # all LEGAL moves
        moves = []

        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToPlay:
            kingI = self.whiteKing[0]
            kingJ = self.whiteKing[1]
        else:
            kingI = self.blackKing[0]
            kingJ = self.blackKing[1]

        if self.inCheck:
            if len(self.checks) == 1:  # block check or move king
                moves = self.getAllPossibleMoves()

                check = self.checks[0]

                checkI = check[0]
                checkJ = check[1]
                diffI = check[2]
                diffJ = check[3]

                pieceChecking = self.getPiece(checkI, checkJ)
                validSquares = []  # squares pieces can move to (to capture or block)
                if Piece.isPieceKnight(pieceChecking):
                    validSquares = [(checkI, checkJ)]  # adding option to catch knight
                else:
                    for i in range(1, 8):
                        validSquare = (kingI + diffI * i, kingJ + diffJ*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkI and validSquare[1] == checkJ: #once we get to attacking piece
                            break

                for i in range(len(moves)-1, -1, -1):
                    move: Move = moves[i]
                    if not Piece.isPieceKing(move.pieceStart):
                        if not (move.endRow, move.endColumn) in validSquares:
                            moves.remove(move)
            else:  # double check
                self.getKingMoves(kingI, kingJ, moves)
        else:  # not in check
            moves = self.getAllPossibleMoves()
            if self.whiteToPlay:
                self.getCastleMoves(self.whiteKing[0], self.whiteKing[1], moves, Piece.WHITE)
            else:
                self.getCastleMoves(self.blackKing[0], self.blackKing[1], moves, Piece.BLACK)

        return moves

    def getAllPossibleMoves(self):  # all POSSIBLE moves
        allMoves = []
        for i in range(8):
            for j in range(8):
                piece = self.getPiece(i, j)
                if (Piece.isPieceWhite(piece) and self.whiteToPlay is True) or (not Piece.isPieceWhite(piece) and self.whiteToPlay is False):
                    self.getPieceMoves(i, j, allMoves)

        return allMoves

    def getPieceMoves(self, i: int, j: int, moves):
        piece = self.getPiece(i, j)
        if Piece.isPiecePawn(piece):
            self.getPawnMoves(i, j, moves)
        elif Piece.isPieceKnight(piece):
            self.getKnightMoves(i, j, moves)
        elif Piece.isPieceBishop(piece):
            self.getBishopMoves(i, j, moves)
        elif Piece.isPieceRook(piece):
            self.getRookMoves(i, j, moves)
        elif Piece.isPieceQueen(piece):
            self.getQueenMoves(i, j, moves)
        elif Piece.isPieceKing(piece):
            self.getKingMoves(i, j, moves)

    def getPiece(self, i, j) -> int:
        if i < 0 or j < 0 or i > 7 or j > 7:
            return Piece.INVALID
        return self.squares[i * 8 + j]

    def setPiece(self, i, j, piece):
        if i < 0 or j < 0 or i > 7 or j > 7 or piece < 0:
            return
        self.squares[i * 8 + j] = piece

    def getPawnMoves(self, i, j, moves):

        piecePinned = False
        pinDirection = ()
        for k in range(len(self.pins)-1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                piecePinned = True
                pinDirection = (self.pins[k][2], self.pins[k][3])
                self.pins.remove(self.pins[k])
                break

        if self.whiteToPlay:
            if self.getPiece(i - 1, j) == Piece.NO_PIECE:  # 1 square move
                if not piecePinned or pinDirection == (-1, 0):
                    if i == 1: # pawn promotions
                        moves.append(Move((i, j), (i - 1, j), self, promotePiece=Piece.WHITE | Piece.KNIGHT))
                        moves.append(Move((i, j), (i - 1, j), self, promotePiece=Piece.WHITE | Piece.BISHOP))
                        moves.append(Move((i, j), (i - 1, j), self, promotePiece=Piece.WHITE | Piece.ROOK))
                        moves.append(Move((i, j), (i - 1, j), self, promotePiece=Piece.WHITE | Piece.QUEEN))
                    else: # 1 square move
                        moves.append(Move((i, j), (i - 1, j), self))
                    if i == 6 and self.getPiece(i - 2, j) == Piece.NO_PIECE:  # no piece 2 squares in front, and we are at starting position
                        moves.append(Move((i, j), (i - 2, j), self))

            if self.getPiece(i - 1, j - 1) != Piece.INVALID and Piece.isPieceBlack(self.getPiece(i - 1, j - 1)):  # left capture
                if not piecePinned or pinDirection == (-1, -1):
                    if i == 1: # pawn promotions
                        moves.append(Move((i, j), (i - 1, j - 1), self, promotePiece=Piece.WHITE | Piece.KNIGHT))
                        moves.append(Move((i, j), (i - 1, j - 1), self, promotePiece=Piece.WHITE | Piece.BISHOP))
                        moves.append(Move((i, j), (i - 1, j - 1), self, promotePiece=Piece.WHITE | Piece.ROOK))
                        moves.append(Move((i, j), (i - 1, j - 1 ), self, promotePiece=Piece.WHITE | Piece.QUEEN))
                    else:
                        moves.append(Move((i, j), (i - 1, j - 1), self))
            elif (i-1, j-1) == self.enpassantPossible: # left en passant
                if not piecePinned or pinDirection == (-1, -1):
                    kingI = self.whiteKing[0]
                    kingJ = self.whiteKing[1]
                    # special case when en passant is done, but our king is on same rank as our pawn, and by eating the pawn we reveal a pin from queen or rook
                    if kingI == i:  # king on same row as pawn
                        if kingJ > j:  # king on right side of pawn
                            inc = -1
                        else:
                            inc = 1

                        enemyJ = -1
                        tmpJ = j + inc # start looking from 1 space left/right (depending on where is king) of pawn

                        while 7 >= tmpJ >= 0: # looking left/right of pawn
                            pieceTmp = self.getPiece(i, tmpJ)
                            if Piece.isPieceBlack(pieceTmp):
                                if Piece.isPieceRook(pieceTmp) or Piece.isPieceQueen(pieceTmp):
                                    enemyJ = tmpJ # found pin
                                    break
                                else:
                                    if Piece.isPiecePawn(pieceTmp):
                                        if self.enpassantPossible[0] != i - 1 or self.enpassantPossible[1] != tmpJ: # the enemy pawn that moved 2 squares
                                            break
                                    else:
                                        break # no pin here
                            else:
                                if Piece.isPieceWhite(pieceTmp):
                                    break # no pin possible here

                            tmpJ = tmpJ + inc
                        if enemyJ == -1:
                            moves.append(Move((i, j), (i - 1, j - 1), self, enPassantMove=True))
                    else: # not special case, add it to list
                        moves.append(Move((i, j), (i - 1, j - 1), self, enPassantMove=True))

            if self.getPiece(i - 1, j + 1) != Piece.INVALID and Piece.isPieceBlack(self.getPiece(i - 1, j + 1)):  # right capture
                if not piecePinned or pinDirection == (-1, 1):
                    if i == 1: # pawn promotions
                        moves.append(Move((i, j), (i - 1, j + 1), self, promotePiece=Piece.WHITE | Piece.KNIGHT))
                        moves.append(Move((i, j), (i - 1, j + 1), self, promotePiece=Piece.WHITE | Piece.BISHOP))
                        moves.append(Move((i, j), (i - 1, j + 1), self, promotePiece=Piece.WHITE | Piece.ROOK))
                        moves.append(Move((i, j), (i - 1, j + 1), self, promotePiece=Piece.WHITE | Piece.QUEEN))
                    else:

                        moves.append(Move((i, j), (i - 1, j + 1), self))
            elif (i-1, j+1) == self.enpassantPossible: # right en passant
                if not piecePinned or pinDirection == (-1, 1):
                    kingI = self.whiteKing[0]
                    kingJ = self.whiteKing[1]

                    # special case when en passant is done, but our king is on same rank as our pawn, and by eating the pawn we reveal a pin from queen or rook
                    if kingI == i:  # king on same row as pawn
                        if kingJ > j:  # king on right side of pawn
                            inc = -1
                        else:
                            inc = 1

                        enemyJ = -1
                        tmpJ = j + inc  # start looking from 1 space left/right (depending on where is king) of pawn

                        while 7 >= tmpJ >= 0:  # looking left/right of pawn
                            pieceTmp = self.getPiece(i, tmpJ)
                            if Piece.isPieceBlack(pieceTmp):
                                if Piece.isPieceRook(pieceTmp) or Piece.isPieceQueen(pieceTmp):
                                    enemyJ = tmpJ  # found pin
                                    break
                                else:
                                    if Piece.isPiecePawn(pieceTmp):
                                        if self.enpassantPossible[0] != i - 1 or self.enpassantPossible[1] != tmpJ:  # the enemy pawn that moved 2 squares
                                            break
                                    else:
                                        break  # no pin here
                            else:
                                if Piece.isPieceWhite(pieceTmp):
                                    break  # no pin possible here

                            tmpJ = tmpJ + inc
                        if enemyJ == -1:
                            moves.append(Move((i, j), (i - 1, j + 1), self, enPassantMove=True))
                    else:
                        moves.append(Move((i, j), (i - 1, j + 1), self, enPassantMove=True))
        else:  # black to play

            if self.getPiece(i + 1, j) == Piece.NO_PIECE:  # 1 square move
                if not piecePinned or pinDirection == (1, 0):
                    if i == 6: #appending all promotions
                        moves.append(Move((i, j), (i + 1, j), self, promotePiece=Piece.BLACK | Piece.KNIGHT))
                        moves.append(Move((i, j), (i + 1, j), self, promotePiece=Piece.BLACK | Piece.BISHOP))
                        moves.append(Move((i, j), (i + 1, j), self, promotePiece=Piece.BLACK | Piece.ROOK))
                        moves.append(Move((i, j), (i + 1, j), self, promotePiece=Piece.BLACK | Piece.QUEEN))
                    else:
                        moves.append(Move((i, j), (i + 1, j), self))
                    if i == 1 and self.getPiece(i + 2, j) == Piece.NO_PIECE:  # no piece 2 squares in front, and we are at starting position
                        moves.append(Move((i, j), (i + 2, j), self))

            if self.getPiece(i + 1, j - 1) != Piece.INVALID and Piece.isPieceWhite(self.getPiece(i + 1, j - 1)):  # left capture
                if not piecePinned or pinDirection == (1, -1):
                    if i == 6: #appeinding all promotions
                        moves.append(Move((i, j), (i + 1, j - 1), self, promotePiece=Piece.BLACK | Piece.KNIGHT))
                        moves.append(Move((i, j), (i + 1, j - 1), self, promotePiece=Piece.BLACK | Piece.BISHOP))
                        moves.append(Move((i, j), (i + 1, j - 1), self, promotePiece=Piece.BLACK | Piece.ROOK))
                        moves.append(Move((i, j), (i + 1, j - 1), self, promotePiece=Piece.BLACK | Piece.QUEEN))
                    else:
                        moves.append(Move((i, j), (i + 1, j - 1), self))
            elif (i+1, j-1) == self.enpassantPossible: # left en passant
                if not piecePinned or pinDirection == (1, -1):

                    kingI = self.blackKing[0]
                    kingJ = self.blackKing[1]
                    # special case when en passant is done, but our king is on same rank as our pawn, and by eating the pawn we reveal a pin from queen or rook
                    if kingI == i:  # king on same row as pawn
                        if kingJ > j:  # king on right side of pawn
                            inc = -1
                        else:
                            inc = 1

                        enemyJ = -1
                        tmpJ = j + inc  # start looking from 1 space left/right (depending on where is king) of pawn
                        while 7 >= tmpJ >= 0:  # looking left/right of pawn
                            pieceTmp = self.getPiece(i, tmpJ)
                            if Piece.isPieceWhite(pieceTmp):
                                if Piece.isPieceRook(pieceTmp) or Piece.isPieceQueen(pieceTmp):
                                    enemyJ = tmpJ  # found pin
                                    break
                                else:
                                    if Piece.isPiecePawn(pieceTmp):
                                        if self.enpassantPossible[0] != i + 1 or self.enpassantPossible[1] != tmpJ:  # the enemy pawn that moved 2 squares
                                            break
                                    else:
                                        break  # no pin here
                            else:
                                if Piece.isPieceBlack(pieceTmp):
                                    break  # no pin possible here

                            tmpJ = tmpJ + inc
                        if enemyJ == -1:
                            moves.append(Move((i, j), (i + 1, j - 1), self, enPassantMove=True))
                    else:
                        moves.append(Move((i, j), (i + 1, j - 1), self, enPassantMove=True))

            if self.getPiece(i + 1, j + 1) != Piece.INVALID and Piece.isPieceWhite(self.getPiece(i + 1, j + 1)):  # right capture
                if not piecePinned or pinDirection == (1, 1):
                    if i == 6: #appending all promotions
                        moves.append(Move((i, j), (i + 1, j + 1), self, promotePiece=Piece.BLACK | Piece.KNIGHT))
                        moves.append(Move((i, j), (i + 1, j + 1), self, promotePiece=Piece.BLACK | Piece.BISHOP))
                        moves.append(Move((i, j), (i + 1, j + 1), self, promotePiece=Piece.BLACK | Piece.ROOK))
                        moves.append(Move((i, j), (i + 1, j + 1), self, promotePiece=Piece.BLACK | Piece.QUEEN))
                    else:
                        moves.append(Move((i, j), (i + 1, j + 1), self))

            elif (i+1, j+1) == self.enpassantPossible: # right en passant
                if not piecePinned or pinDirection == (1, 1):
                    kingI = self.blackKing[0]
                    kingJ = self.blackKing[1]
                    # special case when en passant is done, but our king is on same rank as our pawn, and by eating the pawn we reveal a pin from queen or rook
                    if kingI == i:  # king on same row as pawn
                        if kingJ > j:  # king on right side of pawn
                            inc = -1
                        else:
                            inc = 1

                        enemyJ = -1
                        tmpJ = j + inc  # start looking from 1 space left/right (depending on where is king) of pawn
                        while 7 >= tmpJ >= 0:  # looking left/right of pawn
                            pieceTmp = self.getPiece(i, tmpJ)
                            if Piece.isPieceWhite(pieceTmp):
                                if Piece.isPieceRook(pieceTmp) or Piece.isPieceQueen(pieceTmp):
                                    enemyJ = tmpJ  # found pin
                                    break
                                else:
                                    if Piece.isPiecePawn(pieceTmp):
                                        if self.enpassantPossible[0] != i + 1 or self.enpassantPossible[1] != tmpJ:  # the enemy pawn that moved 2 squares
                                            break
                                    else:
                                        break  # no pin here
                            else:
                                if Piece.isPieceBlack(pieceTmp):
                                    break  # no pin possible here

                            tmpJ = tmpJ + inc
                        if enemyJ == -1:
                            moves.append(Move((i, j), (i + 1, j + 1), self, enPassantMove=True))
                    else:
                        moves.append(Move((i, j), (i + 1, j + 1), self, enPassantMove=True))


    def getKnightMoves(self, i, j, moves):

        coordDifferences = [(2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, -1), (-2, 1)]

        piecePinned = False
        for k in range(len(self.pins)-1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                piecePinned = True
                self.pins.remove(self.pins[k])
                break

        for difference in coordDifferences:
            newI = i + difference[0]
            newJ = j + difference[1]

            if not piecePinned:
                piece = self.getPiece(newI, newJ)
                if piece == Piece.NO_PIECE:  # empty square
                    moves.append(Move((i, j), (newI, newJ), self))
                elif piece != Piece.INVALID:  # piece present
                    if (self.whiteToPlay and Piece.isPieceBlack(piece)) or (
                            not self.whiteToPlay and Piece.isPieceWhite(piece)):
                        moves.append(Move((i, j), (newI, newJ), self))



    def getBishopMoves(self, i, j, moves):

        coordDifferences = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        self.getPieceMovesByCoordIncrements(i, j, moves, coordDifferences)

    def getRookMoves(self, i, j, moves):
        coordDifferences = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        self.getPieceMovesByCoordIncrements(i, j, moves, coordDifferences)

    def getQueenMoves(self, i, j, moves):
        coordDifferences = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        self.getPieceMovesByCoordIncrements(i, j, moves, coordDifferences)

    def getKingMoves(self, i, j, moves):
        coordDifferences = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        kingPiece = self.getPiece(i, j)
        if not Piece.isPieceKing(kingPiece):
            return
        kingColor = Piece.getPieceColor(kingPiece)

        for difference in coordDifferences:
            incrementI = difference[0]
            incrementJ = difference[1]

            newI = i + incrementI
            newJ = j + incrementJ

            piece = self.getPiece(newI, newJ)
            if piece != Piece.INVALID and (piece == Piece.NO_PIECE or (self.whiteToPlay and Piece.isPieceBlack(piece) or (not self.whiteToPlay and Piece.isPieceWhite(piece)))):
                if self.whiteToPlay:
                    self.whiteKing = (newI, newJ)
                else:
                    self.blackKing = (newI, newJ)
                inCheck, pins, checks = self.checkForPinsAndChecks()

                if not inCheck:
                    moves.append(Move((i, j), (newI, newJ), self))

                if self.whiteToPlay:
                    self.whiteKing = (i, j)
                else:
                    self.blackKing = (i, j)


    def getCastleMoves(self, i, j, moves, kingColor):
        if self.inCheck:
            return #cant castle through check

        if (self.whiteToPlay and self.currentCastlingRight.whiteKingSide) or (not self.whiteToPlay and self.currentCastlingRight.blackKingSide):
            self.getKingSideCastleMoves(i, j, moves, kingColor)

        if (self.whiteToPlay and self.currentCastlingRight.whiteQueenSide) or (not self.whiteToPlay and self.currentCastlingRight.blackQueenSide):
            self.getQueenSideCastleMoves(i, j, moves, kingColor)

    def getKingSideCastleMoves(self, i, j, moves, kingColor):
        piece1 = self.getPiece(i, j+1)
        piece2 = self.getPiece(i, j+2)

        rook = self.getPiece(i, j + 3)

        if Piece.getPieceColor(rook) == kingColor and Piece.isPieceRook(rook): # if there is a rook here, needed to stop bugs when enemy piece captures rook and we can castle with the enemy piece
            if piece1 == Piece.NO_PIECE and piece2 == Piece.NO_PIECE: # empty squares
                if not self.squareUnderAttack(i, j+1) and not self.squareUnderAttack(i, j+2): #squares not in check
                    moves.append(Move((i, j),(i, j+2), self, isCastleMove=True))

    def getQueenSideCastleMoves(self, i, j, moves, kingColor):
        piece1 = self.getPiece(i, j - 1)
        piece2 = self.getPiece(i, j - 2)
        piece3 = self.getPiece(i, j - 3)

        rook = self.getPiece(i, j - 4)

        if Piece.getPieceColor(rook) == kingColor and Piece.isPieceRook(rook):  # if there is a rook here, needed to stop bugs when enemy piece captures rook and we can castle with the enemy piece
            if piece1 == Piece.NO_PIECE and piece2 == Piece.NO_PIECE and piece3 == Piece.NO_PIECE:  # empty squares
                if not self.squareUnderAttack(i, j - 1) and not self.squareUnderAttack(i, j - 2):  # squares not in check
                    moves.append(Move((i, j), (i, j - 2), self, isCastleMove=True))

    # puts the moves into moves list, for rook, bishop and queen
    def getPieceMovesByCoordIncrements(self, i: int, j: int, moves, coordDifferences):  # input coords, list in which to put moves and  the coordIncrement list

        piecePinned = False
        pinDirection = ()
        for k in range(len(self.pins)-1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                piecePinned = True
                pinDirection = (self.pins[k][2], self.pins[k][3])
                break

        for difference in coordDifferences:
            incrementI = difference[0]
            incrementJ = difference[1]

            newI = i + incrementI
            newJ = j + incrementJ

            blocked = False

            while 7 >= newI >= 0 and 7 >= newJ >= 0 and blocked is False:

                if not piecePinned or pinDirection == difference or pinDirection == (-difference[0], -difference[1]):
                    piece = self.getPiece(newI, newJ)
                    if piece == Piece.NO_PIECE:  # empty square
                        moves.append(Move((i, j), (newI, newJ), self))
                    elif piece != Piece.INVALID:  # piece present
                        blocked = True
                        if (self.whiteToPlay and Piece.isPieceBlack(piece)) or (
                                not self.whiteToPlay and Piece.isPieceWhite(piece)): #enemy piece caputre
                            moves.append(Move((i, j), (newI, newJ), self))
                newI = newI + incrementI
                newJ = newJ + incrementJ

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToPlay:
            ourColor = Piece.WHITE
            opponentColor = Piece.BLACK

            startI = self.whiteKing[0]
            startJ = self.whiteKing[1]
        else:
            ourColor = Piece.BLACK
            opponentColor = Piece.WHITE

            startI = self.blackKing[0]
            startJ = self.blackKing[1]

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            direction = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endI = startI + direction[0] * i
                endJ = startJ + direction[1] * i
                if 0 <= endI <= 7 and 0 <= endJ <= 7:
                    piece = self.getPiece(endI, endJ)
                    pieceColor = Piece.getPieceColor(piece)
                    #print(pieceColor, endI, endJ)
                    if pieceColor == ourColor and not Piece.isPieceKing(piece):
                        if possiblePin == ():  # 1st piece to cover possible pin
                            #print("possiblePin", endI, endJ, direction[0], direction[1])
                            possiblePin = (endI, endJ, direction[0], direction[1])
                        else:  # there are 2 pieces covering direction, so no check
                            break
                    elif pieceColor == opponentColor:
                        pieceType = Piece.getPieceType(piece)
                        # checking for rook, bishop, pawn, queen checks and king spaces
                        if (j <= 3 and pieceType == Piece.ROOK) or \
                            (4 <= j <= 7 and pieceType == Piece.BISHOP) or \
                            (i == 1 and pieceType == Piece.PAWN and ((opponentColor == Piece.WHITE and 6 <= j <= 7) or (opponentColor == Piece.BLACK and 4 <= j <= 5))) or \
                            (pieceType == Piece.QUEEN) or \
                            (i == 1 and pieceType == Piece.KING):
                            if possiblePin == ():  # no piece blocking
                                inCheck = True
                                checks.append((endI, endJ, direction[0], direction[1]))
                                #print("check", endI, endJ, direction[0], direction[1], sep=", ")
                                break
                            else:
                                #print("pin", possiblePin, sep=", ")
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:
                    break
        # checking knight checks
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for knightMove in knightMoves:
            endI = startI + knightMove[0]
            endJ = startJ + knightMove[1]

            if 0 <= endI <= 7 and 0 <= endJ <= 7:
                piece = self.getPiece(endI, endJ)
                color = Piece.getPieceColor(piece)
                pieceType = Piece.getPieceType(piece)

                if color == opponentColor and pieceType == Piece.KNIGHT:
                    inCheck = True
                    checks.append((endI, endJ, knightMove[0], knightMove[1]))

        return inCheck, pins, checks
