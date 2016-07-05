# Memory Puzzle
# By Sarosh Farhan

import random,pygame,sys
from pygame.locals import *

FPS = 30 # frames per second setting of the game
windoWidth = 640 # size of window's width in pixels
windowHeight = 480 # size of window's height in pixels
revealSpeed = 8 # speed of boxes' sliding reveals and cover
boxSize = 40 # size of box hheight and width in pixels
gapSize = 10 # size of gap between boxes in pixels
boardWidth = 10 #number of columns of icons
boardHeight = 7 # number of rows of icons
assert (boardHeight * boardWidth) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.' #sanity check
XMargin = int((windoWidth - (boardWidth *(boxSize + gapSize))) / 2) #setting margin
YMargin = int((windowHeight - (boardHeight * (boxSize + gapSize)))/ 2) # setting the margin

#            R    G    B
gray     = (100, 100, 100)
navyBlue = ( 60,  60, 100)
white    = (255, 255, 255)
red      = (255,  0,    0)
green    = (  0, 255,   0)
blue     = (  0,   0, 255)
yellow   = (255, 255,   0)
orange   = (255, 128,   0)
purple   = (255,   0, 255)
cyan     = (  0, 255, 255)

bgColor = navyBlue
lightBgColor = gray
boxColor = white
highlightColor = blue

donut = 'donut'
square = 'square'
diamond = 'diamond'
lines = 'lines'
oval = 'oval'

allColors = (red, green, blue, yellow, orange, purple, cyan)
allShapes = (donut, square, diamond, lines, oval)
assert len(allColors) * len(allShapes) * 2 >= boardWidth * boardHeight, "Board is too big for the number of shapes/colors defined." #sanity check again

def main(): # main function of he program
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((windoWidth, windowHeight))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event

    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None #stores the (x,y) of the first box clicked.

    DISPLAYSURF.fill(bgColor)
    startGameAnimation(mainBoard)

    while True: # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(bgColor) #drawing the window
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get(): #event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.type == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)

        if boxx != None and boxy != None:
            # The mouse is currently over a box.
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx, boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True #set the box as "Revealed"
                if firstSelection == None: #the current box was the first box to be clicked
                    firstSelection = (boxx, boxy)
                else: #the current box was the second box clicked. check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        #icons don't match. re-cover up both selections.
                        pygame.time.wait(1000) #wait for 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes): # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        #reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # show the fully unrevealed board for 2 seconds.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(2000)

                        #replay the start game animation.
                        startGameAnimation(mainBoard)
                    firstSelection = None # reset firstSelection variable

     #redraw the screen and wait a clock tick.
    pygame.display.update()
    FPSCLOCK.tick(FPS)

def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(boardWidth):
        revealedBoxes.append([val] * boardHeight)
    return revealedBoxes

def getRandomizedBoard():
    #get a list of every possible shape in every possible color.
    icons = []
    for color in allColors:
        for shape in allShapes:
            icons.append((shape,color))
    random.shuffle(icons) #randomize the order of the icons list
    numIconsUsed = int(boardWidth * boardHeight / 2) #calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2 #make 2 of each
    random.shuffle(icons)

    


