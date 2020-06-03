import curses
import random

# initialization variables
screen = None
width = 79
height = 23
first_letter_code = 97
alphabet_length = 26
unused_letters_x = width//2 - alphabet_length//2
guessed_letters = []

# gameplay variables
ONE_PLAYER = 1
TWO_PLAYER = 2
game_mode = TWO_PLAYER

# phrase variables
phrase_row = 7
phrase = ''

# player variables
players = [
    {'name': 'Player 1', 'wrong': 0},
    {'name': 'Player 2', 'wrong': 0}
]
whose_turn = 0
hang_row = 15
distance_from_edge = 30
distance_player1 = distance_from_edge - len(players[0]['name'])+1
distance_player2 = width - (distance_from_edge + 1)

# Chompy!
chompy_row = height - 1
chompy_open = "(\\ /)~~~( o o )~~~(\\ /)"
chompy_closed = "~(|)~~~~( o o )~~~~(|)~"
chompy_closed_l = "~(|)~~~~( o o )~~~(\\ /)"
chompy_closed_r = "(\\ /)~~~( o o )~~~~(|)~"
chompy_len = len(chompy_open)  # all chompies are the same length
chompy_x = width//2 - chompy_len//2


def show_title():
    """Display the title screen."""
    pass


def show_intro():
    """Display game intro.

    Chompy rises, demonstrates his chompers, and
    returns to his partially submerged resting
    position.
    """
    pass


def show_game():
    """Display the initial game screen."""
    # unused letters row
    update_unused_letters()

    # phrase to solve
    update_phrase()

    str_attr = 0
    # player 1 name, hangman
    if whose_turn == 0:
        str_attr |= curses.A_REVERSE
    screen.addstr(hang_row - 1, distance_player1,
                  players[0]['name'], str_attr)
    screen.hline(hang_row, 1, '=', distance_from_edge)
    update_player(0, num_wrong=0)

    # player 2 name, hangman (if 2-player mode)
    if game_mode == TWO_PLAYER:
        str_attr = 0
        if whose_turn == 1:
            str_attr |= curses.A_REVERSE
        screen.addstr(hang_row - 1, distance_player2,
                      players[1]['name'], str_attr)
        screen.hline(hang_row, distance_player2, '=',
                     distance_from_edge)
        update_player(1, num_wrong=0)

    # Chompy the chompster!
    screen.hline(chompy_row, 1, '~', width-2, curses.A_BOLD)
    screen.addstr(chompy_row, chompy_x,
                  chompy_open, curses.A_BOLD)
    chompy_look(whose_turn)
    screen.refresh()


def init():
    """Initialize the game."""
    guessed_letters.clear()
    update_unused_letters()
    generate_phrase()

    # for a two-player game, randomly choose who goes first
    global whose_turn
    if game_mode == TWO_PLAYER:
        whose_turn = random.choice((0, 1))


def update_unused_letters():
    """Update the list of unused letters."""
    unused_letters = [chr(i) if chr(i) not in guessed_letters
                      else '-'
                      for i in range(first_letter_code,
                      first_letter_code+alphabet_length)]
    screen.addstr(0, unused_letters_x, ''.join(unused_letters),
                  curses.A_BOLD)
    screen.refresh()


def generate_phrase():
    """Generate a new phrase to fill in."""
    global phrase
    # TODO: Actually make this generate various phrases
    # phrase = "What if there is no tomorrow?"
    phrase = 'nnn mm zzz xxx cc v bbbb'


def update_phrase():
    """Update the obscured phrase, with only the
    already-guessed letters revealed.
    """
    obscured_phrase = []
    for char in list(phrase):
        if char.isalnum() and char.lower() not in guessed_letters:
            obscured_phrase.append('_')
        else:
            obscured_phrase.append(char)
    screen.addstr(phrase_row, width//2 - len(phrase)//2,
                  ''.join(obscured_phrase))


def update_player(player_num, num_wrong=0):
    """Update the player's position."""
    x = distance_from_edge if player_num == 0 else distance_player2
    screen.addch(hang_row + 1, x, '|')
    screen.addch(hang_row + 2, x, '|')
    for i in range(1, num_wrong+1):
        screen.addch(hang_row + 2 + i, x, '|')
    if num_wrong <= 3:
        screen.addstr(hang_row + 3 + num_wrong, x - 1, ' O ')
    if num_wrong <= 2:
        screen.addstr(hang_row + 4 + num_wrong, x - 1, '/|\\')
    if num_wrong <= 1:
        screen.addstr(hang_row + 5 + num_wrong, x - 1, '/ \\')
    screen.refresh()


def next_turn():
    global whose_turn

    distances = (distance_player1, distance_player2)
    # remove player name styling from last player
    screen.addstr(hang_row - 1, distances[whose_turn],
                  players[whose_turn]['name'])
    whose_turn ^= 1  # next player's turn
    # add player name styling to next player
    screen.addstr(hang_row - 1, distances[whose_turn],
                  players[whose_turn]['name'], curses.A_REVERSE)
    # Chompy looks in the next player's direction
    chompy_look(whose_turn)


def chompy_look(player_num):
    if player_num == 0:
        # look left
        screen.addch(chompy_row, chompy_x + 10, 'O', curses.A_BOLD)
        screen.addch(chompy_row, chompy_x + 12, 'o', curses.A_BOLD)
    elif player_num == 1:
        # look right
        screen.addch(chompy_row, chompy_x + 10, 'o', curses.A_BOLD)
        screen.addch(chompy_row, chompy_x + 12, 'O', curses.A_BOLD)


def show_outro(losing_player_num):
    """A player has lost. Chomp them!
    Chompy chomps his chomper on the side of the losing
    player. Then, both ropes retract and the winning
    player runs along their name, steps down, and
    continues out of the screen to safety.
    """
    # chomp the losing player
    if losing_player_num == 0:
        # player 1 lost -- chomp the left side
        chompies = (chompy_closed_l, chompy_open)
    else:
        # player 2 lost -- chomp the right side
        chompies = (chompy_closed_r, chompy_open)
    for i in range(1, 11):
        screen.addstr(chompy_row, width//2 - chompy_len//2,
                      chompies[i % 2], curses.A_BOLD)
        chompy_look(losing_player_num)
        curses.napms(150)
        screen.refresh()

    # retract ropes
    distances = (distance_from_edge, distance_player2)
    for i in range(6, 2, -1):
        screen.addch(hang_row + i, distances[losing_player_num], ' ')
        curses.napms(300)
        screen.refresh()
    if game_mode == TWO_PLAYER and losing_player_num == 0:
        # player 2 makes their escape
        len_rope = players[1]['wrong'] + 2
        # pull the player back up to the top
        for i in range(len_rope, 0, -1):
            # screen.addch(hang_row + i, distance_player2, ' ')
            if i <= 5:
                screen.addstr(hang_row + i, distance_player2 - 1, ' O ')
                screen.addstr(hang_row + i + 1, distance_player2 - 1, '/|\\')
            if i <= 4:
                screen.addstr(hang_row + i + 2, distance_player2 - 1, '/ \\')
            if i <= 3:
                screen.addstr(hang_row + i + 3, distance_player2 - 1, '   ')
            curses.napms(300)
            screen.refresh()
        # climb to the top of the platform
        screen.addch(hang_row + 1, distance_player2 - 1, '\\')
        screen.addch(hang_row + 2, distance_player2 - 1, ' ')

    # winning player runs away
    pass

    screen.getch()


def main(stdscr):
    global screen

    curses.curs_set(0)  # do not show the text cursor

    try:
        screen = stdscr.subwin(height, width, 0, 0)
    except curses.error:
        # terminal size too small for subwin height/width, most likely
        raise Exception(
            f"""Terminal window must be at least {height} rows by {width} cols.
            Yours is {curses.LINES} by {curses.COLS}.""")
    screen.box()

    # set up the game screen
    init()
    show_game()

    # begin player turns
    while True:
        c = screen.getch(1, 1)
        char = chr(c)
        if not char.isalpha():
            # ignore non-alpha input
            continue

        if char not in guessed_letters:
            # mark the given letter as used
            guessed_letters.append(char)
            update_unused_letters()
            if char in phrase:
                # correct guess!
                update_phrase()
            else:
                # wrong guess -- lower the player!
                players[whose_turn]['wrong'] += 1
                update_player(whose_turn, players[whose_turn]['wrong'])
                if players[whose_turn]['wrong'] == 4:
                    # game over -- activate Chompy!
                    show_outro(whose_turn)
                    curses.endwin()
                    break
            next_turn()
        else:
            # TODO: user feedback for already-used letter
            pass


if __name__ == '__main__':
    curses.wrapper(main)  # wrapper around program for automatic cleanup
