import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg


class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
                              
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QHBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.simLength = 1000000;

        self.mutationFactor = 0.1
        startPop = {'spontBirthChance':0,'spontBirthRate':0, 'deathChance': 0.1, 'numberDeathEffect':0.0005, 'totalNumberDeathEffect': 0.0005, 'repChance':0.6,'totalNumber':100, 'mutationChance':0.00001, 'mutation':None}

        self.population = [startPop]
        self.newPop = None
        
        self.populationHistory = []
        self.populationHistoryExpected = []
        
        self.plots = []
        
        self.current = self.canvas.addPlot()
        self.current.setXRange(0, 500, padding=0)
        self.current.setYRange(0, 1000, padding=0)

        
        for pop in self.population:
            self.populationHistory.append(list())
            self.populationHistoryExpected.append(list())
                    
            penNew=QtGui.QPen(QtGui.QColor(np.random.randint(100,256), np.random.randint(100,256), np.random.randint(100,256)))
                    
            self.plots.append(self.current.plot(pen=penNew));
            
        self.totalFrameCounter = 0
        self._update()

    def calculate(self):

        counter = 0
        for pop in self.population:

            self.changePopulation(pop)

            if(pop['totalNumber'] > 0):
                self.populationHistory[counter].append(pop['totalNumber'])
                self.plots[counter].setData(self.populationHistory[counter][len(self.populationHistory[counter])-500:],clear=True)           
            else:
                self.plots[counter].setData([],clear=True)
                self.plots[counter].clear()
            if self.newPop != None:
                self.population.append(self.newPop)
                self.newPop = None

            self.totalFrameCounter = self.totalFrameCounter + 1
            self.simLength = self.simLength - 1
            counter = counter + 1
        
    
    def _update(self):
        self.calculate()

        #if at least one population is alive, keep going
        if self.simLength > 0:
            for i in self.population:
                if i['totalNumber'] > 0:
                    QtCore.QTimer.singleShot(0, self._update)
                    break
        
    def getTotalPopulation(self):
        num=0
        for x in self.population:
            num+=x['totalNumber']

        return num

    def rollDice(self,chance):

        rand = np.random.random_sample()

        if rand <= chance:
            return True
        else:
            return False   

    def getAverageStats(self):
        avgDeathChance = 0
        avgTotalDeathChance = 0
        avgDeathNumberChance = 0
        avgRepChance = 0
        avgMutationChance = 0
        
        for pop in self.population:
            avgDeathChance = avgDeathChance + pop['deathChance']
            avgTotalDeathChance = avgTotalDeathChance + pop['totalNumberDeathEffect']
            avgDeathNumberChance = avgDeathNumberChance + pop['numberDeathEffect']
            avgRepChance = avgRepChance + pop['mutationChance']
            avgMutationChance = avgMutationChance + pop['mutationChance']

        avgDeathChance =  avgDeathChance / len(self.population)
        avgTotalDeathChance  = avgTotalDeathChance/ len(self.population)
        avgDeathNumberChance  = avgDeathNumberChance/ len(self.population)
        avgRepChance  = avgRepChance/ len(self.population)
        avgMutationChance = avgMutationChance/ len(self.population)

        return (avgDeathChance,avgTotalDeathChance,avgDeathNumberChance,avgRepChance,avgMutationChance)
         
    def changePopulationExpected(self,popList):
        return ((popList['spontBirthChance'] * popList['spontBirthRate']) + (popList['repChance'] *  popList['totalNumber']) - (popList['deathChance'] * popList['totalNumber']) -  (popList['totalNumberDeathEffect'] * self.getTotalPopulation()))

    def changePopulation(self,popList):
        change = 0

        np.random.seed()
        for i in range(popList['spontBirthRate']):
            if self.rollDice(popList['spontBirthChance']):
                change+=1
                
        np.random.seed()       
        for i in range(popList['totalNumber']):
            if self.rollDice(popList['repChance']):    
                if self.rollDice(popList['mutationChance']):
                    if popList['mutation'] == None:
                        self.newPop = {'spontBirthChance':0,'spontBirthRate':0, 'deathChance': 0.0,'numberDeathEffect':0.0, 'totalNumberDeathEffect': 0.0, 'repChance':0.0,'totalNumber':0, 'mutationChance':0.0001, 'mutation':None}

                        self.newPop['deathChance'] = popList['deathChance'] + popList['deathChance']* np.random.uniform(-self.mutationFactor,self.mutationFactor)
                        self.newPop['totalNumberDeathEffect'] = popList['totalNumberDeathEffect'] + popList['totalNumberDeathEffect'] * np.random.uniform(-self.mutationFactor,self.mutationFactor)
                        self.newPop['numberDeathEffect'] = popList['numberDeathEffect'] + popList['numberDeathEffect'] * np.random.uniform(-self.mutationFactor,self.mutationFactor)
                        self.newPop['repChance'] = popList['repChance'] + popList['repChance'] * np.random.uniform(-self.mutationFactor,self.mutationFactor)
                        self.newPop['mutationChance'] = popList['mutationChance'] + popList['mutationChance'] * np.random.uniform(-self.mutationFactor,self.mutationFactor)
                        
                        self.newPop['totalNumber'] = self.newPop['totalNumber'] + 10              

                        self.populationHistory.append([0] * self.totalFrameCounter)
                                
                        penNew=QtGui.QPen(QtGui.QColor(np.random.randint(50,256), np.random.randint(50,256), np.random.randint(50,256)))
                        penNew.setWidth(2)
                                
                        self.plots.append(self.current.plot(pen=penNew));

                        stats = self.getAverageStats()
                        print("Mutation! Averages: Death Chance: {0}.2f totalDeathEffect: {1}, deathEffect: {2}, repChance: {3}, mutChance: {4}".format(stats[0],stats[1],stats[2],stats[3],stats[4]))

                    else:
                        popList['mutation']['totalNumber'] = popList['mutation']['totalNumber'] + 1
                else:          
                    change+=1
                
        np.random.seed()
        for i in range(popList['totalNumber']):
            if self.rollDice(popList['deathChance'] +  popList['totalNumber'] * popList['numberDeathEffect'] + popList['totalNumberDeathEffect'] * self.getTotalPopulation()):
                change-=1

        popList['totalNumber']+=change
        popList['totalNumber']=max(popList['totalNumber'],0)

        return change
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())
