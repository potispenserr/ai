import time
import random
import baseClasses as base
import clock as clk
import entityManager as em
import messageDispatcher as md
import telegram as tele

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
            print(miner.name, ": gonna get me some nuggets")
            miner.currentLocation = "Mine"

    def execute(self, miner):
        if(miner.currentLocation == "Mine"):
            miner.moneyCarried += 2
            miner.fatigue += 2
            print(miner.name, ": gettin' them nuggets")
            if (miner.moneyCarried >= miner.pocketSize):
                miner.changeState(PushForceBank())
            toolBreakChance = random.randint(1, 10)
            if (toolBreakChance < 2):
                miner.hasTools = False
                print(miner.name, ": Ah shucks my goddamned pickaxe broke")
                miner.changeToWorkState()

    def exit(self, miner):
        if (miner.moneyCarried >= miner.pocketSize):
            print(miner.name, ": Sold all of my chicken nuggets i dug up! Time to deposit all the money", sep="")
        elif (miner.hasTools == False):
            print(miner.name, ": Well my pickaxe broke so i can't continue here", sep="")
        else:
            print(miner.name, ": I'm done working, time to do something else", sep="")

    def onMessage(self, telegram):
        pass


class CallCenter(base.State):
    def enter(self, miner):
        print(miner.name, ": Heading to the dreaded Microsoft tech-support center")
        miner.currentLocation = "CallCenter"

    def execute(self, miner):
        print(miner.name, ":Rude people on the line, why am i not surprised")
        if (miner.moneyCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())
        miner.fatigue += 3
        #Miner gets money deposited into his bank instead of in his hand
        miner.moneyInTheBank += 1
        if (miner.moneyCarried >= miner.pocketSize):
            miner.changeState(PushForceBank())

    def exit(self, miner):
        print(miner.name, ":I've just about had it with rude people on the phone asking stupid shit")

    def onMessage(self, telegram):
        return False


# Sleep
class ISleep(base.State):

    def enter(self, miner):
        if (miner.currentLocation != "Home"):
            miner.currentLocation = "Home"
            print(miner.name, ":I'm going home to sleep")

        miner.currentLocation = "Home"
        print(miner.name, ":I'm so tired... I'm going to rest for a bit")
        miner.interruptableState = False

    def execute(self, miner):
        if(miner.currentLocation == ""):
            miner.currentLocation = "Home"
            miner.interruptableState = False

        print(miner.name, ": zzzzz")
        miner.fatigue -= 6
        if (miner.fatigue < 0):
            miner.fatigue = 0
            if (miner.previousState):
                miner.revertToPreviousState()
            else:
                miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ": Alright let's get this bread")
        miner.interruptableState = True

    def onMessage(self, telegram):
        minerName = em.entityMgr.getNameFromID(telegram.sender)
        print("To ", minerName, ":" " ey b0ss rot op man", sep="")


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
        print(miner.name, ": Hello, i would like to bank some cash please", sep="")

    def execute(self, miner):
        print(miner.name, ": Here's some of the cash", sep="")
        miner.moneyCarried -= 3
        miner.moneyInTheBank += 3
        if (miner.moneyCarried <= 0):
            miner.moneyCarried = 0
            miner.changeToWorkState()

    def exit(self, miner):
        print(miner.name, ": And that was that. Let's do something else", sep="")
        print(miner.name, ": Money in bank: ", miner.moneyCarried, sep="")

    def onMessage(self, telegram):
        return False


class GoToTravven(base.State):
    def enter(self, miner):
        miner.currentLocation = "Travven"
        print("Thirst: ", miner.thirst)
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
        print(miner.name, ": God damn it, it's sista beställningen", sep="")

    def onMessage(self, telegram):
        return False


class DallasTorsdag(base.State):
    def enter(self, miner):
        miner.currentLocation = "Dallas"
        randint = random.randint(0, 2)
        print("Hunger: ", miner.hunger)
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


    def onMessage(self, telegram):
        return False


class Store(base.State):
    def enter(self, miner):
        print(miner.name, ":Time to get a pickaxe so i can mine chicken nuggets")
        miner.currentLocation = "Store"

    def execute(self, miner):
        print(miner.name, ":I got the pickaxe, now Im going to check it out")
        miner.hasTools = True
        miner.moneyInTheBank -= 10
        #Edge Case: If the previous state was working at the call center then
        #It doesn't make much sense to continue working at the call center if miner can work at the nugget mine
        if(isinstance(miner.previousState,CallCenter)):
            miner.changeToWorkState()
        else:
            miner.revertToPreviousState()

    def exit(self, miner):
        print(miner.name, ":This pickaxe cost me a pretty penny so i sure hope it was worth it")

    def onMessage(self, telegram):
        return False


# Rip in kill
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
        # print("You're lying dead on the floor")
        miner.currentState = None
        miner.previousState = None
        miner.dead = True

    def exit(self, miner):
        # print(miner.name, ":Guess who's back, back again")
        pass

    def onMessage(self, telegram):
        return False


class GoToTheMovies(base.State):
    movieEndTime = 0
    minerArrivalList = []
    minerDepartureList = []
    def enter(self, miner):
        self.minerDepartureList.clear()
        #self.movieEndTime = clk.clock.timeNow() + random.randint(2, 3)
        self.movieEndTime = 25
        if (self.movieEndTime > 23):
            self.movieEndTime = self.movieEndTime - 23
            print("movieendtime: ", self.movieEndTime)

        miner.currentLocation = "Cinema"
        #print(miner.name, ": at the cinema now")
        print("MinerArrivalList:", self.minerArrivalList, "entityDict:", em.entityMgr.entityDict)
        #Checks if 
        if(len(self.minerArrivalList) == len(em.entityMgr.entityDict) - 1):
            movieSuggestionDict = {
                0: "How about we watch The Amazing Bulk, i've heard that it's a great movie",
                1: "What do you think about Varning för Jönssonligan? It's a real classic",
                2: "Let's see the movie Cats, it seems like a awesome movie",
                3: "Sweet they're playing The Room. That right there is a masterpiece. What do you say?"
            }
            randMovie = random.randint(0, len(movieSuggestionDict) - 1)
            print(miner.name, ": ", movieSuggestionDict.get(randMovie), sep="")
            md.dispatcher.dispatchMessageAll(0, miner.entityID, "MovieSuggestion")
        miner.interruptableState = False
        self.minerArrivalList.append(miner.entityID)

    def execute(self, miner):
        miner.socialNeed -= 25
        print("MovieEndTime:", self.movieEndTime)

        # Sends a message to all other people that are with the miner at the cinema
        # Only if the last telegram is MeetupAck which means that this miner is the first to arrive at the cinema
        # And only if interruptible state is True which means that this is the first time it's sending the message

        #print("InterruptableStateInCinema:", miner.interruptableState)
        print(miner.name, "*watching the movie*")
        #print("InterruptableStateInCinema2:", miner.interruptableState)

        if (clk.clock.timeNow() >= self.movieEndTime):
            miner.revertToPreviousState()

    def exit(self, miner):
        #print("man that was a great movie")
        self.minerArrivalList.clear()
        miner.interruptableState = True
       #if(len(self.minerDepartureList) == len(em.entityMgr.entityDict) - 1):
       #    print(miner.name, ": So what do you guys think about the movie?")
       #    for id in self.minerDepartureList:
       #        md.dispatcher.dispatchMessage(0,miner.entityID, id, "MovieFeedback")
       #self.minerDepartureList.append(miner.entityID)
        print(miner.name, ":Alright let's leave", sep="")
        miner.hasPlans = False

    def onMessage(self, telegram):
        return False


class GlobalState(base.State):
    def enter(self):
        pass

    def execute(self):
        md.dispatcher.dispatchDelayedMessages()

    def exit(self):
        pass

    def onMessage(self, telegram, miner):
        telegram.printTelegram()
        miner.lastTelegram = telegram
        if (telegram.msg == "MeetupRequest"):
            miner.hasPlans = True
            messageDelay = abs(clk.clock.timeNow() - int(telegram.extraInfo))
            #print("MessageDelay:", messageDelay)
            print(em.entityMgr.getNameFromID(telegram.sender), ": Hey ", miner.name,
                  " do you want to go to the movies at ", telegram.extraInfo, ":00", sep="")

            if(miner.thirst >= 25 or miner.hunger >= 25 or miner.fatigue >= 45):

                print(miner.name, ": Nah mate ", sep="",end="")
                if(miner.thirst >= 25):
                    print("i'm too thirsty", sep="", end="")

                elif(miner.hunger >= 25):
                    print("i'm too hungry", sep="", end="")

                elif(miner.fatigue >= 45):
                    print("i'm too tired", sep="", end="")

                print(" let's do it some other time")

                md.dispatcher.dispatchMessage(0, miner.entityID, telegram.sender, "MeetupDenied", clk.clock.timeNow())
                md.dispatcher.dispatchMessage(0, miner.entityID, miner.entityID, "MeetupDenied", clk.clock.timeNow())
            else:
                print(miner.name,": Sure sounds like a good idea", sep="") 
                md.dispatcher.dispatchMessage(messageDelay, miner.entityID, miner.entityID, "MeetupAck")
                md.dispatcher.dispatchMessage(messageDelay, miner.entityID, telegram.sender, "MeetupAck")

        elif (telegram.msg == "MeetupAck"):
            if(miner.interruptableState == False):
                print(miner.name, ": I'm so sorry something came up so i won't be able to make it to the cinema")
                miner.hasPlans = False
                md.dispatcher.dispatchMessageAll(0,miner.entityID, "MeetupCancelled")
                md.dispatcher.dispatchMessage(0,miner.entityID, miner.entityID, "MeetupCancelled")
            elif(miner.hasPlans == False):
                print(miner.name, ": Guess i'll do something else")
                miner.revertToPreviousState()
            else:
                print(miner.name, ":Yo let's do it")
                miner.changeState(GoToTheMovies())

        elif (telegram.msg == "MovieSuggestion"):
            receiverEntity = em.entityMgr.getEntityFromID(telegram.reciever)
            if (receiverEntity.hasPlans == True):
                responseDict = {
                    0: "Yeah it's a great movie, you really have a good taste in movies",
                    1: "No it's a shit movie let's watch something else",
                    2: "Fuck off with that bullshit! Do i really have to watch it?",
                    3: "I've never heard of it before but sure let's watch it"
                }
                randResponse = random.randint(0, len(responseDict) - 1)
                print(miner.name, ": ", responseDict.get(randResponse), sep="")

        elif (telegram.msg == "MovieFeedback"):
            feedbackDict = {
                0: "Yeah it was a pretty good movie",
                1: "I have to say that it was the best movie i've ever seen",
                2: "It was alright",
                3: "The movie was really boring",
                4: "It was kind of shit",
                5: "I wonder if i can get my money back"
            }
            randFeedback = random.randint(0, len(feedbackDict) - 1)
            print(miner.name, ": ", feedbackDict.get(randFeedback), sep="")
        elif(telegram.msg == "MeetupCancelled"):
            print(miner.name, ": That's too bad", sep="")
            miner.hasPlans = False
        elif(telegram.msg == "MeetupDenied"):
            miner.hasPlans = False
            pass

        return True
        


class Miner(base.BaseGameEntity):
    def __init__(self, ID, minername):
        super().__init__(ID)
        self.name = minername
        self.thirst = random.randint(0, 15)
        self.hunger = random.randint(0, 15)
        self.fatigue = random.randint(0, 15)
        self.socialNeed = random.randint(0, 35)

        self.moneyCarried = 0
        self.moneyInTheBank = random.randint(0, 30)
        self.pocketSize = random.randint(10, 20)
        self.hasTools = bool(random.randint(0, 1))

    # Stats
    name = ""
    previousState = None
    currentState = ISleep()
    globalState = GlobalState()
    currentLocation = "Home"
    loclist = ("Hell?", "Dallas", "Travven", "Home", "Bank", "Mine", "CallCenter", "Store", "Cinema")
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

        # if miner has currentState
        if (self.currentState):
            self.thirst += 2
            self.hunger += 1
            self.socialNeed += 1
            self.fatigue += 1

            #print("Interruptable states:", self.interruptableState)

            # stat printers
            print(self.name, " thirst: ", self.thirst, " hunger: ", self.hunger)
            print(self.name, " fatigue: ", self.fatigue, " social need: ", self.socialNeed)
            print(self.name, " moneyCarried: ", self.moneyCarried, " Money in the Bank: ", self.moneyInTheBank)

            
            # Eat and Drink checks
            if (self.interruptableState == True):
                # Social need checker
                if (self.socialNeed > 70 and self.hasPlans is False):
                    randomMeetUpTime = random.randint(16,22)
                    print("i'm feeling lonely, let's see if any of my friends want to meet up")
                    md.dispatcher.dispatchMessageAll(0, self.entityID, "MeetupRequest", randomMeetUpTime)
                    self.hasPlans = True

                if (self.hasTools == False and self.moneyInTheBank >= 10):
                    if (clk.clock.timeNow() > 8 and clk.clock.timeNow() < 19):
                        self.changeState(Store())
                # Check if Death is imminent
                if (self.thirst >= 30):
                    self.changeState(GoToTravven())
                    pass

                elif (self.hunger >= 30):
                    self.changeState(DallasTorsdag())
                    pass

                elif (self.fatigue >= 50):
                    self.changeState(ISleep())
                    pass
                
            
            #Errorchecking if lastTelegram is None
            if(self.lastTelegram):
                #Checks if last telegram was MeetupDenied and if miner recived it 6 hours earlier
                #So the miner doesn't constantly spam MeetupRequests
                if(self.lastTelegram.msg == "MeetupDenied" and clk.clock.timeNow() >= self.lastTelegram.extraInfo + 6):
                    print(self.name, "MY PLANS HAS BEEN CLEARED")
                    self.hasPlans = False

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

        # If currentState is None check if miner has previous state
        elif (self.previousState):
            self.revertToPreviousState()

    def changeState(self, newstate):
        self.currentState.exit(self)

        self.previousState = self.currentState
        self.currentState = newstate

        self.currentState.enter(self)

    def changeToWorkState(self):
        if (self.hasTools == True):
            self.changeState(NuggetMining())
        else:
            self.changeState(CallCenter())

    def revertToPreviousState(self):
        if (self.previousState):
            self.changeState(self.previousState)

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
    for miner in minerlist:
        em.entityMgr.registerEntity(miner)
    #minerlist[0].thirst = 1000
    #minerlist[0].hunger = 1000
    minerlist[0].fatigue = 1000
    #minerlist[0].currentState = DallasTorsdag()
    minerlist[0].hasTools = True

    #minerlist[1].thirst = 1000
    #minerlist[1].hunger = 1000
    #minerlist[1].fatigue = 1000
    #minerlist[1].currentState = DallasTorsdag()
    minerlist[1].socialNeed = 60

    while (True):
        clk.clock.tick()
        print("____________________________________\n")
        clk.clock.printTime()
        print("\n")

        minerindex = 0

        while (minerindex < len(minerlist)):
            minerindex += 1
            for miner in minerlist:
                if (miner.dead is True):
                    minerlist.remove(miner)

        if (len(minerlist) == 0):
            print("Everyone is dead :(")
            break

        for miner in minerlist:
            print("\n")
            miner.update()
            print("\n")
            

        index = 0
        while (index < len(minerlist)):
            index += 1
            miner.globalState.execute()
            

        # time advancer
        time.sleep(1)


if __name__ == "__main__":
    main()
