import time
import random


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


# Rip in kill
class 死(State):
    def enter(self, miner):
        if (miner.thirst >= 50):
            print("Died of dehydration")
        elif (miner.hunger >= 50):
            print("Died of hunger")

        print("ROBERRRRRRRRTTTTTTTT")

    def execute(self, miner):
        print("You're lying dead on the floor")
        miner.currentState = None

    def exit(self, miner):
        print("Guess who's back, back again")


class Miner(BaseGameEntity):
    def __init__(self, ID):
        super().__init__(ID)

    currentState = State()
    location = ""

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
        print("Miner ", self.entityID," thirst: ", self.thirst, " hunger: ", self.hunger)
        print("Miner ", self.entityID, " fatigue: ", self.fatigue, " social need: ", self.socialNeed)
        if (self.currentState):
            if (self.thirst >= 50):
                self.changeState(死())
            elif (self.hunger >= 45):
                self.changeState(死())
            self.currentState.execute(self)

    def changeState(self, newstate):
        print("changing state")
        self.currentState.exit(self)

        self.currentState = newstate

        self.currentState.enter(self)


def main():
    miner = Miner(1)
    miner.currentState = ISleep()
    while (True):
        miner.update()
        if (miner.socialNeed >= 30):
            print("Miner ", miner.entityID, "is lonely")
        elif (miner.thirst >= 30):
            miner.changeState(GoToTravven())
        elif (miner.hunger >= 50)
        time.sleep(0.5)
        if (miner.currentState is None):
            break


if __name__ == "__main__":
    main()
