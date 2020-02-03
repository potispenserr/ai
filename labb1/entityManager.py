import baseClasses as base

class EntityManager:
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance
        
    entityDict = {

    }

    def registerEntity(self,baseEntity):
        self.entityDict[baseEntity.entityID] = baseEntity()

    def getEntityFromID(self, id):
        if id in self.entityDict:
            return self.entityDict.get(id)
        else:
            print("ID is not registered")

    def removeEntity(self, id):
        self.entityDict.pop(id)