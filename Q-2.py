from copy import deepcopy
import random

xlim, ylim = 3,3  # board dimensions


class GameState:
    """
    Attributes
    ----------
    _board: list(list)
        Represent the board with a 2d array _board[x][y]
        where open spaces are 0 and closed spaces are 1

    _parity: bool
        Keep track of active player initiative (which
        player has control to move) where 0 indicates that
        player one has initiative and 1 indicates player 2

    _player_locations: list(tuple)
        Keep track of the current location of each player
        on the board where position is encoded by the
        board indices of their last move, e.g., [(0, 0), (1, 0)]
        means player 1 is at (0, 0) and player 2 is at (1, 0)
    """

    def __init__(self, x_dimension=3, y_dimension=3):
        global xlim, ylim
        xlim, ylim = x_dimension, y_dimension
        self._board = [[0] * ylim for _ in range(xlim)]
        self._board[-1][-1] = 1  # block lower-right corner
        # self._board[-1][-2] = 1  # block lower-right corner
        self._parity = 0
        self._player_locations = [None, None]

        # set intial postions for players  make sure that both players start from opposite sides
        # check which postiotni are empty in 1st row and last row
        _empty_spaces_top = [(0, y)
                             for y in range(ylim) if self._board[0][y] == 0]
        _empty_spaces_bottom = [(xlim - 1, y)
                                for y in range(ylim) if self._board[xlim - 1][y] == 0]

        # set player 1 and player 2 at random positions in the top and bottom row respectively
        _player1_location = random.choice(_empty_spaces_top)
        _player2_location = random.choice(_empty_spaces_bottom)

        self._player_locations[0] = _player1_location
        self._player_locations[1] = _player2_location

        # update board with player locations
        # self._board[_player1_location[0]][_player1_location[1]] = 2
        # self._board[_player2_location[0]][_player2_location[1]] = 3

        # TODO: temprarily set player 1 and player 2 at fixed positions
        self._board[0][ylim-1] = 2
        self._board[xlim-1][0] = 3

        self._player_locations[0] = (0, ylim-1)
        self._player_locations[1] = (xlim-1, 0)

    def forecast_move(self, move, print_parities=False):
        """ Return a new board object with the specified move
        applied to the current game state.

        Parameters
        ----------
        move: tuple
            The target position for the active player's next move
        """
        if print_parities:
            print(">>> Parity before: ", self._parity)

        if move not in self.get_legal_moves():
            raise RuntimeError("Attempted forecast of illegal move")
        newBoard = deepcopy(self)
        newBoard._board[move[0]][move[1]] = self._parity + \
            2  # Assign symbol for the current player
        newBoard._player_locations[self._parity] = move
        newBoard._parity ^= 1

        if print_parities:
            print(">>> Parity after: ", newBoard._parity)
        return newBoard

    def __str__(self):
        # Custom string representation for the game board
        board_repr = []
        for row in self._board:
            row_str = ""
            for cell in row:
                if cell == 0:
                    row_str += "O "
                elif cell == 1:
                    row_str += "1 "
                elif cell == 2:
                    row_str += "2 "
                else:
                    row_str += "X "
            board_repr.append(row_str)
        return "\n".join(board_repr)

    def get_legal_moves(self):
        """ Return a list of all legal moves available to the
        active player.  Each player should get a list of all
        empty spaces on the board on their first move, and
        otherwise they should get a list of all open spaces
        in a straight line along any row, column or diagonal
        from their current position. (Players CANNOT move
        through obstacles or blocked squares.)
        """
        loc = self._player_locations[self._parity]
        if not loc:
            return self._get_blank_spaces()
        moves = []
        rays = [(1, 0), (1, -1), (0, -1), (-1, -1),
                (-1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in rays:
            _x, _y = loc
            if 0 <= _x + dx < xlim and 0 <= _y + dy < ylim:
                _x, _y = _x + dx, _y + dy
                if self._board[_x][_y]:
                    continue
                moves.append((_x, _y))
        return moves

    def _get_blank_spaces(self):
        """ Return a list of blank spaces on the board."""
        return [(x, y) for y in range(ylim) for x in range(xlim)
                if self._board[x][y] == 0]

    def get_winner(self):
        """0: draw, 1: player 1 wins, 2: player 2 wins, None if game is not over.
        First one to reach the opposite side wins
        Player 1 wins if he reaches the bottom row
        Player 2 wins if he reaches the top row
        """
        if self._player_locations[0][0] == xlim - 1:
            return 1
        elif self._player_locations[1][0] == 0:
            return 2
        else:
            return 0


def terminal_test(gameState):
    """ Return True if the game is over for the active player
    and False otherwise.
    """
    return not bool(gameState.get_legal_moves())


def min_value(gameState, alpha=float("-inf"), beta=float("inf"), print_value=False):
    """ Return the value for a win (+1) if the game is over,
    otherwise return the minimum value over all legal child
    nodes.
    """

    if gameState.get_winner() == 1:
        return 10
    elif gameState.get_winner() == 2:
        return -10
    elif terminal_test(gameState):
        return -10

    v = float("inf")
    for m in gameState.get_legal_moves():
        v = min(v, max_value(gameState.forecast_move(m), alpha, beta))
        beta = min(beta, v)
        if alpha >= beta:
            break

    if print_value:
        print(">>> Min value: ", v)

    return v


def max_value(gameState, alpha=float("-inf"), beta=float("inf")):
    """ Return the value for a loss (-1) if the game is over,
    otherwise return the maximum value over all legal child
    nodes.
    """

    if gameState.get_winner() == 1:
        return 10
    elif gameState.get_winner() == 2:
        return -10
    elif terminal_test(gameState):
        return -10

    v = float("-inf")
    for m in gameState.get_legal_moves():
        v = max(v, min_value(gameState.forecast_move(m), alpha, beta))
        alpha = max(alpha, v)
        if alpha >= beta:
            break

    return v


def minimax_decision(gameState):
    """ Return the move along a branch of the game tree that
    has the best possible value.  A move is a pair of coordinates
    in (column, row) order corresponding to a legal move for
    the searching player.

    You can ignore the special case of calling this function
    from a terminal state.
    """

    # alpha beta pruning
    alpha = float("-inf")
    beta = float("inf")

    return max(gameState.get_legal_moves(), key=lambda m: min_value(gameState.forecast_move(m) , alpha, beta))
    x= max(gameState.get_legal_moves(), key=lambda m: min_value(gameState.forecast_move(m) , alpha, beta, print_value=True))
    print(">>> Minimax decision: ", x)
    return x

# Implement your AI's move logic here


def ai_move_logic(gameState):
    # Implement your AI's move logic
    # For demonstration, return the first legal move
    # return gameState.get_legal_moves()[0]

    # alpha beta pruning
    alpha = float("-inf")
    beta = float("inf")

    return min(gameState.get_legal_moves(), key=lambda m: max_value(gameState.forecast_move(m) , alpha, beta))


# Initialize the game board
initial_board = GameState(x_dimension=4, y_dimension=4)

# Define symbols for visualization
symbols = {
    0: "O",    # Empty space
    1: "X",    # Blocked space
    2: "1",    # Player 1
    3: "2",    # AI Player (Player 2)
}

print("Initial positions of players: ", initial_board._player_locations)
print("Initial game board: ")
for row in initial_board._board:
    print(" ".join(symbols[cell] for cell in row))


# Main game loop
first_player_moves_left = True
second_player_moves_left = True

while True:

    if not first_player_moves_left and not second_player_moves_left:
        break

    if terminal_test(initial_board):
        initial_board._parity ^= 1
        first_player_moves_left = False
    else:
        player_move = minimax_decision(initial_board)
        initial_board = initial_board.forecast_move(
            player_move, print_parities=False)

        print("Current game board: (After Player 1's move)")
        for row in initial_board._board:
            print(" ".join(symbols[cell] for cell in row))

    if initial_board.get_winner() == 1:
        print("Player 1 wins!")
        break
    elif initial_board.get_winner() == 2:
        print("Player 2 wins!")
        break

    # Player 2's turn

    if terminal_test(initial_board):
        second_player_moves_left = False
        initial_board._parity ^= 1
    else:

        ai_move = ai_move_logic(initial_board)
        initial_board = initial_board.forecast_move(ai_move, print_parities=False)

        print("Current game board: (After Player 2's move)")
        for row in initial_board._board:
            print(" ".join(symbols[cell] for cell in row))


    if initial_board.get_winner() == 1:
        print("Player 1 wins!")
        break
    elif initial_board.get_winner() == 2:
        print("Player 2 wins!")
        break

print("=====================================", end="\n\n")
print("Final game board:")
for row in initial_board._board:
    print(" ".join(symbols[cell] for cell in row))

print("Game over!")



# Player 2 wins!
# O O 1 O
# O O O O
# O O O O
# 2 O O X
