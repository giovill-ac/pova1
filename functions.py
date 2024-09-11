from enum import StrEnum
import math
import random
from typing import Optional, Tuple

OVERLAP_PENALTY = 100
WALL_PENALTY = 50
DOOR_PENALTY = 100
PENALTY_DISTANCE_MULTIPLIER = 10
NOT_FACE_TO_FACE_PENALTY = 100


class Orientation(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class FurnitureFront(StrEnum):
    SHORT_SIDE = "short_side"
    LONG_SIDE = "long_side"


class Furniture:
    def __init__(
        self,
        name: str,
        width: int,
        height: int,
        color: str,
        preferred_on_wall: bool = False,
        nearby_furniture: list = [],
        front=Optional[FurnitureFront],
    ):
        self.name = name
        self.width = width
        self.height = height
        self.color = color
        self.preferred_on_wall = preferred_on_wall
        self.nearby_furniture = nearby_furniture
        self.front = front


class Door:
    def __init__(
        self, name: str, pos: Tuple[int, int], length: int, is_horizontal: bool
    ):
        self.name = name
        self.pos = pos
        self.length = length
        self.is_horizontal = is_horizontal


def objective(state, furniture_dict, room_width, room_height, doors):
    """
    Objective function of the current furniture placement.
    The value is based on the distance of each furniture from the door and balcony,
    as well as overlaps between furniture, whether furniture is attached to a wall,
    and the distance between furniture and its nearby furniture.
    """
    energy = 0
    for i, (x, y, orientation) in enumerate(state):
        furniture_name = list(furniture_dict.keys())[i]
        furniture: Furniture = furniture_dict[furniture_name]
        # Check for overlaps
        for j, (x2, y2, orientation2) in enumerate(state):
            if i != j:
                furniture_name2 = list(furniture_dict.keys())[j]
                furniture2 = furniture_dict[furniture_name2]
                if furniture_overlaps(
                    furniture, furniture2, (x, y, orientation), (x2, y2, orientation2)
                ):
                    energy += OVERLAP_PENALTY
            # Penalty for furniture not attached to a wall
            if furniture.preferred_on_wall and not furniture_on_wall(
                furniture, (x, y, orientation), room_width, room_height
            ):
                energy += WALL_PENALTY
        # Penalty for furniture not near its nearby furniture
        for nearby_furniture_name in furniture.nearby_furniture:
            nearby_x, nearby_y, nearby_orientation = next(
                (x2, y2, orientation2)
                for j, (x2, y2, orientation2) in enumerate(state)
                if list(furniture_dict.keys())[j] == nearby_furniture_name
            )
            distance = furniture_distance(
                furniture,
                furniture_dict[nearby_furniture_name],
                (x, y, orientation),
                (nearby_x, nearby_y, nearby_orientation),
            )
            if distance > 0.5:
                energy += distance * PENALTY_DISTANCE_MULTIPLIER
            if not furniture_face_to_face(
                furniture,
                furniture_dict[nearby_furniture_name],
                (x, y, orientation),
                (nearby_x, nearby_y, nearby_orientation),
            ):
                energy += NOT_FACE_TO_FACE_PENALTY
        # Penalty for being in front of a door
        for door in doors:
            if door_furniture_overlap(door, furniture, (x, y), room_width, room_height):
                energy += DOOR_PENALTY
    return energy


def furniture_to_bbox(furniture, furniture_state):
    x, y, orientation = furniture_state
    fwidth, fheight = (furniture.width, furniture.height)
    front = furniture.front
    if orientation == Orientation.TOP or orientation == Orientation.BOTTOM:
        if front == FurnitureFront.SHORT_SIDE:
            width = min(fwidth, fheight)
            height = max(fwidth, fheight)
        elif front == FurnitureFront.LONG_SIDE:
            width = max(fwidth, fheight)
            height = min(fwidth, fheight)
        else:
            width = fwidth
            height = fheight
    elif orientation == Orientation.LEFT or orientation == Orientation.RIGHT:
        if front == FurnitureFront.SHORT_SIDE:
            width = max(fwidth, fheight)
            height = min(fwidth, fheight)
        elif front == FurnitureFront.LONG_SIDE:
            width = min(fwidth, fheight)
            height = max(fwidth, fheight)
        else:
            width = fwidth
            height = fheight
    elif orientation is None:
        width = fwidth
        height = fheight
    else:
        raise ValueError("Invalid orientation")
    return (x, y, x + width, y + height)


def bbox_distance(bbox1, bbox2):
    # Unpack bounding boxes
    x1_1, y1_1, x2_1, y2_1 = bbox1  # bbox1 coordinates
    x1_2, y1_2, x2_2, y2_2 = bbox2  # bbox2 coordinates

    # Calculate horizontal distance
    if x2_1 < x1_2:  # bbox1 is to the left of bbox2
        dx = x1_2 - x2_1
    elif x2_2 < x1_1:  # bbox1 is to the right of bbox2
        dx = x1_1 - x2_2
    else:  # they overlap horizontally
        dx = 0

    # Calculate vertical distance
    if y2_1 < y1_2:  # bbox1 is above bbox2
        dy = y1_2 - y2_1
    elif y2_2 < y1_1:  # bbox1 is below bbox2
        dy = y1_1 - y2_2
    else:  # they overlap vertically
        dy = 0

    # Euclidean distance
    distance = math.sqrt(dx**2 + dy**2)
    return distance


def furniture_distance(furniture1: Furniture, furniture2: Furniture, state1, state2):
    """
    Calculate the distance between two pieces of furniture.
    """
    bbox1 = furniture_to_bbox(furniture1, state1)
    bbox2 = furniture_to_bbox(furniture2, state2)
    return bbox_distance(bbox1, bbox2)


def furniture_face_to_face_one_orientation(bbox1, bbox2, orientation1):
    """
    Check if two pieces of furniture are face to face, only the first one has an orientation.
    """
    if orientation1 == Orientation.TOP:
        # bbox1 is on below of bbox2
        return bbox1[3] <= bbox2[1]
    elif orientation1 == Orientation.BOTTOM:
        # bbox1 is above bbox2
        return bbox1[1] >= bbox2[3]
    elif orientation1 == Orientation.LEFT:
        # bbox1 is to the left of bbox2
        return bbox1[2] <= bbox2[0]
    elif orientation1 == Orientation.RIGHT:
        # bbox1 is to the right of bbox2
        return bbox1[0] >= bbox2[2]


def furniture_face_to_face_both_orientation(bbox1, bbox2, orientation1, orientation2):
    if orientation1 == Orientation.TOP and orientation2 == Orientation.BOTTOM:
        # bbox1 is below bbox2
        return bbox1[3] <= bbox2[1]
    elif orientation1 == Orientation.BOTTOM and orientation2 == Orientation.TOP:
        # bbox1 is above bbox2
        return bbox1[1] >= bbox2[3]
    elif orientation1 == Orientation.LEFT and orientation2 == Orientation.RIGHT:
        # bbox1 is to the left of bbox2
        return bbox1[2] <= bbox2[0]
    elif orientation1 == Orientation.RIGHT and orientation2 == Orientation.LEFT:
        # bbox1 is to the right of bbox2
        return bbox1[0] >= bbox2[2]
    else:
        return False  # The two pieces of furniture are not face to face


def furniture_face_to_face(
    furniture1: Furniture, furniture2: Furniture, state1, state2
):
    """
    Check if two pieces of furniture are not face to face.
    """
    bbox1 = furniture_to_bbox(furniture1, state1)
    bbox2 = furniture_to_bbox(furniture2, state2)

    orientation1 = state1[2]
    orientation2 = state2[2]

    if orientation1 == None and orientation2 == None:
        return True
    elif orientation1 is not None and orientation2 == None:
        return furniture_face_to_face_one_orientation(bbox1, bbox2, orientation1)
    elif orientation1 == None and orientation2 is not None:
        return furniture_face_to_face_one_orientation(bbox2, bbox1, orientation2)
    else:
        return furniture_face_to_face_both_orientation(
            bbox1, bbox2, orientation1, orientation2
        )


def move_furniture(state, furniture, index, room_width, room_height):
    """
    Randomly move a piece of furniture to a new position.
    """

    x = random.randint(0, room_width - furniture.width)
    y = random.randint(0, room_height - furniture.height)
    state[index] = (x, y, state[index][2])
    return state


def rotate_furniture(state, furniture, index, room_width, room_height):
    """
    Randomly rotate a piece of furniture to a new orientation.
    """
    x, y, orientation = state[index]
    new_orientation = random.choice([o for o in Orientation if o != orientation])
    state[index] = (x, y, new_orientation)
    return state


def room_change(state, furniture_dict, room_width, room_height, doors):
    """
    Randomly select a piece of furniture and move it to a new position or change its orientation.
    """
    furniture_names = list(furniture_dict.keys())
    index = random.randint(0, len(furniture_names) - 1)
    furniture_name = furniture_names[index]
    furniture: Furniture = furniture_dict[furniture_name]
    if random.random() < 0.5 and (
        furniture.front is not None or furniture.width != furniture.height
    ):  # Change orientation if it's not a square or it has a front
        return rotate_furniture(state, furniture, index, room_width, room_height)
    # Move furniture
    return move_furniture(state, furniture, index, room_width, room_height)


def generate_initial_state(furniture_dict, room_width, room_height):
    """
    Generate an initial random placement of the furniture in the room.
    """
    state = []
    for furniture in furniture_dict.values():
        x = random.randint(0, room_width - furniture.width)
        y = random.randint(0, room_height - furniture.height)
        if furniture.front:
            state.append((x, y, random.choice(["top", "bottom"])))
        else:
            state.append((x, y, None))
    return state


def furniture_overlaps(furniture1: Furniture, furniture2: Furniture, state1, state2):
    """
    Check if two pieces of furniture overlap.
    """
    bbox1 = furniture_to_bbox(furniture1, state1)
    bbox2 = furniture_to_bbox(furniture2, state2)
    return bbox_overlaps(bbox1, bbox2)


def door_furniture_overlap(
    door: Door, furniture: Furniture, coord, room_width, room_height
):
    # Unpack door coordinates
    x, y = door.pos
    length = door.length
    if door.is_horizontal:
        if y == 0:
            bbox_door = (x, y, x + length, y + length)
        else:
            bbox_door = (x, y - length, x + length, y)
    else:
        if x == 0:
            bbox_door = (x, y, x + length, y + length)
        else:
            bbox_door = (x - length, y, x, y + length)

    # Unpack furniture coordinates
    fx, fy = coord
    bbox_furniture = (fx, fy, fx + furniture.width, fy + furniture.height)
    return bbox_overlaps(bbox_door, bbox_furniture)


def furniture_on_wall(furniture: Furniture, state, room_width, room_height):
    x, y, orientation = state
    bbox = furniture_to_bbox(furniture, state)
    x1, y1, x2, y2 = bbox
    # Back has to be on the wall
    if orientation == Orientation.TOP:
        return y1 == 0
    elif orientation == Orientation.BOTTOM:
        return y2 == room_height
    elif orientation == Orientation.LEFT:
        return x2 == room_width
    elif orientation == Orientation.RIGHT:
        return x1 == 0


def bbox_overlaps(bbox1, bbox2):
    # Unpack bounding boxes
    x1_1, y1_1, x2_1, y2_1 = bbox1  # bbox1 coordinates
    x1_2, y1_2, x2_2, y2_2 = bbox2  # bbox2 coordinates

    # Check if the two bounding boxes overlap
    if x2_1 <= x1_2 or x2_2 <= x1_1 or y2_1 <= y1_2 or y2_2 <= y1_1:
        return False
    return True
