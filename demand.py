# 流量生成函数类
# 后期将会有不同类型的流量生成类
import random

class Demand(object):

    def __init__(self, direction):
        self.direction = direction

    def addVehicle(self):

        if self.direction == '1':
            # 正常情况下使用的比例
            # nodeEntryDict = [['node001', 'node005', 'node015'], [0.8, 0.1, 0.1]]
            # 匝道管控情况下使用的比例
            nodeEntryDict = [['node001', 'node005', 'node015'], [0.6, 0.3, 0.1]]

            randomLaneDict = {'node001': [1, 2, 3], 'node005': [4], 'node015': [4]}
            randomSpeedDict = {'node001': [22, 30], 'node005': [8, 11], 'node015': [8, 11]}
            targetNodeDict = {'node001': [['node004', 'node014', 'node018'], [0.1, 0.1, 0.8]],
                              'node005': [['node014', 'node018'], [0.1, 0.9]],
                              'node015': [['node018'], [1]]}
            targetLaneDict = {'node004': 4, 'node014': 4, 'node018': 0}
        elif self.direction == '0':
            nodeEntryDict = [['node001', 'node005', 'node015'], [0.8, 0.1, 0.1]]
            randomLaneDict = {'node001': [1, 2, 3], 'node005': [4], 'node015': [4]}
            randomSpeedDict = {'node001': [22, 30], 'node005': [8, 11], 'node015': [8, 11]}
            targetNodeDict = {'node001': [['node004', 'node014', 'node018'], [0.1, 0.1, 0.8]],
                              'node005': [['node014', 'node018'], [0.1, 0.9]],
                              'node015': [['node018'], [1]]}
            targetLaneDict = {'node004': 4, 'node014': 4, 'node018': 0}
        else:
            print('direction is wrong')
        # 随机初始化
        beginNode = random.choices(nodeEntryDict[0], nodeEntryDict[1])[0]
        beginLaneNum = random.choice(randomLaneDict[beginNode])
        beginSpeed = random.randint(randomSpeedDict[beginNode][0], randomSpeedDict[beginNode][1])
        targetNode = random.choices(targetNodeDict[beginNode][0], targetNodeDict[beginNode][1])[0]
        targetLaneNum = targetLaneDict[targetNode]

        vehicleTypeList = ['Car', 'SUV', 'Truck']
        vehileType = random.choice(vehicleTypeList)

        # print('add vehcile, path is ', beginNode, beginLaneNum, beginSpeed, targetNode, targetLaneNum)
        # # 插入车辆
        # self.vels.velList.append(Vehicle(beginNode, beginLaneNum, beginSpeed, targetNode, targetLaneNum))  # 输入车辆的函数
        # self.vels.velList[-1].targetEndPosition = self.vels.get_nodePosition(targetNode)
        # self.vels.velList[-1].x = self.vels.get_nodePosition(beginNode)
        return beginNode, beginLaneNum, beginSpeed, targetNode, targetLaneNum, vehileType
