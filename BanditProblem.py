import numpy as np

class BanditProblem(object):

    def __init__(self, trueActionValues, epsilon, totalSteps):
        # Number of arms is the length of the true action values
        self.armNumber = np.size(trueActionValues)
        self.epsilon = epsilon

        # Current step initialized to 0
        self.currentStep = 0

        # Track how many times each arm is selected
        self.howManyTimesParticularArmIsSelected = np.zeros(self.armNumber)

        # Total number of steps to play
        self.totalSteps = totalSteps

        # True action values of the arms
        self.trueActionValues = trueActionValues

        # Track the estimated mean reward of each arm
        self.armMeanRewards = np.zeros(self.armNumber)

        # Current reward for each step
        self.currentReward = 0

        # Mean rewards per step
        self.meanReward = np.zeros(totalSteps + 1)

    def selectActions(self):
        probabilityDraw = np.random.rand()

        # Epsilon-greedy action selection
        if (self.currentStep == 0) or (probabilityDraw <= self.epsilon):
            # Explore: Randomly select an arm
            selectedArmIndex = np.random.choice(self.armNumber)
        else:
            # Exploit: Select the arm with the highest estimated reward
            selectedArmIndex = np.argmax(self.armMeanRewards)

        # Update the current step
        self.currentStep += 1

        # Increase the count of how many times the selected arm was chosen
        self.howManyTimesParticularArmIsSelected[selectedArmIndex] += 1

        # Get a reward from the selected arm, using a normal distribution
        self.currentReward = np.random.normal(self.trueActionValues[selectedArmIndex], 2)

        # Update the overall mean reward
        self.meanReward[self.currentStep] = self.meanReward[self.currentStep - 1] + (1/(self.currentStep))*(self.meanReward)
        # Update the mean reward for the selected arm (incremental update formula)
        self.armMeanRewards[selectedArmIndex] += (self.currentReward - self.armMeanRewards[selectedArmIndex]) / self.howManyTimesParticularArmIsSelected[selectedArmIndex]


    def playGames(self):
        # Simulate the game over the total number of steps
        for _ in range(self.totalSteps):
            self.selectActions()

    def clearAll(self):
        # Reset all values
        self.currentStep = 0
        self.howManyTimesParticularArmIsSelected = np.zeros(self.armNumber)
        self.armMeanRewards = np.zeros(self.armNumber)
        self.currentReward = 0
        self.meanReward = np.zeros(self.totalSteps + 1)
