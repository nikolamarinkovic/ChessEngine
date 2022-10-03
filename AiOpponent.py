from abc import ABC, abstractmethod

class AiOpponent(ABC):
     @abstractmethod
     # input: list of valid moves, whos turn is it to play, and the queue into which to put the result
     def getBestMove(self, validMoves, whiteToPlay, returnQueue):
         pass