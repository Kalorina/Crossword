import time
from datetime import timedelta
import random
from collections import Counter
import copy # for better copy of object
from shapely.geometry import LineString # for finding intersections

# *************************************************************************************
# ********************************* SERVICE METHODS ***********************************
# *************************************************************************************

def load_words(path):
    # Loads all words from file
    raw_words = open(path, 'r').read().splitlines()

    # Keeps all words with more than one char
    words = []
    for w in raw_words:
        if len(w) > 1:
            words.append(w)

    return words


def load_grids(path):
    # Loads empty grids from file
    raw = open(path, 'r').read().split('\n\n')
    per_rows = [grid.rstrip().split('\n') for grid in raw]
    per_char = [[list(row) for row in grid] for grid in per_rows]
    return per_char


def save_grids(solved_grids):
    with open('krizovky_out.txt', 'w') as f:
        for grid in solved_grids:
            for row in grid:
                for item in row:
                    f.write(str(item))
                f.write('\n')
            f.write('\n')


def print_grid(grid):
    # Pretty prints the crossword
    for row in grid:
        print(''.join(row))

# *************************************************************************************
# ********************************* HEURISTIC METHODS *********************************
# *************************************************************************************

# 1st Heuristic -> by length of words
def sort_by_lenght(words):
    return sorted(words, key=len)


# 2nd Heuristic -> by random
def sort_random(words):
    random.shuffle(words)
    return words


# 3rd Heuristic -> by most used letters in given set of words
def sort_by_most_used(words):
    # convert list of strings into a single string
    all_chars = ''.join(words)
    # count the frequency of each character
    char_counter = Counter(all_chars)
    most_common_char = char_counter.most_common(1)[0][0]
    words.sort(key=lambda s: s.index(most_common_char) if most_common_char in s else float('inf'))
    return words


def filter_by_possible_lengths(all_words, possible_words):
    possible_leghts = []
    for w in possible_words:
        if w.length not in possible_leghts:
            possible_leghts.append(w.length)
    print(f'possible lenghts: {possible_leghts}')
    filtered_words = []
    for w in all_words:
        if len(w) in possible_leghts:
            filtered_words.append(w)

    return filtered_words


# *************************************************************************************
# ********************************* CLASSES DEFINITION ********************************
# *************************************************************************************

# Class for word
class Word:
    # # Coordinates:
    # # position of the starting and ending point
    # start_coord = ()
    # end_coord = ()
    #
    #
    # orientation = 0
    #
    # # word length
    # length = 0
    #
    # # value assigned to this word
    # value = ''
    def __init__(self):
        self.start_coord = ()
        self.end_coord = ()

        self.orientation = 0
        # horizontal word -> 0, vertical word -> 1

        self.length = 0
        self.value = ''

# *************************************************************************************
# ********************************* SOLVING CROSSWORD *********************************
# *************************************************************************************

# Check by columns all possible words by char that fit into grid, without value
def find_horizontal_words(grid):
    horizontal_words = []

    for row in range(len(grid)):
        column = 0
        word = Word()
        finished = False
        prev = '#'

        while column <= len(grid[row]) - 1:
            if grid[row][column] == ' ':
                if prev == ' ':
                    word.length += 1
                    prev = ' '
                    if column == len(grid[row]) - 1:
                        if not finished:
                            finished = True
                        word.end_coord = (row, column)
                        prev = '#'
                elif prev == "#":
                    if finished:
                        finished = False
                    word.start_coord = (row, column)
                    word.length += 1
                    prev = ' '

            elif grid[row][column] == '#':
                if prev == ' ':
                    if not finished:
                        finished = True
                    if word.length > 1:
                        word.end_coord = (row, column - 1)
                    else:
                        word = Word()
                    prev = '#'

            if word.length > 1 and finished:
                word.orientation = 0
                horizontal_words.append(word)
                word = Word()
                finished = False

            column += 1

    return horizontal_words


# Check by rows all possible words that fit, without value
def find_vertical_words(grid):
    vertical_words = []
    word = Word()
    started = False

    for column in range(0, len(grid[0])):
        started = False
        for row in range(0, len(grid) - 1):
            if grid[row][column] == ' ' and grid[row + 1][column] == ' ':
                if started == False:
                    started = True
                    word.start_coord = (row, column)

                if row == len(grid) - 2 and started:
                    word.end_coord = (row + 1, column)
                    word.length = word.end_coord[0] - word.start_coord[0] + 1
                    word.orientation = 1
                    vertical_words.append(word)
                    word = Word()
                    started = False
            else:
                if started:
                    word.end_coord = (row, column)
                    word.length = word.end_coord[0] - word.start_coord[0] + 1
                    word.orientation = 1
                    vertical_words.append(word)
                    word = Word()
                    started = False

    return vertical_words


# returns all possible words for the desired variable
def get_possible_words(word, used_words, words):
    possibles_values = []

    for w in words:
        if len(w) == word.length:
            possibles_values.append(w)

    for item in used_words:
        if item.value in possibles_values:
            possibles_values.remove(item.value)

    return possibles_values


def check_intersections(w1, w2):
    line1 = LineString([w1.start_coord, w1.end_coord])
    line2 = LineString([w2.start_coord, w2.end_coord])

    intersection_point = line1.intersection(line2)

    if not intersection_point.is_empty:
        return [intersection_point.coords[0]] #result(float)
    else:
        return []

def check_constraint(item, assigned_variable_list):
    if assigned_variable_list != None:
        for word in assigned_variable_list:
            #if orientation is equal they will never interesect
            if item.orientation != word.orientation:
                intersection = check_intersections(item, word)
                if len(intersection) != 0:
                    if item.orientation == 0: #horizontal
                        if item.value[int(intersection[0][1]-item.start_coord[1])] != word.value[int(intersection[0][0]-word.start_coord[0])]:
                            # print(f' horizontal word: {item.value}')
                            return False
                    else: #vertical
                        if item.value[int(intersection[0][0]-item.start_coord[0])] != word.value[int(intersection[0][1]-word.start_coord[1])]:
                            # print(f'vertival word: {item.value}')
                            return False
    return True


def backtracking(used_words, not_used_words, words):
    #print(f'backtracking')
    # there are no variables to assign a value
    if len(not_used_words) == 0:
        return used_words

    word = not_used_words[0]
    possible_words = get_possible_words(word, used_words, words)

    for w in possible_words:
        # we create the variable check_var to do the checking
        # and avoid assigning values which do not comply with the constraint
        check_var = copy.deepcopy(word)
        check_var.value = w
        if check_constraint(check_var, used_words):
            word.value = w
            #print(f'word: {word.value}')
            result = backtracking(used_words + [word], not_used_words[1:], words)
            if result != None:
                return result
            # we've reached here because the choice we made by putting some 'word' here was wrong
            # hence now leave the word cell unassigned to try another possibilities
            word.value = ''

    return None


def insert_word_to_puzzle(crossword, word, coord, orientation):
    pos_count = 0
    for char in word:
        if orientation == 0: #horizontal == 0
            crossword[coord[0]][coord[1]+pos_count] = char
        else: #vertical == 1
            crossword[coord[0]+pos_count][coord[1]] = char
        pos_count += 1
    return crossword


# *************************************************************************************
# ********************************* MAIN PROGRAM **************************************
# *************************************************************************************

if __name__ == "__main__":
    # Data Loading:
    words = load_words('words.txt')
    print('Puzzle loaded.')
    grids = load_grids('krizovky.txt')
    print('Grids loaded.')

    print('SOLVING CROWSSWORDS')
    itr = 1
    for grid in grids:
        print(f'Grid no. {itr}:')
        print_grid(grid)

        print('Using heuristics')
        words = sort_by_lenght(words)
        horizontal_words = find_horizontal_words(grid)
        print('Horizontal words checked')
        vertical_words = find_vertical_words(grid)
        print('Vertical words checked')
        total_words = horizontal_words + vertical_words
        print('Using heuristic - filter')
        words = sort_by_most_used(words)
        filtered_words = filter_by_possible_lengths(words, total_words)
        print(len(filtered_words))
        new_words = sort_by_most_used(filtered_words)

        used_words = []
        print('Backtraking...')
        start_time = time.time()
        print(timedelta(seconds=start_time))
        possible_solution = backtracking(used_words, total_words, filtered_words)

        end_time = time.time()
        print(timedelta(seconds=end_time))
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time/60}")

        if possible_solution is None:
            print('No solution found')
        else:
            for word in possible_solution:
                insert_word_to_puzzle(grid, word.value, word.start_coord, word.orientation)

        print_grid(grid)
        itr += 1
        print()

    save_grids(grids)
    print('Grids Saved')
