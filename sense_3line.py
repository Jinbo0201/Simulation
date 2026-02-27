# 三车道场景

import os
import datetime
import pandas as pd

from src.demand import *
from src.line import *
from src.vehicle import VehicleList, Vehicle



class SimControl(object):

    def __init__(self, simulationTime, simulationDirection):

        # self.currentPath = os.getcwd()

        self.simDuration = simulationTime
        self.simDirection = simulationDirection

        # 仿真步进时长
        self.dt = 0.1

        self.load_file()
        self.demand = Demand(self.simDirection)
        self.vels = VehicleList(self.dt, self.line)

        # 仿真进程计数
        self.stepCounter = 0

        self.traList = []

        # 匝道管控信号
        self.rampMeterFlag = 0
        self.waitList = []

    # 打开路网文件
    def load_file(self):
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # look for excel files inside a `docs` directory adjacent to this script
        docs_dir = os.path.join(current_dir, 'docs')

        filePath = os.path.join(docs_dir, '3line.xlsx')


        if filePath and os.path.isfile(filePath):
            print("加载路网文件路径：", filePath)
            self.flagOpenFile = 1
            # 初始化线路
            self.line = Line(filePath)
            print("路网数据加载成功!!!")
        else:
            print("路网数据加载失败!!!")

    # 开始仿真跟踪
    def start_simulation(self):
        # if self.flagOpenFile * self.flagConnectFlow > 0:
        # 仿真

        print('仿真开启!!!')
        self.flagStartSim = True

        # self.sim2.start()

    def step_simulation(self):
        print('the simulation step is', self.stepCounter)
        self.vels.updateState()
        self.appendTraList()
        self.stepCounter += 1

    def stop_simulation(self):
        self.saveTraList()
        # self.cal_result()
        print('仿真结束!!!')

    def appendTraList(self):
        if self.stepCounter % 10 == 0:
            for vehicle in self.vels.velList:
                self.traList.append([self.stepCounter * self.dt, vehicle.id, round(vehicle.x,2), vehicle.laneNum, round(vehicle.v,2), self.simDirection])
        # self.stepCounter += 1

    def saveTraList(self):

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"data_{timestamp}.csv"

        # ensure docs directory exists alongside this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        docs_dir = os.path.join(current_dir, 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        full_path = os.path.join(docs_dir, file_name)

        self.traDF = pd.DataFrame(self.traList, columns=['simTime', 'id', 'x', 'laneNum', 'v', 'direction'])
        self.traDF.to_csv(full_path, index=False)
        print(f"轨迹数据已保存: {full_path}")

    def add_vehicle(self):

        flow = 3600
        flag = 36000/flow

        if self.stepCounter % flag == 0:

            beginNode = 'node001'
            beginLaneNum = 1
            beginSpeed = random.randint(20, 30)
            targetNode = 'node002'
            targetLaneNum = random.randint(1, 2)
            vehicleType = random.choice(['Car', 'Truck'])

            self.vels.velList.append(Vehicle(beginNode, beginLaneNum, beginSpeed, targetNode, targetLaneNum, vehicleType))  # 输入车辆的函数
            self.vels.velList[-1].targetEndPosition = 1200
            self.vels.velList[-1].x = 0

            # # self.sim2.addVehicle(self.simDirection)
            # beginNode, beginLaneNum, beginSpeed, targetNode, targetLaneNum, vehicleType = self.demand.addVehicle()

            # if self.rampMeterFlag and beginNode == 'node005':
            #     print('匝道管控')
            # else:
            #     self.vels.velList.append(Vehicle(beginNode, beginLaneNum, beginSpeed, targetNode, targetLaneNum, vehicleType))  # 输入车辆的函数
            #     self.vels.velList[-1].targetEndPosition = self.vels.get_nodePosition(targetNode)
            #     self.vels.velList[-1].x = self.vels.get_nodePosition(beginNode)
    
    def show_simData(self):
        print('在途车辆:', len(self.vels.velList))


    def set_laneBan(self, laneBanDict):
        self.line.set_laneBanWithInput(laneBanDict)

    def set_VSL(self, variableSpeedLimit):
        self.line.set_VSLWithInput(variableSpeedLimit)

    def set_VLF(self, variableLaneFeasibility):
        self.line.set_VLFWithInput(variableLaneFeasibility)

    def set_RM(self, flag):
        self.rampMeterFlag = flag

if __name__ == "__main__":
    
    sim1 = SimControl(3600, '1')
    sim1.start_simulation()
    for i in range(600):
        sim1.add_vehicle()
        sim1.step_simulation()
        sim1.show_simData()
    sim1.stop_simulation()