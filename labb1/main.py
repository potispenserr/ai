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
        print("Fatigue: ", miner.fatigue)
        if (miner.currentLocation != "Mine"):
            print(miner.name, ": gonna get me some nuggies")
            miner.currentLocation = "nuggetmine"

    def execute(self, miner):
        if (miner.moneyCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())
        miner.moneyCarried += 2
        miner.fatigue += 2
        print(miner.name, ":gettin' and sellin' them Nugg Nuggz")
        toolBreakChance = random.randint(1,10)
        if (toolBreakChance < 2):
            miner.hasTools = False
            print(miner.name, ":Ah shucks my goddamned pickaxe broke")
            miner.changeToWorkState()



    def exit(self, miner):
        print("Fatigue: ", miner.fatigue)
        if (miner.moneyCarried >= miner.pocketSize):
            print(miner.name, ":Sold all of my chicken nuggets i dug up! Time to deposit all the money")
        elif(miner.hasTools == False):
            print(miner.name, ":Well my pickaxe broke so i can't continue here")
        else:
            print(miner.name, ":I'm done working, time to do something else")

class CallCenter(base.State):
    def enter(self, miner):
        print(miner.name, ":Where is my cubicle now again?")
        miner.currentLocation = "Office"
    
    def execute(self, miner):
        print(miner.name, ":Rude people on the line, why am i not surprised")
        if(miner.moneyCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())
        miner.fatigue += 3
        miner.moneyCarried += 1
        if(miner.moneyCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())


    def exit(self, miner):
        print("Fatigue: ", miner.fatigue)
        print(miner.name, ":I've just about had it with rude people on the phone asking stupid shit")



# Sleep
class ISleep(base.State):

    def enter(self, miner):
        if(miner.currentLocation != "Home"):
            miner.currentLocation = "Home"
            print(miner.name, ":I'm going home to sleep") 
            
        print(miner.name, ":I'm so tired... I'm going to rest for a bit")

    def execute(self, miner):
        print(miner.name, ":zzzzz")
        miner.fatigue -= 10
        if (miner.fatigue < 0):
            miner.fatigue = 0
            if(miner.previousState):
                miner.revertToPreviousState()
            else:
                miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ":Alright let's get this bread")

"""class SweetHome(base.State):
    def enter(self, miner):
        print("My sweet home in Alabama")

    def execute(self, miner):
        print("I going to watch that Netflix show i've been putting off")
        miner.changeState(ISleep())

    def exit(self, miner):
        print("Time to stop watching Netflix")"""


# Mad Bank YO
class PushForceBank(base.State):

    def enter(self, miner):
        miner.currentLocation = "Bank"
        print(miner.name, ":We want to hurt no one. We're here for the bank's money, not your money.")

    def execute(self, miner):
        print(miner.name, ":Let's drill the safe")
        miner.moneyCarried -= 3
        miner.moneyInTheBank += 3
        if(miner.moneyCarried <= 0):
            miner.moneyCarried = 0
            miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ":Alright let's get outta here")
        print(miner.name, ":Money in bank: ", miner.moneyCarried)


class GoToTravven(base.State):

    def enter(self, miner):
        miner.currentLocation = "Travven"
        print("Thirst: ", miner.thirst)
        randint = random.randint(0,1)
        if(randint == 0):
            print(miner.name, ":Time to get me a delicious budvar at Travven")
        elif(randint == 1):
            print(miner.name, ":Time to get me a delectable alcohol-free Zingo-Hoyt at Travven")

    def execute(self, miner):
        print(miner.name, ":slurp slurp")
        miner.thirst -= 10
        if(miner.thirst < 0):
            miner.thirst = 0
            miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ":God damn it, it's sista beställningen")

class DallasTorsdag(base.State):
    def enter(self, miner):
        miner.currentLocation = "Dallas"
        randint = random.randint(0,2)
        print("Hunger: ", miner.hunger)
        if(randint == 0):
            print(miner.name, ":I'll get Kebabtallrik extra allt today at Dallas")
        elif(randint == 1):
            print(miner.name, ":I'll get Superskrov today at Dallas")
        elif(randint == 2):
            print(miner.name, ":I'll take Hawaii today at Dallas")

    def execute(self, miner):
        print(miner.name, ":Nom Nom Nom Nom")
        miner.hunger -= 10
        if(miner.hunger < 0):
            miner.hunger = 0
            miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ":Always nice with some Dallas but time to get back to it")
        print("Hunger: ", miner.hunger)

class Store(base.State):
    def enter(self, miner):
        print(miner.name, ":Time to get a pickaxe so i can mine chicken nuggets")

    def execute(self, miner):
        print(miner.name, ":I got the pickaxe, now Im going to check it out")
        miner.hasTools = True
        miner.moneyInTheBank -= 10
        miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ":This pickaxe cost me a pretty penny so i sure hope it was worth it")


# Rip in kill
class YouDied(base.State):
    def enter(self, miner):
        miner.currentLocation = "Hell?"
        if (miner.thirst >= 50):
            print(miner.name, ":Died of dehydration")
        elif (miner.hunger >= 50):
            print(miner.name, ":Died of hunger")
        


    def execute(self, miner):
        print(death)
        #print("You're lying dead on the floor")
        miner.currentState = None
        miner.previousState = None
        miner.dead = True
        

    def exit(self, miner):
        print(miner.name, ":Guess who's back, back again")


class Miner(base.BaseGameEntity):
    def __init__(self, ID, minername):
        super().__init__(ID)
        self.name = minername


    #Stats
    name = ""
    previousState = None
    currentState = ISleep()
    currentLocation = ""
    loclist = ("Hell?", "Dallas", "Travven", "Home", "Bank", "Mine", "CallCenter", "Store")
    currentTime = 8
    interruptableState = True
    dead = False


    thirst = 0
    hunger = 0
    fatigue = 0
    socialNeed = 0

    moneyCarried = 0
    moneyInTheBank = 0
    pocketSize = 10
    hasTools = False

    #Where everything happens
    def update(self):

        #if currentState is not None
        if (self.currentState):
            self.thirst += 2
            self.hunger += 1
            self.socialNeed += 1
            self.fatigue += 1
            self.currentTime += 1

            if(self.currentTime > 23):
                self.currentTime = 0

            #stat printers
            print(self.currentTime,":00")
            #print("Miner ", self.entityID," thirst: ", self.thirst, " hunger: ", self.hunger)
            #print("Miner ", self.entityID, " fatigue: ", self.fatigue, " social need: ", self.socialNeed)
            #print("Miner ", self.entityID, " moneyCarried: ", self.moneyCarried, " Money in the Bank: ", self.moneyInTheBank)
            print(self.name, "Has Tools: ", self.hasTools)

            if(self.hasTools == False and self.moneyInTheBank >= 10):
                if(self.currentTime > 8 and self.currentTime < 19):
                    self.changeState(Store())

            if(self.interruptableState == True):
                #Check if Death is imminent
                if (self.thirst >= 30):
                    self.changeState(GoToTravven())

                elif (self.hunger >= 30):
                    self.changeState(DallasTorsdag())

            elif (self.fatigue >= 50):
                self.changeState(ISleep())
            #Death states
            if (self.thirst >= 50):
                self.changeState(YouDied())
            elif (self.hunger >= 50):
                self.changeState(YouDied())
            #execute current state
            self.currentState.execute(self)
    
        #If currentState is None check if miner has previous state 
        elif(self.previousState):
            self.revertToPreviousState()

    def changeState(self, newstate):
        self.currentState.exit(self)

        self.previousState = self.currentState
        self.currentState = newstate

        self.currentState.enter(self)

    def changeToWorkState(self):
        if(self.hasTools == True):
            self.changeState(NuggetMining())
        else:
            self.changeState(CallCenter())


    def revertToPreviousState(self):
        if(self.previousState):
            self.changeState(self.previousState)


def main():
    minerlist = []
    minerlist.append(Miner(1, "Sven"))
    minerlist.append(Miner(2, "Steffe"))
    

    while (True):
        
        for miner in minerlist:
            if(miner.dead is True):
                minerlist.remove(miner)

        if (len(minerlist) == 0):
             print("Everyone is dead :(")
             break
        
        for miner in minerlist:
            miner.update()

        time.sleep(1)
        


if __name__ == "__main__":
    main()
