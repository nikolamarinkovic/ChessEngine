# Piece is a int, consists of 5 bits, right most 3 bits indicate what type of piece (rook, pawn..), left most 2 bits indicate color(while,black)
# This is a static helper class, no instances will be made
class Piece:
    # Type of piece
    NO_PIECE = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    INVALID = 7

    # Color of piece
    WHITE = 8
    BLACK = 16

    # Value of pieces
    QUEEN_VALUE = 9
    ROOK_VALUE = 5
    BISHOP_VALUE = 3.2
    KNIGHT_VALUE = 3
    PAWN_VALUE = 1

    # color methods

    @staticmethod
    def getPieceColor(piece: int) -> int:
        if piece <= 0:
            return Piece.INVALID
        return piece & 0b11000

    @staticmethod
    def isPieceWhite(piece: int) -> bool:
        if piece & Piece.WHITE > 0:
            return True
        return False

    @staticmethod
    def isPieceBlack(piece: int) -> bool:
        if piece & Piece.BLACK > 0:
            return True
        return False

    @staticmethod
    def sameColors(piece1: int, piece2: int) -> bool:
        return Piece.getPieceColor(piece1) == Piece.getPieceColor(piece2)

    # type methods

    @staticmethod
    def getPieceType(piece: int) -> int:
        if piece <= 0:
            return Piece.INVALID
        return piece & 0b00111

    @staticmethod
    def isPiecePawn(piece: int) -> bool:
        pieceType = Piece.getPieceType(piece)
        if pieceType == Piece.PAWN:
            return True
        return False

    @staticmethod
    def isPieceKnight(piece: int) -> bool:
        pieceType = Piece.getPieceType(piece)
        if pieceType == Piece.KNIGHT:
            return True
        return False

    @staticmethod
    def isPieceBishop(piece: int) -> bool:
        pieceType = Piece.getPieceType(piece)
        if pieceType == Piece.BISHOP:
            return True
        return False

    @staticmethod
    def isPieceRook(piece: int) -> bool:
        pieceType = Piece.getPieceType(piece)
        if pieceType == Piece.ROOK:
            return True
        return False

    @staticmethod
    def isPieceQueen(piece: int) -> bool:
        pieceType = Piece.getPieceType(piece)
        if pieceType == Piece.QUEEN:
            return True
        return False

    @staticmethod
    def isPieceKing(piece: int) -> bool:
        pieceType = Piece.getPieceType(piece)
        if pieceType == Piece.KING:
            return True
        return False

    @staticmethod
    def getPieceImageName(piece: int) -> str:
        res = ""
        if Piece.isPieceWhite(piece):
            res += "w"
        elif Piece.isPieceBlack(piece):
            res += "b"

        if Piece.isPiecePawn(piece):
            res += "p"
        elif Piece.isPieceBishop(piece):
            res += "B"
        elif Piece.isPieceKnight(piece):
            res += "N"
        elif Piece.isPieceRook(piece):
            res += "R"
        elif Piece.isPieceQueen(piece):
            res += "Q"
        elif Piece.isPieceKing(piece):
            res += "K"

        return res

    @staticmethod
    def getPieceValue(piece) -> int:
        if piece == Piece.NO_PIECE or piece < 0:
            return 0
        if Piece.isPieceWhite(piece):
            color = 1
        elif Piece.isPieceBlack(piece):
            color = -1
        else:
            return 0 # error
        val = 0
        if Piece.isPiecePawn(piece):
            val = Piece.PAWN_VALUE
        elif Piece.isPieceKnight(piece):
            val = Piece.KNIGHT_VALUE
        elif Piece.isPieceBishop(piece):
            val = Piece.BISHOP_VALUE
        elif Piece.isPieceRook(piece):
            val = Piece.ROOK_VALUE
        elif Piece.isPieceQueen(piece):
            val = Piece.QUEEN_VALUE

        return val * color

