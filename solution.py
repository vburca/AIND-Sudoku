assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Create the primary diagonal unit
d1_unit = [r + c for r, c in list(zip(list(rows), list(cols)))]
# Create the secondary diagonal unit
d2_unit = [r + c for r, c in list(zip(list(reversed(rows)), list(cols)))]
# Create the diagonal units, from both primary and secondary diagonals
diagonal_units = [d1_unit, d2_unit]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
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
    # Find all instances of naked twins, going unit by unit 
    # (since a naked pair is defined in the context of a unit)
    for unit in unitlist:
        # first see what boxes have exactly 2 value possibilities
        possible_naked_twins = {}
        for box in unit:
            if len(values[box]) == 2:
                possible_naked_twins.setdefault(values[box], []).append(box)

        # out of all the 2 value possibilities, we only want to get the "naked twins", which
        # are 2 boxes having the same 2 value possibilities
        naked_twins = {vs: bs for vs, bs in possible_naked_twins.items() if len(bs) == 2}
        
        # Eliminate the naked twins as possibilities for their peers within the current unit
        for vs, bs in naked_twins.items():
            # take only 1 box of the 2, doesn't really matter since we are eliminating only
            # in the current unit
            box = bs[0]
            # go through peers (in the current unit), excluding the boxes that are in the naked twin
            for peer in (set(unit) - set(bs)):
                for v in vs:
                    values = assign_value(values, peer, values[peer].replace(v, ''))

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict(zip(boxes, map(check_empty, list(grid))))


def check_empty(box):
  return cols if box == '.' else box

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    for box in values.keys():
      if len(values[box]) == 1:
        for peer in peers[box]:
          values = assign_value(values, peer, values[peer].replace(values[box], ''))
    return values

def only_choice(values):
    for unit in unitlist:
      for digit in cols:
        digit_places = [box for box in unit if digit in values[box]]
        if len(digit_places) == 1:
            values = assign_value(values, digit_places[0], digit)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Use the Only Choice Strategy
        values = only_choice(values)

        # Use the Naked Twins Strategy
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    # Check for previous errors
    if values is False:
        return False

    # Check if we are done
    if all(len(values[box]) == 1 for box in boxes):
        return values
    
    # Choose one of the unfilled squares with the fewest possibilities
    _, box = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for value in values[box]:
        new_values = values.copy()
        # new_values[box] = value
        new_values = assign_value(new_values, box, value)
        attempt = search(new_values)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

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
