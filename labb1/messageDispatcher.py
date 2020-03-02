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

    #Sends a message to reciever
    def dispatchMessage(self, delay, sender, reciever, msg, extrainfo = None):
        recieverEntity = em.entityMgr.getEntityFromID(reciever)

        if(recieverEntity is None):
            print("Warning! No reciever has the ID: ", reciever)
            
        else:
            telegram = tele.Telegram(sender, reciever, msg, 0, extrainfo)
            if(delay <= 0):
                self.discharge(recieverEntity, telegram)
            
            else:
                telegram.dispatchTime = clk.clock.timeNow() + delay
                if (telegram.dispatchTime > 23):
                    telegram.dispatchTime = telegram.dispatchTime - 23
                self.msgqueue.append(telegram)

    #Sends a message to everyone except the sender
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
                    if (telegram.dispatchTime > 23):
                        telegram.dispatchTime = telegram.dispatchTime - 23
                    telegram.dispatchTime = clk.clock.timeNow() + delay
                    self.msgqueue.append(telegram)
                    



    #Loops through msgqueue and discharges the messages that are ready
    def dispatchDelayedMessages(self):
        lastTelegram = None
        index = 1
        while(len(self.msgqueue) > 0):
            for msg in self.msgqueue:
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
                else:
                    break
            break


    def discharge(self, recieverEntity, telegram):
        recieverEntity.handleMessage(telegram)
dispatcher = MessageDispatcher()

