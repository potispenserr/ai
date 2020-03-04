import pygame
import time

def main():
    # initialize the pygame module
    pygame.init()
    
    # load and set the logo
    pygame.display.set_caption("first blit")
    screenWidth = 240
    screenHeight = 180

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

    screen.set_at((0, 0), (255, 0, 0, 0))

    # update the screen to make the changes visible (fullscreen update)
    pygame.display.flip()
    
    # define a variable to control the main loop
    running = True
    
    # main loop
    while running:
        if(xpos > screenWidth - 64 or xpos <= 0):
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
                    if (x < 20 and y < 20):
                        screen.set_at((x, y), (255, 0, 0, 0))
                    else:
                        screen.set_at((x, y), (255, 255, 0, 0))

            rangeX += 1
            rangeY += 1

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