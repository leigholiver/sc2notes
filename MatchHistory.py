import json
import datetime
from Observer import Observer


class MatchHistory(Observer):
    matches = {}
    recents = []

    def notify(self, data):
        if data['event'] == 'exit' and len(data['players']) == 2:
            found = False
            opFound = False
            result = ""
            op = None
            for p in data['players']:
                if p['isme']:
                    # if we already found us, we're probably same name?
                    if found:
                        opFound = True
                        op = p
                        result = "Unknown"
                    else:
                        found = True
                        result = p['result']
                elif p['isme'] == False and opFound == False:
                    opFound = True
                    op = p

            if found and opFound:
                m = {}
                m['opponent'] = op['name']
                m['race'] = op['race']
                m['gametime'] = data['displayTime']
                m['result'] = result
                m['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                if op['name'] in self.matches:
                    self.matches[op['name']].append(m)
                else:
                    self.matches[op['name']] = [m]

                with open('matches.json', 'w+') as outfile:
                    json.dump(self.matches, outfile)

                self.recents.append(m)
                print(self.recents)

    def __init__(self):
        Observer.__init__(self)
        try:
            with open('matches.json', 'r') as infile:
                m = json.load(infile)
                self.matches = m
        except:
            # exception if file doesnt exist, we dont need to
            # create it now - matches dict is already created
            # and file will get created on first write
            pass
