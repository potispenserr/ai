import time
import random
import baseClasses as base
import clock as clk
import entityManager as em
import messageDispatcher as md
import telegram as tele

death = """
______ _____  ___ _____ _   _ 
|  _  \  ___|/ _ \_   _| | | |
| | | | |__ / /_\ \| | | |_| |
| | | |  __||  _  || | |  _  |
| |/ /| |___| | | || | | | | |
|___/ \____/\_| |_/\_/ \_| |_/"""


class NuggetMining(base.State):

    def enter(self, miner):
        if (miner.currentLocation != "Mine"):
            print(miner.name, ": gonna get me some nuggets" , sep="")
            miner.currentLocation = "Mine"

    def execute(self, miner):
        if(miner.currentLocation == "Mine"):
            miner.moneyCarried += 2
            miner.fatigue += 1
            print(miner.name, ": gettin' them nuggets", sep="")
            if (miner.moneyCarried >= miner.pocketSize):
                miner.changeState(PushForceBank())

            toolBreakChance = random.randint(1, 10)
            if (toolBreakChance < 2):
                miner.hasTools = False
                print(miner.name, ": Ah shucks my goddamned pickaxe broke", sep="")
                miner.changeToWorkState()

            if(clk.clock.timeNow() >= 19):
                miner.changeState(SweetHome())

    def exit(self, miner):
        if (miner.moneyCarried >= miner.pocketSize):
            print(miner.name, ": Sold all of my chicken nuggets i dug up! Time to deposit all the money", sep="")
        elif (miner.hasTools == False):
            print(miner.name, ": Well my pickaxe broke so i can't continue here", sep="")
        else:
            print(miner.name, ": I'm done working for now, time to do something else", sep="")



class CallCenter(base.State):
    def enter(self, miner):
        print(miner.name, ": Heading to the dreaded Microsoft tech-support center", sep="")
        miner.currentLocation = "CallCenter"

    def execute(self, miner):
        print(miner.name, ": Rude people on the line, why am i not surprised", sep="")
        if (miner.moneyCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())
        miner.fatigue += 1
        #Miner gets money deposited into his bank instead of in his hand
        miner.moneyInTheBank += 1
        if (miner.moneyCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())
        if(clk.clock.timeNow() >= 19):
            miner.changeState(SweetHome())

    def exit(self, miner):
        print(miner.name, ": I've just about had it with rude people on the phone asking stupid things", sep="")


class ISleep(base.State):

    def enter(self, miner):
        if (miner.currentLocation != "Home"):
            miner.currentLocation = "Home"
            print(miner.name, ": I'm going home to sleep", sep="")

        miner.currentLocation = "Home"
        print(miner.name, ": I'm so tired... I'm going to rest for a bit", sep="")
        miner.interruptableState = False

    def execute(self, miner):
        if(miner.currentLocation == ""):
            miner.currentLocation = "Home"
            miner.interruptableState = False

        print(miner.name, ": zzzzz" ,sep="")
        miner.fatigue -= 6
        if (miner.fatigue < 0):
            miner.fatigue = 0

        if(clk.clock.timeNow() > 8):
            miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ": Alright let's get this bread" , sep="")
        miner.interruptableState = True

class SweetHome(base.State):
    def enter(self, miner):
        miner.currentLocation = "Home"
        print(miner.name, ": My sweet home in Alabama", sep="")

    def execute(self, miner):
        print(miner.name, ": Chillin' at home", sep="")
        if(miner.fatigue >= 50 or (clk.clock.timeNow() >= 23 or clk.clock.timeNow() <= 8)):
            miner.changeState(ISleep())

    def exit(self, miner):
        print(miner.name, ": Time to stop watching Netflix and do something else", sep="")

class PushForceBank(base.State):

    def enter(self, miner):
        miner.currentLocation = "Bank"
        print(miner.name, ": Hello, i would like to bank some cash please", sep="")

    def execute(self, miner):
        print(miner.name, ": Here's some of the cash", sep="")
        miner.moneyCarried -= 5
        miner.moneyInTheBank += 5
        if (miner.moneyCarried <= 0):
            miner.moneyCarried = 0
            if(clk.clock.timeNow() >= 19):
                miner.changeState(SweetHome())
            else:
                miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ": And that was that. Let's do something else", sep="")


class GoToTravven(base.State):
    def enter(self, miner):
        miner.currentLocation = "Travven"
        randint = random.randint(0, 1)
        if (randint == 0):
            print(miner.name, ": Time to get me a delicious budvar at Travven", sep="")
        elif (randint == 1):
            print(miner.name, ": Time to get me a delectable alcohol-free Zingo-Hoyt at Travven", sep="")

    def execute(self, miner):
        print(miner.name, ": slurp slurp", sep="")
        miner.interruptableState = False
        miner.thirst -= 15
        if (miner.thirst < 0):
            miner.thirst = 0
            miner.changeToWorkState()

    def exit(self, miner):
        miner.interruptableState = True
        print(miner.name, ": Oh no, it's sista beställningen", sep="")


class DallasTorsdag(base.State):
    def enter(self, miner):
        miner.currentLocation = "Dallas"
        randint = random.randint(0, 2)
        if (randint == 0):
            print(miner.name, ": I'll get Kebabtallrik extra allt today at Dallas", sep="")
        elif (randint == 1):
            print(miner.name, ": I'll get Superskrov today at Dallas", sep="")
        elif (randint == 2):
            print(miner.name, ": I'll take Hawaii today at Dallas", sep="")

    def execute(self, miner):
        print(miner.name, ": Nom Nom Nom Nom", sep="")
        miner.interruptableState = False
        miner.hunger -= 15
        if (miner.hunger < 0):
            miner.hunger = 0
            miner.changeToWorkState()

    def exit(self, miner):
        miner.interruptableState = True
        print(miner.name, ": Always nice with some Dallas but time to get back to it", sep="")


class Store(base.State):
    def enter(self, miner):
        print(miner.name, ": Time to get a pickaxe so i can mine chicken nuggets", sep="")
        miner.currentLocation = "Store"

    def execute(self, miner):
        print(miner.name, ": I got the pickaxe, now Im going to check it out", sep="")
        miner.hasTools = True
        miner.moneyInTheBank -= 10
        # if the clock is 18 miner can only work for a hour before going home which is kinda dumb
        # so the miner goes home directly
        if(clk.clock.timeNow() >= 18):
            miner.changeState(SweetHome())
        else:
            miner.changeState(NuggetMining())

    def exit(self, miner):
        print(miner.name, ": This pickaxe cost me a pretty penny so i sure hope it was worth it", sep="")


# Rip
class YouDied(base.State):
    def enter(self, miner):
        miner.currentLocation = "Hell?"

    def execute(self, miner):
        print(death)
        if (miner.thirst >= 50):
            print("Dehydration")
        elif (miner.hunger >= 50):
            print("Hunger")
        elif (miner.socialNeed >= 100):
            print("It's just not worth it anymore :/")
            print("Lonelyness")
        miner.currentState = None
        miner.dead = True

    def exit(self, miner):
        pass


class GoToTheMovies(base.State):
    movieEndTime = 0
    minerArrivalList = []

    def enter(self, miner):
        self.movieEndTime = clk.clock.timeNow() + random.randint(2, 3)
        print(miner.name, ": Heading to the cinema now", sep="")
        if (self.movieEndTime > 23):
            self.movieEndTime = self.movieEndTime - 23

        miner.currentLocation = "Cinema"
        #Checks if this miner is the last to arrive and if it is then it'll ask which movie they should watch
        if(len(self.minerArrivalList) == len(em.entityMgr.entityDict) - 1):
            movieSuggestionDict = {
                0: "How about we watch The Amazing Bulk, i've heard that it's a great movie",
                1: "What do you think about Varning för Jönssonligan? It's a real classic",
                2: "Let's see the movie Blade Runner, it seems like a awesome movie",
                3: "Sweet they're playing The Room. That right there is a masterpiece. What do you say?"
            }
            randMovie = random.randint(0, len(movieSuggestionDict) - 1)
            print(miner.name, ": ", movieSuggestionDict.get(randMovie), sep="")
            md.dispatcher.dispatchMessageAll(0, miner.entityID, "MovieSuggestion")

        miner.interruptableState = False
        self.minerArrivalList.append(miner.entityID)

    def execute(self, miner):
        if(miner.currentLocation == "Cinema" and miner.hasPlans == True):
            miner.socialNeed -= 40
            print("MovieEndTime:", self.movieEndTime)
            print(miner.name, "*watching the movie*")
            if(miner.socialNeed <= 0):
                miner.socialNeed = 0

            if (self.movieEndTime == clk.clock.timeNow()):
                miner.changeState(SweetHome())
        else:
            miner.changeState(SweetHome())
        

    def exit(self, miner):
        self.minerArrivalList.clear()
        miner.interruptableState = True
        print(miner.name, ": Alright let's leave", sep="")
        miner.hasPlans = False


class GlobalState(base.State):
    def enter(self):
        pass

    def execute(self):
        md.dispatcher.dispatchDelayedMessages()

    def exit(self):
        pass

    def onMessage(self, telegram, miner):
        miner.lastTelegram = telegram
        if (telegram.msg == "MeetupRequest"):
            miner.hasPlans = True
            messageDelay = abs(clk.clock.timeNow() - int(telegram.extraInfo))
            print(em.entityMgr.getNameFromID(telegram.sender), ": Hey ", miner.name,
                  " do you want to go to the movies at ", telegram.extraInfo, ":00", sep="")
            print(miner.name,": Sure, sounds like a good idea", sep="") 
            md.dispatcher.dispatchMessage(messageDelay, miner.entityID, miner.entityID, "MeetupAck")

        elif (telegram.msg == "MeetupAck"):
            if(miner.interruptableState == False and miner.hasPlans == False):
                print(miner.name, ": i'm busy as well", sep="")
                return True

            if(miner.interruptableState == False):
                print(miner.name, ": I'm so sorry something came up so i won't be able to make it to the cinema", sep="")
                miner.hasPlans = False
                md.dispatcher.dispatchMessageAll(0,miner.entityID, "MeetupCancelled")
                md.dispatcher.dispatchMessage(0,miner.entityID, miner.entityID, "MeetupCancelled")
            elif(miner.hasPlans == False):
                print(miner.name, ": Well guess i'll go home then", sep="")
                if(isinstance(miner.currentState, GoToTheMovies)):
                    miner.changeState(SweetHome())
                
            else:
                miner.changeState(GoToTheMovies())

        elif (telegram.msg == "MovieSuggestion"):
            receiverEntity = em.entityMgr.getEntityFromID(telegram.reciever)
            if (receiverEntity.hasPlans == True):
                responseDict = {
                    0: "Yeah it's a great movie, you really have a good taste in movies",
                    1: "I guess?",
                    2: "I mean i'll watch it but i've heard that it's not really a good movie",
                    3: "I've never heard of it before but sure let's watch it"
                }
                randResponse = random.randint(0, len(responseDict) - 1)
                print(miner.name, ": ", responseDict.get(randResponse), sep="")
        elif(telegram.msg == "MeetupCancelled"):
            miner.hasPlans = False

        return True
        


class Miner(base.BaseGameEntity):
    def __init__(self, ID, minername):
        base.BaseGameEntity.nextValidID = ID + 1
        super().__init__(ID)
        self.name = minername
        self.thirst = random.randint(0, 15)
        self.hunger = random.randint(0, 15)
        self.fatigue = 0
        self.socialNeed = random.randint(0, 35)

        self.moneyCarried = 0
        self.moneyInTheBank = random.randint(0, 30)
        self.pocketSize = random.randint(10, 20)
        self.hasTools = bool(random.randint(0, 1))

    # Stats
    name = ""
    currentState = ISleep()
    globalState = GlobalState()
    currentLocation = "Home"
    interruptableState = False
    dead = False
    hasPlans = False
    lastTelegram = None

    thirst = 0
    hunger = 0
    fatigue = 0
    socialNeed = 0

    moneyCarried = 0
    moneyInTheBank = 0
    pocketSize = 10
    hasTools = False

    # Where everything happens
    def update(self):

        # if miner has currentState aka if miner is not dead
        if (self.currentState):
            self.thirst += 2
            self.hunger += 1
            self.socialNeed += 1
            self.fatigue += 1

            # stat printers
            print(self.name, " thirst: ", self.thirst, " hunger: ", self.hunger)
            print(self.name, " fatigue: ", self.fatigue, " social need: ", self.socialNeed)
            print(self.name, " moneyCarried: ", self.moneyCarried, " Money in the Bank: ", self.moneyInTheBank)
            print("\n")

            
            # If miner is in a state that can be interrupted
            if (self.interruptableState == True):
                # Social need checker
                if (self.socialNeed > 50 and self.hasPlans is False):
                    #Miner shouldn't be able to make plans while everyone is sleeping
                    if(clk.clock.timeNow() >= 22 and clk.clock.timeNow() < 8):
                        print(self.name, ": I want to make plans for tomorrow but i don't think anyone is awake now", sep="")
                    #Here everyone is awake
                    else:
                        randomMeetUpTime = random.randint(19,22)
                        print(self.name, ": i'm feeling lonely, let's see if any of my friends want to meet up later", sep="")
                        md.dispatcher.dispatchMessageAll(0, self.entityID, "MeetupRequest", randomMeetUpTime)
                        md.dispatcher.dispatchMessage(abs(randomMeetUpTime - clk.clock.timeNow()), self.entityID, self.entityID, "MeetupAck")
                        self.hasPlans = True
                #Miner goes to the store and buys a pickaxe if he doesn't have one
                if (self.hasTools == False and self.moneyInTheBank >= 10):
                    if(clk.clock.timeNow() > 8 and clk.clock.timeNow() < 19):
                        self.changeState(Store())

                # Thirst check
                if (self.thirst >= 30):
                    self.changeState(GoToTravven())
                    pass
                # Hunger check
                elif (self.hunger >= 30):
                    self.changeState(DallasTorsdag())
                    pass
                # Sleep check
                elif (self.fatigue >= 50 or (clk.clock.timeNow() > 23 or clk.clock.timeNow() < 8)):
                    if(self.hasPlans == True):
                        print(": I want to go to bed but i've already made plans tonight", sep="")
                    else:
                        #Check if currentState is already in Sleep and if it is just carry on
                        if(isinstance(self.currentState, ISleep) or isinstance(self.currentState, SweetHome)):
                            pass
                        else:
                            self.changeState(SweetHome())
            
            # This happens regardless if miner is in a interruptable state or not
            # Death states
            if (self.thirst >= 50):
                self.changeState(YouDied())
                pass
            elif (self.hunger >= 50):
                self.changeState(YouDied())
                pass
            elif (self.socialNeed >= 100):
                self.changeState(YouDied())
                pass

            # execute current state
            self.currentState.execute(self)

    def changeState(self, newstate):
        self.currentState.exit(self)

        self.currentState = newstate

        self.currentState.enter(self)

    def changeToWorkState(self):
        if(clk.clock.timeNow() > 8 and clk.clock.timeNow() < 19):
            if (self.hasTools == True):
                self.changeState(NuggetMining())
            else:
                self.changeState(CallCenter())
        else:
            self.changeState(SweetHome())
            

    def handleMessage(self, telegram):
        if (self.globalState and self.globalState.onMessage(telegram, self)):
            return True
        elif (self.globalState is None):
            raise TypeError("globalState is None")
        else:
            print("message was not delivered")
            return False


def main():
    minerlist = []
    minerlist.append(Miner(1, "Sven"))
    minerlist.append(Miner(2, "Steffe"))
    minerlist.append(Miner(3, "Åke"))
    minerlist.append(Miner(4, "Tim-Johan"))

    for miner in minerlist:
        em.entityMgr.registerEntity(miner)

    while (True):
        clk.clock.tick()
        print("____________________________________\n")
        clk.clock.printTime()
        print("\n")

        for miner in minerlist:
            if (miner.dead is True):
                minerlist.remove(miner)

        if (len(minerlist) == 0):
            print("Everyone is dead :(")
            break

        for miner in minerlist:
            miner.update()
            print("\n")
        

        index = 0
        while (index < len(minerlist)):
            index += 1
            miner.globalState.execute()
            

        # time advancer
        time.sleep(1)

#duttad
if __name__ == "__main__":
    main()
