import pygame
import time

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
    image = pygame.image.load("01_image.png")
    image.set_colorkey((255,0,255))

    xpos = 50
    ypos = 50
    stepX = 10
    stepY = 10

    screen.fill((255,255,255))
    

    # blit image to screen
    #screen.blit((image), (xpos,ypos))
    f = open("Map1.txt", "r")
    linelength = 0
    startX = 50
    startY = 100

    currentX = 50
    currentY = 100

    squaresY = len(f.readlines())
    f.close()

    f = open("Map1.txt", "r")
    for line in f:
        print(line)
        linelength = len(line.rstrip())
        squaresX = int((screenWidth - startX * 2) / linelength)
        squareSize = 26
        for char in line:
            print(char,"#")
            if(char == "X"):
                for y in range(squareSize):
                    for x in range(squareSize):
                        screen.set_at((currentX, currentY), (255, 0, 0, 0))
                        print("drawing", char, "at", startX, startY)
                        currentX += 1
                        currentY += 1
            if(char == "S"):
                for x in range(squareSize):
                    screen.set_at((startX, startY), (0, 0, 255, 0))
                    startX += 1
            if(char == "O"):
                for x in range(squareSize):
                    screen.set_at((startX, startY), (255, 255, 255, 0))
                    startX += 1
            if(char == "G"):
                for x in range(squareSize):
                    screen.set_at((startX, startY), (0, 255, 0, 0))
                    startX += 1
            currentY = startY
        
        print("changing line")
        startX = 50
        startY += 10

    
    f.close()

    #for x in range(50):
    #    screen.set_at((startX, startY), (255, 0, 0, 0))
    #    startX += 1

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