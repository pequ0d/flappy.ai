from __future__ import division
import pygame
import time
from random import randint
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional, ZeroOrMore, Forward, nums, alphas, oneOf)
import math
import operator


# Colors
black = (0, 0, 0)
textcolor1 = (255, 32, 23)
textcolor2 = (235, 32, 55)
textcolorBlock = (0, 0, 235)
sunset = (255, 0, 0)
green = (100, 255, 100)
darkgreen = (6, 127, 2)
brightblue = (47, 228, 253)
orange = (255, 113, 0)
yellow = (255, 236, 0)
purple = (252, 67, 255)


pygame.init ()


# Global variables
surfaceWidth = 800
surfaceHeight = 500
surface = pygame.display.set_mode ((surfaceWidth, surfaceHeight))
pygame.display.set_caption ("flappy.ai")
clock = pygame.time.Clock ()
BIRD_COUNT = 10


# Use a image with transparent background
background = pygame.image.load("../assets/background1.jpg")


class Bird:
    """
    x, y represent bird's position relative to top-left corner and y_move represents amount by which the bird should move
    """

    def __init__(self, no):
        self.x = 200
        self.y = 150
        self.number = no
        self.current_score = 0
        self.img = pygame.image.load ("../assets/bird.png")
        self.imageWidth = self.img.get_width ()
        self.imageHeight = self.img.get_height ()
        self.expr = list()

    def randomizer(self):

        self.expr = list()
        self.expr.append(randomValue())

        opcount = randint(10, 100)

        for i in (1, opcount):
            self.expr.append(randomOp())
            self.expr.append(randomValue())


    def mutate(self):
        mutated = False
        while not mutated:
            x = randint(0, len(self.expr) - 1)
            if self.expr[x] == "+" or self.expr[x] == "-" or self.expr[x] == "*" or self.expr[x] == "/":
                self.expr[x] = randomOp()
                mutated = True
            else:
                self.expr[x] = randomValue()
                mutated = True


    def move(self, polex, poley):
        nsp = NumericStringParser(self.x, self.y, polex, poley)
        return nsp.eval("".join(self.expr))


def sortScore(b):
    return b.current_score


def crossover(a, b):
    posa = randint(0, len(a) - 1)
    while a[posa] not in ["+", "-", "*", "/"]:
        posa = randint(0, len(a) - 1)
    posb = randint(0, len(b) - 1)
    while b[posb] not in ["+", "-", "*", "/"]:
        posb = randint(0, len(b) - 1)
    newa = list()
    newb = list()
    for i in range(0, posa):
        newa.append(a[i])
    for i in range(posb, len(b)):
        newa.append(b[i])
    for i in range(0, posb):
        newb.append(b[i])
    for i in range(posa, len(a)):
        newb.append(a[i])
    a[:] = newa
    b[:] = newb


def randomValue():

    opval = randint(1, 5)

    if opval == 1:
        return str(randint(1, 100))
    elif opval == 2:
        return "px"
    elif opval == 3:
        return "py"
    elif opval == 4:
        return "bx"
    elif opval == 5:
        return "by"
    elif opval == 6:
        return "PI"
    elif opval == 7:
        return "E"


def randomOp():

    opval = randint(1, 4)

    if opval == 1:
        return "+"
    elif opval == 2:
        return "-"
    elif opval == 3:
        return "*"
    elif opval == 4:
        return "/"


class NumericStringParser(object):
    '''
    Most of this code comes from the fourFn.py pyparsing example

    '''

    def updateValues(self, birdX, birdY, poleX, poleY):
        self.birdx = birdX
        self.birdy = birdY
        self.polex = poleX
        self.poley = poleY

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')

    def __init__(self, birdX, birdY, poleX, poleY):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: bx | by | px | py | PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        self.birdx = birdX
        self.birdy = birdY
        self.polex = poleX
        self.poley = poleY
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        px = CaselessLiteral("px")
        py = CaselessLiteral("py")
        bx = CaselessLiteral("bx")
        by = CaselessLiteral("by")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | bx | by | px | py | pi | e | fnumber).setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        # addop_term = ( addop + term ).setParseAction( self.pushFirst )
        # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
        # expr <<  general_term
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow}
        self.fn = {"sin": math.sin,
                   "cos": math.cos,
                   "tan": math.tan,
                   "exp": math.exp,
                   "abs": abs,
                   "trunc": lambda a: int(a),
                   "round": round,
                   "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}

    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op == "px":
            return self.polex
        elif op == "py":
            return self.poley
        elif op == "bx":
            return self.birdx
        elif op == "by":
            return self.birdy
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val


# Restart/quit the game
def replay_or_quit():
    for event in pygame.event.get ([pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT]):
        if event.type == pygame.QUIT:
            pygame.quit ()
            quit ()

        elif event.type == pygame.KEYDOWN:
            continue

        return event.key

    return None


# Display stats
def score(count, number):

    smallText = pygame.font.Font ("freesansbold.ttf", 20)

    score = "Score: " + str(count) + " Bird: " + str(number)
    titleTextSurface, titleTextRectangle = makeTextObjs (score, smallText, sunset)
    titleTextRectangle.center = surfaceWidth / 2, 20
    # Put text on screen
    surface.blit (titleTextSurface, titleTextRectangle)


# Drawing obstacles(blocks)
def blocks(x_block, y_block, blockWidth, blockHeight, gap,color):

    # Pipe body
    pygame.draw.rect (surface, color, [x_block, y_block, blockWidth, blockHeight])
    pygame.draw.rect (surface, color,[x_block, y_block + blockHeight + gap, blockWidth, surfaceHeight - gap - blockHeight])
    # Pipe ends
    pygame.draw.rect (surface, darkgreen, [x_block - 5, blockHeight - 10, blockWidth + 10, 30])
    pygame.draw.rect (surface, darkgreen, [x_block - 5, y_block + blockHeight + gap, blockWidth + 10, 30])


# Small function to render text
def makeTextObjs(text, font, color):
    textSurface = font.render (text, True, color)
    return textSurface, textSurface.get_rect ()


# This function is used to display messages on screen
def msgsurface(text):
    smallText = pygame.font.Font ("freesansbold.ttf", 20)
    largeText = pygame.font.Font ("freesansbold.ttf", 50)

    titleTextSurface, titleTextRectangle = makeTextObjs (text, largeText, textcolor1)
    titleTextRectangle.center = surfaceWidth / 2, surfaceHeight / 2
    surface.blit (titleTextSurface, titleTextRectangle)

    smallTextSurface, smallTextRectangle = makeTextObjs ("Press any key to begin simulation", smallText, textcolor2)
    # Adjust height for small text
    smallTextRectangle.center = surfaceWidth / 2, ((surfaceHeight / 2) + 100)

    surface.blit (smallTextSurface, smallTextRectangle)

    # updating the screen to make text appear
    pygame.display.update ()
    time.sleep (1)

    while replay_or_quit () == None:
        clock.tick ()
    main ()


# Gameover function
def gameOver(finalscore):
    # TODO: show stats 
    msgsurface("Game Over")


# x and y are co-ordinates measured from top left
def image(x, y, img):
    surface.blit (img, (x, y))


def main():
    # Crossover and mutate rate
    r = 0.2
    m = 0.4

    # x_block and y_block determine the positions of block
    x_block = surfaceWidth
    y_block = 0
    blockWidth = 80

    # Block  height is randomed between 100 and  around half of surface height
    blockHeight1 = randint(1, surfaceHeight)

    # Initialize array of Bird objects
    birds = []
    for i in range(1, BIRD_COUNT + 1):
        birds.append(Bird(i))

    # Gap is the distance between blocks
    gap = int(birds[0].imageHeight * 2)

    # Movement speed of block
    block_move = 4

    game_over = False

    # Generate random genes initially
    for b in birds:
        b.randomizer()

    while True:
        for b in birds:
            b.current_score = 0
            b.x = 200
            b.y = 150
        for b in birds:
            game_over = False
            scoreVal = 0
            while not game_over:
                print(b.move(x_block, y_block))
                print("".join(b.expr))
                b.y += b.move(x_block, y_block)

                image(0,0,background)
                image(b.x, b.y,b.img)
                blocks(x_block, y_block, blockWidth, blockHeight1, gap,green)

                # Move block towards bird
                x_block -= block_move

                # Display score
                score(b.current_score, b.number)

                # Check whether bird is in frame
                if b.y > surfaceHeight - b.imageHeight or b.y < 0:
                    game_over = True

                # Draw new block as current block exits frame
                if x_block < (-1 * blockWidth):
                    x_block = surfaceWidth
                    blockHeight1 = randint (0, int (surfaceHeight / 1.5))

                # Check for collision with upper block
                if b.x + b.imageWidth > x_block:
                    # bird is within the block
                    if b.x < x_block + blockWidth:
                        if b.y < blockHeight1 + 15:
                            if b.x - b.imageWidth < blockWidth + x_block:
                                game_over = True

                # Check for collision with lower block
                if b.x + b.imageWidth > x_block:
                    if b.y + b.imageHeight > blockHeight1 + gap:
                        if b.x < x_block + blockWidth:
                            game_over = True
                
                # Update score
                if b.x > x_block - block_move + i * 20:
                    b.current_score += 1

                pygame.display.update ()
                clock.tick (60)

            # Reset block position for each bird
            x_block = surfaceWidth
            y_block = 0

        # Elitism and crossover
        birds.sort(key = sortScore)
        for i in range(int((1 - r) * len(birds)), len(birds) - 1, 2):
            crossover(birds[i].expr, birds[i + 1].expr)

        # Mutation
        count = 0
        while count < m * len(birds):
            for b in birds:
                if randint(0, 1) == 0:
                    b.mutate
                    count += 1
                if count == m * len(birds):
                    break

        for b in birds:
            print("".join(b.expr))

if __name__ == '__main__':
    main ()
    pygame.quit ()
    quit ()
