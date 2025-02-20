import sympy as sy
import json

## Data for creating equations is formated as such:

## //x,y,a

## x and y are the names of two teams
## a is (score of team x - score of team y)


## teams are the variables for the matrix
teams = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U']

## List of massey equation rows
MASSEY_PATH = "sportsData.txt"
## Formatted list of game data
GAMES_PATH = "gameTriples.txt"


class Game():
    def __init__(self, charP, charN, dif):
        ## player 1 is called p because it is  positive in the row
        ## player 2 is called n because it is negitive in the row
        self.p = charP
        self.n = charN
        self.d = dif

    ## creates a row for the equation: Rplayer1- Rplayer2 = player1 score - player2 score with
    ## all teams as its variables

    def prodRow(self):
        l = []
        for c in teams:
            if c == self.p:
                l.append(1)
            elif c == self.n:
                l.append(-1)
            else:
                l.append(0)
        l.append(self.d)
        return (l)


## class Season will create equations in the form of lists from a file of formated game results; saving lists is supported
## class Season will also create an augmented matrix from a file of formated lists
class Season():
    def __init__(self):

        self.newGames = set()
        self.m = None

    ## .saveGames will append the user created games to the data file
    ## Leaving a "," at the end of the list is unoptimal
    def saveNewGames(self):
        open(MASSEY_PATH, "w").close()
        with open(MASSEY_PATH, "a") as data:
            for g in self.newGames:
                data.write(str(g.prodRow()) + ',')

    ## Read the data and package it into the instance's matrix
    ## "," must be trimmed from end of the data and data must be enclosed in "[]"
    def loadMatrix(self):
        with open(MASSEY_PATH, "r") as data:
            d = data.read()
            d = d[:-1]
            d = json.loads('[' + d + ']')
            self.m = sy.Matrix(d)

    ## takes a .txt file with lines formatted as "player1, player2, difference" and create new game classes
    def loadNewGames(self):
        with open(GAMES_PATH, "r") as data:
            for line in data.readlines():
                if line == '\n':
                    pass
                else:
                    pnd = line.replace('\n', '').split(',')
                    g = Game(pnd[0], pnd[1], int(pnd[2]))
                    self.newGames.add(g)

                ## class Calculation takes an augmented matrix as a parameter


## it applys Least Squares Solution and Massey's Method to predict the result of a match between any two players
class Calculation():
    def __init__(self, matrix):

        ## the parameter "matrix" is an augmented matrix of all the game equations

        ## get the shape of the AUGMENTED matrix; m x n + 1
        self.rows, self.columns = matrix.shape

        ## Use Least Squares Solution  AT*Ax = AT*b

        ## grab last column of augmented matrix to get b
        self.b = matrix.col(self.columns - 1)

        ## trim the last row to get matrix A. A is m x n
        self.A = matrix.copy()
        self.A.col_del(self.columns - 1)

        ## get AT*A
        self.AT = self.A.T
        self.ATA = self.AT * self.A

        ## get AT*b
        self.ATb = self.AT * self.b

        ## form augmented matrix [AT*A | AT*b] and find rref to solve for x
        self.LSS = self.ATA.copy().row_join(self.ATb).rref()[0]

        ## through observation, I determined my data set requires Massey's soltion
        ## this may not apply to other data sets, so this section of the program is unsecure

        ## delete the last row of [AT*A | AT*b] with [1 1 ... 1 | 0] and row reduce to find x-hat

        self.MS = self.LSS.copy()
        self.MS.row_del(self.columns - 2)
        self.MS = self.MS.row_insert(self.columns - 2, self.masseyRow())

        ## grab the last row of the sovled augmented matrix to use for later
        self.sol = self.MS.rref()[0].col(self.columns - 1)

    ## simple generated a matrix with 1 row and n columns in the form [1 1 ... 1 | 0]
    def masseyRow(self):
        l = []
        for i in range(0, self.columns - 1):
            l.append(1)
        l.append(0)
        return sy.Matrix([l])

    ## prints each player with their score difference component
    def displaySolutions(self):
        for i in range(self.sol.rows):
            v = str(float(self.sol[i]))
            print('Player ' + teams[i] + ': ' + v)

    ## prints the predicted result of a match
    def getT1vT2(self, T1, T2):
        dif = None
        T1S = None
        T2S = None

        for i in range(self.sol.rows):
            if teams[i] == T1:
                T1S = float(self.sol[i])
            elif teams[i] == T2:
                T2S = float(self.sol[i])

        if T1S > T2S:
            print('Team ', T1, ' will beat team ', T2,
                  ' by ', T1S - T2S, ' points.')
        elif T2S > T1S:
            print('Team ', T2, ' will beat team ', T1,
                  ' by ', T2S - T1S, ' points.')


def main():
    s = Season()
    s.loadNewGames()
    s.saveNewGames()
    s.loadMatrix()
    c = Calculation(s.m)
    c.displaySolutions()

    print('\nJosh v Claudia: ')
    c.getT1vT2('L', 'K')

    print('\nEthan v JP: ')
    c.getT1vT2('A', 'S')

    print('\nJosh v Ethan: ')
    c.getT1vT2('L', 'A')

    print('\nJosh v JP: ')
    c.getT1vT2('L', 'S')

    print('\nEthan v Claudia: ')
    c.getT1vT2('A', 'K')

    print('\nClaudia v JP: ')
    c.getT1vT2('K', 'S')

    print('\nEthan v Liza')
    c.getT1vT2('I', 'A')

    print('\nLiza v Josh')
    c.getT1vT2('I', 'L')

    print('\nLiza v Claudia')
    c.getT1vT2('I', 'K')


main()