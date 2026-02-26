import pandas as pd


class Line(object):

    def __init__(self, filePath):
        self.dfNode = pd.read_excel(filePath, sheet_name='Node')
        self.dfEdge = pd.read_excel(filePath, sheet_name='Edge')
        self.dfDevice = pd.read_excel(filePath, sheet_name='Device')

        # print(self.dfDevice)

        # print(self.dfEdge)
        # print(self.dfNode)
        # print(self.dfEdge)
        self.nodeNum = len(self.dfNode)
        self.edgeNum = len(self.dfEdge)
        self.lineLength = self.dfNode['position'][self.nodeNum - 1] - self.dfNode['position'][0]
        # 障碍物路段
        # self.dataLaneBan = [[3600, 3600, 4],
        #                     [11200, 11200, 4]]
        self.dataLaneBan = self.get_onRampEndPosition()
        # print(self.dataLaneBan)
        self.laneBan = pd.DataFrame(self.dataLaneBan, columns=['positionBeg', 'positionEnd', 'laneNum'])
        self.VSL = []

    def get_onRampEndPosition(self):
        dataLaneBan = []
        for index, row in self.dfNode.iterrows():
            if self.dfNode['type'][index] == 'onRampEnd':
                dataLaneBan.append([self.dfNode['position'][index], self.dfNode['position'][index], 4])

        return dataLaneBan

    def set_laneBanWithInput(self, laneBanDict):
        lanes = laneBanDict['lanes']
        startPosition = laneBanDict['startPosition']
        endPosition = laneBanDict['endPosition']
        for i in range(len(lanes)):
            self.laneBan.loc[len(self.laneBan)] = [startPosition, endPosition, lanes[i]]

    def set_VSLWithInput(self, VSL):
        self.VSL = VSL

    def set_VLFWithInput(self, VLF):
        startPosition = VLF['startPosition']
        allowsList = VLF['allows']
        print(allowsList)
        for i in range(len(allowsList)):
            if not allowsList[i]:
                self.laneBan.loc[len(self.laneBan)] = [startPosition, self.lineLength, i+1]


