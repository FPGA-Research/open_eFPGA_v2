#!/usr/bin/env python3
import math
import re

#TODO: Improve this script so e.g. arguments can be given from the command line


# ignore_strings = ["BlockRAM", "cvxif_pau", "data_mem", "LUT4AB", "W_IO"]
# ignore_strings = ["BlockRAM", "cvxif_pau", "data_mem"]
ignore_strings = []

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) *  (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def clip_to_next_multiple(offset, pitch):
    """
    Clips the given offset to the next multiple of pitch.

    Parameters:
        offset (int): The offset value to be clipped.
        pitch (int): The pitch value (step size).

    Returns:
        int: The smallest multiple of pitch greater than or equal to the offset.
    """
    # if offset < 0 or pitch <= 0:
    if pitch <= 0:
        raise ValueError("Offset must be non-negative and pitch must be positive.")

    return ((offset + pitch - 1) // pitch) * pitch


def parse_coordinates(s):
    """
    Extracts the numeric coordinates following 'X' and 'Y' from a given string.

    Parameters:
        s (str): The input string containing the coordinates. The string must
                 contain 'X' and 'Y' exactly once, each followed by digits.

    Returns:
        tuple: A tuple (x, y), where:
            - x (int): The number following 'X'.
            - y (int): The number following 'Y'.

    Raises:
        ValueError: If the required format (X<number>Y<number>) is not found in the string.
    """
    match = re.search(r'X(\d+)Y(\d+)', s)
    if match:
        return int(match.group(1)), int(match.group(2))
    raise ValueError("No coordinates found in the string")

def read_tiles(file_path):
    """
    Reads the input file and extracts tile information into a list of dictionaries.

    Parameters:
        file_path (str): Path to the input file.

    Returns:
        list: A list of dictionaries with tile data (e.g., [{'name': value, 'x': value, ...}]).
    """
    tiles = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.strip() and not line.startswith(" "):
                parts = line.strip().split()
                name = parts[0]
                x, y = map(float, parts[1:3])  # Assuming x, y coordinates are the 2nd and 3rd columns
                flip = parts[3]
                tiles.append({'name': name, 'x': x, 'y': y, "flip": flip})
    return tiles

def print_tiles(tiles):
    """
    Prints the tile data in a readable format.

    Parameters:
        tiles (list): A list of dictionaries with tile data.
    """
    for tile in tiles:
        print(f"TILE name: {tile['name']} x: {tile['x']}, y: {tile['y']}, flip: {tile['flip']}")

def rotate_tiles(tiles, origin, angle_degrees):
    """
    Rotates all tiles around a given origin by a specified angle.

    Parameters:
        tiles (list): A list of dictionaries with tile data.
        origin (tuple): The (x, y) coordinates of the rotation origin.
        angle_degrees (float): The rotation angle in degrees.

    Returns:
        list: A list of rotated tile data.
    """
    # Convert the angle from degrees to radians
    angle = math.radians(angle_degrees)
    
    for tile in tiles:
        if any(ignore_string in tile["name"] for ignore_string in ignore_strings):
            continue
        flip = "N"
        x, y = rotate(origin, (tile["x"], tile["y"]), angle)
        x += 2000
        tile.update({"x": x, "y": y, "flip": flip})
    
    return tiles

def move_tiles(tiles, x_offset, y_offset):
    for tile in tiles:
        if any(ignore_string in tile["name"] for ignore_string in ignore_strings):
            continue
        x = tile["x"] + x_offset
        y = tile["y"] + y_offset
        tile.update({"x": x, "y": y})
    return tiles


def change_space_between_tiles_vertical(tiles, space, pdn_pitch, start_bot=True):
    """
    Adjusts the vertical space between tiles in each row.

    Parameters:
        tiles (list): A list of dictionaries containing tile data.
        space (float): The amount of space to add between tiles vertically.
        pdn_pitch (float): The vertical pitch of the PDN.
        start_top (bool): Whether to start adjusting from the topmost row (True)
                          or the bottommost row (False).

    Returns:
        list: The modified list of tiles with updated y-coordinates.
    """
    print(f"""\033[93mWARNING: Changed vertical space between tiles. Make sure to
        adjust the height of all supertiles by {space:.1f}!\033[0m""")
    # Group tiles by their y-coordinate (rows)
    rows = {}
    rams = {}
    for tile in tiles:
        if any(ignore_string in tile["name"] for ignore_string in ignore_strings):
            continue
        if "BlockRAM" in tile["name"]:
            ram = tile['y']
            if ram not in rams:
                rams[ram] = []
            rams[ram].append(tile)
        else:
            y = tile['y']
            if y not in rows:
                rows[y] = []
            rows[y].append(tile)
    sorted_rams = sorted(rams.keys(), reverse=not start_bot)

    y_offset_ram = 0
    # Handle RAM separately
    for ram in sorted_rams:
        ram_cell = rams[ram][0]
        if start_bot:
            ram_cell['y'] += y_offset_ram
        else:
            ram_cell['y'] -= y_offset_ram
        # The ram spans over two tiles, so it has to be shifted by two spaces
        #TODO: this is not entirely correct and should be read from the tiles
        #somehow instead
        y_offset_ram += 2*space

    sorted_rows = sorted(rows.keys(), reverse=not start_bot)
    # Update the horizontal spacing for each column
    y_offset = 0
    for row_y in sorted_rows:
        for tile in sorted(rows[row_y], key=lambda t: t['x']):
            if any(ignore_string in tile["name"] for ignore_string in ignore_strings):
                continue

            elif "N_term" in tile["name"] and start_bot:
                    n_term_offset = clip_to_next_multiple(y_offset, pdn_pitch)
                    tile['y'] += n_term_offset

            elif "S_term" in tile["name"] and not start_bot:
                    s_term_offset = clip_to_next_multiple(y_offset, pdn_pitch)
                    tile['y'] -= s_term_offset
            else:
                if start_bot:
                    tile['y'] += y_offset
                else:
                    tile['y'] -= y_offset

        y_offset += space  # Increment the x_offset by the space value

    return tiles


def change_space_between_tiles_horizontal(tiles, space, start_left=True, start=None, stop=None):
    """
    Adjusts the horizontal space between tiles in each column.

    Parameters:
        tiles (list): A list of dictionaries containing tile data.
        space (float): The amount of space to add between tiles horizontally.
        start_top (bool): Whether to start adjusting from the topleftmost column (True)
                          or the bottommost column (False).

    Returns:
        list: The modified list of tiles with updated x-coordinates.
    """
    # Group tiles by their x-coordinate (columns)
    column = {}
    for tile in tiles:
        if any(ignore_string in tile["name"] for ignore_string in ignore_strings):
            continue
        x = tile['x']
        if x not in column:
            column[x] = []
        column[x].append(tile)
    sorted_rows = sorted(column.keys(), reverse=not start_left)

    # Update the horizontal spacing for each column
    x_offset = 0
    reached_end = False
    reached_start = False
    for column_x in sorted_rows:
        for tile in sorted(column[column_x], key=lambda t: t['y']):
            if any(ignore_string in tile["name"] for ignore_string in ignore_strings):
                continue
            if stop != None and start != None:
                # BlockRAM has no XY fabric coordinate
                if "BlockRAM" in tile["name"]:
                    continue
                x_coord, _ = parse_coordinates(tile["name"])
                if start_left:
                    if x_coord < start:
                        continue
                    reached_start = True
                    if x_coord == stop:
                        reached_end = True
                else:
                    if x_coord > start:
                        continue
                    reached_start = True
                    if x_coord == stop:
                        reached_end = True

            if start_left:
                tile['x'] += x_offset
            else:
                tile['x'] -= x_offset

        if reached_start and not reached_end:
            x_offset += space  # Increment the x_offset by the space value

    return tiles

def write_tiles_to_file_flip(tiles, file_path):
    """
    Writes the tile data to a specified file.

    Parameters:
        tiles (list): A list of dictionaries with tile data.
        file_path (str): Path to the output file.
    """
    with open(file_path, "w") as f:
        for tile in tiles:
            if tile['flip'] == "N":
                line = f"{tile['name']} {tile['x']} {tile['y']} W\n"
            else:
                line = f"{tile['name']} {tile['x']} {tile['y']} {tile['flip']}\n"
            f.write(line)

def write_tiles_to_file(tiles, file_path):
    """
    Writes the tile data to a specified file.

    Parameters:
        tiles (list): A list of dictionaries with tile data.
        file_path (str): Path to the output file.
    """
    with open(file_path, "w") as f:
        for tile in tiles:
            line = f"{tile['name']} {tile['x']:.1f} {tile['y']:.1f} {tile['flip']}\n"
            f.write(line)

def main():
    #TODO: add these as command line parameters
    input_path = "../openlane/user_project_wrapper/macro_tmp_test.cfg"  # Path to your input configuration file
    output_path = "../openlane/user_project_wrapper/macro_manipulated_test.cfg"
    # origin = (2400, 245)  # Rotation origin (x, y)
    origin = (150, 50)  # Rotation origin (x, y)
    angle = -90  # Rotation angle in degrees
    x_offset = -113 
    y_offset = 0
    x_space_offset = 5
    y_space_offset = -3.5 
    pdn_pitch_vertical = 75

    # x_start = 6
    # x_stop = 5
    #
    # # Read the tiles from the input file
    tiles = read_tiles(input_path)
    #
    # tiles = change_space_between_tiles_horizontal(tiles, x_space_offset, False,
    #                                               x_start, x_stop)
    # x_start = 7
    # x_stop = 5
    # tiles = change_space_between_tiles_horizontal(tiles, x_space_offset, False,
                                                 # x_start, x_stop)
    # tiles = change_space_between_tiles_horizontal(tiles, x_space_offset, False,
    #                                         x_start, x_stop)
    move_tiles(tiles, x_offset, y_offset)
    # tiles = change_space_between_tiles_vertical(tiles, y_space_offset,
    #                                             pdn_pitch_vertical)

    # Rotate the tiles around the given origin
    # tiles = rotate_tiles(tiles, origin, angle)

    # Write the rotated tiles to the output file
    write_tiles_to_file(tiles, output_path)

if __name__ == "__main__":
    main()
