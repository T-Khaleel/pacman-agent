# my_team.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import random, time, util, sys
import contest.game
from contest.distance_calculator import DistanceCalculator
from contest.capture_agents import CaptureAgent
from contest.game import Directions
from contest.util import nearest_point
import math


#################
# Team creation #
#################

def create_team(first_index, second_index, is_red,
                first='OffensiveReflexAgent', second='DefensiveReflexAgent', num_training=0):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --red_opts and --blue_opts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """
    return [eval(first)(first_index), eval(second)(second_index)]


##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that choose score-maximizing actions
    """

    def get_successor(self, game_state, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = game_state.generate_successor(self.index, action)
        pos = successor.get_agent_state(self.index).get_position()
        if pos != nearest_point(pos):
            # Only half a grid position was covered
            return successor.generate_successor(self.index, action)
        else:
            return successor

    def evaluate(self, game_state, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.get_features(game_state, action)
        weights = self.get_weights(game_state, action)
        return features * weights

    def get_features(self, game_state, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.get_successor(game_state, action)
        features['successor_score'] = self.get_score(successor)
        return features

    def get_weights(self, game_state, action):
        """
        Normally, weights do not depend on the game state.  They can be either
        a counter or a dictionary.
        """
        return {'successor_score': 1.0}


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
    def __init__(self, index):
        CaptureAgent.__init__(self, index)        
        self.presentCoordinates = (-5 ,-5)
        self.counter = 0
        self.attack = False
        self.lastFood = []
        self.presentFoodList = []
        self.shouldReturn = False
        self.capsulePower = False
        self.targetMode = None
        self.eatenFood = 0
        self.initialTarget = []
        self.hasStopped = 0
        self.capsuleLeft = 0
        self.prevCapsuleLeft = 0

    def register_initial_state(self, game_state):
        self.currentFoodSize = 9999999
        
        CaptureAgent.register_initial_state(self, game_state)
        self.initPosition = game_state.get_agent_state(self.index).get_position()
        self.initialAttackCoordinates(game_state)
        
    def initialAttackCoordinates(self ,game_state):
        
        layoutInfo = []
        x = (game_state.data.layout.width - 2) // 2
        if not self.red:
            x +=1
        y = (game_state.data.layout.height - 2) // 2
        layoutInfo.extend((game_state.data.layout.width , game_state.data.layout.height ,x ,y))
       
        self.initialTarget = []

        
        for i in range(1, layoutInfo[1] - 1):
            if not game_state.has_wall(layoutInfo[2], i):
                self.initialTarget.append((layoutInfo[2], i))
        
        noTargets = len(self.initialTarget)
        if(noTargets%2==0):
            noTargets = (noTargets//2) 
            self.initialTarget = [self.initialTarget[noTargets]]
        else:
            noTargets = (noTargets-1)//2
            self.initialTarget = [self.initialTarget[noTargets]] 
            
        
    def get_features(self, game_state, action):
        features = util.Counter()
        successor = self.get_successor(game_state, action) 
        position = successor.get_agent_state(self.index).get_position() 
        foodList = self.get_food(successor).as_list() 
        features['successor_score'] = self.get_score(successor) 

        if successor.get_agent_state(self.index).is_pacman:
            features['offence'] = 1
        else:
            features['offence'] = 0

        if foodList: 
            features['foodDistance'] = min([self.get_maze_distance(position, food) for food in foodList])

        opponentsList = []
       
        disToGhost = []
        opponentsList = self.get_opponents(successor)

        for i in range(len(opponentsList)):
            enemyPos = opponentsList[i]
            enemy = successor.get_agent_state(enemyPos)
            if not enemy.is_pacman and enemy.get_position() != None:
                ghostPos = enemy.get_position()
                disToGhost.append(self.get_maze_distance(position ,ghostPos))


        if len(disToGhost) > 0:
            minDisToGhost = min(disToGhost)
            if minDisToGhost < 5:
                features['distanceToGhost'] = minDisToGhost + features['successor_score']
            else:
                features['distanceToGhost'] = 0


        return features

    def get_weights(self, game_state, action):
        '''
        Setting the weights manually after many iterations
        '''

        if self.attack:
            if self.shouldReturn is True:
                return {'offence' :3010,
                        'successor_score': 202,
                        'foodDistance': -8,
                        'distancesToGhost' :215}
            else:
                return {'offence' :0,
                        'successor_score': 202,
                        'foodDistance': -8,
                        'distancesToGhost' :215}
        else:
            successor = self.get_successor(game_state, action) 
            weightGhost = 210
            enemies = [successor.get_agent_state(i) for i in self.get_opponents(successor)]
            invaders = [a for a in enemies if not a.is_pacman and a.get_position() != None]
            if len(invaders) > 0:
                if invaders[-1].scared_timer > 0:
                    weightGhost = 0
                    
            return {'offence' :0,
                    'successor_score': 202,
                    'foodDistance': -8,
                    'distancesToGhost' :weightGhost}

    def getOpponentPositions(self, game_state):
        return [game_state.get_agent_position(enemy) for enemy in self.get_opponents(game_state)]

    def bestPossibleAction(self ,mcsc):
        ab = mcsc.get_legal_actions(self.index)
        ab.remove(Directions.STOP)

        if len(ab) == 1:
            return ab[0]
        else:
            reverseDir = Directions.REVERSE[mcsc.get_agent_state(self.index).configuration.direction]
            if reverseDir in ab:
                ab.remove(reverseDir)
            return random.choice(ab)

    def monteCarloSimulation(self ,game_state ,depth):
        ss = game_state.deep_copy()
        while depth > 0:
            ss = ss.generate_successor(self.index ,self.bestPossibleAction(ss))
            depth -= 1
        return self.evaluate(ss ,Directions.STOP)

    def getBestAction(self,legalActions,game_state,possibleActions,distanceToTarget):
        shortestDistance = 9999999999
        for i in range (0,len(legalActions)):    
            action = legalActions[i]
            nextState = game_state.generate_successor(self.index, action)
            nextPosition = nextState.get_agent_position(self.index)
            distance = self.get_maze_distance(nextPosition, self.initialTarget[0])
            distanceToTarget.append(distance)
            if(distance<shortestDistance):
                shortestDistance = distance

        bestActionsList = [a for a, distance in zip(legalActions, distanceToTarget) if distance == shortestDistance]
        bestAction = random.choice(bestActionsList)
        return bestAction
        
    def choose_action(self, game_state):
        self.presentCoordinates = game_state.get_agent_state(self.index).get_position()
    
        if self.presentCoordinates == self.initPosition:
            self.hasStopped = 1
        if self.presentCoordinates == self.initialTarget[0]:
            self.hasStopped = 0

        # find next possible best move 
        if self.hasStopped == 1:
            legalActions = game_state.get_legal_actions(self.index)
            legalActions.remove(Directions.STOP)
            possibleActions = []
            distanceToTarget = []
            
            bestAction=self.getBestAction(legalActions,game_state,possibleActions,distanceToTarget)
            
            return bestAction

        if self.hasStopped==0:
            self.presentFoodList = self.get_food(game_state).as_list()
            self.capsuleLeft = len(self.get_capsules(game_state))
            realLastCapsuleLen = self.prevCapsuleLeft
            realLastFoodLen = len(self.lastFood)

            # Set returned = 1 when pacman has secured some food and should to return back home           
            if len(self.presentFoodList) < len(self.lastFood):
                self.shouldReturn = True
            self.lastFood = self.presentFoodList
            self.prevCapsuleLeft = self.capsuleLeft

           
            if not game_state.get_agent_state(self.index).is_pacman:
                self.shouldReturn = False

            # checks the attack situation           
            remainingFoodList = self.get_food(game_state).as_list()
            remainingFoodSize = len(remainingFoodList)
    
        
            if remainingFoodSize == self.currentFoodSize:
                self.counter = self.counter + 1
            else:
                self.currentFoodSize = remainingFoodSize
                self.counter = 0
            if game_state.get_initial_agent_position(self.index) == game_state.get_agent_state(self.index).get_position():
                self.counter = 0
            if self.counter > 20:
                self.attack = True
            else:
                self.attack = False
            
            
            actionsBase = game_state.get_legal_actions(self.index)
            actionsBase.remove(Directions.STOP)

            # distance to closest enemy        
            distanceToEnemy = 999999
            enemies = [game_state.get_agent_state(i) for i in self.get_opponents(game_state)]
            invaders = [a for a in enemies if not a.is_pacman and a.get_position() != None and a.scared_timer == 0]
            if len(invaders) > 0:
                distanceToEnemy = min([self.get_maze_distance(self.presentCoordinates, a.get_position()) for a in invaders])
            
            '''
            Capsule eating:
            -> If there is capsule available then capsulePower is True.
            -> If enemy Distance is less than 5 then capsulePower is False.
            -> If pacman scored a food then return to home capsulePower is False.
            '''
            if self.capsuleLeft < realLastCapsuleLen:
                self.capsulePower = True
                self.eatenFood = 0
            if distanceToEnemy <= 5:
                self.capsulePower = False
            if (len(self.presentFoodList) < len (self.lastFood)):
                self.capsulePower = False

        
            if self.capsulePower:
                if not game_state.get_agent_state(self.index).is_pacman:
                    self.eatenFood = 0

                modeMinDistance = 999999

                if len(self.presentFoodList) < realLastFoodLen:
                    self.eatenFood += 1

                if len(self.presentFoodList )==0 or self.eatenFood >= 5:
                    self.targetMode = self.initPosition
        
                else:
                    for food in self.presentFoodList:
                        distance = self.get_maze_distance(self.presentCoordinates ,food)
                        if distance < modeMinDistance:
                            modeMinDistance = distance
                            self.targetMode = food

                legalActions = game_state.get_legal_actions(self.index)
                legalActions.remove(Directions.STOP)
                possibleActions = []
                distanceToTarget = []
                
                k=0
                while k!=len(legalActions):
                    a = legalActions[k]
                    newpos = (game_state.generate_successor(self.index, a)).get_agent_position(self.index)
                    possibleActions.append(a)
                    distanceToTarget.append(self.get_maze_distance(newpos, self.targetMode))
                    k+=1
                
                minDis = min(distanceToTarget)
                bestActions = [a for a, dis in zip(possibleActions, distanceToTarget) if dis== minDis]
                bestAction = random.choice(bestActions)
                return bestAction
            else:
               
                self.eatenFood = 0
                distanceToTarget = []
                for a in actionsBase:
                    nextState = game_state.generate_successor(self.index, a)
                    value = 0
                    for i in range(1, 24):
                        value += self.monteCarloSimulation(nextState ,20)
                    distanceToTarget.append(value)

                best = max(distanceToTarget)
                bestActions = [a for a, v in zip(actionsBase, distanceToTarget) if v == best]
                bestAction = random.choice(bestActions)
            return bestAction

class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """

    def __init__(self, index):
        CaptureAgent.__init__(self, index)
        self.target = None
        self.previousFood = []
        self.counter = 0
        
    def register_initial_state(self, game_state):
        CaptureAgent.register_initial_state(self, game_state)
        self.setPatrolPoint(game_state)
        
    def setPatrolPoint(self ,game_state):
        '''
        Look for center of the maze for patrolling
        '''
        x = (game_state.data.layout.width - 2) // 2
        if not self.red:
            x += 1
        self.patrolPoints = []
        for i in range(1, game_state.data.layout.height - 1):
            if not game_state.has_wall(x, i):
                self.patrolPoints.append((x, i))

        for i in range(len(self.patrolPoints)):
            if len(self.patrolPoints) > 2:
                self.patrolPoints.remove(self.patrolPoints[0])
                self.patrolPoints.remove(self.patrolPoints[-1])
            else:
                break

    def getNextDefensiveMove(self,game_state):

        agentActions = []
        actions = game_state.get_legal_actions(self.index)
        
        rev_dir = Directions.REVERSE[game_state.get_agent_state(self.index).configuration.direction]
        actions.remove(Directions.STOP)

        for i in range(0, len(actions)-1):
            if rev_dir == actions[i]:
                actions.remove(rev_dir)


        for i in range(len(actions)):
            a = actions[i]
            new_state = game_state.generate_successor(self.index, a)
            if not new_state.get_agent_state(self.index).is_pacman:
                agentActions.append(a)
        
        if len(agentActions) == 0:
            self.counter = 0
        else:
            self.counter = self.counter + 1
        if self.counter > 4 or self.counter == 0:
            agentActions.append(rev_dir)

        return agentActions

    def choose_action(self, game_state):
        
        position = game_state.get_agent_position(self.index)
        if position == self.target:
            self.target = None
        invaders = []
        nearestInvader = []
        minDistance = float("inf")


        # Look for enemy position in our home        
        opponentsPositions = self.get_opponents(game_state)
        i = 0
        while i != len(opponentsPositions):
            opponentPos = opponentsPositions[i]
            opponent = game_state.get_agent_state(opponentPos)
            if opponent.is_pacman and opponent.get_position() != None:
                opponentPos = opponent.get_position()
                invaders.append(opponentPos)
            i = i + 1

        # if enemy is found chase it and kill it
        if len(invaders) > 0:
            for oppPosition in invaders:
                dist = self.get_maze_distance(oppPosition ,position)
                if dist < minDistance:
                    minDistance = dist
                    nearestInvader.append(oppPosition)
            self.target = nearestInvader[-1]

        # if enemy has eaten some food, then remove it from targets
        else:
            if len(self.previousFood) > 0:
                if len(self.get_food_you_are_defending(game_state).as_list()) < len(self.previousFood):
                    yummy = set(self.previousFood) - set(self.get_food_you_are_defending(game_state).as_list())
                    self.target = yummy.pop()

        self.previousFood = self.get_food_you_are_defending(game_state).as_list()
        
        if self.target == None:
            if len(self.get_food_you_are_defending(game_state).as_list()) <= 4:
                highPriorityFood = self.get_food_you_are_defending(game_state).as_list() + self.get_capsules_you_are_defending(game_state)
                self.target = random.choice(highPriorityFood)
            else:
                self.target = random.choice(self.patrolPoints)
        candAct = self.getNextDefensiveMove(game_state)
        awsomeMoves = []
        fvalues = []

        i=0
        
        # find the best move       
        while i < len(candAct):
            a = candAct[i]
            nextState = game_state.generate_successor(self.index, a)
            newpos = nextState.get_agent_position(self.index)
            awsomeMoves.append(a)
            fvalues.append(self.get_maze_distance(newpos, self.target))
            i = i + 1

        best = min(fvalues)
        bestActions = [a for a, v in zip(awsomeMoves, fvalues) if v == best]
        bestAction = random.choice(bestActions)
        return bestAction
