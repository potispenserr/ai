import entityManager
import baseClasses as base
import telegram as tele
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

        self.discharge(reciever, telegram)

    def dispatchDelayedMessages(self):
        pass


    def discharge(self, reciever, telegram):
        pass