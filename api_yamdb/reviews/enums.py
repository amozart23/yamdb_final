from enum import Enum


class Role(str, Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class Score(int, Enum):
    PERFECT = 10
    OUTSTANDING = 9
    EXCELLENT = 8
    VERY_GOOD = 7
    GOOD = 6
    ABOVE_AVERAGE = 5
    AVERAGE = 4
    BELOW_AVERAGE = 3
    WEAK = 2
    VERY_WEAK = 1
