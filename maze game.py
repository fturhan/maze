# import enum
from io import BytesIO
from flask import Flask, make_response, render_template, render_template_string, send_file
from random import randrange

from PIL import Image
from selenium import webdriver


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

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


def moves_needed(from_position: Position, to_position: Position):
    """
    Calculate the difference between the 2 position
    """
    x = abs(to_position.x - from_position.x)
    y = abs(to_position.y - from_position.y)
    return y + x + 1


def generate_move_correct_way(start: Position, end: Position, size: int, previous_pos: Position = None):
    """
    Return the next position which is the nearest to the end 
    """
    possibles_next = start.possible_next(size, previous_pos=previous_pos)
    current_moves_needed = moves_needed(start, end)
    possibles_next = list(
        filter(lambda n:
               moves_needed(n, end) < current_moves_needed,
               possibles_next)
    )
    next: Position
    _random = randrange(0, len(possibles_next))
    next = possibles_next[_random]

    return next


def generate_path(start: Position, end: Position, size: int, variance: int) -> list[Position]:
    """
    Return a random path containing all the position from the start to the end
    """

    moves = [start]
    _moves_needed = moves_needed(start, end)
    for i in range(1, _moves_needed - 1):
        previous_pos = None
        if (i >= 2):
            previous_pos: Position = moves[i-2]
        move = generate_move_correct_way(
            moves[i-1], end, size, previous_pos=previous_pos)
        moves.append(move)
    moves.append(end)
    return moves


app = Flask(__name__)


def show_maze(size):
    """
    Print the maze on a web page 
    """
    final_maze = "<div id='maze'>"
    for x in range(0, size):
        for y in range(0, size):
            final_maze += f"""
                <div style="border: solid 1px; height: 50px; width: 50px; position: absolute; top: {y * 50}; left: {x * 50}"></div>
            """
    return final_maze + '/<div>'


def div_cell(position: Position, color: str = "rgba(200,200,140,0.5)"):
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
    return generate_path(start, end, size, size)


class Icon():
    START = "https://images.template.net/102134/racing-start-flag-clipart-0osxw.jpg"
    TREASURE = "https://cdn-icons-png.flaticon.com/512/2374/2374884.png"
    END = "https://cdn-icons-png.flaticon.com/512/1986/1986876.png"


def display_image(position: Position, image: str):
    return f"""
        <div style="height: 48px; width: 48px; position: absolute; top: {position.y * 50}; left: {position.x * 50}; 
        background-size: cover; background: no-repeat center/85% url('{image}')">
            </div>
    """


@app.route("/")
def generate_screenshot():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Exécution sans affichage
    browser = webdriver.Chrome(options=options)

    # Accédez à la page Flask
    browser.get("http://127.0.0.1:5000/maze")

    # Prend une capture d'écran de la page
    image = browser.get_screenshot_as_png()
    with open("maze.png", "wb") as file:
        file.write(image)

    # Ferme le navigateur Web
    browser.close()

    # Renvoie la capture d'écran
    return send_file("./maze.png", mimetype="image/png", as_attachment=True, download_name="maze_game.png")


@app.route("/maze")
def hello_world():

    size = 10
    variance = size
    start_possition = generate_random_position(size)  # Position(0, 9)
    out_position = generate_random_position(size)  # Position(size-1, 0)
    path = generate_path(start_possition, out_position, size, variance)
    treasur_position = generate_random_position(size)
    treasur_path = generate_path(
        start_possition, treasur_position, size, variance)
    random_paths = ""
    # for i in range(0, size - 1):
    # random_paths += display_path(generate_path(
    # generate_random_position(size), generate_random_position(size), size))
    res = show_maze(size) + display_path(treasur_path) + display_path(path, "grey") + display_image(treasur_position,
                                                                                                    Icon.TREASURE) + display_image(start_possition, Icon.START) + display_image(out_position, Icon.END)

    return res
