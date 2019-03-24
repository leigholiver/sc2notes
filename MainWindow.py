import json, requests
from functools import partial
from PyQt5.QtWidgets import QWidget, QTextEdit, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit, QFormLayout, QPushButton, QScrollArea, QSlider
from PyQt5.QtGui import QIcon, QFont
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
		self.ui.updateRecents.connect(self.loadRecents)
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

		col1.addWidget(QLabel("Font Size"))
		self.fontSize = QSlider(Qt.Horizontal)
		self.fontSize.setMinimum(9)
		self.fontSize.setMaximum(48)
		if self.settings.value("fontSize") != None:
			self.fontSize.setValue(int(self.settings.value("fontSize")))
			self.setFontSize()
		self.fontSize.valueChanged.connect(self.setFontSize)

		col1.addWidget(self.fontSize)
		layout.addLayout(col1, 3)

		col2 = QVBoxLayout()
		col2.setAlignment(Qt.AlignTop)

		col2.addWidget(QLabel("")) # spacer

		# check for updates
		self.updates = QVBoxLayout()
		self.updates.setAlignment(Qt.AlignTop)
		self.updates.setContentsMargins(0, 0, 0, 0)
		col2.addLayout(self.updates)
		self.checkForUpdates()

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
		tmplayout = QVBoxLayout()
		tmplayout.setAlignment(Qt.AlignTop)
		tmplayout.setContentsMargins(0, 0, 0, 0)
		self.searchResults.setLayout(tmplayout)

		self.scroll = QScrollArea()
		self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.searchResults)

		scroll_layout = QVBoxLayout()
		scroll_layout.setAlignment(Qt.AlignTop)
		scroll_layout.addWidget(self.scroll)
		scroll_layout.setContentsMargins(0, 0, 0, 0)
		col2.addWidget(self.scroll)
		self.scroll.hide()

		self.gameLabel = QLabel("")
		col2.addWidget(self.gameLabel)

		col2.addWidget(QLabel("Match History"))
		

		self.historyLabel = QLabel()
		widget = QWidget()
		tmplayout = QVBoxLayout()
		tmplayout.setAlignment(Qt.AlignTop)
		tmplayout.setContentsMargins(0, 0, 0, 0)
		tmplayout.addWidget(self.historyLabel)
		widget.setLayout(tmplayout)

		self.historyLabelScroll = QScrollArea()
		self.historyLabelScroll.setAlignment(Qt.AlignTop)
		self.historyLabelScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.historyLabelScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.historyLabelScroll.setWidgetResizable(True)
		self.historyLabelScroll.setWidget(widget)

		scroll_layout = QVBoxLayout()
		scroll_layout.setAlignment(Qt.AlignTop)
		scroll_layout.addWidget(self.historyLabelScroll)
		scroll_layout.setContentsMargins(0, 0, 0, 0)
		col2.addWidget(self.historyLabelScroll)

		self.recentMatchesText = QLabel("Recent Matches")
		col2.addWidget(self.recentMatchesText)

		self.recentMatches = QWidget()
		tmplayout = QVBoxLayout()
		tmplayout.setAlignment(Qt.AlignTop)
		tmplayout.setContentsMargins(0, 0, 0, 0)
		self.recentMatches.setLayout(tmplayout)

		self.recentMatchesScroll = QScrollArea()
		self.recentMatchesScroll.setAlignment(Qt.AlignTop)
		self.recentMatchesScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.recentMatchesScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.recentMatchesScroll.setWidgetResizable(True)
		self.recentMatchesScroll.setWidget(self.recentMatches)

		scroll_layout = QVBoxLayout()
		scroll_layout.setAlignment(Qt.AlignTop)
		scroll_layout.addWidget(self.recentMatchesScroll)
		scroll_layout.setContentsMargins(0, 0, 0, 0)
		col2.addWidget(self.recentMatchesScroll)

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
					btn.clicked.connect(partial(self.loadFromUsername, name))
					layout.addWidget(btn)			
			
			self.scroll.show()		
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
				winrate = str(int((wins/games) * 100))
			self.gameLabel.setText("History against " + username + " - " + 
						str(wins) + ":" + str(games - wins) + " (" + winrate + "%)")
			if (username in self.notes) == False:
				self.noteText.setText("")
		self.scroll.hide()

	def loadRecents(self):
		layout = self.recentMatches.layout()
		index = layout.count()
		while(index >= 0):
			if layout.itemAt(index) != None:
				myWidget = layout.itemAt(index).widget()
				myWidget.setParent(None)
			index -=1
		wins = 0
		games = 0
		for i in reversed(range(len(self.mh.recents))):
			games = len(self.mh.recents)
			m = self.mh.recents[i]
			secs = float(m['gametime'])
			mins = secs / 60
			secs = secs % 60
			btn = QPushButton(m['result'] + " - " + m['opponent'] + " - " + m['race'] + " - " + str(int(mins)) + "m" + str(int(secs)) + "s - " + m['date'])
			btn.clicked.connect(partial(self.loadFromUsername, m['opponent']))
			layout.addWidget(btn)
			if m['result'] == 'Victory': wins = wins + 1
		winrate = "0"
		if games > 0:
			winrate = str(int((wins/games) * 100))
			self.recentMatchesText.setText("Recent Matches - " + 
					str(wins) + ":" + str(games - wins) + " (" + winrate + "%)")

	def setFontSize(self):
		font = QFont()
		font.setPointSize(self.fontSize.value())
		self.noteText.setFont(font)
		self.settings.setValue("fontSize", self.fontSize.value())

	def checkForUpdates(self):
		r = requests.get('https://api.github.com/repos/leigholiver/sc2notes/releases/latest')
		response = r.json()
		if float(response['tag_name']) > 0.3:
			updateLink = QLabel("<a href=\"" + response['html_url'] + "\">Update Available. Click here to download.</a>")
			updateLink.setTextFormat(Qt.RichText)
			updateLink.setTextInteractionFlags(Qt.TextBrowserInteraction)
			updateLink.setOpenExternalLinks(True)
			self.updates.addWidget(updateLink)
			self.updates.addWidget(QLabel(response['body']))