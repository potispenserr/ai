import baseClasses as base

class EntityManager:    
    entityDict = {

    }

    def registerEntity(self,baseEntity):
        self.entityDict[baseEntity.entityID] = baseEntity

    def getEntityFromID(self, id):
        if id in self.entityDict:
            return self.entityDict.get(id)
        else:
            print("ID is not registered")

    def getNameFromID(self, id):
        if id in self.entityDict:
            return self.entityDict[id].name

    def removeEntity(self, id):
        self.entityDict.pop(id)

    def printEntityDict(self):
        for elem in self.entityDict.values():
            print(elem.name)

entityMgr = EntityManager()
    
