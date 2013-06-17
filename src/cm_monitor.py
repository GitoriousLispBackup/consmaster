from collections import defaultdict, OrderedDict
from cm_globals import MODES

class ExoType:
    def __init__(self):
        self.training = defaultdict(list)
        self.exercices = defaultdict(dict)
    def current_level(self):
        for lvl in sorted(self.training.keys(), reverse=True):
            results = self.training[lvl]
            if len(results) >= 10 and sum(results[-10:]) >= 7:
                return lvl + 1
        return 0
    def __repr__(self):
        return 'ExoType(training=' + repr(self.training) + ', exercices=' + repr(self.exercices) + ')'

class UserData:
    def __init__(self, name, mail):
        self.name = name
        self.mail = mail
        self.modes = OrderedDict()
        for mode in MODES:
            if mode.name != "Mode Libre":
                self.modes[mode.name] = ExoType()
    def get_mode(self, name):
        return self.modes[name]
    def __repr__(self):
        return '<UserData:\n' + self.name + ',\n' + self.mail + ',\n' + '\n'.join(repr(mode) for mode in self.modes.values()) + '\n>'
