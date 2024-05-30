#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 22:04:35 2024

@author: matthewdobre
"""
#fix multiple simulation functionality?, fix file importing
#fix memory with pd large imports

import numpy as np
import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5.QtGui import *

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.style as style
import sympy as smp
#import pyqtgraph as pg

import re


dfDict = {} # global variable that stores all of the data

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
            
        # position frames within widget
        self.main = QWidget()
        self.setMinimumSize(700, 500)
        self.layout = QVBoxLayout(self.main)
        self.setWindowTitle("Xyce Waveform Viewer")
        self.setCentralWidget(self.main)  # Set the main widget
        self.df = None



        self.splitter = QSplitter(Qt.Horizontal)        

        self.plot_window = Plot()
        self.sidebar = Sidebar(self.plot_window)

        self.splitter.addWidget(self.sidebar)  # Add the sidebar to the layout
        self.splitter.addWidget(self.plot_window)
        
        self.utils = Utils(self.plot_window)
        self.layout.addWidget(self.utils)  # Add the sidebar to the layout
        self.utils.dataLoaded.connect(self.reloadSidebar)

        self.layout.addWidget(self.splitter, 70)
                


        
        if (len(sys.argv) > 1 and os.path.isfile(sys.argv[1])):
            self.utils.prnParser(sys.argv[1])
            self.reloadSidebar()
            #convert to regular expression for math 
            

        '''
        sandia image
       # Load the image
        self.pixmap = QPixmap('logo.png')
        
        self.pixmap = self.pixmap.scaled(128, 128, Qt.KeepAspectRatio)

       # Create a QLabel object
        self.label = QLabel(self)

       # Set the pixmap to the QLabel
        self.label.setPixmap(self.pixmap)

       # Resize the QLabel to fit the pixmap
        self.label.resize(self.pixmap.width(), self.pixmap.height())

       # Add the QLabel to the QGridLayout at the top right corner
        self.layout.addWidget(self.label, 0, 1, )
        '''
        
        

    
    def reloadSidebar(self):
        self.sidebar.deleteLater()  # Delete the old sidebar
        self.sidebar = Sidebar(self.plot_window)  # Create a new sidebar
        self.splitter.addWidget(self.sidebar)  # Add the new sidebar to the layout
        self.splitter.addWidget(self.plot_window)
        
        
        
class Item(QStandardItem): 
    def __init__(self, txt='', font=12, setBold = False, color = QColor(0,0,0), data = []):
        super().__init__()
        
        fnt = QFont('Helvetica', font)
        fnt.setBold(setBold)
        
        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
        self.setData(data, Qt.UserRole+1)

# Frame for the tree information
class Sidebar(QFrame):
    
    
    def getData(self, item): 
        # Create a Figure instance
        data = item.data(Qt.UserRole+1)
        title = item.data()

        t = [np.array(t_).astype(float) for t_ in data[0]]
        #t = t_.astype(float)
        #y_ = np.array(data[1])
        y = [np.array(y_).astype(float) for y_ in data[1]]
        # Generate a plot
        style.use('ggplot')
        self.figure = Figure()

        # Create a FigureCanvas instance
        self.canvas = FigureCanvas(self.figure)

        # Create an Axes instance
        
        self.ax = self.figure.add_subplot(111)
        for i in range(len(t)):
            self.ax.plot(t[i], y[i])
        
        self.ax.ticklabel_format(axis='both', style='sci', scilimits=(0,0))
        #self.ax.set_xticks(self.ax.get_xticks()[::500])
        self.ax.set_title(title)
        self.ax.set_xlabel('T')
        self.ax.set_ylabel(title[0])

        
        
        currentPlane = self.plot.planeWidget.currentWidget()
        self.toolbar = NavigationToolbar(self.canvas, self)
        currentPlane.layout().addWidget(self.toolbar)
        currentPlane.layout().addWidget(self.canvas)
        

        
        # Draw the plot
        self.canvas.draw()
        
        
    def plotOptions(self, position): 
        selected = self.treeView.selectedIndexes()
        numSel = len(selected)
        
        
        menu = QMenu()
        group = menu.addAction("Plot Group")
        math = menu.addAction("Plot Math")
        remove = menu.addAction("Remove Signals")
        
        action = menu.exec_(self.treeView.mapToGlobal(position))
            
        if action == group: 
            self.plotGroup(selected)
        elif action == math: 
            string, ok = QInputDialog.getText(self, 'Plot Math', 'Enter Expression of Selected Signals')
            if ok:
                self.plotMath(string, selected)
        elif action == remove: 
            self.removeSignals(selected)
            
    def removeSignals(self, selected):
        # check to see if you'd like to remove all signals if root is selected
        global dfDict
        for signal in selected:
            if signal.data(Qt.UserRole+1) == 'root': 
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText('You have selected the root. Would you like to delete all signals?')
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel) 
                ok = msg.exec_()
                
                if ok:
                    dfDict.pop(signal.data(), None)
                    self.treeModel.removeRow(signal.row(), signal.parent())
            else:
                self.treeModel.removeRow(signal.row(), signal.parent())
                
    def plotGroup(self, selected): 
        # Create a Figure instance
        
            
        #data = item.data(Qt.UserRole+1)
        #title = item.data()
        style.use('ggplot')
        headers = []
        self.figure = Figure()

        # Create a FigureCanvas instance
        self.canvas = FigureCanvas(self.figure)

        # different sizes exception?s 
        # some error with scale here
        self.ax = self.figure.add_subplot(111)
        for signal in selected: 
            data = signal.data(Qt.UserRole+1)
            if(data != 'root'):

                headers.append(signal.data())

                t = [np.array(t_).astype(float) for t_ in data[0]]
                y = [np.array(y_).astype(float) for y_ in data[1]]
                for i in range(len(t)): 
                    self.ax.plot(t[i], y[i])
            
        # Generate a plot
        
        
        self.ax.ticklabel_format(axis='both', style='sci', scilimits=(0,0))
        formattedTitle = "Group {0}".format(' '.join(headers))
        self.ax.set_title(formattedTitle)
        self.ax.set_xlabel('T')
        
        # Add the FigureCanvas instance to the layout
        currentPlane = self.plot.planeWidget.currentWidget()
        self.toolbar = NavigationToolbar(self.canvas, self)
        currentPlane.layout().addWidget(self.toolbar)
        currentPlane.layout().addWidget(self.canvas)
        
        # Draw the plot
        self.canvas.draw()
        
    def plotMath(self, string, selected): 
        varDict = {}
        t = []

        style.use('ggplot')
        self.figure = Figure()

        self.canvas = FigureCanvas(self.figure)

        self.ax = self.figure.add_subplot(111)
        
        for signal in selected: 
            data = signal.data(Qt.UserRole+1)
            y = [np.array(y_).astype(float) for y_ in data[1]]
            varDict[signal.data()] = y
            t = [np.array(t_).astype(float) for t_ in data[0]]
        
        print(t)
        symbols = smp.symbols(list(varDict.keys()))
        
        expr = smp.simplify(string)

        f = smp.lambdify(symbols, expr, "numpy")
        
        for i in range(len(t)):
            args = []
            for key in varDict.keys():
                args.append(varDict[key][i])
    
            y = f(*args)
            t_ = t[i]
            
            self.ax.plot(t_, y)
        
        self.ax.ticklabel_format(axis='both', style='sci', scilimits=(0,0))
        self.ax.set_title(string)
        self.ax.set_xlabel('T')
        currentPlane = self.plot.planeWidget.currentWidget()
        self.toolbar = NavigationToolbar(self.canvas, self)
        currentPlane.layout().addWidget(self.toolbar)
        currentPlane.layout().addWidget(self.canvas)

        self.canvas.draw()
        
        
    def __init__(self, plot):
        super().__init__()
        self.plot = plot
        global dfDict
        self.side_frame = QFrame()
        self.side_layout = QVBoxLayout()
        
        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(True)
        
        self.treeModel = QStandardItemModel()
        rootNode = self.treeModel.invisibleRootItem()
        
        # parse columns of dataframe
        if(len(dfDict) > 0):
            for key in dfDict: 
                df = dfDict[key]
                sidebarRoot = Item(key, 14, setBold = True, color = QColor(200,200,200), data = 'root') # dependent variable column
                t = df.columns[1]
                children = []
            
                for i in range(2, len(df.columns)): 
                    column = df.columns[i]
                    children.append(Item(column, color = QColor(200,200,200), data = [df[t], df[column], str(key)]))
                
    
                sidebarRoot.appendRows(children)        
                rootNode.appendRow(sidebarRoot)
                
            self.treeView.setModel(self.treeModel)
            self.treeView.expandAll()
            self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.treeView.doubleClicked.connect(self.getData)
            self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
            self.treeView.customContextMenuRequested.connect(self.plotOptions)
        
        self.side_layout.addWidget(self.treeView)
        self.setLayout(self.side_layout)
        
 
    
                    
        
        
# frame for plotting information  
class Plot(QFrame):
    def addPlane(self): 
        newPlane = QWidget()
        newPlane.setLayout(QVBoxLayout())
        self.planeWidget.addTab(newPlane, f"Plane {self.planeWidget.count()}")

    def __init__(self):
        super().__init__()
        self.plot_frame = QFrame()

        self.planeWidget = QTabWidget()
        self.planeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.planeWidget.customContextMenuRequested.connect(self.openMenu)

        self.initPlane = QWidget()
        self.initPlane.setLayout(QVBoxLayout())
        self.planeWidget.addTab(self.initPlane, "Welcome")

        self.plot_layout = QGridLayout()



        self.plot_layout.addWidget(self.planeWidget, 0, 0)

        self.setLayout(self.plot_layout)  # Set the layout for the sidebar

    def openMenu(self, position):
        menu = QMenu()
        deleteAction = menu.addAction("Delete")
        renameAction = menu.addAction("Rename")
        action = menu.exec_(self.planeWidget.mapToGlobal(position))
        if action == deleteAction:
            self.planeWidget.removeTab(self.planeWidget.currentIndex())
        if action == renameAction:
            self.renameTab()
        
    def renameTab(self):
        index = self.planeWidget.currentIndex()
        newName, ok = QInputDialog.getText(self, 'Rename Tab', 'Enter new name:')
        if ok:
            self.planeWidget.setTabText(index, newName)
        
# frame for utilities bar (adding files)


class Utils(QFrame):
    dataLoaded = pyqtSignal()

    def loadPrn(self):
        self.fname = QFileDialog.getOpenFileName(self)
        
        if os.path.isfile(self.fname[0]): 
            self.prnParser(self.fname[0])
            print(dfDict.keys())
        else:
            '''
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('File Not Found!')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel) 
            msg.exec_()
            '''
            pass
    def prnParser(self, file):
        global dfDict
        dataLoaded = pyqtSignal()
        df = pd.read_csv(file, sep = '\s+', skipfooter=1, engine = 'python')

        df.columns = df.columns.str.replace('[^a-zA-Z0-9_]', '', regex = True)

        df_new = pd.DataFrame([], columns = df.columns)
        # first column is index, split it 
        indexCol = df.columns[0]
        #obtain the indicies of repeating columns
        idx0 = np.where(np.array(df[indexCol]) == 0)[0]

        for col in df_new.columns:
            df_new[col] = np.split(np.array(df[col]), idx0[1:])
        

        dfDict[file] = df_new
        self.dataLoaded.emit()


    def addPaneAction(self):
        self.plot.addPlane()

    def __init__(self, plot):
        super().__init__()
        self.plot = plot
        self.fname = None
        self.utils_frame = QFrame()

        self.utils_layout = QVBoxLayout()
        self.addBtn = QPushButton("Utils")
        
        # Create a QMenu
        menu = QMenu(self)
        loadAction = QAction('Import File', self)
        loadAction.triggered.connect(self.loadPrn)
        addPaneAction = QAction('Add Plane', self)
        addPaneAction.triggered.connect(self.addPaneAction)
        
        menu.addAction(loadAction)
        menu.addAction(addPaneAction)
        
        self.addBtn.setMenu(menu)
        
        self.utils_layout.addWidget(self.addBtn)
        
        self.setLayout(self.utils_layout)  # Set the layout for the sidebar

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()

        
        
        

