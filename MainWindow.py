import json
from PyQt5.QtWidgets import QWidget, QTextEdit, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit, QFormLayout, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QSettings, QSize
from webhook import httpListener
from MatchHistory import MatchHistory
from UIListener import UIListener

class MainWindow(QWidget):
	notes = {}
	OPName = ""

	def __init__(self):
		QWidget.__init__(self)
		try:
			with open('notes.json', 'r') as infile:  
				m = json.load(infile)
				self.notes = m
		except:
			pass 

		self.hl = httpListener(8081)
		self.mh = MatchHistory()
		self.ui = UIListener(self, self.mh)
		self.ui.loadText.connect(self.updateText)
		self.hl.attach(self.mh)
		self.hl.attach(self.ui)
		self.hl.start()

		# window
		self.setWindowTitle('SC2Notes')
		self.settings = QSettings('leigholiver', 'sc2notes')
		self.resize(self.settings.value("size", QSize(900, 450)))
		if self.settings.value("pos") != None:
			self.move(self.settings.value("pos"))

		# layout
		layout = QHBoxLayout()
		layout.setAlignment(Qt.AlignTop)

		col1 = QVBoxLayout()
		col1.setAlignment(Qt.AlignTop)
		col1.addWidget(QLabel("Notes"))

		self.noteText = QTextEdit()
		self.noteText.textChanged.connect(lambda: self.saveNoteText(self.noteText.document().toPlainText()))

		col1.addWidget(self.noteText)
		layout.addLayout(col1, 3)

		col2 = QVBoxLayout()
		col2.setAlignment(Qt.AlignTop)

		col2.addWidget(QLabel("")) # spacer

		ipaddrForm = QHBoxLayout()
		ipaddrLabel = QLabel("SC2Switcher URL:")
		ipaddrBox = QLineEdit("http://localhost:8081/")
		ipaddrForm.addWidget(ipaddrLabel)
		ipaddrForm.addWidget(ipaddrBox)
		col2.addLayout(ipaddrForm)

		searchLabel = QLabel("Search:")
		self.searchBox = QLineEdit()
		self.searchBox.returnPressed.connect(lambda: self.doSearch(self.searchBox.text()))
		searchForm = QHBoxLayout()
		searchbtn = QPushButton("Go")
		searchbtn.clicked.connect(lambda: self.doSearch(self.searchBox.text()))
		searchForm.addWidget(searchLabel)
		searchForm.addWidget(self.searchBox)
		searchForm.addWidget(searchbtn)
		col2.addLayout(searchForm)

		self.searchResults = QWidget()
		self.searchResults.hide()
		self.searchResults.setLayout(QVBoxLayout())
		col2.addWidget(self.searchResults)

		self.gameLabel = QLabel("")
		col2.addWidget(self.gameLabel)

		col2.addWidget(QLabel("Match History"))

		self.historyLabel = QLabel()
		col2.addWidget(self.historyLabel)

		layout.addLayout(col2, 2)

		self.setLayout(layout)
		self.show()

	def saveNoteText(self, text):
		self.notes[self.OPName] = text			
		with open('notes.json', 'w') as outfile:  
			json.dump(self.notes, outfile)
	
	def closeEvent(self, e):
		self.settings.setValue("size", self.size())
		self.settings.setValue("pos", self.pos())
		e.accept()

	def updateText(self, text):
		self.noteText.setText(text)

	def doSearch(self, query):
		layout = self.searchResults.layout()
		index = layout.count()
		while(index >= 0):
			if layout.itemAt(index) != None:
				myWidget = layout.itemAt(index).widget()
				myWidget.setParent(None)
			index -=1

		self.gameLabel.setText("");
		results = []
		for name in self.notes.keys():
			if query in name and name not in results:
				results.append(name)
			if query in self.notes[name] and name not in results:
				results.append(name)
		for name in self.mh.matches.keys():
			if query in name and name not in results:
				results.append(name)
		
		if len(results) > 0:
			for name in results:
				if name != "":
					btn = QPushButton(name)
					btn.clicked.connect(lambda: self.loadFromUsername(name))
					layout.addWidget(btn)			
			
			self.searchResults.show()		
		else:
			self.gameLabel.setText("No results found.");

	def loadFromUsername(self, username):
		if username in self.notes:
			self.OPName = username
			self.noteText.setText(self.notes[username])
			if (username in self.mh.matches) == False:
				self.historyLabel.setText("")

		if username in self.mh.matches:
			out = ""
			wins = 0
			games = 0
			for i in reversed(range(len(self.mh.matches[username]))):
				games = len(self.mh.matches[username])
				m = self.mh.matches[username][i]
				secs = float(m['gametime'])
				mins = secs / 60
				secs = secs % 60
				out += m['result'] + " - " + m['race'] + " - " + str(int(mins)) + "m" + str(int(secs)) + "s - " + m['date'] + "\n"
				if m['result'] == 'Victory': wins = wins + 1
			self.OPName = username
			self.historyLabel.setText(out)
			winrate = "0"
			if games > 0:
				winrate = str(int(wins/games))
			self.gameLabel.setText("History against " + username + " - " + 
						str(wins) + ":" + str(games - wins) + " (" + winrate + "%)")
			if (username in self.notes) == False:
				self.noteText.setText("")
		self.searchResults.hide()