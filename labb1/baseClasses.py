class BaseGameEntity:
    entityID = 1
    nextValidID = 2

    def __init__(self, val):
        if(val > self.nextValidID):
            raise IndexError("Invalid entityID")
        else:
            self.entityID = val
            self.nextValidID = val + 1

    def update(self):
        raise NotImplementedError("pls implement me :(")

# Base State class
class State:
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def enter(self):
        print("Enter the gungeon")
        raise NotImplementedError("plizz ipmelemnt me :/")

    def execute(self):
        print("YOU HAVE BEEN EXECUTED")
        raise NotImplementedError("plizz ipmelemnt me :/")

    def exit(self):
        print("Escaped from tarkob")
        raise NotImplementedError("plizz ipmelemnt me :/")