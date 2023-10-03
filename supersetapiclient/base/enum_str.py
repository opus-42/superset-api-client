from enum import Enum

class StringEnum(Enum):
    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if str(self.__class__) == str(other.__class__):
            return self.value == other.value
        # elif isinstance(other, str):
        #     return self.value == other
