

class State():

    def Enter(self, miner):
        print ("Enter the gungeon")
        raise NotImplementedError("plizz ipmelemnt me :/")
    def Execute(self, miner):
        print("YOU HAVE BEEN EXECUTED")
        raise NotImplementedError("plizz ipmelemnt me :/")

    def Exit(self, miner):
        print ("Escaped from tarkob")
        raise NotImplementedError("plizz ipmelemnt me :/")

class BaseGameEntity:

    entityID = 0
    nextValidID = 1

    def __init__(self, val):
        self.entityID = val
        self.nextValidID = val+1
    def update(self):
        raise NotImplementedError("pls implement me :(")

class Miner(BaseGameEntity):
    def __init__(self,ID):
        super().__init__(ID)
    
    currentState = State()
    location = ""

    thirst = 0
    hunger = 0
    fatigue = 0
    socialNeed = 0

    nuggiesCarried = 0
    nuggiesInThebank = 0
    pocketsize = 2

    def update(self):
        self.thirst += 1
        print (self.thirst)
        if(self.currentState):
            self.currentState.Execute(self)
    

    def changeState(self, newState):
        self.currentState.Exit()

        self.currentState = newState

        self.currentState.Enter()



def main():
    miner = Miner(1)
    miner.update()

if __name__ == "__main__":
    main()

