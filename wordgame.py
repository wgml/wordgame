__author__ = 'vka'
import string #letters
import random
from Getch import _Getch
import terminalsize
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
        if len(possibilities) == 0:
            return
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
                    self.board[x][y] = random.choice(letters)

class Game(object):
    #contains board, score etc
    #is able to generate game which contain desired words
    #and load random words from file

    def __init__(self, dim = 15):
        self.size = dim
        self.board = None
        #self.loadedWords = ["word", "test", "another", "much", "words", "blue", "etc"] #todo
        self.terminalSize = terminalsize.get_terminal_size()
        self.getchar = _Getch()
        self.cls = ClearScreen()

        self.loadWords()

        self.manageMenu()

    def loadWords(self, file = None):
        if file == None:
            file = "words.txt"

        with open(file, 'r') as f:
            print("plik otworzony")
            data = f.read()
            self.loadedWords = data.split()

    def generate(self, words = None, size = None):
        #generates board containing desired words
        #if no params given, uses self.loadedWords and self.dim

        if words == None:
            words = self.loadedWords
        if size == None:
            size = self.size

        self.board = Board(size)

        #select random words from list
        numWords = self.size
        selectedWords = []
        for i in range(numWords):
            selectedWords.append(random.choice(words))
        for word in selectedWords:
            self.board.addWord(word.upper())

        self.board.fillRandomly()

    def manageMenu(self):

        self.cls()

        txt = '/' + '-' * (self.terminalSize[0] - 2) + '\\\n'
        txt += '|' + ' ' * (self.terminalSize[0] - 2) + '|\n'
        txt += '|' + "Simple Wordgame v1".center(self.terminalSize[0] - 2) + '|\n'
        txt += '|' + "Welcome!".center(self.terminalSize[0] - 2) + '|\n'
        txt += '|' + ' ' * (self.terminalSize[0] - 2) + '|\n'
        txt += '|' + "Rules are simple:".center(self.terminalSize[0] - 2) + '|\n'
        txt += '|' + "*) SWv1 generates map, you find all words, you win.".center(self.terminalSize[0] - 2) + '|\n'
        txt += '|' + "Words are being loaded from default file \"words.txt\"".center(self.terminalSize[0] - 2) + '|\n'
        txt += '|' + "Feel free to edit it and add your sets.".center(self.terminalSize[0] - 2) + '|\n'
        txt += '|' + "And....have fun!".center(self.terminalSize[0] - 2) + '|\n'
        txt += ('|' + (' ' * (self.terminalSize[0] - 2) + '|\n')) * (self.terminalSize[1] - 12)
        txt += '|' + "Press any key to start, escape/q key to quit...".rjust(self.terminalSize[0] - 2) + '|\n'
        txt += '\\' + '-' * (self.terminalSize[0] - 2)
        print(txt, end='')
        c = self.getchar()

        while c not in [chr(27), 'q', 'Q']:
            self.generate(self.loadedWords, self.size)
            isWon = self.play()

            txt = '/' + '-' * (self.terminalSize[0] - 2) + '\\\n'
            txt += ('|' + ' ' * (self.terminalSize[0] - 2) + '|\n') * int((self.terminalSize[1] / 2 - 2))
            txt += '|' + "GAME ENDED!".center(self.terminalSize[0] - 2) + "|\n"
            txt += ('|' + ' ' * (self.terminalSize[0] - 2) + '|\n') * int((self.terminalSize[1] / 2 - 2))
            txt += '|' + "Press any key to play again or q/ESC to quit...".rjust(self.terminalSize[0] - 2) + '|\n'
            txt += '\\' + '-' * (self.terminalSize[0] - 2)
            print(txt, end='')
            c = self.getchar()
        self.cls()

    def play(self):

        curPos = [0, 0]
        enterPressed = {}
        enterPressed["state"] = False
        coordsToShow = [curPos.copy()]
        allFound = False
        self.cls()
        c = ''
        while c not in [chr(27), 'q', 'Q'] and allFound == False:

            txt = '/' + '-' * (self.terminalSize[0] - 2) + '\\\n'
            txt += '|' + ' ' * 10 + "BOARD".center(self.size * 2) + ' ' * 10  + "WORDS" + " " * (self.terminalSize[0] - 27 - self.size * 2) + '|'

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

            for y in range(self.size):
                txt += '\n|' + ' ' * 10
                for x in range(self.size):
                    if ([x, y]) in coordsToShow:
                        txt += Color.PINK + self.board.board[x][y] + Color.END + ' '
                    elif [x, y] in foundCoords:
                        txt += Color.GREEN + self.board.board[x][y] + Color.END + ' '
                    else:
                        txt += self.board.board[x][y] + ' '

                length = 41
                if y < len(self.board.words):
                    if self.board.words[y]["found"] == True:
                        txt += ' ' * 10 + Color.GREEN + self.board.words[y]["word"] + Color.END
                    else:
                        txt += ' ' * 10 + Color.RED + self.board.words[y]["word"] + Color.END
                    length += 10 + len(self.board.words[y]["word"])

                txt += '|'.rjust(self.terminalSize[0] - length)

            txt += '|' + ' ' * (self.terminalSize[0] - 2) + '|\n'
            txt += '|' + "Press WASD to move, ENTER to select and confirm, q od ESC to quit...".rjust(self.terminalSize[0] - 2) + '|\n'
            txt += '\\' + '-' * (self.terminalSize[0] - 2)
            print(txt, end='')

            c = self.getchar()
            self.cls()

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
            else:
                coordsToShow = [curPos.copy()]
            #check if all words were found

            allFound = True
            for word in self.board.words:
                if word["found"] == False:
                    allFound = False
                    break



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
    game = Game(15)
    # ch = _Getch()
    # v = ch()
