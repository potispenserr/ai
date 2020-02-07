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
        print("dispatching message")

        if(recieverEntity is None):
            print("Warning! No reciever has the ID: ", reciever)
            
        else:
            telegram = tele.Telegram(sender, reciever, msg, 0, extrainfo)
            if(delay <= 0):
                self.discharge(recieverEntity, telegram)
            
            else:
                telegram.dispatchTime = clk.clock.timeNow() + delay
                print("Dispatch time:",telegram.dispatchTime)
                self.msgqueue.append(telegram)

    def dispatchDelayedMessages(self):
        for msg in self.msgqueue:
            if (msg.dispatchTime <= clk.clock.timeNow() and msg.dispatchTime > 0):
                reciever = em.entityMgr.getEntityFromID(msg.reciever)
                self.discharge(reciever, msg)
                self.msgqueue.pop(0)


    def discharge(self, recieverEntity, telegram):
        #print(telegram.sender, "discharged a message for", telegram.reciever, "at time", clk.clock.timeNowFormat(), "with the message", telegram.msg, "extra info:", telegram.extraInfo)
        print("discharging message")
        print(em.entityMgr.getNameFromID(telegram.sender), "said", telegram.msg, "to",recieverEntity.name, "with extra info", telegram.extraInfo)
        recieverEntity.handleMessage(telegram)
dispatcher = MessageDispatcher()