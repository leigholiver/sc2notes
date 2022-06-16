import json
from PyQt5.QtCore import pyqtSignal
from Observer import Observer


class UIListener(Observer):
    loadText = pyqtSignal(str)
    updateRecents = pyqtSignal()

    def notify(self, data):
        if len(data['players']) == 2:
            found = False
            opFound = False
            op = None
            result = ""
            for p in data['players']:
                if p['isme']:
                    # if we already found us, we're probably same name?
                    if found:
                        opFound = True
                        op = p
                        result = "Unknown Result"
                    found = True
                    result = p['result']
                elif p['isme'] == False and opFound == False:
                    opFound = True
                    op = p

            if found and opFound and op != None:
                if data['event'] == 'enter':
                    self.ui.OPName = op['name'] + "/" + op['race']
                    if op['name'] + "/" + op['race'] in self.ui.notes:
                        self.loadText.emit(
                            self.ui.notes[op['name'] + "/" + op['race']])
                    elif op['name'] in self.ui.notes:
                        self.loadText.emit(self.ui.notes[op['name']])
                    else:
                        self.loadText.emit("")

                    wins = 0
                    games = 0
                    self.ui.historyLabel.setText("")
                    if op['name'] in self.mh.matches:
                        games = len(self.mh.matches[op['name']])
                        out = ""
                        for i in reversed(range(len(self.mh.matches[op['name']]))):
                            m = self.mh.matches[op['name']][i]
                            secs = float(m['gametime'])
                            mins = secs / 60
                            secs = secs % 60
                            out += m['result'] + " - " + m['race'] + " - " + \
                                str(int(mins)) + "m" + str(int(secs)) + \
                                "s - " + m['date'] + "\n"
                            if m['result'] == 'Victory':
                                wins = wins + 1
                        self.ui.historyLabel.setText(out)

                    if games == 0:
                        winrate = "0"
                    else:
                        winrate = str(int((wins/games) * 100))

                    self.ui.gameLabel.setText("In game against " + op['name'] + " (" + op['race'] + ") - " +
                                              str(wins) + ":" + str(games - wins) + " (" + winrate + "%)")
                elif data['event'] == 'exit':
                    self.ui.gameLabel.setText(
                        result + " against " + op['name'] + " (" + op['race'] + ")")
                    self.updateRecents.emit()
            else:
                self.ui.gameLabel.setText(" ")

    def __init__(self, ui, mh):
        Observer.__init__(self)
        self.ui = ui
        self.mh = mh
