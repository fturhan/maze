
class Position():
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def can_left(self):
        if self.x == 0:
            return False
        return True

    def can_up(self):
        if self.y == 0:
            return False
        return True

    def can_right(self, size: int):
        if self.x >= size - 1:
            return False
        return True

    def can_down(self, size: int):
        if self.y >= size - 1:
            return False
        return True

    def go_up(self):
        return Position(self.x, self.y - 1)

    def go_right(self):
        return Position(self.x + 1, self.y)

    def go_down(self):
        return Position(self.x, self.y + 1)

    def go_left(self):
        return Position(self.x - 1, self.y)

    def possible_next(self, size: int, previous_pos: "Position" = None):
        possibilities: list[Position] = []

        if self.can_up() and (previous_pos is None or not self.is_equals_to(previous_pos.go_down())):
            possibilities.append(self.go_up())

        if self.can_right(size) and (previous_pos is None or not self.is_equals_to(previous_pos.go_left())):
            possibilities.append(self.go_right())

        if self.can_down(size) and (previous_pos is None or not self.is_equals_to(previous_pos.go_up())):
            possibilities.append(self.go_down())

        if self.can_left() and (previous_pos is None or not self.is_equals_to(previous_pos.go_right())):
            possibilities.append(self.go_left())
        return possibilities

    def is_equals_to(self, other: "Position") -> bool:
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def moves_needed_to(self, other: "Position") -> int:
        """
        Calculate the difference between the 2 position
        """
        x = abs(self.x - other.x)
        y = abs(self.y - other.y)
        return y + x + 1

    def __str__(self) -> str:
        return f"({self.x},{self.y})"
