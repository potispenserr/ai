import pygame
import time

class Level:
    background = pygame.Surface((520, 460))
    # starting positions
    # startX is constant
    startX = 50
    # startY will increment by self.squareSize for each line
    startY = 100

    currentX = 50
    currentY = 100

    lineX = 50

    # how many pixels each side a square has
    squareSize = 12

    nodeDict = {}

    def render(self):
        f = open("Map1.txt", "r")
        
        squaresY = len(f.readlines())
        f.close()

        self.background.fill((255,255,255))

        f = open("Map1.txt", "r")
        for line in f:
            
            self.lineX = self.startX
            self.currentX = self.lineX
            self.currentY = self.startY
            for char in line:
                if(char == "X"):
                    self.drawSquare("Wall")

                if(char == "S"):
                    self.drawSquare("Start")

                if(char == "0"):
                    self.drawSquare("Walkable")

                if(char == "G"):
                    self.drawSquare("Goal")

                self.currentY = self.startY
                self.lineX += self.squareSize
                self.currentX = self.lineX
                print("\n")
                #for char ends
            
            self.startX = 50
            self.startY += self.squareSize

        f.close()

    def drawSquare(self, obj):
        self.nodeDict[(self.currentX, self.currentY)] = obj
        if(obj == "Wall"):
            for y in range(self.squareSize):
                for x in range(self.squareSize):
                    self.background.set_at((self.currentX, self.currentY), (255, 0, 0, 0))
                    self.currentX += 1
                self.currentX = self.lineX
                self.currentY += 1
                print("")

        elif(obj == "Goal"):
            self.nodeDict[obj] = (self.currentX, self.currentY)
            for y in range(self.squareSize):
                for x in range(self.squareSize):
                    self.background.set_at((self.currentX, self.currentY), (0, 255, 0, 0))
                    self.currentX += 1
                self.currentX = self.lineX
                self.currentY += 1
                print("")

        elif(obj == "Start"):
            self.nodeDict[obj] = (self.currentX, self.currentY)
            for y in range(self.squareSize):
                for x in range(self.squareSize):

                    self.background.set_at((self.currentX, self.currentY), (0, 0, 255, 0))
                    self.currentX += 1
                self.currentX = self.lineX
                self.currentY += 1
                print("")

        elif(obj == "Walkable"):
            self.nodeDict[(self.currentX, self.currentY)] = obj
            for y in range(self.squareSize):
                for x in range(self.squareSize):

                    self.background.set_at((self.currentX, self.currentY), (200, 200, 200, 0))
                    self.currentX += 1
                self.currentX = self.lineX
                self.currentY += 1
                print("")

    def test(self):
        image = pygame.image.load("player.png")
        self.background.blit(image, self.nodeDict["Start"])
        print(self.background.get_at((50,50)))

class Player:
    def __init__(self, startpos, sprite):
        self.xpos = startpos[0]
        self.ypos = startpos[1]

    xpos = 0
    ypos = 0
    sprite = None

def main():
    # initialize the pygame module
    pygame.init()

    # load and set the logo
    pygame.display.set_caption("drunk ai stumbles around")
    screenWidth = 520
    screenHeight = 460

    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((screenWidth,screenHeight))

    # load image (it is in same directory)
    #image = pygame.image.load("01_image.png")
    #image.set_colorkey((255,0,255))

    screen.fill((255,255,255))

    level = Level()
    level.render()
    screen.blit(level.background, (0, 0))

    image = pygame.image.load("player.png")
    screen.blit(image, level.nodeDict["Start"])

    player = Player(level.nodeDict["Start"], image)
    

    stepX = level.squareSize
    stepY = level.squareSize



    # update the screen to make the changes visible (fullscreen update)
    pygame.display.flip()

    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        if(level.nodeDict[(player.xpos + stepX, player.ypos + stepY)] == "Wall"):
            stepX = -stepX


        player.xpos += stepX
        player.ypos += stepY

        screen.blit(level.background, (0,0))

        screen.blit(image, (player.xpos, player.ypos))

        pygame.display.flip()


        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event if of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

        time.sleep(1)



if __name__ == "__main__":
    main()