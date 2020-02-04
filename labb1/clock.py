class Clock:
    def __init__(self):
        self.currentHour = 0

    currentHour = 0

    def tick(self):
        self.currentHour += 1
        if(self.currentHour > 23):
            self.currentHour = 0
    
    def printTime(self):
        print(self.currentHour,":00",sep="")
clock = Clock()
