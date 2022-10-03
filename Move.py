from Piece import Piece


class Move():
    rowToRankDict = {0: 8, 1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2,
                     7: 1}  # translates class board row to real board rank
    columnToFileDict = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g',
                        7: 'h'}  # translates class board column to real board rank

    def __init__(self, startSquare, endSquare, board, enPassantMove=False, isCastleMove=False, promotePiece=Piece.NO_PIECE):
        self.startRow = startSquare[0]
        self.startColumn = startSquare[1]

        self.endRow = endSquare[0]
        self.endColumn = endSquare[1]

        self.pieceStart = board.squares[self.startRow * 8 + self.startColumn]
        self.pieceEnd = board.squares[self.endRow * 8 + self.endColumn]

        #promotion
        self.isPawnPromotion = False
        if (Piece.isPiecePawn(self.pieceStart) and Piece.isPieceWhite(self.pieceStart) and self.endRow == 0) \
                or (Piece.isPiecePawn(self.pieceStart) and Piece.isPieceBlack(self.pieceStart) and self.endRow == 7):
            self.isPawnPromotion = True

        #en passant
        self.isEnPassantMove = enPassantMove
        if self.isEnPassantMove:
            if Piece.isPieceWhite(self.pieceStart) and Piece.isPiecePawn(self.pieceStart):
                self.pieceEnd = Piece.BLACK | Piece.PAWN
            elif Piece.isPieceBlack(self.pieceStart) and Piece.isPiecePawn(self.pieceStart):
                self.pieceEnd = Piece.WHITE | Piece.PAWN

        #castling
        self.isCastleMove = isCastleMove

        if self.pieceEnd != Piece.NO_PIECE and self.pieceEnd != Piece.INVALID:
            self.isCapture = True
        else:
            self.isCapture = False

        self.isCheck = False
        self.isCheckmate = False
        self.isStalemate = False

        self.promotePiece = promotePiece


        self.moveId = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn # for easier comparing of 2 objects


    # methods for debuging
    def getChessNotation(self) -> str:
        return Move.getRankFile(self.startRow, self.startColumn) + self.getRankFile(self.endRow, self.endColumn)

    @staticmethod
    def getRankFile(row, column) -> str:  # transforms class board coord to real board coords, (e4, c6, d5 .. )
        return str(Move.columnToFileDict[column]) + str(Move.rowToRankDict[row])

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.moveId == other.moveId and self.isPawnPromotion == other.isPawnPromotion and self.promotePiece == other.promotePiece

    def __str__(self):
        if self.isCastleMove:
            if self.endColumn == 6:
                res = "O-O"
            else:
                res = "O-O-O"

        else:
            endSquare = Move.getRankFile(self.endRow, self.endColumn)
            moveString = ""

            #pawn moves
            if Piece.isPiecePawn(self.pieceStart):
                if self.isCapture:

                    res = Move.columnToFileDict[self.startColumn] + "x" + endSquare
                else:
                    res = endSquare
            else:
                #TODO: pawn promotions

                if Piece.isPieceQueen(self.pieceStart):
                    moveString = "Q"
                elif Piece.isPieceRook(self.pieceStart):
                    moveString = "R"
                elif Piece.isPieceKnight(self.pieceStart):
                    moveString = "N"
                elif Piece.isPieceBishop(self.pieceStart):
                    moveString = "B"
                else:
                    moveString = "K"

                if self.isCapture:
                    moveString += "x"

                res = moveString + endSquare


        if self.isCheck:
            res += "+"

        elif self.isCheckmate:
            res += "#"

        elif self.isStalemate:
            res += "="

        return res