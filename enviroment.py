import random
import math
import numpy as np

class Environment(object):
    def __init__(self, server, largestRequest, timeOfSimulation):
        self.server = server
        self.largestRequest = largestRequest
        self.timeOfSimulation = timeOfSimulation
        random.seed(0)

    def generatePoisson(self, lambda_):
        return -math.log(1.0 - random.random()) / lambda_

    def generateExpo(self, lambda_):
        return -math.log(1.0 - random.random()) / lambda_

    def runOneServer(self):
        nReq = 0
        nRes = 0
        ongoingUsers = 0
        t = 0 

        ongoingRequestTime = self.generatePoisson(self.largestRequest)
        ongoingResponseTime = math.inf

        requests = {}
        responses = {}
        totalTime = []

        while t <= self.timeOfSimulation or ongoingUsers > 0:
            if (ongoingRequestTime <= ongoingResponseTime and ongoingRequestTime <= self.timeOfSimulation):
                t = ongoingRequestTime
                nReq += 1
                ongoingUsers += 1
                ongoingRequestTime = t + self.generatePoisson(self.largestRequest)
                if (ongoingUsers == 1):
                    random_var = self.generateExpo(self.server.max)
                    ongoingResponseTime = t + random_var
                requests[nReq] = t
                totalTime.append(random_var)
            elif (ongoingResponseTime < ongoingRequestTime and ongoingResponseTime <= self.timeOfSimulation):
                t = ongoingResponseTime
                ongoingUsers -= 1
                nRes += 1
                if (ongoingUsers == 0):
                    ongoingResponseTime = math.inf
                else:
                    random_var = self.generateExpo(self.server.max)
                    ongoingResponseTime = t + random_var
                responses[nRes] = t
                totalTime.append(random_var)
            elif (min(ongoingRequestTime, ongoingResponseTime) > self.timeOfSimulation and ongoingUsers > 0):
                t = ongoingResponseTime
                ongoingUsers -= 1
                nRes += 1
                if (ongoingUsers > 0):
                    random_var = self.generateExpo(self.server.max)
                    ongoingResponseTime = t + random_var   
                responses[nRes] = t
                totalTime.append(random_var)
            elif (min(ongoingRequestTime, ongoingResponseTime) > self.timeOfSimulation and ongoingUsers == 0):
                break

        self.showingResultsOfOneServer(nRes, requests, responses, totalTime)

    def showingResultsOfOneServer(self, nRes, requests, responses, totalTime):
        busyTime = sum(totalTime)/3600
        idleTime = 3600-sum(totalTime)
        nAttended = min(len(requests), len(responses))
        listOfRequests = list(requests.values())
        listOfResponses = list(responses.values())
        times = [(listOfResponses[i]-listOfRequests[i]) for i in range(nAttended)]
        meanTime = sum(times)/nAttended
        meanAttended = len(responses)/3600
        print(f"Results in server {self.server.name}")
        print(f"Attended requests: {str(nRes)}")
        print(f"Time: {str(busyTime)}")
        print(f"Idle Time: {str(idleTime)}")
        print(f"Total time of requests in queue: {str(sum(totalTime))}")
        print(f"Average time requests in queue: {str(meanTime)}")
        print(f"Average requests in queue per time: {str(meanAttended)}")
        print(f"Last request time {str(list(requests.values())[-1])}")

    def runningNServers(self):
        nReq = 0
        nRes = 0
        ongoingUsers = 0
        backendRequestsAtt = [0 for _ in range(self.server.limit_Amount)]
        backendUsersStates = [0 for _ in range(self.server.limit_Amount)]
        backendBusyTime = [0 for _ in range(self.server.limit_Amount)]
        comingResponses = [math.inf for _ in range(self.server.limit_Amount)]
        ongoingRequestTime = self.generatePoisson(self.largestRequest)
        requests, responses = {}, {}
        queueTimes, dequeueTimes = {}, {}
        t = ongoingRequestTime
        while t <= self.timeOfSimulation or ongoingUsers > 0:
            if (ongoingRequestTime <= np.amin(comingResponses)) and ongoingRequestTime <= self.timeOfSimulation:
                t = ongoingRequestTime
                nReq = nReq + 1
                ongoingRequestTime = t + self.generatePoisson(self.largestRequest)
                requests[nReq] = t
                if ongoingUsers < self.server.limit_Amount:
                    for i in range(self.server.limit_Amount):
                        if backendUsersStates[i] == 0:
                            backendUsersStates[i] = nReq
                            nextDuration = self.generateExpo(self.server.max)
                            comingResponses[i] = t + nextDuration
                            backendBusyTime[i] += nextDuration
                            break
                else:
                    queueTimes[nReq] = t
                ongoingUsers = ongoingUsers + 1
            else:
                minimumTime = math.inf
                backendIndex = 0
                for i in range(self.server.limit_Amount):
                    if comingResponses[i] < minimumTime:
                        minimumTime = comingResponses[i]
                        backendIndex = i
                t = comingResponses[backendIndex]
                nRes = nRes + 1
                temp = backendRequestsAtt[backendIndex]
                backendRequestsAtt[backendIndex] = temp + 1
                responses[nRes] = t
                ongoingUsers = ongoingUsers - 1

                if ongoingUsers >= self.server.limit_Amount:
                    m = np.amax(backendUsersStates)
                    backendUsersStates[backendIndex] = m + 1
                    nextDuration = self.generateExpo(self.server.max)
                    comingResponses[backendIndex] = t + nextDuration
                    backendBusyTime[backendIndex] += nextDuration
                    dequeueTimes[backendUsersStates[backendIndex]] = t
                else:
                    backendUsersStates[backendIndex] = 0
                    comingResponses[backendIndex] = math.inf

        self.showNServersResults(t, nReq, backendRequestsAtt, backendBusyTime, requests, responses, queueTimes, dequeueTimes)

    def showNServersResults(self, t, nReq, backendRequestsAtt, backendBusyTime, requests, responses, queueTimes, dequeueTimes):
        q_sum = 0
        for k in queueTimes:
            q_sum += (dequeueTimes[k] - queueTimes[k])
        req_time = 0
        for k in requests:
            req_time += (responses[k] - requests[k])
        print(f"Results in server {self.server.name}")
        print(f"Total time of requests in queue: {q_sum}")
        print(f"Average time requests in queue: {q_sum / len(queueTimes) if len(queueTimes) > 0 else 0}")
        print(f"Average requests in queue per time: {req_time / len(requests)}")
        print(f"Last request time {t}")

        n_servers = len(backendRequestsAtt)
        for i in range(n_servers):
            print("Server " + str(i + 1))
            print("Attended requests: " + str(backendRequestsAtt[i]))
            print("Time: " + str(backendBusyTime[i]))
            print("Idle Time: " + str(t - backendBusyTime[i]))
            print()