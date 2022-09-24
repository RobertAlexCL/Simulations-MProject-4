import random
import math
import numpy as np

class Server(object):
    def __init__(self, name, limit_Amount, max):
        self.name = name
        self.limit_Amount = limit_Amount 
        self.amount = 1 
        self.max = max 
        self.backendRequests = [[] for _ in range(self.amount)] 
        self.backendResponses = [[] for _ in range(self.amount)] 
        self.backendStates = [0 for _ in range(self.amount)] 
        self.backendBusyTime = [0 for _ in range(self.amount)] 

    def handleReq(self, reqTime, backendIndex):
        if self.backendStates[backendIndex] < self.max:
            self.backendStates[backendIndex] += 1
            self.backendRequests[backendIndex].append(reqTime)
            self.backendResponses[backendIndex].append(math.inf)
            return True
        return False 

    def getFreeServer(self):
        leastCurrentUser = math.inf
        backendIndex = -1
        for i in range(self.amount):
            if self.backendStates[i] < leastCurrentUser and self.backendStates[i] < self.max:
                leastCurrentUser = self.backendStates[i]
                backendIndex = i
        return backendIndex

    def getComingResponseTime(self):
        leastComingResponseTime = math.inf
        backendIndex = -1
        for i in range(self.amount):
            if len(self.backendResponses[i]) > 0:
                if self.backendResponses[i][-1] < leastComingResponseTime:
                    leastComingResponseTime = self.backendResponses[i][-1]
                    backendIndex = i
        return backendIndex
    
    def addServer(self):
        if self.server.amount < self.server.limit_Amount:
            self.server.amount += 1
            self.server.backendRequests.append([])
            self.server.backendResponses.append([])
            self.server.backendStates.append(0)
            self.server.backendBusyTime.append(0)
            return True
        return False 

    def rResponse(self, resTime, backendIndex):
        self.backendStates[backendIndex] -= 1
        self.backendResponses[backendIndex].append(resTime)
        self.backendBusyTime[backendIndex] += resTime - self.backendRequests[backendIndex][-1]

