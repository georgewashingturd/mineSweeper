import random
import sys
import os


'''
GUI stuffs   :) 
'''
from ctypes import *
import msvcrt
 
STD_OUTPUT_HANDLE = -11
 
class COORD(Structure):
    pass
COORD._fields_ = [("X", c_short), ("Y", c_short)]

class CURSORINFO(Structure):
    pass
CURSORINFO._fields_ = [("size", c_int), ("visible", c_byte)]

class SMALLRECT(Structure):
    pass
SMALLRECT._fields_ = [("left", c_short), ("top", c_short),("right", c_short), ("bottom", c_short)]
    
class CONSOLESCREENBUFFERINFO(Structure):
    pass
CONSOLESCREENBUFFERINFO._fields_ = [("size", COORD), ("cursorposition", COORD), ("attributes", c_short), ("window",SMALLRECT), ("maxwindowsize",COORD)]


FG_BLUE = 0x00000001
FG_GREEN = 0x00000002
FG_RED = 0x00000004
FG_INTENSITY = 0x00000008
FG_WHITE = FG_BLUE | FG_GREEN | FG_RED  
         
BG_BLUE = 0x00000010
BG_GREEN = 0x00000020
BG_RED = 0x00000040
BG_INTENSITY = 0x00000080
BG_WHITE = BG_BLUE | BG_GREEN | BG_RED


h = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def getConsoleSize():
    csbi = CONSOLESCREENBUFFERINFO()
    windll.kernel32.GetConsoleScreenBufferInfo(h, byref(csbi))
    return csbi.window.right - csbi.window.left, csbi.window.bottom - csbi.window.top

def setCursorSize(s):
    global h
    ci = CURSORINFO()
    windll.kernel32.GetConsoleCursorInfo(h, byref(ci))
    ci.size = s
    windll.kernel32.SetConsoleCursorInfo(h, byref(ci))
    
def setCursorLocation(r, c):
    global h
    windll.kernel32.SetConsoleCursorPosition(h, COORD(c, r))
    
                
def printAt(r, c, s, color=FG_WHITE):
    setCursorLocation(r,c)
    c = s.encode("windows-1252")
    windll.kernel32.SetConsoleTextAttribute(h, color)
    windll.kernel32.WriteConsoleA(h, c_char_p(c), len(c), None, None)

def printWindowsString(s, color=FG_WHITE):
    c = s.encode("windows-1252")
    windll.kernel32.SetConsoleTextAttribute(h, color)
    windll.kernel32.WriteConsoleA(h, c_char_p(c), len(c), None, None)
    
    
    
    
    
    
    
    
    
    
    
    
# default values
row = 5
col = 5
mines = 5
marker = mines

maxRow = 20
maxCol = 20
maxMines = 50


# to check if user wins 
revealed = 0

# easier for debugging we can just use a dictionary for the mine list
# since the board is limited to 20 x 20 we can use multiple boards like this
# countBoard makes it easier for us to check if a tile is empty or not
mineBoard = [[0 for _ in range(col)] for _ in range(row)]
countBoard = [[0 for _ in range(col)] for _ in range(row)]
displayBoard = [["H" for _ in range(col)] for _ in range(row)]


# to make it easier to iterate through all neighbours
dr = [-1,-1,-1,0,0,1,1,1]
dc = [-1,0,1,-1,1,-1,0,1]

numOfNeighbors = 8

hiddenSpot = "H"
emptySpot = " "
flagSpot = "F"
mineSpot = "*"


'''
for GUI 
'''

rowCursor = 0
colCursor = 0

rowCursor = 0
colCursor = 0

minRowCursor = 0
minColCursor = 0

maxRowCursor = 10
maxColCursor = 10

UP = 0x48
DOWN = 0x50
LEFT = 0x4b
RIGHT = 0x4d

ESC = 0x1b
CTRLC = 0x03

SPACE = 0x20
M = 0x6d


def exitMineSweeper():
    global maxRowCursor, maxColCursor
    windll.kernel32.SetConsoleTextAttribute(h, FG_WHITE)
    setCursorLocation(maxRowCursor + 3, maxColCursor)
    sys.exit()
    
# update the number of neighbouring mines
def updateCountBoard(r,c):
    for i in range(numOfNeighbors):
        nr = r + dr[i]
        nc = c + dc[i]

        if 0 <= nr < row and 0<= nc < col:
            countBoard[nr][nc] += 1

# prepare the mines and the counBoard
def prepareBoard():
    mineDict = {}
    i = mines
    while i:
        r = random.randint(0,row-1)
        c = random.randint(0,col-1)
        if (r,c) not in mineDict:
            mineDict[(r,c)] = 1
            mineBoard[r][c] = 1
            updateCountBoard(r,c)
            i -= 1

def updateBoard(r,c,s):
    global displayBoard
    
    displayBoard[r][c] = s
    
    color = FG_WHITE
    if str(displayBoard[r][c]) == hiddenSpot:
        color = FG_INTENSITY | FG_BLUE
    elif str(displayBoard[r][c]) == flagSpot or str(displayBoard[r][c]) == mineSpot:
        color = FG_INTENSITY | FG_RED
    elif str(displayBoard[r][c]).isdigit():
        color = FG_INTENSITY | FG_GREEN
    
    displayRow = r + 1
    displayCol = (c + 1) * 3
    setCursorLocation(displayRow, displayCol)
    printWindowsString(" %2s" % displayBoard[r][c], color = color)
    
    
    
            
# expand the display board when user chooses an empty board
def expandBoard(r,c):
    global row, col, revealed, countBoard, displayBoard
    
    # bfs traversal

    # v is visited dist
    v = {}
    # q is used to do bfs
    q = [(r,c)]

    # update visited dict
    v[(r,c)] = 1
    l = len(q)
    
    while q:
        # find children
        n = q.pop(0)
        for j in range(numOfNeighbors):
            nr = n[0] + dr[j]
            nc = n[1] + dc[j]
            if (nr,nc) not in v:
                v[(nr,nc)] = 1
                if 0 <= nr < row and 0<= nc < col:
                    # we don't want to double count
                    if displayBoard[nr][nc] == hiddenSpot:
                        revealed += 1
                        # if tile is empty put in q so that we can continue bfs
                        if not countBoard[nr][nc]:
                            updateBoard(nr, nc, emptySpot)
                            q.append((nr,nc))
                        # if tile is not empty just display it but don't put in q
                        # because we are done 
                        else:
                            updateBoard(nr, nc, str(countBoard[nr][nc]))
'''              
def printBoard(board):
    global marker
    
    # print col header
    s = ""
    s += "   "
    for i in range(1,col+1):
        s += " %2d" % (i)

    s += "\n"

    # print row by row 
    for r in range(row):
        s += " %2d" % (r+1)
        for c in range(col):
            s += " %2s" % board[r][c]
        s += "\n"

    s += "\n mines: %3d" % (marker)
    printAt(0,0,s)
    setCursorLocation(rowCursor, colCursor)
'''
    
    
def printBoard(board):
    global marker
    
    # print col header
    setCursorLocation(0, 0)
    printWindowsString("   ")
    for i in range(1,col+1):
        printWindowsString( " %2d" % (i) , color=FG_INTENSITY | FG_WHITE)

    printWindowsString ("\n")

    # print row by row 
    for r in range(row):
        printWindowsString (" %2d" % (r+1) , color=FG_INTENSITY | FG_WHITE)
        for c in range(col):
            color = FG_WHITE
            if str(board[r][c]) == hiddenSpot:
                color = FG_INTENSITY | FG_BLUE
            elif str(board[r][c]) == flagSpot or str(board[r][c]) == mineSpot:
                color = FG_INTENSITY | FG_RED
            elif str(board[r][c]).isdigit():
                color = FG_INTENSITY | FG_GREEN
            
            printWindowsString(" %2s" % board[r][c], color = color)
        printWindowsString ("\n")

    printWindowsString ("\n mines: %3d" % (marker) , color=FG_INTENSITY | FG_WHITE)
    
    setCursorLocation(rowCursor, colCursor)

    
    
def printLoseBoard():
    # reveal all mines 
    for r in range(row):
        for c in range(col):
            if mineBoard[r][c]:
                updateBoard(r, c, mineSpot)


def checkWinLose(r,c):
    global revealed, marker 

    if displayBoard[r][c] != hiddenSpot and displayBoard[r][c] != flagSpot:
        return 0
        
    # check if mine is selected
    if mineBoard[r][c]:
        return -1


    # prevent double count
    if displayBoard[r][c] == hiddenSpot or displayBoard[r][c] == flagSpot:
        revealed += 1
    
    if displayBoard[r][c] == flagSpot:
        marker += 1
        
    # empty cell
    if not countBoard[r][c]:
        updateBoard(r, c, emptySpot)
        expandBoard(r,c)
    # non empty cell
    else:
        updateBoard(r, c, str(countBoard[r][c]))
        
    # check for win
    if revealed == row*col - mines:
        return 1

    return 0

def updateMarkDisplay():
    displayRow = maxRowCursor
    displayCol = 2
    setCursorLocation(displayRow, displayCol)
    printWindowsString ("\n mines: %3d" % (marker) , color=FG_INTENSITY | FG_WHITE)
    
    
def handleMark(r, c):
    global marker

    if displayBoard[r][c] == flagSpot:
        marker += 1
        updateBoard( r, c, hiddenSpot)
    elif displayBoard[r][c] == hiddenSpot:
        marker -= 1
        updateBoard(r, c, flagSpot)
        

    
def getUserInput():
    global rowCursor, colCursor, minRowCursor, maxRowCursor, minColCursor, maxColCursor
    '''
    # array index starts with 0 so minus 1 
    r = int(raw_input("Enter row: ")) - 1
    c = int(raw_input("Enter col: ")) - 1
    '''
   
    mark = False
    while True:
        ch = msvcrt.getch()
        if ch[0] in [0x00, 0xe0]:  # arrow or function key prefix?
            ch = msvcrt.getch()
            if ch[0] == UP:
                rowCursor = max(minRowCursor, rowCursor -1)
            elif ch[0] == DOWN:
                rowCursor = min (maxRowCursor, rowCursor + 1)
            elif ch[0] == LEFT:
                colCursor = max(minColCursor, colCursor - 1)
            elif ch[0] == RIGHT:
                colCursor = min (maxColCursor, colCursor + 1)
            setCursorLocation(rowCursor, colCursor)
        elif ch[0] == SPACE:
            if (colCursor + 1) % 3 == 0:
                break
        elif ch[0] == M:
            if (colCursor + 1) % 3 == 0:
                mark = True
                break
        elif ch[0] == ESC:
            exitMineSweeper()
        else:
            # print (''.join('{:02x}'.format(x) for x in ch))
            pass  
        
    # check win lose and update board 
    r = rowCursor - 1
    c = (colCursor - 3)//3
    
    if mark:
        handleMark(r, c)
    else:
        w = checkWinLose(r,c)
        if w == -1:
            printLoseBoard()
            exitMineSweeper()
        elif w == 1:
            exitMineSweeper()
    
    updateMarkDisplay()
    setCursorLocation(rowCursor, colCursor)
    




def main():
    global row, col, mines, marker, mineBoard, countBoard, displayBoard, rowCursor, colCursor, minRowCursor, maxRowCursor, minColCursor, maxColCursor
    # there are three arguments (optional) row col and number of mines
    # if not provided it defaults to 5 5 5 
    
    X,Y = getConsoleSize()
    
    maxRow = min(Y - 5, 99)
    maxCol = min((X - 3)//3 - 1, 99)
    
    l = len(sys.argv)
    if l == 4:
        row = min(abs(int(sys.argv[1])),maxRow)
        col = min(abs(int(sys.argv[2])),maxCol)
        maxMines = (row*col) // 2
        mines = min(abs(int(sys.argv[3])),maxMines)
        marker = mines

    # check if playable
    if mines >= row*col:
        print ("not playable")
        return

    # re adjust board based on userinput
    mineBoard = [[0 for _ in range(col)] for _ in range(row)]
    countBoard = [[0 for _ in range(col)] for _ in range(row)]
    displayBoard = [["H" for _ in range(col)] for _ in range(row)]
    
    
    os.system("cls")

    prepareBoard()
    
    # for debugging should be turned off
    #printBoard(mineBoard)
    #printBoard(countBoard)
    
    printBoard(displayBoard)
    
    maxRowCursor = row + 1
    maxColCursor = (col + 1) * 3
    setCursorSize(100)
    setCursorLocation(rowCursor, colCursor)

    while True:
        getUserInput()
    
        
if __name__ == "__main__":
    main()



    
    
