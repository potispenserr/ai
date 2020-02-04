import entityManager
import baseClasses as base
import telegram as tele
import clock as clk
from collections import deque
class MessageDispatcher:
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    msgqueue = []
    entityMgr = entityManager.EntityManager

    def dispatchMessage(self, delay, sender, reciever, msg, extrainfo):
        pReciever = self.entityMgr.getEntityFromID(sender)

        telegram = tele.Telegram(sender, reciever, msg, 0, extrainfo)
        if(delay <= 0):
            self.discharge(reciever, telegram)
        
        else:
            telegram.dispatchTime = clk.clock.timeNow + delay
            self.msgqueue.append(telegram)

    def dispatchDelayedMessages(self):
        for msg in self.msgqueue:
            if (msg.dispatchTime < clk.clock.timeNow and msg.dispatchTime > 0):
                reciever = self.entityMgr.getEntityFromID(msg.reciever)
                self.discharge(reciever, msg)
                self.msgqueue.pop(0)


    def discharge(self, reciever, telegram):
        pass