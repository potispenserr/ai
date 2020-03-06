import pygame
import time

class Level:
    background = pygame.Surface((520, 460))
    # starting positions
    # startX is constant
    startX = 50
    # startY will increment by squareSize for each line
    startY = 100

    currentX = 50
    currentY = 100

    lineX = 50

    def render(self):
        f = open("Map1.txt", "r")
        

        squaresY = len(f.readlines())
        f.close()

        self.background.fill((255,255,255))

        f = open("Map1.txt", "r")
        for line in f:
            # how many pixels a square has
            squareSize = 10

            self.lineX = self.startX
            self.currentX = self.lineX
            self.currentY = self.startY
            for char in line:
                if(char == "X"):
                    for y in range(squareSize):
                        for x in range(squareSize):
                            self.background.set_at((self.currentX, self.currentY), (255, 0, 0, 0))
                            self.currentX += 1
                        self.currentX = self.lineX
                        self.currentY += 1
                        print("")
                if(char == "S"):
                    for y in range(squareSize):
                        for x in range(squareSize):
                            self.background.set_at((self.currentX, self.currentY), (0, 0, 255, 0))
                            self.currentX += 1
                        self.currentX = self.lineX
                        self.currentY += 1
                        print("")
                if(char == "O"):
                    for y in range(squareSize):
                        for x in range(squareSize):
                            self.background.set_at((self.currentX, self.currentY), (255, 255, 255, 0))
                            self.currentX += 1
                        self.currentX = self.lineX
                        self.currentY += 1
                        print("")
                if(char == "G"):
                    for y in range(squareSize):
                        for x in range(squareSize):
                            self.background.set_at((self.currentX, self.currentY), (0, 255, 0, 0))
                            self.currentX += 1
                        self.currentX = self.lineX
                        self.currentY += 1
                        print("")

                self.currentY = self.startY
                self.lineX += squareSize
                self.currentX = self.lineX
                print("\n")
                #for char ends
            
            self.startX = 50
            self.startY += squareSize
        f.close()
    
    def drawSquare(self, obj):
        if(obj == "wall"):
            for y in range(squareSize):
                for x in range(squareSize):
                    self.background.set_at((self.currentX, self.currentY), (255, 0, 0, 0))
                    self.currentX += 1
                self.currentX = self.lineX
                self.currentY += 1
                print("")
        elif(obj == "Goal"):
            pass

    def test(self):
        image = pygame.image.load("1_img.png")
        self.background.fill((255,255,255))
        self.background.blit(image, (50,50))
        print(self.background.get_at((50,50)))

def main():
    # initialize the pygame module
    pygame.init()

    # load and set the logo
    pygame.display.set_caption("first blit")
    screenWidth = 520
    screenHeight = 460

    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((screenWidth,screenHeight))

    # load image (it is in same directory)
    #image = pygame.image.load("01_image.png")
    #image.set_colorkey((255,0,255))

    xpos = 50
    ypos = 50
    stepX = 10
    stepY = 10

    screen.fill((255,255,255))

    level = Level()
    level.render()
    screen.blit(level.background, (0, 0))


    # update the screen to make the changes visible (fullscreen update)
    pygame.display.flip()

    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        """ if(xpos > screenWidth - 64 or xpos <= 0):
            stepX = -stepX
        
        if(ypos > screenHeight - 64 or ypos <= 0):
            stepY = -stepY

        xpos += stepX
        ypos += stepY

        screen.fill((255,255,255))
        

        #screen.blit(image, (xpos, ypos))
        index = 0
        rangeX = 0
        rangeY = 0
        while(index < 16):
            index += 1
            for y in range(rangeY):
                for x in range(rangeX):
                    if (x < 20 or y < 20):
                        screen.set_at((x, y), (255, 0, 0, 0))
                    else:
                        screen.set_at((x, y), (255, 255, 0, 0))

            rangeX += 20
            rangeY += 20

        pygame.display.flip() """


        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event if of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

        time.sleep(1)



if __name__ == "__main__":
    main()