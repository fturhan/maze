from position import Position


def display_image(position: Position, image: str):
    """Display the image above all element in the web page at the correct position"""
    return f"""
        <div style="height: 48px; width: 48px; position: absolute; top: {position.y * 50}; left: {position.x * 50}; 
        background-size: cover; background: no-repeat center/85% url('{image}')">
            </div>
    """


class Icon():
    START = "https://images.template.net/102134/racing-start-flag-clipart-0osxw.jpg"
    TREASURE = "https://cdn-icons-png.flaticon.com/512/2374/2374884.png"
    END = "https://cdn-icons-png.flaticon.com/512/1986/1986876.png"


# This function is used above the maze to hide the borders between 2 position to render the path


def hide_divider(position1: Position, position2: Position, n_item: int):
    x = ((position2.x + position1.x) / 2) * 50 + 2
    y = ((position2.y + position1.y) / 2) * 50 + 1
    return f"""<div style="height: 48px; width: 48px; background-color: white; position: absolute;
            top: {y}; left: {x}"></div>"""

# this function was used when debugging to highligh the real path created


def div_cell(position: Position, color: str = "rgba(200,200,140,0.5)"):
    return f"""
        <div style="height: 49px; width: 49px; background-color: {color}; border: solid 1px red; position: absolute; 
        top: {position.y * 50}; left: {position.x * 50}"> {position.x, position.y} </div>
    """


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
