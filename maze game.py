# import enum
from random import randrange
import png


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
    
    def can_right(self, size:int):
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

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
def moves_needed(from_position: Position, to_position: Position):
    x = abs(to_position.x - from_position.x)
    y = abs(to_position.y - from_position.y)
    return y + x + 1

def generate_move_correct_way(start: Position, end: Position, size:int, _moves_needed:int, previous_pos: Position = None ):
    possibles_next = start.possible_next(size, previous_pos=previous_pos)
    next_moves_needed = _moves_needed
    next: Position
    while next_moves_needed >= _moves_needed:
        _random = randrange(0, len(possibles_next))
        next = possibles_next[_random]
        next_moves_needed = moves_needed(next, end)
    
    return next


def generate_path(start: Position, end: Position, size: int):
    moves = [start]
    print(start)
    _moves_needed = moves_needed(start, end)
    for i in range(1, _moves_needed - 1):
        __moves_needed = moves_needed(moves[i-1], end)
        previous_pos = None
        if (i>=2):
            previous_pos: Position = moves[i-2]
        print(i-1) 
        move = generate_move_correct_way(moves[i-1], end, size, __moves_needed, previous_pos=previous_pos)
        print(move)
        moves.append(move)
    print(end)
    moves.append(end)
    return moves



from flask import Flask

app = Flask(__name__)

def show_maze(size):
    final_maze = "<div id='maze'>"
    for x in range(0, size):
        for y in range(0, size):
            final_maze += f"""
                <div style="border: solid 1px; height: 50px; width: 50px; position: absolute; top: {y * 50}; left: {x * 50}"></div>
            """
    return final_maze + '/<div>'

def div_cell(position: Position, color: str="rgba(200,200,140,0.5)"):
    return f"""
        <div style="height: 49px; width: 49px; background-color: {color}; border: solid 1px red; position: absolute; 
        top: {position.y * 50}; left: {position.x * 50}"> {position.x, position.y} </div>
    """

def hide_divider(position1: Position, position2: Position, n_item: int):
    x = ((position2.x + position1.x) / 2) * 50 + 2
    y = ((position2.y + position1.y) / 2) * 50 + 1
    return f"""<div style="height: 48px; width: 48px; background-color: white; position: absolute;
            top: {y}; left: {x}"></div>"""

def display_path(path: list[Position], color="rgba(145,60,90, 0.3)"):
    render = "<div class='path'>"
    length = len(path)
    for index in range(0, length):
        # render += div_cell(path[index], color)
        if index > 0 and index < length:
            # pass
            render += hide_divider(path[index-1], path[index], index)
    return render + "</div>"

def generate_random_position(size: int):
    return Position(randrange(0, size - 1), randrange(0, size - 1))

def generate_random_paths(size: int):
    start = generate_random_position(size)
    end = generate_random_position(size)
    _moves_needed = moves_needed(start, end)
    while _moves_needed < int(size) or start.x + start.y < end.x + end.y:
        end = generate_random_position(size)
        _moves_needed = moves_needed(start, end)
    return generate_path(start, end, size)

class Image():
    START = "https://images.template.net/102134/racing-start-flag-clipart-0osxw.jpg"
    TREASURE = "https://cdn-icons-png.flaticon.com/512/2374/2374884.png"
    END =  "https://cdn-icons-png.flaticon.com/512/1986/1986876.png"

def display_image(position: Position, image: str):
    return f"""
        <div style="height: 48px; width: 48px; position: absolute; top: {position.y * 50}; left: {position.x * 50}; 
        background-size: cover; background: no-repeat center/85% url('{image}')">
            </div>
    """



@app.route("/")
def hello_world():

    size = 10
    start_possition = Position(0,0)
    out_position = Position(size-1, size-1)
    path = generate_path(start_possition, out_position, size)
    treasur_position = generate_random_position(size) 
    treasur_path = generate_path(start_possition, treasur_position, size)
    
    random_paths = ""
    for i in range(0, size - 1):
        random_paths +=  display_path(generate_path(generate_random_position(size), generate_random_position(size), size))
    return  show_maze(size) + display_path(treasur_path) + display_path(path, "grey") + random_paths + display_image(treasur_position, Image.TREASURE) + display_image(start_possition, Image.START) + display_image(out_position, Image.END)


