import random
import numpy as np
import pandas as pd




# 存活车辆类
class VehicleList(object):
    def __init__(self, dt, line):
        self.velList = [Vehicle() for _ in range(0)]  # 存活车辆的列表
        self.dt = dt  # 仿真步进时间
        self.line = line
        self.laneNumList = self.line.dfEdge['laneNum'].tolist()
        self.laneNumPositionList = self.line.dfNode['position'].tolist()

        # 获取和转换路段限速
        self.laneSpeedLimitList = self.line.dfEdge['speedLimit'].tolist()
        for i in range(len(self.laneSpeedLimitList)):
            self.laneSpeedLimitList[i] = eval(self.laneSpeedLimitList[i])

        self.laneNum = max(self.laneNumList)
        self.indices_list = [None] * self.laneNum  # 相同车道的车辆序号列表
        # 换道相关的距离参数
        self.changeLaneLength = 400
        self.stopPointLength = 400
        # 安全相关参数
        self.timeSafe = 1
        self.sSafe = 4

    # 更新列车速度
    def updateState(self):
        # 按照位置进行排序
        self.sort_x()
        # 获取各车道车辆的序号
        self.set_idSameLane()
        # 更新各车辆的限速
        self.updateVmax()
        # 进行车辆位置的更新
        for i in range(self.laneNum):
            # 对每个车道的第一辆车进行数据更新
            if len(self.indices_list[i]) != 0:
                self.updateV(self.indices_list[i][0], None, self.dt)
            # 对每个车道的后续车辆进行数据更新
            for j in range(1, len(self.indices_list[i])):
                self.updateV(self.indices_list[i][j], self.indices_list[i][j - 1], self.dt)

        # 进行车辆车道的更新
        for i in range(len(self.velList)):
            # self.updateLaneTarget(i)
            # self.updateLaneStop(i)
            # self.updateLaneLowSpeed(i)
            self.updateLane(i)

        # 删除过界车辆
        self.delete_vehicle()

    # 按照位置对车辆进行排序
    def sort_x(self):
        # 进行车辆位置排序
        def compare_x(Vehicle):
            return Vehicle.x

        self.velList = sorted(self.velList, key=compare_x, reverse=True)

    # 按照位置计算车辆所在的edge序号
    def get_idEdgeBasedPosition(self, position):
        for i in range(len(self.laneNumPositionList)-1):
            if position >= self.laneNumPositionList[i] and position < self.laneNumPositionList[i+1]:
                break
        return i


    # 获取各车道对应的velList的序号
    def set_idSameLane(self):
        for target_lanNum in range(self.laneNum):
            self.indices_list[target_lanNum] = [i for i, obj in enumerate(self.velList) if
                                                obj.laneNum == target_lanNum + 1]

    # 设定车辆限速
    def updateVmax(self):
        for i in range(len(self.velList)):
            # print(self.velList[i].x)
            # print(self.get_idEdgeBasedPosition(self.velList[i].x))
            # print(self.velList[i].laneNum-1)
            v_max_lane = self.laneSpeedLimitList[self.get_idEdgeBasedPosition(self.velList[i].x)][self.velList[i].laneNum-1]

            # 还需要增加管控措施实施的动态限速
            v_max_VSL = 33
            # print('len(self.line.VSL)', len(self.line.VSL))
            if len(self.line.VSL):
                if self.velList[i].x >= self.line.VSL[0]:
                    v_max_VSL = self.line.VSL[1]
            # print(self.velList[i].x, self.line.VSL[0], v_max_VSL, self.line.VSL[1])

            self.velList[i].v_max = min(self.velList[i].v_max_vehicle, v_max_lane, v_max_VSL)


    # 删除车辆
    def delete_vehicle(self):
        for i in range(len(self.velList)):
            if self.velList[i].x > self.velList[i].targetEndPosition:
                del self.velList[i]
                print('delet vehicle: ', i, ' in position: ', self.velList[i].x)
                break

    # 更新两车间速度，跟驰模型实现
    def updateV(self, idVehicle, idVehicleFront, dt):
        # 更新加速度
        if self.velList[idVehicle].v + self.velList[idVehicle].a * dt < 0:
            self.velList[idVehicle].x -= 1 / 2 * self.velList[idVehicle].v * self.velList[idVehicle].v / self.velList[
                idVehicle].a
            self.velList[idVehicle].v = 0
        else:
            self.velList[idVehicle].v += self.velList[idVehicle].a * dt
            self.velList[idVehicle].x += self.velList[idVehicle].v * dt + self.velList[idVehicle].a * dt * dt / 2
        # 更新加速度
        alpha = 0
        if idVehicleFront:
            deltaX = self.velList[idVehicleFront].x - self.velList[idVehicle].x - self.velList[idVehicleFront].l
            deltaV = self.velList[idVehicle].v - self.velList[idVehicleFront].v
            alpha = (self.sSafe + max(0,
                                      self.timeSafe * self.velList[idVehicle].v + deltaV * self.velList[idVehicle].v /
                                      self.velList[idVehicle].sqrt_ab)) / deltaX
        self.velList[idVehicle].a = self.velList[idVehicle].a_max * (
                1 - (self.velList[idVehicle].v / self.velList[idVehicle].v_max) ** 4 - alpha ** 2)

        if self.ide_stopWithLaneBan(idVehicle):
            # self.ide_stopWithLaneBan(idVehicle)
            self.velList[idVehicle].a = -self.velList[idVehicle].b_max

        if self.velList[idVehicle].stopped:
            self.velList[idVehicle].a = -self.velList[idVehicle].b_max * self.velList[idVehicle].v / self.velList[
                idVehicle].v_max

    # 获得目标车道的前车序号
    def get_idTargetLaneFront(self, targetLaneNum, vehicleId):
        for i in range(vehicleId - 1, -1, -1):
            if self.velList[i].laneNum == targetLaneNum:
                return i
        return -1

    # 获取目标车道的后车序号
    def get_idTargetLaneLater(self, targetLaneNum, vehicleId):
        for i in range(vehicleId + 1, len(self.velList)):
            if self.velList[i].laneNum == targetLaneNum:
                return i
        return -1

    # 计算两车之间的距离
    def cal_vehicleDistance(self, idFront, idLater):
        if idFront == -1 or idLater == -1:
            return 1000
        else:
            distance = self.velList[idFront].x - self.velList[idLater].x - self.velList[idFront].l
            return distance

    # 计算两车之间的安全距离
    def cal_vehicleDistanceSafe(self, idFront, idLater):
        if idFront == -1 or idLater == -1:
            return 0
        else:
            distance = (self.velList[idLater].v - self.velList[idFront].v) * self.timeSafe
            return distance

    # 计算前车的速度
    def cal_speedFront(self, idFront):
        if idFront == -1:  # 前车不为有效序号，返回一个大值
            return 200
        else:
            return self.velList[idFront].v

    # 根据车辆位置计算当前所在edge的车道数量
    def cal_laneNum(self, x):
        for i in range(len(self.laneNumPositionList)):
            if x < self.laneNumPositionList[i]:
                break
        return self.laneNumList[i - 1]

    # 根据车辆位置计算当前所在edge的是否包括匝道加速带
    def ide_laneRampFlag(self, x):
        for i in range(len(self.laneNumPositionList)):
            if x < self.laneNumPositionList[i]:
                break
        if self.line.dfEdge['type'][i - 1] == 'normal':
            return 0
        else:
            return 1

    # 计算Node所对应的位置
    def get_nodePosition(self, nodeID):
        rowIndex = self.line.dfNode[self.line.dfNode.values == nodeID].index.tolist()[0]
        return self.line.dfNode['position'][rowIndex]

    # 获取目标车道
    def get_targetLaneWithoutBan(self, i):
        # 选取没有障碍物的车道
        laneNumNow = self.velList[i].laneNum
        targetLane = laneNumNow
        feasibleLaneList = self.get_laneWithoutBan(i)
        if len(feasibleLaneList) == 0:
            print('不存在可行的车道')
        else:
            # 这个需要后期好好判断一下
            # targetLane = random.choice(feasibleLaneList)
            closestLane = min(feasibleLaneList, key=lambda x: abs(x - laneNumNow))

            if closestLane > laneNumNow:
                targetLane = laneNumNow + 1
            elif closestLane == laneNumNow:
                targetLane = laneNumNow
            else:
                targetLane = laneNumNow - 1

        # print('closestLane, laneNumNow, targetLane:', closestLane, laneNumNow, targetLane)
        return targetLane

    # 获取前方没有障碍物的车道
    def get_laneWithoutBan(self, i):
        laneNumNow = self.cal_laneNum(self.velList[i].x)
        laneRampFlagNow = self.ide_laneRampFlag(self.velList[i].x)
        feasibleLaneList = []
        for iLane in range(laneNumNow):
            flag = 1
            for j in range(self.line.laneBan.shape[0]):
                if 0 < self.line.laneBan['positionBeg'][j] - self.velList[i].x < self.stopPointLength and iLane + 1 == \
                        self.line.laneBan['laneNum'][j]:
                    flag = 0
                    break
            if flag:
                feasibleLaneList.append(iLane + 1)
        return feasibleLaneList

    # 判断车辆前方是否有障碍物
    def ide_laneBanFlag(self, i):
        flag = False
        for j in range(self.line.laneBan.shape[0]):
            if 0 < self.line.laneBan['positionBeg'][j] - self.velList[i].x < self.stopPointLength and self.velList[
                i].laneNum == self.line.laneBan['laneNum'][j]:
                flag = True
                break
        return flag, j

    # 判断车辆前方是否存在造成停车的障碍物
    def ide_stopWithLaneBan(self, i):
        flag = False
        brakingDistance = 120
        for j in range(self.line.laneBan.shape[0]):
            if 0 < self.line.laneBan['positionBeg'][j] - self.velList[i].x < brakingDistance and self.velList[
                i].laneNum == self.line.laneBan['laneNum'][j]:
                flag = True
                break
        return flag


    # 判断目标车道是否在封闭区域内
    def ide_inLaneBan(self, i, target_lane):
        flag = False
        for j in range(self.line.laneBan.shape[0]):
            if self.line.laneBan['positionBeg'][j] < self.velList[i].x < self.line.laneBan['positionEnd'][
                j] and target_lane == self.line.laneBan['laneNum'][j]:
                flag = True
                break
        return flag

    # 判断车辆换道是否存在空间，首先需要前后车换道空间存在，其次目标车道为非障碍车道
    def ide_changeLaneFlag(self, i, target_lane):
        flag = 0
        # 计算目标车道前后车序号
        idTargetLaneFront = self.get_idTargetLaneFront(target_lane, i)
        idTargetLaneLater = self.get_idTargetLaneLater(target_lane, i)
        # 计算与前后车的实际距离
        distanceTargetLaneFront = self.cal_vehicleDistance(idTargetLaneFront, i)
        distanceTargetLaneLater = self.cal_vehicleDistance(i, idTargetLaneLater)
        # 计算与前后车的安全距离
        distanceTargetLaneFrontSafe = self.cal_vehicleDistanceSafe(idTargetLaneFront, i)
        distanceTargetLaneLaterSafe = self.cal_vehicleDistanceSafe(i, idTargetLaneLater)
        # 为了换道后可以增加速度需要满足的条件
        flagFront = distanceTargetLaneFront > max(distanceTargetLaneFrontSafe, self.velList[i].l * 2)
        flaglater = distanceTargetLaneLater > max(distanceTargetLaneLaterSafe, self.velList[i].l / 2)
        # 不在封闭区域内
        flagInLaneBan = self.ide_inLaneBan(i, target_lane)
        # 整体判断
        if flagFront and flaglater and (not flagInLaneBan):
            flag = 1
        return flag

    # 车道更新函数
    def updateLane(self, i):
        target_lane = self.velList[i].laneNum
        # 计算目标车道可行性标识
        flagTargetLane = 0 < self.velList[i].targetLaneNum != self.velList[i].laneNum and self.velList[
            i].targetEndPosition - self.velList[i].x < self.changeLaneLength
        # 计算禁止驶入的车道
        # flagBanLane, idLaneBan = self.ide_laneBanFlag(i)
        flagBanLane = False
        id_front = self.get_idTargetLaneFront(self.velList[i].laneNum, i)
        # 计算是否低速行驶的标识
        flagLowSpeed = self.cal_speedFront(id_front) < self.velList[i].v_max - 5 and 0 < self.velList[id_front].x - \
                       self.velList[i].x < self.velList[i].l * 10
        # 计算可行的车道
        feasibleLaneList = self.get_laneWithoutBan(i)
        flagChangeForBan = 0
        # 进行车道更新
        if flagBanLane == True and flagTargetLane == True:
            # 目标车道引发的换道
            target_lane = self.velList[i].laneNum + 1
        elif flagBanLane == True and flagTargetLane == False:
            # 且没有障碍物的车道
            target_lane = self.get_targetLaneWithoutBan(i)
            flagChangeForBan = 1
        elif flagBanLane == False and flagTargetLane == True:
            target_lane = self.velList[i].laneNum + 1
        else:
            if flagLowSpeed:
                # 低速引发的换道
                target_lane = self.velList[i].laneNum + random.choice([-1, 1])

        # 车道范围进行修正
        laneNumNow = self.cal_laneNum(self.velList[i].x)
        if target_lane < 1:
            target_lane = 1
        elif target_lane > laneNumNow:
            target_lane = laneNumNow

        # 最终判断换道的可行性
        if self.velList[i].laneNum != target_lane and (target_lane in feasibleLaneList or flagChangeForBan):
            if self.ide_changeLaneFlag(i, target_lane) > 0:
                self.velList[i].laneNum = target_lane

    # 低速造成的换道
    def updateLaneLowSpeed(self, i):
        laneNumNow = self.cal_laneNum(self.velList[i].x)
        laneRampFlagNow = self.ide_laneRampFlag(self.velList[i].x)
        # 首先需要判断前车是不是很慢
        id_front = self.get_idTargetLaneFront(self.velList[i].laneNum, i)
        if (self.cal_speedFront(id_front) < self.velList[i].v_max - 5) and (
                0 < self.velList[id_front].x - self.velList[i].x < self.velList[i].l * 10):
            probability = 0.8
            random_number = random.random()
            # 低速行驶造成的换道
            if random_number < probability:
                # 计算目标车道
                target_lane = self.velList[i].laneNum + random.choice([-1, 1])
                if target_lane < 1:
                    target_lane = 1
                elif target_lane > laneNumNow:
                    target_lane = laneNumNow
                if self.velList[i].laneNum != target_lane:
                    # 计算目标车道前后车序号
                    idTargetLaneFront = self.get_idTargetLaneFront(target_lane, i)
                    idTargetLaneLater = self.get_idTargetLaneLater(target_lane, i)
                    # 计算与前后车的实际距离
                    distanceTargetLaneFront = self.cal_vehicleDistance(idTargetLaneFront, i)
                    distanceTargetLaneLater = self.cal_vehicleDistance(i, idTargetLaneLater)
                    # 计算与前后车的安全距离
                    distanceTargetLaneFrontSafe = self.cal_vehicleDistanceSafe(idTargetLaneFront, i)
                    distanceTargetLaneLaterSafe = self.cal_vehicleDistanceSafe(i, idTargetLaneLater)
                    # 为了换道后可以增加速度需要满足的条件
                    flagFront = distanceTargetLaneFront > max(distanceTargetLaneFrontSafe, self.velList[i].l * 2)
                    flaglater = distanceTargetLaneLater > max(distanceTargetLaneLaterSafe, self.velList[i].l / 2)
                    flagSpeed = self.cal_speedFront(idTargetLaneFront) > self.velList[i].v + 5
                    # 为了避免换道换到应急车道
                    flagRamp = not (laneRampFlagNow and (target_lane == laneNumNow))
                    # 进行换道
                    if flagFront * flaglater * flagSpeed * flagRamp > 0:
                        self.velList[i].laneNum = target_lane

    # 目标匝道引起的换道
    def updateLaneTarget(self, i):
        if self.velList[i].targetLaneNum > 0 and self.velList[i].targetEndPosition - self.velList[
            i].x < self.changeLaneLength and self.velList[i].laneNum != self.velList[i].targetLaneNum:
            target_lane = self.velList[i].laneNum + 1
            changeProbability = 1 - (self.velList[i].targetEndPosition - self.velList[i].x) / self.changeLaneLength
            random_number = random.random()
            if target_lane <= self.cal_laneNum(self.velList[i].x) and changeProbability > random_number:
                idTargetLaneFront = self.get_idTargetLaneFront(target_lane, i)
                idTargetLaneLater = self.get_idTargetLaneLater(target_lane, i)
                # 计算与前后车的实际距离
                distanceTargetLaneFront = self.cal_vehicleDistance(idTargetLaneFront, i)
                distanceTargetLaneLater = self.cal_vehicleDistance(i, idTargetLaneLater)
                # 计算与前后车的安全距离
                distanceTargetLaneFrontSafe = self.cal_vehicleDistanceSafe(idTargetLaneFront, i)
                distanceTargetLaneLaterSafe = self.cal_vehicleDistanceSafe(i, idTargetLaneLater)
                # 为了换道后可以增加速度需要满足的条件
                flagFront = distanceTargetLaneFront > max(distanceTargetLaneFrontSafe, self.velList[i].l / 2)
                flaglater = distanceTargetLaneLater > max(distanceTargetLaneLaterSafe, self.velList[i].l / 2)
                # 进行换道
                if flagFront * flaglater > 0:
                    self.velList[i].laneNum = target_lane

    # 前方障碍点引起的换道，目前考虑的是入口匝道
    def updateLaneStop(self, i):
        # 场景1前方为入口匝道终点
        for j in range(self.line.laneBan.shape[0]):
            if 0 < self.line.laneBan['positionBeg'][j] - self.velList[i].x < self.stopPointLength and self.velList[
                i].laneNum == self.line.laneBan['laneNum'][j]:
                changeProbability = 1 - (self.line.laneBan['positionBeg'][j] - self.velList[i].x) / self.stopPointLength
                random_number = random.random()
                if changeProbability > random_number:
                    laneNumNow = self.cal_laneNum(self.velList[i].x)
                    target_lane = self.velList[i].laneNum + random.choice([-1, 1])
                    if target_lane < 1:
                        target_lane = 1
                    elif target_lane > laneNumNow:
                        target_lane = laneNumNow
                    if self.velList[i].laneNum != target_lane:
                        idTargetLaneFront = self.get_idTargetLaneFront(target_lane, i)
                        idTargetLaneLater = self.get_idTargetLaneLater(target_lane, i)
                        # 计算与前后车的实际距离
                        distanceTargetLaneFront = self.cal_vehicleDistance(idTargetLaneFront, i)
                        distanceTargetLaneLater = self.cal_vehicleDistance(i, idTargetLaneLater)
                        # 计算与前后车的安全距离
                        distanceTargetLaneFrontSafe = self.cal_vehicleDistanceSafe(idTargetLaneFront, i)
                        distanceTargetLaneLaterSafe = self.cal_vehicleDistanceSafe(i, idTargetLaneLater)
                        # 为了换道后可以增加速度需要满足的条件
                        flagFront = distanceTargetLaneFront > max(distanceTargetLaneFrontSafe, self.velList[i].l / 2)
                        flaglater = distanceTargetLaneLater > max(distanceTargetLaneLaterSafe, self.velList[i].l / 2)
                        # 进行换道
                        if flagFront * flaglater > 0:
                            self.velList


# 车辆类
class Vehicle:

    numVehicle = 0

    vehileTyepDataDict = {'Car': 33, 'SUV': 30, 'Truck': 25}

    def __init__(self, begainNode, beginLaneNum, beginSpeed, targetNode, targetLaneNum, vehicleType):
        
        Vehicle.numVehicle += 1

        self.id = Vehicle.numVehicle
        # 重要动态信息
        self.x = 0
        self.v = beginSpeed
        self.a = 0
        self.stopped = False
        # 起点信息
        self.begainNode = begainNode
        self.laneNum = beginLaneNum
        # 终点信息
        self.targetNode = targetNode
        self.targetLaneNum = targetLaneNum
        # self.targetEndPosition = 100000

        #
        #
        # 和车辆类型相关的参数，应该进行索引赋值，20240730
        #
        #

        # 车型相关静态参数
        self.l = 4  # 根据车辆特殊化
        # self.v_max = 33  # 根据车辆特殊化
        self.vehicleType = vehicleType

        print('add vehcile, path is ', begainNode, beginLaneNum, beginSpeed, targetNode, targetLaneNum, vehicleType)

        self.v_max_vehicle = Vehicle.vehileTyepDataDict[self.vehicleType]
        self.v_max = self.v_max_vehicle
        self.a_max = 1.44  # 根据车辆特殊化
        self.b_max = 4.61  # 根据车辆特殊化
        self.sqrt_ab = 2 * np.sqrt(self.a_max * self.b_max)  # 根据车辆特殊化
        