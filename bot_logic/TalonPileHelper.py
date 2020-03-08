class TalonPileHelper:
    def __init__(self, id, game):
        self.id = id
        self.game = game
        self.points = 0
        self.grade = 0
        self.scale_grade_color = {
            1: 0,
            2: 0,
            3: 0,
            4: 0.05,
            5: 0.2,
            6: 0.5,
            7: 1,
            8: 5
        }
