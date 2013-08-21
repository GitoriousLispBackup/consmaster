#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from cm_globals import *


def getModeStats(mode):
    """
    Make statistics html table for defined training mode.
    """
    nrows = len(mode.training)
    htmlTable = '<tr><th>Niveau</th><th>Réalisations</th><th>Moyenne</th></tr>'
    for lvl in sorted(mode.training.keys()):
        lst = mode.training[lvl]
        k = len(lst)
        avg = sum(lst) / k
        row = '<tr><td>{}</td><td>{}</td><td>{:.2%}</td></tr>'.format(lvl, k, avg)
        htmlTable += row
    return  '<table border="1">' + htmlTable + '</table>'


class StatsDialog(QDialog):
    """
    Dialog for display statistics for current selected user.
    """
    def __init__(self, userData):
        super().__init__()

        label = QLabel('<b>User :</b> ' + userData.nick + '<br> mail : <i>' + userData.mail + '<i>')

        tabWidget = QTabWidget()
        for name, mode in userData.modes.items():
            tabWidget.addTab(QLabel(getModeStats(mode)), name)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(tabWidget)

        self.setLayout(layout)
        self.resize(400, 200)
