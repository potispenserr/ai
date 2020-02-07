class Telegram:
    sender = 0
    reciever = 0
    msg = ""
    dispatchTime = 0
    extraInfo = ""
    def __init__(self, sender, reciever, msg, dispatchtime, extrainfo = None):
        self.sender = sender
        self.reciever = reciever 
        self.msg = msg
        self.dispatchTime = dispatchtime
        self.extraInfo = extrainfo
    def printTelegram(self):
        print("Sender:", self.sender, "Reciever", self.reciever, "Message: ", self.msg, "DispatchTime:", self.dispatchTime, "ExtraInfo: ", self.extraInfo)