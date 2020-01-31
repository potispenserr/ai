import time
import random
import baseClasses as base

death = """
                                          ,,,xxxx
 ``''==xx#################xxxxx===---xxx##########
                `''################################
                   ####           ####P'
--                ####            ####
                ####              ####
              ####`'=..           ####      ,#####
          ,####      ###,,        ####,,==#####""'
       ,###`'==        '####\     ####
    ,,##`     ""###      ####     ####
                 ####   ####      ####
                   #######        ####
                    ####          ####
                  ####            ####
                ####              ####            #
            ,####'                ####           ##
        ,####'                    #################
    ,x##                            ##############
    
            ______ _____  ___ _____ _   _ 
            |  _  \  ___|/ _ \_   _| | | |
            | | | | |__ / /_\ \| | | |_| |
            | | | |  __||  _  || | |  _  |
            | |/ /| |___| | | || | | | | |
            |___/ \____/\_| |_/\_/ \_| |_/"""

# Work mining
class NuggetMining(base.State):

    def enter(self, miner):
        if (miner.currentLocation != "nuggetmine"):
            print("gonna get me some nuggies")
            miner.currentLocation = "nuggetmine"

    def execute(self, miner):
        miner.nuggiesCarried += 1
        miner.fatigue += 2
        print("gettin' them Nugg Nuggz")
        print("thirst: ", miner.thirst)

        if (miner.nuggiesCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())


    def exit(self, miner):
        print("brexit")


# Sleep
class ISleep(base.State):

    def enter(self, miner):
        print("I'm so tired... I'm going to rest for a bit")

    def execute(self, miner):
        print("zzzzz")
        miner.fatigue -= 10
        if (miner.fatigue < 0):
            miner.fatigue = 0
            miner.changeState(NuggetMining())

    def exit(self, miner):
        print("Alright let's get this bread")

class SweetHome(base.State):

    def enter(self, miner):
        print("My sweet home in Alabama")

    def execute(self, miner):
        miner.changeState(ISleep())

    def exit(self, miner):
        print("Back to the grind")


# Mad Bank YO
class PushForceBank(base.State):

    def enter(self, miner):
        print("We want to hurt no one. We're here for the bank's money, not your money.")

    def execute(self, miner):
        print("Let's drill the safe")
        miner.nuggiesCarried -= 2
        miner.nuggiesInTheBank += 2
        if(miner.nuggiesCarried <= 0):
            miner.nuggiesCarried = 0
            miner.changeState(NuggetMining())

    def exit(self, miner):
        print("Alright let's get the fuck outta here")


class GoToTravven(base.State):

    def enter(self, miner):
        randint = random.randint(0,1)
        if(randint == 0):
            print("Time to get me a delicious budvar at Travven")
        elif(randint == 1):
            print("Time to get me a delectable alcohol-free Zingo-Hoyt at Travven")

    def execute(self, miner):
        print("slurp slurp")
        miner.thirst -= 10
        if(miner.thirst < 0):
            miner.thirst = 0
            miner.changeState(NuggetMining())

    def exit(self, miner):
        print("God damn it, it's sista beställningen")

class DallasTorsdag(base.State):
    def enter(self, miner):
        randint = random.randint(0,2)
        if(randint == 0):
            print("I'll get kebabtallrik extra allt today")
        elif(randint == 1):
            print("I'll get Superskrov today")
        elif(randint == 2):
            print("I'll take hawaii today")

    def execute(self, miner):
        print("Nom Nom Nom Nom")
        miner.hunger -= 10
        if(miner.hunger < 0):
            miner.hunger = 0
            miner.changeState(NuggetMining())

    def exit(self, miner):
        print("Always nice with some Dallas but time to get back to it")


# Rip in kill
class YouDied(base.State):
    def enter(self, miner):
        if (miner.thirst >= 50):
            print("Died of dehydration")
        elif (miner.hunger >= 50):
            print("Died of hunger")


    def execute(self, miner):
        print(death)
        #print("You're lying dead on the floor")
        miner.currentState = None

    def exit(self, miner):
        print("Guess who's back, back again")


class Miner(base.BaseGameEntity):
    def __init__(self, ID):
        super().__init__(ID)

    #Stats
    currentState = ISleep()
    currentLocation = ""
    loclist = ["Travven", "Home", "Dallas", "Hell?", "NuggetMine", "Bank"]
    currentTime = 0


    thirst = 0
    hunger = 0
    fatigue = 0
    socialNeed = 0

    nuggiesCarried = 0
    nuggiesInTheBank = 0
    pocketSize = 10

    def update(self):
        self.thirst += 2
        self.hunger += 1
        self.socialNeed += 1
        self.fatigue += 1
        self.currentTime += 1

        if(self.currentTime > 23):
            self.currentTime = 0

        #stat printers
        print(self.currentTime,":00")
        print("Miner ", self.entityID," thirst: ", self.thirst, " hunger: ", self.hunger)
        print("Miner ", self.entityID, " fatigue: ", self.fatigue, " social need: ", self.socialNeed)
        print("Miner ", self.entityID, " NuggsCarried: ", self.nuggiesCarried, " Nuggies in the Bank: ", self.nuggiesInTheBank)

        #Check if Death is imminent
        if (self.thirst >= 55):
            self.changeState(GoToTravven())
        elif (self.hunger >= 30):
            self.changeState(DallasTorsdag())
        elif (self.fatigue >=50):
            self.changeState(ISleep())

        elif (self.fatigue >= 70):
            self.changeState(ISleep())

        if (self.currentState):
            #Death states
            if (self.thirst >= 70):
                self.changeState(YouDied())
            elif (self.hunger >= 50):
                self.changeState(YouDied())

            #execute current state
            self.currentState.execute(self)

        

    def changeState(self, newstate):
        print("changing state")
        self.currentState.exit(self)

        self.currentState = newstate

        self.currentState.enter(self)


def main():
    miner = Miner(1)
    
    while (True):
       miner.update()
       time.sleep(0.5)
       if (miner.currentState is None):
            break


if __name__ == "__main__":
    main()
