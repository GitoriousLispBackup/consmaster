#!/usr/bin/python3
# -*- coding: utf-8 -*-


try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

def getModeTab(mode):
    nrows = len(mode.training)
    table = QTableWidget(nrows, 2)
    table.setHorizontalHeaderLabels(['Niveau', 'Moyenne'])
    for lvl in sorted(mode.training.keys()):
        lst = mode.training[lvl]
        average = sum(lst) / len(lst)
        table.setItem(lvl, 0, QTableWidgetItem(str(lvl)))
        table.setItem(lvl, 1, QTableWidgetItem(str(average)))
        print(lvl, average)
    table.setDisabled(True)
    return table

class StatsDialog(QDialog):
    def __init__(self, userData):
        super().__init__()
        self.userData = userData

        label = QLabel('<b>User :</b> ' + userData.name + '<br> mail : <i>' + userData.mail + '<i>')
        
        tabWidget = QTabWidget()
        for mode in userData.modes:
            tabWidget.addTab(getModeTab(mode), 'test')

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(tabWidget)

        self.setLayout(layout)
