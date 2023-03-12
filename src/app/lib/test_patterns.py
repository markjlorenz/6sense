MAX_FREQ = 32_764

class TestPattern:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

    def rosette(self):
        if self.x > 0:
            self.x = 0
            self.y = MAX_FREQ
            self.z = 0
        elif self.y > 0:
            self.x = 0
            self.y = 0
            self.z = MAX_FREQ
        else:
            self.x = MAX_FREQ
            self.y = 0
            self.z = 0

        return self.x, self.y, self.z
