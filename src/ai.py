from numpy.random import randint

from actions import MovementAction

class RabbitAI():
    def __init__(self, rabbit):
        self.rabbit = rabbit

    def perform(self):
        num = randint(4)

        if(num == 0):
            MovementAction(-1, 0).perform(self.rabbit)
        elif(num == 1):
            MovementAction(1, 0).perform(self.rabbit)
        elif(num == 2):
            MovementAction(0, -1).perform(self.rabbit)
        elif(num == 3):
            MovementAction(0, 1).perform(self.rabbit)
