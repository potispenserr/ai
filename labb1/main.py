import time
import random

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


class BaseGameEntity:
    entityID = 0
    nextValidID = 1

    def __init__(self, val):
        self.entityID = val
        self.nextValidID = val + 1

    def update(self):
        raise NotImplementedError("pls implement me :(")


# Base State class
class State:

    def enter(self, miner):
        print("Enter the gungeon")
        raise NotImplementedError("plizz ipmelemnt me :/")

    def execute(self, miner):
        print("YOU HAVE BEEN EXECUTED")
        raise NotImplementedError("plizz ipmelemnt me :/")

    def exit(self, miner):
        print("Escaped from tarkob")
        raise NotImplementedError("plizz ipmelemnt me :/")


# Work mining
class NuggetMining(State):
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)

        return cls.instance

    def enter(self, miner):
        if (miner.location != "nuggetmine"):
            print("gonna get me some nuggies")
            miner.location = "nuggetmine"

    def execute(self, miner):
        miner.nuggiesCarried += 1
        miner.fatigue += 3
        print("gettin' them Nugg Nuggz")
        print("thirst: ", miner.thirst)

        if (miner.nuggiesCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())


    def exit(self, miner):
        print("brexit")


# Sleep
class ISleep(State):
    def enter(self, miner):
        print("I'm so tired... I'm going to rest for a bit")

    def execute(self, miner):
        print("zzzzz")
        miner.fatigue -= 10
        if (miner.fatigue < 0):
            miner.fatigue = 0
            miner.changeState(NuggetMining())

    def exit(self, miner):
        print("Let's get this bread")


# Mad Bank YO
class PushForceBank(State):
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)

        return cls.instance

    def enter(self, miner):
        print("We want to hurt no one. We're here for the bank's money, not your money.")

    def execute(self, miner):
        print("Let's drill the safe")
        miner.nuggiesCarried -= 2
        miner.nuggiesInTheBank += 2
        if(miner.nuggiesCarried == 0):
            miner.changeState(NuggetMining())

    def exit(self, miner):
        print("Alright let's get the fuck outta here")


class GoToTravven(State):
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

class DallasTorsdag(State):
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
class 死(State):
    def enter(self, miner):
        if (miner.thirst >= 50):
            print("Died of dehydration")
        elif (miner.hunger >= 50):
            print("Died of hunger")

        print(death)

    def execute(self, miner):
        print("You're lying dead on the floor")
        miner.currentState = None

    def exit(self, miner):
        print("Guess who's back, back again")


class Miner(BaseGameEntity):
    def __init__(self, ID):
        super().__init__(ID)

    #Stats
    currentState = State()
    currentLocation = ""
    #locdict = 
    tired = False


    thirst = 0
    hunger = 0
    fatigue = 0
    socialNeed = 0

    nuggiesCarried = 0
    nuggiesInTheBank = 0
    pocketSize = 10

    def update(self):
        self.thirst += 3
        self.hunger += 1
        self.socialNeed += 1
        self.fatigue += 1
        #stat printers
        print("Miner ", self.entityID," thirst: ", self.thirst, " hunger: ", self.hunger)
        print("Miner ", self.entityID, " fatigue: ", self.fatigue, " social need: ", self.socialNeed)
        print("Miner ", self.entityID, " NuggsCarried: ", self.nuggiesCarried, " Nuggies in the Bank: ", self.nuggiesInTheBank)

        #Check if Death is imminent
        if (self.thirst >= 55):
            self.changeState(GoToTravven())
        elif (self.hunger >= 30):
            self.changeState(DallasTorsdag())
        elif (self.fatigue >=50):
            #self.
            pass

        elif (self.fatigue >= 70):
            self.changeState(ISleep())

        if (self.currentState):
            #Death states
            if (self.thirst >= 70):
                self.changeState(死())
            elif (self.hunger >= 50):
                self.changeState(死())

            #execute current state
            self.currentState.execute(self)

    def changeState(self, newstate):
        print("changing state")
        self.currentState.exit(self)

        self.currentState = newstate

        self.currentState.enter(self)


def main():
    miner = Miner(1)
    miner.currentState = ISleep()
    miner.thirst = 1000
    while (True):
       miner.update()
       time.sleep(0.5)
       if (miner.currentState is None):
            break


if __name__ == "__main__":
    main()
