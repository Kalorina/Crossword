############################### CLASS DEFINITION ##############################

class CrossWord():
    # Dict of possible directions {name: (delta_row, delta_col)}
    directions = {'down': (1, 0), 'right': (0, 1)}

    def __init__(self, grid):
        self.grid = grid
        self.positions = self.get_positions(grid)

    def get_positions(self, grid):
        # Computes list of all possible positions for words.
        # Each position is a touple: (start_row, start_col, length, direction),
        # and length must be at least 2, i.e. positions for a single letter
        # (length==1) are omitted.
        # Note: Currently only for 'down' and 'right' directions.
        def check_line(line):
            res = []
            start_i, was_space = 0, False
            for i in range(len(line)):
                if line[i] == '#' and was_space:
                    was_space = False
                    if i - start_i > 1:
                        res.append((start_i, i - start_i))
                elif line[i] == ' ' and not was_space:
                    start_i = i
                    was_space = True
            return res

        poss = []
        for r in range(len(grid)):
            row = grid[r]
            poss = poss + [(r, p[0], p[1], 'right') for p in check_line(row)]
        for c in range(len(grid[0])):
            column = [row[c] for row in grid]
            poss = poss + [(p[0], c, p[1], 'down') for p in check_line(column)]
        return poss

    def print_grid(self):
        # Pretty prints the crossword
        for row in self.grid:
            print(''.join(row))

    def text_at_pos(self, position):
        # Returns text actually written in specified position.
        dr, dc = self.directions[position[3]]
        r, c = position[0], position[1]
        return ''.join([self.grid[r + i * dr][c + i * dc] for i in range(position[2])])

    def write_word(self, position, word):
        # Writes word to specified position and direction.
        # Note: this method does not check whether the word can be placed into
        # specified position.
        dr, dc = self.directions[position[3]]
        r, c = position[0], position[1]
        for i in range(position[2]):
            self.grid[r + i * dr][c + i * dc] = word[i]

    def can_write_word(self, position, word):
        # Check whether the word can be placed into specified position,
        # i.e. position is empty, or all letters within the position are same
        # as those in the word.
        ### YOUR CODE GOES HERE ###
        pass


############################### SERVICE METHODS ###############################

def load_words(path):
    # Loads all words from file
    return open(path, 'r').read().splitlines()


def load_grids(path):
    # Loads empty grids from file
    raw = open(path, 'r').read().split('\n\n')
    per_rows = [grid.rstrip().split('\n') for grid in raw]
    per_char = [[list(row) for row in grid] for grid in per_rows]
    return per_char


################################### SOLVING ###################################

def solve(crossword, words):
    # Fill the empty spaces in crossword with words
    ### YOUR CODE GOES HERE ###
    pass


################################ MAIN PROGRAM #################################

if __name__ == "__main__":
    ## Load data:
    words = load_words('words.txt')
    grids = load_grids('krizovky.txt')

    ## Examples:
    dummy_grid = [list(s) for s in ['########', '#      #', '#      #', '#      #', '###    #', '#      #', '########']]
    cw = CrossWord(dummy_grid)
    cw.print_grid()  # empty grid
    print('Positions: ' + str(cw.positions))
    cw.write_word((2, 1, 5, 'right'), 'hello')
    cw.write_word((1, 5, 5, 'down'), 'world')
    cw.write_word((4, 3, 4, 'right'), 'milk')
    cw.print_grid()  # 3 words already filled in
    print('Text at position (1,4) down: "' + cw.text_at_pos((1, 4, 5, 'down')) + '"\n\n\n')

    points = [0.5, 1, 1.5, 1.5, 1.5, 2, 2, 2, 2, 2]
    points_so_far = 0
    # Solve crosswords (the last one is a bonus)
    # instead of range(len(grids)) specify in which order do you want your crosswords to be tested
    for i in range(len(grids)):
        print('==== Crossword No.' + str(i + 1) + ' ====')
        cw = CrossWord(grids[i])
        solve(cw, words)
        cw.print_grid()

        points_so_far += points[i]
        print(f'Given all the solved crosswords are correct, you have so far {points_so_far}'
              ' points!')

