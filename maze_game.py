from flask import Flask, abort, request, send_file
from random import randrange

from selenium import webdriver
import re

from position import Position


def generate_move_correct_way(start: Position, end: Position, size: int, previous_pos: Position = None):
    """
    Return the next position which is the nearest to the end 
    """
    possibles_next = start.possible_next(size, previous_pos=previous_pos)
    current_moves_needed = start.moves_needed_to(end)
    possibles_next = list(
        filter(lambda n:
               n.moves_needed_to(end) < current_moves_needed,
               possibles_next)
    )
    next: Position
    _random = randrange(0, len(possibles_next))
    next = possibles_next[_random]

    return next


def generate_path(start: Position, end: Position, size: int) -> list[Position]:
    """
    Return a random path containing all the position from the start to the end
    """

    moves = [start]
    print("start, end")
    print(start, end)
    _moves_needed = start.moves_needed_to(end)
    for i in range(1, _moves_needed - 1):
        previous_pos = None
        if (i >= 2):
            previous_pos: Position = moves[i-2]
        move = generate_move_correct_way(
            moves[i-1], end, size, previous_pos=previous_pos)
        moves.append(move)
    moves.append(end)
    return moves


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


# this function was used when debugging to highligh the real path created
def div_cell(position: Position, color: str = "rgba(200,200,140,0.5)"):
    return f"""
        <div style="height: 49px; width: 49px; background-color: {color}; border: solid 1px red; position: absolute; 
        top: {position.y * 50}; left: {position.x * 50}"> {position.x, position.y} </div>
    """

# This function is used above the maze to hide the borders between 2 position to render the path


def hide_divider(position1: Position, position2: Position, n_item: int):
    x = ((position2.x + position1.x) / 2) * 50 + 2
    y = ((position2.y + position1.y) / 2) * 50 + 1
    return f"""<div style="height: 48px; width: 48px; background-color: white; position: absolute;
            top: {y}; left: {x}"></div>"""

# actually render the path with a list of position


def display_path(path: list[Position]):
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
    _moves_needed = start.moves_needed_to(end)

    # add a minimum of moves needed to create a valid path
    while _moves_needed < int(size) or start.x + start.y < end.x + end.y:
        end = generate_random_position(size)
        _moves_needed = start.moves_needed_to(end)
    return generate_path(start, end, size, size)


class Icon():
    START = "https://images.template.net/102134/racing-start-flag-clipart-0osxw.jpg"
    TREASURE = "https://cdn-icons-png.flaticon.com/512/2374/2374884.png"
    END = "https://cdn-icons-png.flaticon.com/512/1986/1986876.png"


def display_image(position: Position, image: str):
    """Display the image above all element in the web page at the correct position"""
    return f"""
        <div style="height: 48px; width: 48px; position: absolute; top: {position.y * 50}; left: {position.x * 50}; 
        background-size: cover; background: no-repeat center/85% url('{image}')">
            </div>
    """


app = Flask(__name__)


@app.route("/", methods=["POST"])
def generate_screenshot():
    # Primary route used to download the png file of the maze
    start_position, treasure_position, exit_position = transform_request(
        request.get_json())

    size_needed = exit_position.x * 60  # each cell is 50px

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Exécution sans affichage
    browser = webdriver.Chrome(options=options)
    browser.set_window_size(size_needed, size_needed)
    # request_data = request.get_json()

    # Accédez à la page Flask
    browser.get(
        f"http://127.0.0.1:5000/maze?start={str(start_position)}&treasure={str(treasure_position)}&exit={str(exit_position)}")

    # Prend une capture d'écran de la page
    image = browser.get_screenshot_as_png()
    with open("./maze_game.png", "wb") as file:
        file.write(image)

    # Ferme le navigateur Web
    browser.close()

    # Renvoie la capture d'écran
    return send_file("./maze_game.png", mimetype="image/png", as_attachment=True, download_name="maze_game.png")


def get_data(request_data, name: str) -> Position:
    """
    transform the request data "(x, y)" to a position Position(x, y)
    """
    data = request_data[name]
    args = re.findall("\d+", data)
    if len(args) != 2:
        abort(400, "The provided data is not correctly formatted ")
    pos = Position(*list(map(lambda a: int(a), args)))
    return pos


def transform_request(request_data) -> tuple[Position]:
    return get_data(request_data, "start"), get_data(request_data, "treasure"), get_data(request_data, "exit")


@app.route("/maze", methods=["GET"])
def hello_world():
    # Route used to test the maze and show it on a web page. arguments are in the url
    args = request.args
    # request_data = request.get_json()
    start_position, treasure_position, exit_position = transform_request(
        args)

    # size is determined by the exit position
    size = int(max([exit_position.x, exit_position.y])) + 1
    path = generate_path(start_position, exit_position, size)
    treasure_path = generate_path(
        start_position, treasure_position, size)
    random_paths = ""
    for i in range(0, size - 1):
        random_paths += display_path(generate_path(
            generate_random_position(size), generate_random_position(size), size))
    res = show_maze(size) + display_path(treasure_path) + display_path(path) + random_paths + \
        display_image(treasure_position, Icon.TREASURE) + display_image(start_position, Icon.START) + \
        display_image(exit_position, Icon.END)

    return res
