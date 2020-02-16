class Clock:
    def __init__(self):
        self.currentHour = 7
        self.day = 1
        self.currentYear = 2020

    currentHour = 8
    currentDay = 1
    currentYear = 2020

    def tick(self):
        self.currentHour += 1
        if(self.currentHour > 23):
            self.currentHour = 0
            self.currentDay += 1
        if(self.currentDay > 365):
            self.currentDay = 0
            self.currentYear += 1
    
    def timeNow(self):
        return self.currentHour
    
    def timeNowFormat(self):
        return str(self.currentHour) + ":00"
    
    def printTime(self):
        print("Year: ", self.currentYear, " Day: ", self.currentDay, " ", self.currentHour,":00",sep="")
clock = Clock()
