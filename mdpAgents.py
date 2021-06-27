# mdpAgents.py
# parsons/20-nov-2017
#
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

#We will use couple of seperate classes, which will help us encapsulate specific functionalities and make the main part of the code more readable
#This class will make 2D array representation of the world


class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        # variables that will hold the bounds of the map
        self.length = 0
        self.height = 0

        #variable that will represent the grid
        self.grid = []

        #Boolean which is used, so we go through the piece of code that creates the grid only once
        self.isGridCreated = False

        #variables for the different types of rewards and the discount factor
        self.discountFactor = 0.8
        self.emptyCellReward = -0.5
        self.foodReward = 2
        self.capsuleReward = 3
        self.ghostReward5 = -8.5
        self.ghostReward4 = -10
        self.ghostReward3 = -11
        self.ghostReward2 = -11.5
        self.ghostReward1 = -12
        self.scaredGhostReward5 = 3
        self.scaredGhostReward4 = 5
        self.scaredGhostReward3 = 6.5
        self.scaredGhostReward2 = 8
        self.scaredGhostReward1 = 9
        self.printed = False

        #printing values so they can be easily imported and analysed in spreadhseets
        print self.discountFactor, self.emptyCellReward, self.foodReward, self.capsuleReward
        print self.ghostReward1, self.ghostReward2, self.ghostReward3, self.ghostReward4, self.ghostReward5
        print self.scaredGhostReward1, self.scaredGhostReward2, self.scaredGhostReward3, self.scaredGhostReward4, self.scaredGhostReward5

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        pass
        #print "Running registerInitialState for MDPAgent!"
        #print "I'm at:"
        #print api.whereAmI(state)
        
    # This is what gets run in between multiple games
    def final(self, state):
        pass
        #print "Looks like the game just ended!"

    #main function that will make Pacman move the way it does
    def getAction(self, state):
        self.corners = api.corners(state)

        #current coordinates of pacman
        self.pacX = api.whereAmI(state)[0]
        self.pacY = api.whereAmI(state)[1]

        #If the boolean flag for creating the grid is false, we create it
        if not self.isGridCreated :
            # loop through the corner array and set the bounds variables according to corners coordinates
            for corner in self.corners:
                self.length = corner[0]
                self.height = corner[1]

            if self.length < 8 :
                self.discountFactor = 0.8
                self.emptyCellReward = -0.1
                self.foodReward = 2
                self.ghostReward5 = -12
                self.ghostReward4 = -12
                self.ghostReward3 = -12
                self.ghostReward2 = -12
                self.ghostReward1 = -12


            # we iterate as many times as the map is long and for each iteration we add a column at that slot
            for x in range(0, self.length + 1):
                col = []
                # then we iterate once more as many times as the map is high and append an element at each iteration
                for y in range(0, self.height + 1):
                    #each cell will contain a 2-element tuple, first element will store the reward for that cell, while the second one will store the utility
                    col.append([self.emptyCellReward, 0.0])

                self.grid.append(col)
            #after the grid is created we set the flag to true, so we don't ever execute those line again
            self.isGridCreated = True



        #if the flag is already true, we just reset the grid, so we can do all the calculations

        else:
            for x in range(0, self.length + 1):
                for y in range(0, self.height + 1):
                    if self.grid[x][y][1] != "X" :
                        distances = []
                        for ghost in api.ghosts(state):
                            distances.append(abs(x - ghost[0]) + abs(y - ghost[1]))
                        if self.length < 8 :
                            if min(distances) < 3:
                                self.grid[x][y][0] = self.ghostReward3
                                if min(distances) < 2:
                                    self.grid[x][y][0] = self.ghostReward2
                            else:
                                self.grid[x][y][0] = self.emptyCellReward
                        else :
                            if min(distances) < -3:
                                self.grid[x][y][0] = self.ghostReward3
                                if min(distances) < 2:
                                    self.grid[x][y][0] = self.ghostReward2
                            else:
                                self.grid[x][y][0] = self.emptyCellReward

        #adding the wall locations to the map
        for wall in api.walls(state):
            #only the cells that, represent walls will have just "X" in them
            self.grid[wall[0]][wall[1]] = ["X", "X"]

        #adding food locations to map and setting them to
        for food in api.food(state):
            #we will calculate how far this food is from ghosts, if there is a ghost in vicinity, the cell wont be rewarding
            ghostDistances = []
            for ghost in api.ghosts(state) :
                ghostDistances.append(abs(food[0] - ghost[0]) + abs(food[1] - ghost[1]))
            if self.length < 8 :
                if min(ghostDistances) < 2:
                    self.grid[food[0]][food[1]][0] = 0
                else:
                    self.grid[food[0]][food[1]][0] = self.foodReward
            else :
                if min(ghostDistances) < -2:
                    self.grid[food[0]][food[1]][0] = 0
                else:
                    self.grid[food[0]][food[1]][0] = self.foodReward

        #adding capsules to map setting the rewards
        for capsule in api.capsules(state):
            self.grid[capsule[0]][capsule[1]][0] = self.capsuleReward

        for ghost in api.ghostStates(state):
            distance = abs(self.pacX - ghost[0][0]) + abs(self.pacY - ghost[0][1])
            if ghost[1] == 0 :
                if distance > 10:
                    self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.ghostReward5
                else:
                    if distance > 7:
                        self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.ghostReward4
                    else:
                        if distance > 5:
                            self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.ghostReward3
                        else:
                            if distance > 3:
                                self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.ghostReward2
                            else:
                                self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.ghostReward1
            else :
                if distance > 10:
                    self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.scaredGhostReward5
                else:
                    if distance > 7:
                        self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.scaredGhostReward4
                    else:
                        if distance > 5:
                            self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.scaredGhostReward3
                        else:
                            if distance > 3:
                                self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.scaredGhostReward2
                            else:
                                self.grid[int(ghost[0][0])][int(ghost[0][1])][0] = self.scaredGhostReward1


        #setting the rewards as initial values for value iterations
        for x in range(0, self.length + 1):
            for y in range(0, self.height + 1):
                self.grid[x][y][1] = self.grid[x][y][0]



        '''
         
        '''



        #adding ghosts to the map and setting their reward according to their state and distance to pacman




        #here we will set the utilities for every space
        self.valuesChanged = False
        #we iterate through the whole grid so we can set utilities
        z = 0
        while z < 30  and not self.valuesChanged :
            for x in range(0, self.length + 1):
                for y in range(0, self.height + 1):
                    # of course, we're not interested in the cells, representing walls
                    if self.grid[x][y][1] != "X":

                        # calculating the members of the max function
                        maxList = []
                        # we start calculating the utilities of the moves in order N, E, S, W
                        # we first check if the given move is possible, then which of the neighbouring moves(the ones with 0.1 probability), so we can calculate accordingly
                        if self.grid[x][y + 1][1] != "X":
                            # if both side moves(for example, side moves for N are W and E) are not walls, they have 0.1 each, if any of them is a wall, we get 0.1 for stayin at the same spot
                            if self.grid[x - 1][y][1] != "X":
                                if self.grid[x + 1][y][1] != "X":
                                    maxList.append(0.8 * self.grid[x][y + 1][1] + 0.1 * self.grid[x + 1][y][1] + 0.1 * self.grid[x - 1][y][1])
                                else:
                                    maxList.append(0.8 * self.grid[x][y + 1][1] + 0.1 * self.grid[x][y][1] + 0.1 * self.grid[x - 1][y][1])
                            else:
                                # we add exta case, if both side moves are walls, we have 0.2 for staying where he is
                                if self.grid[x + 1][y][1] == "X":
                                    maxList.append(0.8 * self.grid[x][y + 1][1] + 0.2 * self.grid[x][y][1])
                                else:
                                    maxList.append(0.8 * self.grid[x][y + 1][1] + 0.1 * self.grid[x + 1][y][1] + 0.1 * self.grid[x][y][1])

                        if self.grid[x + 1][y][1] != "X":
                            if self.grid[x][y + 1][1] != "X":
                                if self.grid[x][y - 1][1] != "X":
                                    maxList.append(0.8 * self.grid[x + 1][y][1] + 0.1 * self.grid[x][y - 1][1] + 0.1 * self.grid[x][y + 1][1])
                                else:
                                    maxList.append(0.8 * self.grid[x + 1][y][1] + 0.1 * self.grid[x][y][1] + 0.1 * self.grid[x][y + 1][1])
                            else:
                                if self.grid[x][y - 1][1] == "X":
                                    maxList.append(0.8 * self.grid[x + 1][y][1] + 0.2 * self.grid[x][y][1])
                                else:
                                    maxList.append(0.8 * self.grid[x + 1][y][1] + 0.1 * self.grid[x][y - 1][1] + 0.1 * self.grid[x][y][1])

                        if self.grid[x][y - 1][1] != "X":
                            if self.grid[x + 1][y][1] != "X":
                                if self.grid[x - 1][y][1] != "X":
                                    maxList.append(0.8 * self.grid[x][y - 1][1] + 0.1 * self.grid[x + 1][y][1] + 0.1 *self.grid[x + 1][y][1])
                                else:
                                    maxList.append(0.8 * self.grid[x][y - 1][1] + 0.1 * self.grid[x][y][1] + 0.1 * self.grid[x + 1][y][1])
                            else:
                                if self.grid[x - 1][y][1] == "X":
                                    maxList.append(0.8 * self.grid[x][y - 1][1] + 0.2 * self.grid[x][y][1])
                                else:
                                    maxList.append(0.8 * self.grid[x][y - 1][1] + 0.1 * self.grid[x - 1][y][1] + 0.1 * self.grid[x][y][1])

                        if self.grid[x - 1][y][1] != "X":
                            if self.grid[x][y - 1][1] != "X":
                                if self.grid[x][y + 1][1] != "X":
                                    maxList.append(0.8 * self.grid[x - 1][y][1] + 0.1 * self.grid[x][y - 1][1] + 0.1 * self.grid[x][y - 1][1])
                                else:
                                    maxList.append(0.8 * self.grid[x - 1][y][1] + 0.1 * self.grid[x][y][1] + 0.1 * self.grid[x][y - 1][1])
                            else:
                                if self.grid[x][y - 1][1] == "X":
                                    maxList.append(0.8 * self.grid[x - 1][y][1] + 0.2 * self.grid[x][y][1])
                                else:
                                    maxList.append(0.8 * self.grid[x - 1][y][1] + 0.1 * self.grid[x][y + 1][1] + 0.1 * self.grid[x][y][1])

                        # apply value iteration
                        currentReward = self.grid[x][y][0]
                        currentUtility = self.grid[x][y][1]
                        self.grid[x][y][1] = round(currentReward + self.discountFactor * max(maxList), 3)
                        if currentUtility == self.grid[x][y][1]:
                            self.valuesChanged = True
                            if not self.printed :
                                print z
                                self.printed = True
            '''
            


            '''
            z = z + 1



        #this bit of code will let pacman decide which move he can do
        legal = api.legalActions(state)

        #dictionaty that will hold pairs of a legal move and its expected utility
        meu = {}


        #from now on we check which of the possible moves are legal and we calculate the expected utility fro all of them
        if Directions.NORTH in legal:
            #we create list that will hold the different expected policies for the moves that we can do after we execute North, but only those terms from the whole equation which will need a max chosen from
            furtherutilities = []
            #checking if second north action is applicable and we add policy to the list accordingly, similar for the other actions that are possible after executing north
            #Because of checking indeces with up to +2 or down to -2, we need to be careful for index out of bounds, we're using try/except blocks, because if the index is put of bounds, we're absolutely alright with just ignoring the case
            try :
                if self.grid[self.pacX][self.pacY + 2][1] != "X":
                    try:
                        # we have 2 variables that will help us : left and right: they represent the moves with 0.1 probability, if they're possible, the ultitily of the next move will be set, if they arent, the utility of the current cell will be set
                        if self.grid[self.pacX - 1][self.pacY + 1][1] != "X":
                            left = self.grid[self.pacX - 1][self.pacY + 1][1]
                        else:
                            left = self.grid[self.pacX][self.pacY + 1][1]
                    except:
                        left = self.grid[self.pacX][self.pacY + 1][1]

                    try:
                        if self.grid[self.pacX + 1][self.pacY + 1][1] != "X":
                            right = self.grid[self.pacX + 1][self.pacY + 1][1]
                        else:
                            right = self.grid[self.pacX][self.pacY + 1][1]
                    except :
                        right = self.grid[self.pacX][self.pacY + 1][1]

                        # we append the sum of probabilites times utilities of further moves to the further utilities list
                        furtherutilities.append(0.8 * self.grid[self.pacX][self.pacY + 2][1] + 0.1 * left + 0.1 * right)

            except :
                pass

            #we act similarly for all other moves that may come after the one to the north
            try:
                if self.grid[self.pacX + 1][self.pacY + 1][1] != "X":
                    try :
                        if self.grid[self.pacX][self.pacY + 2][1] != "X":
                            left = self.grid[self.pacX][self.pacY + 2][1]
                        else:
                            left = self.grid[self.pacX][self.pacY + 1][1]
                    except :
                        left = self.grid[self.pacX][self.pacY + 1][1]

                    try :
                        if self.grid[self.pacX][self.pacY][1] != "X":
                            right = self.grid[self.pacX][self.pacY][1]
                        else:
                            right = self.grid[self.pacX][self.pacY + 1][1]
                    except :
                        right = self.grid[self.pacX][self.pacY + 1][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX + 1][self.pacY + 1][1] + 0.1 * left + 0.1 * right)
            except:
                pass


            try:
                if self.grid[self.pacX][self.pacY][1] != "X":
                    try :
                        if self.grid[self.pacX + 1][self.pacY + 1][1] != "X":
                            left = self.grid[self.pacX + 1][self.pacY + 1][1]
                        else:
                            left = self.grid[self.pacX][self.pacY + 1][1]
                    except :
                        left = self.grid[self.pacX][self.pacY + 1][1]

                    try :
                        if self.grid[self.pacX - 1][self.pacY + 1][1] != "X":
                            right = self.grid[self.pacX - 1][self.pacY + 1][1]
                        else:
                            right = self.grid[self.pacX][self.pacY + 1][1]
                    except :
                        right = self.grid[self.pacX][self.pacY + 1][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX][self.pacY][1] + 0.1 * left + 0.1 * right)
            except:
                pass

            try:
                if self.grid[self.pacX - 1][self.pacY + 1][1] != "X":
                    try :
                        if self.grid[self.pacX][self.pacY][1] != "X":
                            left = self.grid[self.pacX][self.pacY][1]
                        else:
                            left = self.grid[self.pacX][self.pacY + 1][1]
                    except :
                        left = self.grid[self.pacX][self.pacY + 1][1]

                    try :
                        if self.grid[self.pacX][self.pacY + 2][1] != "X":
                            right = self.grid[self.pacX][self.pacY + 2][1]
                        else:
                            right = self.grid[self.pacX][self.pacY + 1][1]
                    except :
                        right = self.grid[self.pacX][self.pacY + 1][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX - 1][self.pacY + 1][1] + 0.1 * left + 0.1 * right)
            except:
                pass

            #now we add to the dictionary the direction as a value and as a key we calculate the expected utility for this move
            key = round(self.grid[self.pacX][self.pacY + 1][0] + self.discountFactor*max(furtherutilities), 3)
            meu[key] = Directions.NORTH

        if Directions.WEST in legal:
            furtherutilities = []

            try:
                if self.grid[self.pacX - 1][self.pacY + 1][1] != "X":
                   try :
                       if self.grid[self.pacX - 2][self.pacY][1] != "X":
                           left = self.grid[self.pacX - 2][self.pacY][1]
                       else:
                           left = self.grid[self.pacX - 1][self.pacY][1]
                   except:
                       left = self.grid[self.pacX - 1][self.pacY][1]

                   try :
                       if self.grid[self.pacX][self.pacY][1] != "X":
                           right = self.grid[self.pacX][self.pacY][1]
                       else:
                           right = self.grid[self.pacX][self.pacY][1]
                   except :
                       right = self.grid[self.pacX][self.pacY][1]
                   furtherutilities.append(0.8 * self.grid[self.pacX - 1][self.pacY + 1][1] + 0.1 * left + 0.1 * right)
            except:
                pass

            try:
                if self.grid[self.pacX][self.pacY][1] != "X":
                    try :
                        if self.grid[self.pacX - 1][self.pacY + 1][1] != "X":
                            left = self.grid[self.pacX - 1][self.pacY + 1][1]
                        else:
                            left = self.grid[self.pacX - 1][self.pacY][1]
                    except :
                        left = self.grid[self.pacX - 1][self.pacY][1]

                    try :
                        if self.grid[self.pacX - 1][self.pacY - 1][1] != "X":
                            right = self.grid[self.pacX - 1][self.pacY - 1][1]
                        else:
                            right = self.grid[self.pacX - 1][self.pacY][1]
                    except :
                        right = self.grid[self.pacX - 1][self.pacY][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX][self.pacY][1] + 0.1 * left + 0.1 * right)
            except:
                pass


            try:
                if self.grid[self.pacX - 1][self.pacY - 1][1] != "X":
                    try :
                        if self.grid[self.pacX][self.pacY][1] != "X":
                            left = self.grid[self.pacX][self.pacY][1]
                        else:
                            left = self.grid[self.pacX - 1][self.pacY][1]
                    except :
                        left = self.grid[self.pacX - 1][self.pacY][1]

                    try :
                        if self.grid[self.pacX - 2][self.pacY][1] != "X":
                            right = self.grid[self.pacX - 2][self.pacY][1]
                        else:
                            right = self.grid[self.pacX - 1][self.pacY][1]
                    except :
                        right = self.grid[self.pacX - 1][self.pacY][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX - 1][self.pacY - 1][1] + 0.1 * left + 0.1 * right)
            except:
                pass

            try:
                if self.grid[self.pacX - 2][self.pacY][1] != "X":
                    try :
                        if self.grid[self.pacX - 1][self.pacY - 1][1] != "X":
                            left = self.grid[self.pacX - 1][self.pacY - 1][1]
                        else:
                            left = self.grid[self.pacX - 1][self.pacY][1]
                    except :
                        left = self.grid[self.pacX - 1][self.pacY][1]

                    try :
                        if self.grid[self.pacX - 1][self.pacY + 1][1] != "X":
                            right = self.grid[self.pacX - 1][self.pacY + 1][1]
                        else:
                            right = self.grid[self.pacX - 1][self.pacY][1]
                    except :
                        right = self.grid[self.pacX - 1][self.pacY][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX - 2][self.pacY][1] + 0.1 * left + 0.1 * right)
            except :
                pass

            key = round(self.grid[self.pacX - 1][self.pacY][0] + self.discountFactor*max(furtherutilities), 3)
            meu[key] = Directions.WEST


        if Directions.SOUTH in legal:
            furtherutilities = []

            try :
                if self.grid[self.pacX][self.pacY][1] != "X":
                    try :
                        if self.grid[self.pacX - 1][self.pacY - 1][1] != "X":
                            left = self.grid[self.pacX - 1][self.pacY - 1][1]
                        else:
                            left = self.grid[self.pacX][self.pacY - 1][1]
                    except :
                        left = self.grid[self.pacX][self.pacY - 1][1]

                    try :
                        if self.grid[self.pacX + 1][self.pacY - 1][1] != "X":
                            right = self.grid[self.pacX + 1][self.pacY - 1][1]
                        else:
                            right = self.grid[self.pacX][self.pacY - 1][1]
                    except :
                        right = self.grid[self.pacX][self.pacY - 1][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX][self.pacY][1] + 0.1 * left + 0.1 * right)
            except :
                pass

            try :
                if self.grid[self.pacX + 1][self.pacY - 1][1] != "X":
                    try :
                        if self.grid[self.pacX][self.pacY][1] != "X":
                            left = self.grid[self.pacX][self.pacY][1]
                        else:
                            left = self.grid[self.pacX][self.pacY - 1][1]
                    except :
                        left = self.grid[self.pacX][self.pacY - 1][1]

                    try :
                        if self.grid[self.pacX][self.pacY - 2][1] != "X":
                            right = self.grid[self.pacX][self.pacY - 2][1]
                        else:
                            right = self.grid[self.pacX][self.pacY - 1][1]
                    except :
                        right = self.grid[self.pacX][self.pacY - 1][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX + 1][self.pacY - 1][1] + 0.1 * left + 0.1 * right)
            except :
                pass


            try :
                if self.grid[self.pacX][self.pacY - 2][1] != "X":
                    try :
                        if self.grid[self.pacX + 1][self.pacY - 1][1] != "X":
                            left = self.grid[self.pacX + 1][self.pacY - 1][1]
                        else:
                            left = self.grid[self.pacX][self.pacY - 1][1]
                    except :
                        left = self.grid[self.pacX][self.pacY - 1][1]

                    try :
                        if self.grid[self.pacX - 1][self.pacY - 1][1] != "X":
                            right = self.grid[self.pacX - 1][self.pacY - 1][1]
                        else:
                            right = self.grid[self.pacX][self.pacY - 1][1]
                    except :
                        right = self.grid[self.pacX][self.pacY - 1][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX][self.pacY - 2][1] + 0.1 * left + 0.1 * right)
            except :
                pass

            try :
                if self.grid[self.pacX - 1][self.pacY - 1][1] != "X":
                    try :
                        if self.grid[self.pacX][self.pacY - 2][1] != "X":
                            left = self.grid[self.pacX][self.pacY - 2][1]
                        else:
                            left = self.grid[self.pacX][self.pacY - 1][1]
                    except :
                        left = self.grid[self.pacX][self.pacY - 1][1]

                    try :
                        if self.grid[self.pacX][self.pacY][1] != "X":
                            right = self.grid[self.pacX][self.pacY][1]
                        else:
                            right = self.grid[self.pacX][self.pacY - 1][1]
                    except :
                        right = self.grid[self.pacX][self.pacY - 1][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX - 1][self.pacY - 1][1] + 0.1 * left + 0.1 * right)
            except :
                pass

            key = round(self.grid[self.pacX][self.pacY - 1][0] + self.discountFactor*max(furtherutilities), 3)
            meu[key] = Directions.SOUTH

        if Directions.EAST in legal:
            furtherutilities = []

            try :
                if self.grid[self.pacX + 1][self.pacY + 1][1] != "X":
                    try :
                        if self.grid[self.pacX][self.pacY][1] != "X":
                            left = self.grid[self.pacX][self.pacY][1]
                        else:
                            left = self.grid[self.pacX + 1][self.pacY][1]
                    except :
                        left = self.grid[self.pacX + 1][self.pacY][1]

                    try :
                        if self.grid[self.pacX + 2][self.pacY][1] != "X":
                            right = self.grid[self.pacX + 2][self.pacY][1]
                        else:
                            right = self.grid[self.pacX + 1][self.pacY][1]
                    except :
                        right = self.grid[self.pacX + 1][self.pacY][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX + 1][self.pacY + 1][1] + 0.1 * left + 0.1 * right)
            except :
                pass

            try :
                if self.grid[self.pacX + 2][self.pacY][1] != "X":
                    try :
                        if self.grid[self.pacX + 1][self.pacY + 1][1] != "X":
                            left = self.grid[self.pacX + 1][self.pacY + 1][1]
                        else:
                            left = self.grid[self.pacX + 1][self.pacY][1]
                    except :
                        left = self.grid[self.pacX + 1][self.pacY][1]

                    try :
                        if self.grid[self.pacX + 1][self.pacY - 1][1] != "X":
                            right = self.grid[self.pacX + 1][self.pacY - 1][1]
                        else:
                            right = self.grid[self.pacX + 1][self.pacY][1]
                    except :
                        right = self.grid[self.pacX + 1][self.pacY][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX + 2][self.pacY][1] + 0.1 * left + 0.1 * right)
            except :
                pass


            try :
                if self.grid[self.pacX + 1][self.pacY - 1][1] != "X":
                    try :
                        if self.grid[self.pacX+ 2][self.pacY][1] != "X":
                            left = self.grid[self.pacX + 2][self.pacY][1]
                        else:
                            left = self.grid[self.pacX + 1][self.pacY][1]
                    except :
                        left = self.grid[self.pacX + 1][self.pacY][1]

                    try :
                        if self.grid[self.pacX][self.pacY][1] != "X":
                            right = self.grid[self.pacX][self.pacY][1]
                        else:
                            right = self.grid[self.pacX + 1][self.pacY][1]
                    except :
                        right = self.grid[self.pacX + 1][self.pacY][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX + 1][self.pacY - 1][1] + 0.1 * left + 0.1 * right)
            except :
                pass

            try :
                if self.grid[self.pacX][self.pacY][1] != "X":
                    try :
                        if self.grid[self.pacX + 1][self.pacY - 1][1] != "X":
                            left = self.grid[self.pacX + 1][self.pacY - 1][1]
                        else:
                            left = self.grid[self.pacX + 1][self.pacY][1]
                    except :
                        left = self.grid[self.pacX + 1][self.pacY][1]

                    try :
                        if self.grid[self.pacX + 1][self.pacY + 1][1] != "X":
                            right = self.grid[self.pacX + 1][self.pacY + 1][1]
                        else:
                            right = self.grid[self.pacX + 1][self.pacY][1]
                    except :
                        right = self.grid[self.pacX + 1][self.pacY][1]

                    furtherutilities.append(0.8 * self.grid[self.pacX][self.pacY][1] + 0.1 * left + 0.1 * right)
            except :
                pass

            key = round(self.grid[self.pacX + 1][self.pacY][0] + self.discountFactor*max(furtherutilities), 3)
            meu[key] = Directions.EAST


        #deciding the direction of next move
        bestUtility = max(meu.keys())
        nextMove = meu[bestUtility]




        #couple print statements, used for debugging and analysing performance
        '''
        print "Pacman :", api.whereAmI(state)
        print "Ghosts :", api.ghosts(state)
        print nextMove
        for y in range(0, self.height + 1):
            for x in range(0, self.length + 1):
                if self.grid[x][self.height - y][1] == "X":
                    print "{.. ", self.grid[x][self.height - y][1], "..}",
                else:
                    print "{", self.grid[x][self.height - y][1], "}",

            print
        print
        '''

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(nextMove, legal)
