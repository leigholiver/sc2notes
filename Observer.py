from PyQt5.QtCore import QObject

class Observer(QObject):
	def __init__(self):
		QObject.__init__(self)

	def notify(self, data):
		pass

# data = {
#   "players": [
#     {
#       "name": "playerA",
#       "type": "user",
#       "race": "Prot",
#       "result": "Defeat",
#       "isme": "true"
#     },
#     {
#       "name": "playerB",
#       "type": "computer",
#       "race": "random",
#       "result": "Victory",
#       "isme": "false"
#     }
#   ],
#   "displayTime": "5.000000",
#   "event": "enter"
# }