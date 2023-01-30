# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util, math

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generateSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newGhosts = successorGameState.getGhostPositions()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        "***Reference to https://github.com/janluke/cs188***"
        ghostDistances = [manhattanDistance(newPos, ghost.configuration.pos)
                          for ghost in newGhostStates
                          if ghost.scaredTimer == 0]

        minGhostDist = min(ghostDistances, default=100)
        if minGhostDist == 0:
            return -math.inf
        numFood = successorGameState.getNumFood()
        if numFood == 0:
            return math.inf

        food = currentGameState.getFood()
        if food[newPos[0]][newPos[1]]:
            minFoodDist = 0
        else:
            foodDistances = [
                manhattanDistance(newPos, (x, y))
                for x in range(food.width)
                for y in range(food.height)
                if food[x][y]
            ]
            minFoodDist = min(foodDistances, default=0)

        danger = 1 / (minGhostDist - 0.5)
        profit = 1 / (minFoodDist + 0.5)
        score = -danger + profit
        return score
    
def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()
        
        def value(gameState: GameState, agentIndex: int, depth: int):
            if agentIndex >= numAgents:
                agentIndex = 0
                depth -= 1
            if depth <= 0 or gameState.isWin() or gameState.isLose():
                return self.evaluationFunction(gameState)
            succValues = [value(gameState.generateSuccessor(agentIndex, action), agentIndex + 1, depth) \
                            for action in gameState.getLegalActions(agentIndex)]
            if agentIndex == 0:
                return max(succValues)
            else:
                return min(succValues)
        
        maxScore, minimaxAction = -math.inf, None  # maxScore可能是负分！
        for action in gameState.getLegalActions():
            succValue = value(gameState.generateSuccessor(0, action), 1, self.depth)  # 下一个agent编号是1啊！
            if succValue > maxScore:
                maxScore, minimaxAction = succValue, action
        return minimaxAction

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()
        
        def value(gameState: GameState, agentIndex: int, depth: int, alpha: int, beta: int):
            if agentIndex >= numAgents:
                agentIndex = 0
                depth -= 1
            if depth <= 0 or gameState.isWin() or gameState.isLose():
                return self.evaluationFunction(gameState)
            if agentIndex == 0:
                v = -math.inf
                for action in gameState.getLegalActions(agentIndex):
                    v = max(v, value(gameState.generateSuccessor(agentIndex, action), agentIndex + 1, depth, alpha, beta))
                    if v > beta:  # beta是当前min节点的最优选择，既然已经比他大了就肯定不可能成为最优选择，直接把这个值当作该节点的value返回即可（反正后续不会用到它的）
                        return v
                    alpha = max(alpha, v)
            else:
                v = math.inf
                for action in gameState.getLegalActions(agentIndex):
                    v = min(v, value(gameState.generateSuccessor(agentIndex, action), agentIndex + 1, depth, alpha, beta))
                    if v < alpha:
                        return v
                    beta = min(beta, v)
            return v
        
        alpha, beta = -math.inf, math.inf
        maxScore, minimaxAction = -math.inf, None
        for action in gameState.getLegalActions():
            succValue = value(gameState.generateSuccessor(0, action), 1, self.depth, alpha, beta)
            if succValue > maxScore:
                maxScore, minimaxAction = succValue, action
            alpha = max(alpha, succValue)  # 别忘了最外层的alpha更新！！！
        return minimaxAction

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()
        
        def value(gameState: GameState, agentIndex: int, depth: int):
            if agentIndex >= numAgents:
                agentIndex = 0
                depth -= 1
            if depth <= 0 or gameState.isWin() or gameState.isLose():
                return self.evaluationFunction(gameState)
            succValues = [value(gameState.generateSuccessor(agentIndex, action), agentIndex + 1, depth) \
                            for action in gameState.getLegalActions(agentIndex)]
            if agentIndex == 0:
                return max(succValues)
            else:
                return sum(succValues) / len(succValues)
        
        maxScore, minimaxAction = -math.inf, None  # maxScore可能是负分！
        for action in gameState.getLegalActions():
            succValue = value(gameState.generateSuccessor(0, action), 1, self.depth)  # 下一个agent编号是1啊！
            if succValue > maxScore:
                maxScore, minimaxAction = succValue, action
        return minimaxAction

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    "***Reference to https://github.com/janluke/cs188 with little modification***"
    state = currentGameState
    currentScore = state.getScore()
    if state.isWin() or state.isLose():
        return currentScore
    pacman = state.getPacmanPosition()
    ghosts = state.getGhostStates()
    ghostDistances = [manhattanDistance(pacman, tuple(map(int, ghost.configuration.pos)))
                      for ghost in ghosts]
    scaredTimers = [ghost.scaredTimer for ghost in ghosts]
    distFromUnscared = [dist for dist, timer in zip(ghostDistances, scaredTimers) if timer == 0]
    distFromScared = [dist for dist, timer in zip(ghostDistances, scaredTimers) if timer > 2]
    ghostPenalty = sum((300 / dist ** 2 for dist in distFromUnscared), 0)
    ghostBonus = sum((200 / dist for dist in distFromScared), 0)

    foods = state.getFood().asList()
    manhattanDistances = [manhattanDistance(pacman, food) for food in foods]
    foodBonus = sum(10 / d for d in manhattanDistances[:5])

    score = currentScore - ghostPenalty + ghostBonus + foodBonus # + capsuleBonus
    return score

# Abbreviation
better = betterEvaluationFunction
