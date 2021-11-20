import copy
import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """ 
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        new_cells = set()
        for c in self.cells:
            if c != cell:
                new_cells.add(c)
            else:
                self.count -= 1
        self.cells = new_cells

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        new_cells = set()
        for c in self.cells:
            if c != cell:
                new_cells.add(c)
        self.cells = new_cells


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """

        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        #The function should add a new sentence to the AI’s knowledge base,
        #  based on the value of cell and count,
        #  to indicate that count of the cell’s neighbors are mines.
        #  Be sure to only include cells whose state is still undetermined in the sentence.

        def create_neighbours(cell):
            neighbours = []
            # pattern we see for cell[0] is first three -1 then 0 then plus 1
            # for cell[1] we can see first -1 second 0 third +1
            for i in range(-1, 2):
                for j in range(-1, 2):
                    neighb = (cell[0] +i, cell[1] +j)
                    # make sure the cells are in the field
                    # when our cell is on a wall or in the corner
                    if neighb[0] >= 0 and neighb[0] <= 7 and neighb[1] >= 0 and neighb[1] <= 7 :
                        if neighb != cell:
                            neighbours.append(neighb)
            return neighbours
        # now we loop through our cells and check if they are mines or safes
        # then we remove the ones that are 

        neighbours = create_neighbours(cell)
        for c in list(neighbours):
            if c in self.mines:
                neighbours.remove(c)
                count -= 1
            if c in self.safes:
                neighbours.remove(c)


        # then we can add a new sentence to our knowledge base 
        # containing the cells and the count
        sentence = Sentence(neighbours, count)
        self.knowledge.append(sentence)

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        
        for knowledge in self.knowledge:
            if knowledge.known_mines():
                [self.mark_mine(cell) for cell in  knowledge.cells]
                
            if knowledge.known_safes():
                [self.mark_safe(cell) for cell in  knowledge.cells]


        ## Remove empty Sentences
        self.knowledge = [k for k in self.knowledge if len(k.cells)]

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        """
        Removing subsets.

        KNOWLEDGE BEFORE   {(0, 3), (1, 3)} = 1 
                           {(2, 1), (0, 3), (2, 3), (2, 2), (1, 3)} = 2

        KNOWLEDGE AFTER    {(0, 3), (1, 3)} = 1 
                           {(2, 1), (2, 3), (2, 2)} = 1
        """
        # TODO i dont like the modifing the thing we loop through  
        for knowledge in self.knowledge:
            for k in self.knowledge: 
                if k.cells.issubset(knowledge.cells) and k is not knowledge:
                    knowledge.cells -= k.cells
                    knowledge.count -= k.count


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        # Check in self.moves_made to see what moves are still left
        # Check in self.safes what what is safe
        for move in self.safes:
            if move not in self.moves_made:
                return move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
         
        possible_moves = []
        for i in range(0, 8):
            for j in range(0, 8):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    possible_moves.append((i,j))
        try:
            return possible_moves[0]
        except:
            return None
