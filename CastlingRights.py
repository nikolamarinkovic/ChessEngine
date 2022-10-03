#class to save castle right
class CastlingRights():

    def __init__(self, whiteKingSide: bool = True, blackKingSide: bool = True, whiteQueenSide: bool = True, blackQueenSide: bool = True):
        self.whiteKingSide: bool = whiteKingSide
        self.blackKingSide: bool = blackKingSide
        self.whiteQueenSide: bool = whiteQueenSide
        self.blackQueenSide: bool = blackQueenSide
