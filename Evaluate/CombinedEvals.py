import chess
from Evaluate import evaluateScore, calculate, calculateRapid


def eval(board: chess.Board, color):
    return (0.5 * evaluateScore(board, color)) + (0.5 * calculateRapid(board, color))