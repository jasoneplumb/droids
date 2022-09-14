def Reading():
    from analogio import AnalogIn
    import board
    return 10 * (AnalogIn(board.A3).value * 3.3) / 65536

def Units():
    return 'UV Index'