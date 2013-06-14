from collections import defaultdict

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
    def __init__(self, name, mail, nmodes=3):
        self.name = name
        self.mail = mail
        self.modes = [ExoType() for _ in range(nmodes)]
    def get_mode(self, n):
        return self.modes[n]
    def __repr__(self):
        return '<UserData:\n' + self.name + ',\n' + self.mail + ',\n' + '\n'.join(repr(mode) for mode in self.modes) + '\n>'
