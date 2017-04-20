#contains items for visualization
assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'
#http://stackoverflow.com/questions/931092/reverse-a-string-in-python
cols_reversed = cols[::-1]

#a1->b1,b2,b3 / a2->b1,b2,b3 etc..
def cross(a, b):
    return [s+t for s in a for t in b]

#build [A1,A2]..etc
boxes = cross(rows, cols)

#build row labels
row_units = [cross(r, cols) for r in rows]

#build column labels
column_units = [cross(rows, c) for c in cols]

#groups the items into 3x3 squares.
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

#build the full grid
unitlist = row_units + column_units + square_units

#left to right diagonal
lrdiag = []

#right to left diagonal
rldiag = []

def generate_diagonals():
    """Generates the diagonals
    which are used in the diagonal sudokos
    """
    for i in range(0, len(rows)):
        lrdiag.append(rows[i] + cols[i])

    for i in range(0, len(rows)):
        rldiag.append(rows[i] + cols_reversed[i])


#this flag marks whether to sudoku is diagonal or vertical
is_diagonal = True

#if the sudoku is diagonal add the two diagonals to be later considered
if is_diagonal:
    unitlist.append(rldiag)
    unitlist.append(lrdiag)

#build a dictionary which contains the box in which the node is present
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

#get the keys of the peers of each sudoku box
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)



#generate the diagonals
generate_diagonals()


def assign_value(values, box, value):
    """Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())

    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    #get all possible boxes which have length 2
    possible_node_keys = [item for item in values.keys() if len(values[item]) == 2]
    naked_twins_nodes = []

    #get all possible boxes which are peers to one another
    #and are part of the possible nodes array
    for box in possible_node_keys:
        for peer in peers[box]:
            if peer in possible_node_keys and values[peer] == values[box]:
                naked_twins_nodes.append((box, peer))

    #remove both values from all the peers which are
    #part of the peers of both the boxes
    for twins in naked_twins_nodes:
        box1 = twins[0]
        box2 = twins[1]
        #get the intersecting peers
        all_update_peers = peers[box1] & peers[box2]
        for peer_key in all_update_peers:
            if len(values[peer_key]) > 2:
                for remove in values[box1]:
                    #replace continiously to see the results
                    values = assign_value(values, peer_key, values[peer_key].replace(remove, ''))
    return values

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.
    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """

    width = 1+max(len(values[s]) for s in boxes)

    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)

def eliminate(values):
    """If a single box is already solved then it's peers cannot contain the
    value which is present in the box, so remove that value from all
    the peers of the box
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(digit, ''))
    return values

def only_choice(values):
    """If there's only one choice
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """Iterate eliminate() and only_choice().
    If at some point, there is a box with no available values,
    return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after

        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    dict_grid = grid_values(grid)
    result_grid = search(dict_grid)

    return result_grid
    
if __name__ == '__main__':

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
