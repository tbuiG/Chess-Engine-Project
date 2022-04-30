import math

import chess
from chess import *

# Chess location to index dictionary.
chessToIndex = {
        'a8': 56, 'b8': 57, 'c8': 58, 'd8': 59, 'e8': 60, 'f8': 61, 'g8': 62, 'h8': 63,
        'a7': 48, 'b7': 49, 'c7': 50, 'd7': 51, 'e7': 52, 'f7': 53, 'g7': 54, 'h7': 55,
        'a6': 40, 'b6': 41, 'c6': 42, 'd6': 43, 'e6': 44, 'f6': 45, 'g6': 46, 'h6': 47,
        'a5': 32, 'b5': 33, 'c5': 34, 'd5': 35, 'e5': 36, 'f5': 37, 'g5': 38, 'h5': 39,
        'a4': 24, 'b4': 25, 'c4': 26, 'd4': 27, 'e4': 28, 'f4': 29, 'g4': 30, 'h4': 31,
        'a3': 16, 'b3': 17, 'c3': 18, 'd3': 19, 'e3': 20, 'f3': 21, 'g3': 22, 'h3': 23,
        'a2': 8, 'b2': 9, 'c2': 10, 'd2': 11, 'e2': 12, 'f2': 13, 'g2': 14, 'h2': 15,
        'a1': 0, 'b1': 1, 'c1': 2, 'd1': 3, 'e1': 4, 'f1': 5, 'g1': 6, 'h1': 7
}

# Initialize evaluation with current move. (Maybe just make this a method for a parent object?)
# This algorithm assumes 'myColor' is the person whose turn it is.
# Evaluates in 4 parts: Material, King Safety, Control of Center, and possible Activity
def calculateRapid(board: chess.Board, color):
    myColor = color
    enemyColor = not color

    allMyPieces = set()
    allTheirPieces = set()

    # ------------------------------------------------------------------------------------------------------------------
    # Get all pieces on the board for each side. Create unions to group all into a general group.

    # Kings
    myKings = board.pieces(KING, myColor)
    theirKings = board.pieces(KING, enemyColor)

    allMyPieces = allMyPieces.union(myKings)
    allTheirPieces = allTheirPieces.union(theirKings)

    # Queens
    myQueens = board.pieces(QUEEN, myColor)
    theirQueens = board.pieces(QUEEN, enemyColor)

    allMyPieces = allMyPieces.union(myQueens)
    allTheirPieces = allTheirPieces.union(theirQueens)

    # Rooks
    myRooks = board.pieces(ROOK, myColor)
    theirRooks = board.pieces(ROOK, enemyColor)

    allMyPieces = allMyPieces.union(myRooks)
    allTheirPieces = allTheirPieces.union(theirRooks)

    # Bishops
    myBishops = board.pieces(BISHOP, myColor)
    theirBishops = board.pieces(BISHOP, enemyColor)

    allMyPieces = allMyPieces.union(myBishops)
    allTheirPieces = allTheirPieces.union(theirBishops)

    # Knights
    myKnights = board.pieces(KNIGHT, myColor)
    theirKnights = board.pieces(KNIGHT, enemyColor)

    allMyPieces = allMyPieces.union(myKnights)
    allTheirPieces = allTheirPieces.union(theirKnights)

    # Pawns
    myPawns = board.pieces(PAWN, myColor)
    theirPawns = board.pieces(PAWN, enemyColor)

    allMyPieces = allMyPieces.union(myPawns)
    allTheirPieces = allTheirPieces.union(theirPawns)

    # ------------------------------------------------------------------------------------------------------------------
    # Gets the material score.
    kingWt = len(myKings) - len(theirKings)
    queenWt = len(myQueens) - len(theirQueens)
    rookWt = len(myRooks) - len(theirRooks)
    bishWt = len(myBishops) - len(theirBishops)
    kntWt = len(myKnights) - len(theirKnights)
    pawnWt = len(myPawns) - len(theirPawns)

    materialVal = (200 * kingWt) + (9 * queenWt) + (5 * rookWt) + (3 * (kntWt + bishWt)) + pawnWt

    # ------------------------------------------------------------------------------------------------------------------
    # Gets the activity score. Here I'm comparing the average number of moves per piece.
    if board.turn == myColor:
        myMoves = list(board.legal_moves)
        theirMoves = list()
    else:
        theirMoves = list(board.legal_moves)
        myMoves = list()

    if board.turn == myColor:
        if len(myMoves) > 0:
            board.push(myMoves[0])
            theirMoves = list(board.legal_moves)
            board.pop()
    else:
        if len(theirMoves) > 0:
            board.push(theirMoves[0])
            myMoves = list(board.legal_moves)
            board.pop()

    activityVal = 0

    if (allMyPieces == 0 and allTheirPieces == 0):
        activityVal = 0
    elif (allMyPieces == 0):
        activityVal = -1 * len(theirMoves) / len(allTheirPieces)
    elif (allTheirPieces == 0):
        activityVal = len(myMoves) / len(allMyPieces)
    else:
        activityVal = (len(myMoves) / len(allMyPieces)) - (len(theirMoves) / len(allTheirPieces))

    # ------------------------------------------------------------------------------------------------------------------
    # Gets the center control. How many pawns are in a4 to h5.
    myControl = 0
    theirControl = 0

    for x in range(16):
        for piece in myPawns:
            if piece == 16 + x:
                myControl = myControl + 1
        for piece in theirPawns:
            if piece == 16 + x:
                theirControl = theirControl + 1

    controlVal = myControl - theirControl

    # ------------------------------------------------------------------------------------------------------------------
    # Gets the King safety. How safe is my King to the enemy King?
    # This part is pretty big...

    # To reduce time to process all these conditions - If I'm in check, my King is DEFINITELY not safe.
    kingSafetyVal = 0

    if board.is_check():
        kingSafetyVal = -2
    else:
        # Pt.1 How mobile is my King to the enemy King?
        myEscape = countMoves(myKings, myMoves)
        theirEscape = countMoves(theirKings, theirMoves)
        escapeVal = myEscape - theirEscape

        # Pt.2 How many pawns are nearby my King?

        # The 5x5 area around the King
        fiveByFiveRange = [-18, -17, -16, -15, -14, -10, -9, -8, -7, -6, -2, -1, 1, 2, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18]

        myPawnShield = 0
        theirPawnShield = 0

        for dif in fiveByFiveRange:
            for king in myKings:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and \
                        ((dif > 0 and math.floor((king + dif)/8 - king/dif) <= 2) or (dif < 0 and math.ceil((king + dif)/8 - king/dif) >= -2)):
                    if king + dif in myPawns:
                        myPawnShield = myPawnShield + 1

            for king in theirKings:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and \
                        ((dif > 0 and math.floor((king + dif)/8 - king/dif) <= 2) or (dif < 0 and math.ceil((king + dif)/8 - king/dif) >= -2)):
                    if king + dif in theirPawns:
                        theirPawnShield = theirPawnShield + 1

        pawnShieldVal = myPawnShield - theirPawnShield

        # Pt.3 How many friendly pieces are nearby my King? (not counting pawns)

        # The 5x8 area around the King. Ensure these differences don't extend outside 5x8 area
        fiveByEightRange = [-23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

        myDefenders = 0
        theirDefenders = 0

        for dif in fiveByEightRange:
            for king in myKings:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64:
                    if ((dif > 0 and math.floor((king + dif)/8 - king/dif) <= 3) or (dif < 0 and math.ceil((king + dif)/8 - king/dif) >= -3)):
                        # Don't count pawns.
                        if king + dif in allMyPieces and not king + dif in myPawns:
                            myDefenders = myDefenders + 1

            for king in theirKings:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64:
                    if ((dif > 0 and math.floor((king + dif)/8 - king/dif) <= 3) or (dif < 0 and math.ceil((king + dif)/8 - king/dif) >= -3)):
                        # Don't count pawns.
                        if king + dif in allTheirPieces and not king + dif in theirPawns:
                            theirDefenders = theirDefenders + 1

        defenderVal = myDefenders - theirDefenders

        # Pt. 4 How many enemy pieces are nearby my King?
        myAttackers = 0
        theirAttackers = 0

        for dif in fiveByEightRange:
            for king in myKings:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64:
                    if ((dif > 0 and math.floor((king + dif)/8 - king/dif) <= 3) or (dif < 0 and math.ceil((king + dif)/8 - king/dif) >= -3)):
                        if king + dif in allTheirPieces:
                            myAttackers = myAttackers + 1

            for king in theirKings:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64:
                    if ((dif > 0 and math.floor((king + dif)/8 - king/dif) <= 3) or (dif < 0 and math.ceil((king + dif)/8 - king/dif) >= -3)):
                        # Don't count pawns.
                        if king + dif in allMyPieces:
                            theirAttackers = theirAttackers + 1

        # This field we want the enemy to have more of
        attackerValue = theirAttackers - myAttackers

        # Pt. 5 How many Horizontal/Vertical/Diagonal lanes lack protection from one or more pieces
        # The Row spaces the King is on
        rowNegRange = [-1, -2, -3, -4, -5, -6, -7]
        rowPosRange = [1, 2, 3, 4, 5, 6, 7]

        # The Column spaces the king is on
        colNegRange = [-8, -16, -24, -32, -40, -48, -56]
        colPosRange = [8, 16, 24, 32, 40, 48, 56]

        # The Diagonals the king is on
        diagBLRange = [-9, -18, -27, -36, -45, -54, -63]        # Bottom left diagonal
        diagBRRange = [-7, -14, -21, -28, -35, -42, -49]        # Bottom right diagonal
        diagTLRange = [7, 14, 21, 28, 35, 42, 49]               # Top left diagonal
        diagTRRange = [9, 18, 27, 36, 45, 54, 63]               # Top right diagonal

        # Conditions:
        #   If I'm at or one space from an edge, consider me safe unless I spot an enemy.
        #   If I spot an enemy first, consider me NOT safe.
        #   If I spot an ally first, consider me safe.
        myProtection = 0
        theirProtection = 0

        for king in myKings:
            for dif in colNegRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64:
                    if king + dif in allTheirPieces:
                        break
                    elif king + dif in allMyPieces:
                        myProtection = myProtection + 1
                        break
                elif colNegRange.index(dif) < 1:
                    myProtection = myProtection + 1
                    break
                else:
                    break

            for dif in colPosRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64:
                    if king + dif in allTheirPieces:
                        break
                    elif king + dif in allMyPieces:
                        myProtection = myProtection + 1
                        break
                elif colPosRange.index(dif) < 1:
                    myProtection = myProtection + 1
                    break
                else:
                    break

            for dif in rowNegRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and math.floor(king + dif / 8) == math.floor(king / 8):
                    if king + dif in allTheirPieces:
                        break
                    elif king + dif in allMyPieces:
                        myProtection = myProtection + 1
                        break
                elif rowNegRange.index(dif) < 1:
                    myProtection = myProtection + 1
                    break
                else:
                    break

            for dif in rowPosRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and math.floor(king + dif / 8) == math.floor(king / 8):
                    if king + dif in allTheirPieces:
                        break
                    elif king + dif in allMyPieces:
                        myProtection = myProtection + 1
                        break
                elif rowPosRange.index(dif) < 1:
                    myProtection = myProtection + 1
                    break
                else:
                    break

            for dif in diagTLRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and abs(math.floor(king + dif / 8) - math.floor(king / 8)) == diagTLRange.index(dif) + 1:
                    if king + dif in allTheirPieces:
                        break
                    elif king + dif in allMyPieces:
                        myProtection = myProtection + 1
                        break
                elif diagTLRange.index(dif) < 1:
                    myProtection = myProtection + 1
                    break
                else:
                    break

            for dif in diagTRRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and abs(math.floor(king + dif / 8) - math.floor(king / 8)) == diagTRRange.index(dif) + 1:
                    if king + dif in allTheirPieces:
                        break
                    elif king + dif in allMyPieces:
                        myProtection = myProtection + 1
                        break
                elif diagTRRange.index(dif) < 1:
                    myProtection = myProtection + 1
                    break
                else:
                    break

            for dif in diagBLRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and abs(math.floor(king + dif / 8) - math.floor(king / 8)) == diagBLRange.index(dif) + 1:
                    if king + dif in allTheirPieces:
                        break
                    elif king + dif in allMyPieces:
                        myProtection = myProtection + 1
                        break
                elif diagBLRange.index(dif) < 1:
                    myProtection = myProtection + 1
                    break
                else:
                    break

            for dif in diagBRRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and abs(math.floor(king + dif / 8) - math.floor(king / 8)) == diagBRRange.index(dif) + 1:
                    if king + dif in allTheirPieces:
                        break
                    elif king + dif in allMyPieces:
                        myProtection = myProtection + 1
                        break
                elif diagBRRange.index(dif) < 1:
                    myProtection = myProtection + 1
                    break
                else:
                    break

        for king in theirKings:
            for dif in colNegRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64:
                    if king + dif in allMyPieces:
                        break
                    elif king + dif in allTheirPieces:
                        theirProtection = theirProtection + 1
                        break
                elif colNegRange.index(dif) < 1:
                    theirProtection = theirProtection + 1
                    break
                else:
                    break

            for dif in colPosRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64:
                    if king + dif in allMyPieces:
                        break
                    elif king + dif in allTheirPieces:
                        theirProtection = theirProtection + 1
                        break
                elif colPosRange.index(dif) < 1:
                    theirProtection = theirProtection + 1
                    break
                else:
                    break

            for dif in rowNegRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and math.floor(king + dif / 8) == math.floor(king / 8):
                    if king + dif in allMyPieces:
                        break
                    elif king + dif in allTheirPieces:
                        theirProtection = theirProtection + 1
                        break
                elif rowNegRange.index(dif) < 1:
                    theirProtection = theirProtection + 1
                    break
                else:
                    break

            for dif in rowPosRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and math.floor(king + dif / 8) == math.floor(king / 8):
                    if king + dif in allMyPieces:
                        break
                    elif king + dif in allTheirPieces:
                        theirProtection = theirProtection + 1
                        break
                elif rowPosRange.index(dif) < 1:
                    theirProtection = theirProtection + 1
                    break
                else:
                    break

            for dif in diagTLRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and abs(math.floor(king + dif / 8) - math.floor(king / 8)) == diagTLRange.index(dif) + 1:
                    if king + dif in allMyPieces:
                        break
                    elif king + dif in allTheirPieces:
                        theirProtection = theirProtection + 1
                        break
                elif diagTLRange.index(dif) < 1:
                    theirProtection = theirProtection + 1
                    break
                else:
                    break

            for dif in diagTRRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and abs(math.floor(king + dif / 8) - math.floor(king / 8)) == diagTRRange.index(dif) + 1:
                    if king + dif in allMyPieces:
                        break
                    elif king + dif in allTheirPieces:
                        theirProtection = theirProtection + 1
                        break
                elif diagTRRange.index(dif) < 1:
                    theirProtection = theirProtection + 1
                    break
                else:
                    break

            for dif in diagBLRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and abs(math.floor(king + dif / 8) - math.floor(king / 8)) == diagBLRange.index(dif) + 1:
                    if king + dif in allMyPieces:
                        break
                    elif king + dif in allTheirPieces:
                        theirProtection = theirProtection + 1
                        break
                elif diagBLRange.index(dif) < 1:
                    theirProtection = theirProtection + 1
                    break
                else:
                    break

            for dif in diagBRRange:
                # Ensure space difference is valid and doesn't extend outside desired range
                if king + dif >= 0 and king + dif < 64 and abs(math.floor(king + dif / 8) - math.floor(king / 8)) == diagBRRange.index(dif) + 1:
                    if king + dif in allMyPieces:
                        break
                    elif king + dif in allTheirPieces:
                        theirProtection = theirProtection + 1
                        break
                elif diagBRRange.index(dif) < 1:
                    theirProtection = theirProtection + 1
                    break
                else:
                    break

        protectionValue = myProtection - theirProtection

        kingSafetyVal = protectionValue + attackerValue + defenderVal + pawnShieldVal + escapeVal

    # Finalize weights, some weights have caps.
    # Activity caps at +/- 1.5
    if activityVal > 1.5:
        activityVal = 1.5
    elif activityVal < -1.5:
        activityVal = -1.5

    # King safety caps at +/- 1 or 2
    if round(kingSafetyVal) > 2:
        kingSafetyVal = 2
    elif round(kingSafetyVal) < -2:
        kingSafetyVal = -1
    elif round(kingSafetyVal) == 0:
        if kingSafetyVal > 0:
            kingSafetyVal = 1
        else:
            kingSafetyVal = -1
    else:
        kingSafetyVal = round(kingSafetyVal)

    totalScore = materialVal + activityVal + kingSafetyVal + controlVal

    return totalScore

# Count Moves
def countMoves(pieces, legalMoves):
    returnResult = 0

    for piece in pieces:
        for move in legalMoves:
            if move.from_square == piece:
                returnResult = returnResult + 1
    return returnResult
