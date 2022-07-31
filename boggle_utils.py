import itertools
from boggle_board_randomizer import *


def load_words_dict(file_path):
    """A function that unpacks a word file into a dictionary of words and a default value of 'True' for each word."""
    with open(file_path) as data_file:
        words_dict = {}
        for line in data_file:
            word = line.strip()
            words_dict[word] = True
        return words_dict


def is_valid_path(board, path, words):
    """A function that returns a word if a path given is valid and the word chosen is in word database.
     If the path is invalid or the word doesn't exist, function returns None."""
    word = _build_valid_word(board, path)
    if word in words:
        return word
    return None


def _build_valid_word(board, path):
    """A helper function that tests if a path is valid. Function tests 2 things: (1) if the next coordinate in path is a legal selection, and (2) if the letter hasn't been chosen yet.
     If all three tests pass, the selected letter is added to the word. Word is returned in all cases."""
    word = ""
    last_coord = None
    cur_list = []
    for coord in path:
        if _is_next_to(last_coord, coord) and coord not in cur_list:
            letter = board[coord[0]][coord[1]]
            word += letter
            last_coord = coord
            cur_list.append(coord)
        else:
            break
    return word


def _is_next_to(cord1, cord2):
    """A helper function that calculates if a coordinate can be chosen after another coordinate.
    Coordinate must be adjacent to previous coordinate in any of 8 directions (u,d,l,r,ur,ul,dr,dl)."""
    if cord1 is None:
        return True
    if cord1[0] != cord2[0] and cord1[0] != cord2[0]-1 and cord1[0] != cord2[0]+1:
        return False
    if cord1[1] != cord2[1] and cord1[1] != cord2[1]-1 and cord1[1] != cord2[1]+1:
        return False
    return True


def find_length_n_words(n, board, words):
    """A function that finds all legal words on the board of 'n' length. The function returns a list of tuple,
    where each tuple contains the word found and the words path (list of coordinates) on the board.
    The function builds the said list from the dictionary of words."""
    for word in words:
        _remove_wrong_length(n, word, words)
        if words[word] is True:
            _check_word_by_letter(board, word, words)
    # Creates tuple list from dictionary
    tuple_list = _build_tuple_list(words)
    _reset_dictionary(words)
    return tuple_list


def _check_word_by_letter(board, word, words):
    """A helper function that tests a word letter by letter to see if it is on the board and legal.
    The function checks if each letter exists on the board, and if the coordinate is valid. """
    count_inc_u = 0
    count_exc_u = 0
    word_paths = []

    for i, letter in enumerate(word):
        count_inc_u += 1
        if letter != 'U' or (letter == 'U' and word[i - 1] != 'Q'):
            count_exc_u += 1
            coord = _get_coord(board, letter)
            # If letter doesnt exist:
            if not coord:
                words[word] = False
                break
            # Add coordinate to path:
            word_paths.extend(coord)
        # Check if coordinate is valid:
        check = _not_valid_letter(board, word_paths, count_inc_u, count_exc_u, word, letter)
        if check is True:  # Not valid letter
            words[word] = False
            break
        if check is False:  # Valid letter
            continue
        words[word] = list(check)  # Valid word


def _get_coord(board, letter):
    """A helper function that finds the coordinates of any given letter on the board."""
    coords = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if letter == 'Q':
                if board[i][j] == letter + 'U':
                    coords.append((i, j))
            elif board[i][j] == letter:
                coords.append((i,j))
    return coords


def _remove_wrong_length(n, word, words):
    """A helper function that changes the value of a word in word dictionary to False if the word doesnt exist."""
    if len(word) != n:
        words[word] = False


def _not_valid_letter(board, word_paths, count_inc_u, count_exc_u, word, letter):
    """A helper function that checks if the letter that is being tested is valid."""
    for path in itertools.combinations(word_paths, count_exc_u):
        path_word = _build_valid_word(board, path)
        path_word = _del_if_q(path_word, letter, count_inc_u)
        valid_word = word[:count_inc_u]
        if path_word == valid_word:
            if path_word == word:
                return path
            return False
    return True


def _del_if_q(path_word, letter, count_inc_u):
    """A helper function that changes the letter 'QU' to 'Q'."""
    if letter == 'Q' and len(path_word) >= count_inc_u:
        path_word = path_word[:count_inc_u-1] + path_word[count_inc_u-1].replace('QU', 'Q')
    return path_word


def _build_tuple_list(words):
    """A helper function that builds the returned list from the dictionary; words that their value is falsed are
    passed over, and words that their value is not false are packaged into a tuple with their coordinates."""
    tuple_list = []
    for word in words:
        if words[word] is not False:
            tuple_list.append((word, words[word]))
    return tuple_list


def _reset_dictionary(words):
    for word in words:
        words[word] = True


if __name__ == '__main__':
    board = randomize_board(LETTERS)
    words = load_words_dict("boggle_dict.txt")
    print(find_length_n_words(5, board, words))