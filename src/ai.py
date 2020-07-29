from numpy.random import randint


class AI:
    def perform(self, entity):
        pass # should raise 'not implemented' or whatever

class RabbitAI():
    def __init__(self, rabbit):
        self.rabbit = rabbit
    def perform(self):
        num = randint(4)

        if(num == 0):
            self.rabbit.x = self.rabbit.x - 1
        elif(num == 1):
            self.rabbit.x = self.rabbit.x + 1
        elif(num == 2):
            self.rabbit.y = self.rabbit.y - 1
        elif(num == 3):
            self.rabbit.y = self.rabbit.y + 1
