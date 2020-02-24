import entityManager as em
import baseClasses as base
import telegram as tele
import clock as clk
class MessageDispatcher:
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    msgqueue = []
    #entityMgr = entityManager.EntityManager

    def dispatchMessage(self, delay, sender, reciever, msg, extrainfo = None):
        recieverEntity = em.entityMgr.getEntityFromID(reciever)
        #print("dispatching message")

        if(recieverEntity is None):
            print("Warning! No reciever has the ID: ", reciever)
            
        else:
            telegram = tele.Telegram(sender, reciever, msg, 0, extrainfo)
            if(delay <= 0):
                self.discharge(recieverEntity, telegram)
            
            else:
                telegram.dispatchTime = clk.clock.timeNow() + delay
                if (telegram.dispatchTime > 23):
                    telegram.dispatchTime = self.movieEndTime - 23
                print(em.entityMgr.getNameFromID(telegram.sender), "said", telegram.msg, "to",recieverEntity.name, "but we'll put it into the backburner")
                self.msgqueue.append(telegram)

    def dispatchMessageAll(self, delay, sender, msg, extrainfo = None):
        for entID, ent in em.entityMgr.entityDict.items():
            if(entID == sender):
                pass
            else:
                recieverEntity = ent
                
                telegram = tele.Telegram(sender,entID,msg,0,extrainfo)
                if(delay <= 0):
                    self.discharge(recieverEntity, telegram)
                else:
                    telegram.dispatchTime = clk.clock.timeNow() + delay
                    print(em.entityMgr.getNameFromID(telegram.sender), "said", telegram.msg, "to",recieverEntity.name, "but we'll put it into the backburner")
                    self.msgqueue.append(telegram)
                    




    def dispatchDelayedMessages(self):
        lastTelegram = None
        index = 1
        while(len(self.msgqueue) > 0):
            for msg in self.msgqueue:
                #print(msg.msg, " and dispatchtime", msg.dispatchTime)
                #print("looping through message number",self.msgqueue.index(msg))
                index += 1
                if (msg.dispatchTime <= clk.clock.timeNow() and msg.dispatchTime > 0):
                    if(lastTelegram is not None and lastTelegram == msg):
                        print("Duplicate telegram")
                        self.msgqueue.pop(self.msgqueue.index(msg))
                    else:
                        lastTelegram = msg
                        reciever = em.entityMgr.getEntityFromID(msg.reciever)
                        self.discharge(reciever, msg)
                        self.msgqueue.pop(self.msgqueue.index(msg))
                        #print("dispatching telegram")
                else:
                    break
            break


    def discharge(self, recieverEntity, telegram):
        #print(telegram.sender, "discharged a message for", telegram.reciever, "at time", clk.clock.timeNowFormat(), "with the message", telegram.msg, "extra info:", telegram.extraInfo)
        #print("discharging message")
        print(em.entityMgr.getNameFromID(telegram.sender), "said", telegram.msg, "to",recieverEntity.name, "with extra info", telegram.extraInfo)
        recieverEntity.handleMessage(telegram)
dispatcher = MessageDispatcher()

