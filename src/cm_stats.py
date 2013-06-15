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
    htmlTable = '<tr><td>Niveau</td><td>Moyenne</td></tr>'
    for lvl in sorted(mode.training.keys()):
        lst = mode.training[lvl]
        avg = sum(lst) / len(lst)
        row = '<tr><td>{}</td><td>{:.2%}</td></tr>'.format(lvl, avg)
        htmlTable += row
    htmlTable = '<table border="1">' + htmlTable + '</table>'
    table = QLabel(htmlTable)
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
