import time

class BaseGameEntity:

    entityID = 0
    nextValidID = 1

    def __init__(self, val):
        self.entityID = val
        self.nextValidID = val+1
    def update(self):
        raise NotImplementedError("pls implement me :(")




class State():

    def enter(self, miner):
        print ("Enter the gungeon")
        raise NotImplementedError("plizz ipmelemnt me :/")
    def execute(self, miner):
        print("YOU HAVE BEEN EXECUTED")
        raise NotImplementedError("plizz ipmelemnt me :/")

    def exit(self, miner):
        print ("Escaped from tarkob")
        raise NotImplementedError("plizz ipmelemnt me :/")


class ImMiningForDiamonds(State):
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
        
        return cls.instance

    def enter(self, miner):
        if(miner.location != "goldmine"):
            print("wAlKinG tO tHE mINe")
            miner.location = "goldmine"
       
    def execute(self, miner):
        miner.nuggiesCarried +=1
        miner.fatigue += 5
        print("gettin' them Nugg Nuggz")

        if(miner.nuggiesCarried >= miner.pocketsize):
            miner.changeState(PushForceBank())
        
        if(miner.thirst > 50):
            miner.changeState(GoToTravven())


    def exit(self, miner):
        print("brexit")




class PushForceBank(State):

    def enter(self, miner):
        print("We want to hurt no one. We're here for the bank's money, not your money.")

    def execute(self, miner):
        print("Let's drill the safe")

    def exit(self, miner):
        print("Alright let's get the fuck outta here")

    

class GoToTravven(State):
    pass


class DanceTillYoureDead(State):
    def enter(self, miner):
        print("I don't feel so good Mr. Stark")

    def execute(self, miner):
        print("You lie dead on the floor")
        miner.currentState = None

    def exit(self, miner):
        print("Guess who's back, back again")
        


class Miner(BaseGameEntity):
    def __init__(self,ID):
        super().__init__(ID)
    
    currentState = State()
    location = ""

    thirst = 45
    hunger = 0
    fatigue = 0
    socialNeed = 0

    nuggiesCarried = 0
    nuggiesInThebank = 0
    pocketsize = 10

    def update(self):
        self.thirst += 1
        print ("thirst: ", self.thirst)
        if(self.currentState):
            if(self.thirst >= 50):
                self.changeState(DanceTillYoureDead())
            self.currentState.execute(self)
    

    def changeState(self, newState):
        print("changing state")
        self.currentState.exit(self)

        self.currentState = newState

        self.currentState.enter(self)





def main():
    miner = Miner(1)
    miner.currentState = ImMiningForDiamonds()
    #miner.update()
    #miner.changeState(PushForceBank())
    while(True):
        miner.update()
        time.sleep(0.5)
        if(miner.currentState == None):
            break
    

if __name__ == "__main__":
    main()

