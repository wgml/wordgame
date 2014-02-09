__author__ = 'vka'
import string #letters
import random
from Getch import _Getch
import unicodedata

class Direction:
    HORIZONTAL = 0
    VERTICAL = 1
    DIAGONALRIGHT = 2

class Color:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

class ClearScreen(object):
    def __call__(self):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        return

class Board(object):
    #contains boards, its dimension, list of words with linked coords
    def __init__(self, size):
        self.size = size

        self.board = [[" "] * size for i in range(size)]

        self.words = []

    def addWord(self, word, randomly = True, x = None, y = None):

        #get all possibilities with brute force
        possibilities = []
        #horizontal
        for y in range(self.size):
            for x in range(0, self.size - len(word)):
                startX = x
                possible = True
                for pos in range(len(word)):
                    if self.board[startX + pos][y] != " " and self.board[startX + pos][y] != word[pos]:
                        possible = False
                        break

                if possible:
                    possibilities.append([[startX, y], [startX + len(word) - 1, y], Direction.HORIZONTAL])

        #vectical
        for x in range(self.size):
            for y in range(0, self.size - len(word)):
                startY = y
                possible = True
                for pos in range(len(word)):
                    if self.board[x][startY + pos] != " " and self.board[x][startY + pos] != word[pos]:
                        possible = False
                        break

                if possible:
                    possibilities.append([[x, startY], [x, startY + len(word) - 1], Direction.VERTICAL])

        #diagonal
        for x in range(self.size - len(word)):
            for y in range(self.size - len(word)):
                startX = x
                possible = True
                for pos in range(len(word)):
                    if self.board[x + pos][y + pos] != " " and self.board[x + pos][y + pos] != word[pos]:
                        possible = False
                        break

                if possible:
                    possibilities.append([[x, y], [x + len(word) - 1, y + len(word) - 1], Direction.DIAGONALRIGHT])

        #select random possibility and put word in place
        choice = random.choice(possibilities)
        startPos = choice[0]
        endPos = choice[1]
        style = choice[2]

        pairs = []
        if style == Direction.HORIZONTAL:
            for i in range(startPos[0], endPos[0] + 1):
                pairs.append([i, startPos[1]])
        elif style == Direction.VERTICAL:
            for i in range(startPos[1], endPos[1] + 1):
                pairs.append([startPos[0], i])
        elif style == Direction.DIAGONALRIGHT:
            for i in range(endPos[0] - startPos[0] + 1):
                pairs.append([startPos[0] + i, startPos[1] + i])

        pos = 0
        for pair in pairs:
            self.board[pair[0]][pair[1]] = word[pos]
            pos += 1

        self.words.append({"word": word,
                           "startPos": startPos.copy(),
                           "endPos": endPos.copy(),
                           "found": False })

    def fillRandomly(self):
        #fills empty cells with random txt
        letters = string.ascii_uppercase

        for y in range(self.size):
            for x in range(self.size):
                if self.board[x][y] == " ":
                    # self.board[x][y] = random.choice(letters)
                    self.board[x][y] = 'a'

    def __str__(self, showWords = False):

        if not showWords:
            coords = None

        else:
            coords = []
            for word in self.words:
                start = word["startPos"]
                end = word["endPos"]

                for i in range(len(word["word"])):
                    if end[0] - start[0] == 0:
                        coords.append([start[0], start[1] + i])
                    elif end[1] - start[1] == 0:
                        coords.append([start[0] + i, start[1]])
                    else:
                        coords.append(([start[0] + i, start[1] + i]))

        txt = ' '
        for y in range(self.size):
            txt += '\n'
            for x in range(self.size):
                if showWords == True:
                    if [x, y] in coords:
                        txt += Color.RED + self.board[x][y] + Color.END + ' '
                    else:
                        txt += self.board[x][y] + ' '
                else:
                    txt += self.board[x][y] + ' '

            if y < len(self.words):
                txt += ' ' * 10
                if self.words[y]["found"] == True:
                    txt += Color.GREEN
                else:
                    txt += Color.RED

                txt += self.words[y]["word"] + Color.END
        return txt


class Game(object):
    #contains board, score etc
    #is able to generate game which contain desired words
    #and load random words from file

    def __init__(self, dim = 15):
        self.size = dim

        self.loadedWords = ["word", "test", "another", "much", "words", "blue", "etc"]
        # self.loadedWords = ["a", "b", "c", "d"]
        self.generate(self.loadedWords, dim)

        self.play()

    def generate(self, words = None, size = None):
        #generates board containing desired words
        #if no params given, uses self.loadedWords and self.dim

        if words == None:
            words == self.loadedWords
        if size == None:
            size = self.size

        self.board = Board(size)

        for word in words:
            self.board.addWord(word.upper())

        self.board.fillRandomly()

    def play(self):

        #todo loading from file

        getchar = _Getch()
        cls = ClearScreen()

        print("Welcome!")
        print("Use arrows to move, enter to select first letter of the word and then enter to select last")
        print("Press escape or q to abort.")
        print("Press anykey to start game!")

        c = getchar()
        if c == chr(27) or c == "q":
            print("Goodbye!")
            return

        curPos = [0, 0]
        enterPressed = {}
        enterPressed["state"] = False
        coordsToShow = [curPos]
        cls()

        while c is not chr(27) and c is not "q":

            print("")
            self.showBoard(coordsToShow)
            print("\nWASD to move, ESC od q to quit")
            c = getchar()
            cls()
            if c == 'a' and curPos[0] > 0:
                curPos[0] -= 1
            elif c == 'd' and curPos[0] < self.size - 1:
                curPos[0] += 1
            elif c == 'w' and curPos[1] > 0:
                curPos[1] -= 1
            elif c == 's' and curPos[1] < self.size - 1:
                curPos[1] += 1
            elif c == chr(13):
                #enter pressed
                if enterPressed["state"] == False:
                    enterPressed["state"] = True
                    enterPressed["coords"] = [curPos.copy()]
                    enterPressedStartingCoords = curPos.copy()
                else:
                    enterPressed["state"] = False
                    enterPressed["coords"] = []
                    coordsToShow = [curPos]

                    #check if word is fully contained in desired
                    for word in range(len(self.board.words)):
                        if self.board.words[word]["startPos"] in [enterPressedStartingCoords, curPos] \
                                and self.board.words[word]["endPos"] in [curPos, enterPressedStartingCoords]:
                            #word found!
                            self.board.words[word]["found"] = True
                            break

            if enterPressed["state"] == True:
                if curPos not in enterPressed["coords"]:
                    enterPressed["coords"].append(curPos.copy())
                #prepare coords
                start = enterPressed["coords"][0].copy()
                end = curPos.copy()
                coordsToShow = []
                if start[0] == end[0]:
                    #vertical
                    coordsToShow = []
                    for i in range(min(start[1], end[1]), max(start[1], end[1]) + 1):
                        coordsToShow.append([start[0], i])
                elif start[1] == end[1]:
                    #horizontal
                    coordsToShow = []
                    for i in range(min(start[0], end[0]), max(start[0], end[0]) + 1):
                        coordsToShow.append([i, start[1]])
                elif abs(end[1] - start[1]) == abs(end[0] - start[0]):
                    #diagonal
                    coordsToShow = []
                    for i in range(abs(start[0] - end[0]) + 1):
                        if end[0] > start[0] and end[1] > start[1]:
                            #top right
                            coordsToShow.append([start[0] + i, start[1] + i])
                        elif end[0] > start[0] and end[1] < start[1]:
                            #bottom right
                            coordsToShow.append([start[0] + i, start[1] - i])
                        elif end[0] < start[0] and end[1] < start[1]:
                            #bottom left
                            coordsToShow.append([start[0] - i, start[1] - i])
                        else:
                            #top left
                            coordsToShow.append([start[0] - i, start[1] + i])
                else:
                    coordsToShow = [curPos.copy(), start.copy()]

            #check if all words were found
            all = True
            for word in self.board.words:
                if word["found"] == False:
                    all = False
                    break

            if all:
                cls()
                print("Gratz! All words were found!")
                self.showBoard()

                print("\nWanna play again?(Y/n)")
                c = getchar()
                if c != 'n' and c != 'N':
                    cls()
                    Game(self.size)
                return

    def showBoard(self, coords = None):
        foundCoords = []
        for word in self.board.words:
            if word["found"] == True:
                start = word["startPos"]
                end = word["endPos"]

                for i in range(len(word["word"])):
                    if end[0] - start[0] == 0:
                        foundCoords.append([start[0], start[1] + i])
                    elif end[1] - start[1] == 0:
                        foundCoords.append([start[0] + i, start[1]])
                    else:
                        foundCoords.append(([start[0] + i, start[1] + i]))

        txt = " " * 10 + "BOARD" + " " * 15 + "WORDS"
        for y in range(self.size):
            txt += '\n'
            for x in range(self.size):
                if coords is not None and ([x, y]) in coords:
                    txt += Color.PINK + self.board.board[x][y] + Color.END + ' '
                elif [x, y] in foundCoords:
                    txt += Color.GREEN + self.board.board[x][y] + Color.END + ' '
                else:
                    txt += self.board.board[x][y] + ' '

            if y < len(self.board.words):
                txt += ' ' * 10
                if self.board.words[y]["found"] == True:
                    txt += Color.GREEN
                else:
                    txt += Color.RED

                txt += self.board.words[y]["word"] + Color.END

        print(txt)
if __name__ == "__main__":
    game = Game(10)
    # ch = _Getch()
    # v = ch()
