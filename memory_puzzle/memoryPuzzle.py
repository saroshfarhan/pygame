# Memory Puzzle
# By Sarosh Farhan

import random, pygame, sys
from pygame.locals import *

FPS = 30  # frames per second setting of the game
windoWidth = 640  # size of window's width in pixels
windowHeight = 480  # size of window's height in pixels
revealSpeed = 8  # speed of boxes' sliding reveals and cover
boxSize = 40  # size of box height and width in pixels
gapSize = 10  # size of gap between boxes in pixels
boardWidth = 10  # number of columns of icons
boardHeight = 7  # number of rows of icons
assert (
       boardHeight * boardWidth) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'  # sanity check
XMargin = int((windoWidth - (boardWidth * (boxSize + gapSize))) / 2)  # setting margin
YMargin = int((windowHeight - (boardHeight * (boxSize + gapSize))) / 2)  # setting the margin

#            R    G    B
gray = (100, 100, 100)
navyBlue = (60, 60, 100)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
orange = (255, 128, 0)
purple = (255, 0, 255)
cyan = (0, 255, 255)

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
assert len(allColors) * len(
    allShapes) * 2 >= boardWidth * boardHeight, "Board is too big for the number of shapes/colors defined."  # sanity check again


def main():  # main function of he program
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((windoWidth, windowHeight))

    mousex = 0  # used to store x coordinate of mouse event
    mousey = 0  # used to store y coordinate of mouse event

    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None  # stores the (x,y) of the first box clicked.

    DISPLAYSURF.fill(bgColor)
    startGameAnimation(mainBoard)

    while True:  # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(bgColor)  # drawing the window
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():  # event handling loop
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
            if not revealedBoxes[boxx][ boxy] and mouseClicked:
                revealBoxAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True  # set the box as "Revealed"
                if firstSelection == None:  # the current box was the first box to be clicked
                    firstSelection = (boxx, boxy)
                else:  # the current box was the second box clicked. check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # icons don't match. re-cover up both selections.
                        pygame.time.wait(1000)  # wait for 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes):  # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # show the fully unrevealed board for 2 seconds.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(2000)

                        # replay the start game animation.
                        startGameAnimation(mainBoard)
                    firstSelection = None  # reset firstSelection variable

                    # redraw the screen and wait a clock tick.
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(boardWidth):
        revealedBoxes.append([val] * boardHeight)
    return revealedBoxes


def getRandomizedBoard():
    # get a list of every possible shape in every possible color.
    icons = []
    for color in allColors:
        for shape in allShapes:
            icons.append((shape, color))
    random.shuffle(icons)  # randomize the order of the icons list
    numIconsUsed = int(boardWidth * boardHeight / 2)  # calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2  # make 2 of each
    random.shuffle(icons)

    # create the board data sructure, with randomly placed icon.
    board = []
    for x in range(boardWidth):
        column = []
        for y in range(boardHeight):
            column.append((icons[0]))
            del icons[0]  # remove the icons as we assign them
        board.append(column)
    return board


def splitIntoGroupsOf(groupSize, theList):
    # splits lists into lists of lists, where the inner lists have ay most groupize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(boxx, boxy):
    # conver board coordinates to pixel coordinates
    left = boxx * (boxSize + gapSize) + XMargin
    top = boxy * (boxSize + gapSize) + YMargin
    return (left, top)


def getBoxAtPixel(x, y):
    for boxx in range(boardWidth):
        for boxy in range(boardHeight):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, boxSize, boxSize)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def drawIcon(shape, color, boxx, boxy):
    quarter = int(boxSize * 0.25)  # syntactic sugar
    half = int(boxSize * 0.5)  # syntactic sugar

    left, top = leftTopCoordsOfBox(boxx, boxy)  # get pixel coords from bord coords
    # draw the shapes
    if shape == donut:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSURF, bgColor, (left + half, top + half), quarter - 5)
    elif shape == square:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, boxSize - half, boxSize - half))
    elif shape == diamond:
        pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left
                                                                      + boxSize - 1, top + half),
                                                 (left + half, top + boxSize - 1), (left, top +
                                                                                    half)))
    elif shape == lines:
        for i in range(0, boxSize, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURF, color, (left + i, top + boxSize - 1), (left + boxSize - 1, top + i))
    elif shape == oval:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, boxSize, half))


def getShapeAndColor(board, boxx, boxy):
    # shape value for x,y spot is stored in board[x][y][0]
    # color value for x,y spot is stored in board[x][y][1]
    return board[boxx][boxy][0], board[boxx][boxy][1]


def drawBoxCovers(board, boxes, coverage):
    # draws boxes being covred/revealed. "boxes" is a list of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, bgColor, (left, top, boxSize, boxSize))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0:  # only draw the cover if there is a coverage
            pygame.draw.rect(DISPLAYSURF, boxColor, (left, top, coverage, boxSize))
            pygame.display.update()
            FPSCLOCK.tick(FPS)


def revealBoxAnimation(board, boxesToReveal):
    # do the "box reveal" animation.
    for coverage in range(boxSize, (-revealSpeed) - 1, -revealSpeed):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # do the "box cover" animation.
    for coverage in range(0, boxSize + revealSpeed, revealSpeed):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # draw all of the boxes in their covered or revealed state
    for boxx in range(boardWidth):
        for boxy in range(boardHeight):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # draw a coverd box.
                pygame.draw.rect(DISPLAYSURF, boxColor, (left, top, boxSize, boxSize))
            else:
                # draw the revealed icon.
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, highlightColor, (left - 5, top - 5, boxSize + 10, boxSize + 10), 4)


def startGameAnimation(board):
    # randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(boardWidth):
        for y in range(boardHeight):
            boxes.append((x, y))
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredboxes = generateRevealedBoxesData(True)
    color1 = lightBgColor
    color2 = bgColor

    for i in range(13):
        color1, color2 = color2, color1  # swap color
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredboxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    # returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False  # return False if any boxes are covered.
        return True


if __name__ == '__main__':
    main()
