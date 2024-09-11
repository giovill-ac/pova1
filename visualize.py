import matplotlib.pyplot as plt

from room.functions import FurnitureFront, Orientation, furniture_to_bbox


def xyxy_to_xywh(bbox):
    """
    Convert bounding box from (x1, y1, x2, y2) format to (x, y, width, height) format.
    """
    x1, y1, x2, y2 = bbox
    return x1, y1, x2 - x1, y2 - y1


def print_room(furniture_dict, state):
    """
    Print the room layout coordinates
    """

    print("\nFurnitures layout:")
    for i, (x, y, orientation) in enumerate(state):
        furniture_name = list(furniture_dict.keys())[i]
        furniture = furniture_dict[furniture_name]
        print(furniture.name, (x, y), orientation)

def draw_room(room_width, room_height, doors, furniture_dict, state):
    """
    Draw the room layout with the final furniture placements.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw the room
    ax.add_patch(plt.Rectangle((0, 0), room_width, room_height, fill=False, edgecolor='black', linewidth=2))

    DOOR_WIDTH = 0.25
    DOOR_COLOR = 'lightgreen'

    # Draw the doors
    for door in doors:
        x, y = door.pos
        if door.is_horizontal:
            if y == 0:      
                ax.add_patch(plt.Rectangle((x, y), door.length, DOOR_WIDTH, facecolor=DOOR_COLOR, edgecolor='black', linewidth=1))
                ax.text(x + door.length/2, y + DOOR_WIDTH / 2, door.name, ha='center', va='center', fontsize=8)
            else:
                ax.add_patch(plt.Rectangle((x, y - DOOR_WIDTH), door.length, DOOR_WIDTH, facecolor=DOOR_COLOR, edgecolor='black', linewidth=1))
                ax.text(x + door.length/2, y - DOOR_WIDTH / 2, door.name, ha='center', va='center', fontsize=8)
        else:
            if x == 0:
                ax.add_patch(plt.Rectangle((x, y), DOOR_WIDTH, door.length, facecolor=DOOR_COLOR, edgecolor='black', linewidth=1))
                ax.text(x + DOOR_WIDTH / 2, y + door.length/2, door.name, ha='center', va='center', fontsize=8, rotation=90)
            else:
                ax.add_patch(plt.Rectangle((x - DOOR_WIDTH, y), DOOR_WIDTH, door.length, facecolor=DOOR_COLOR, edgecolor='black', linewidth=1))
                ax.text(x - DOOR_WIDTH / 2, y + door.length/2, door.name, ha='center', va='center', fontsize=8, rotation=90)

    print("-------")
    # Draw the furniture
    for i, (x, y, orientation) in enumerate(state):
        furniture_name = list(furniture_dict.keys())[i]
        furniture = furniture_dict[furniture_name]
        bbox = furniture_to_bbox(furniture, (x, y, orientation))
        x, y, w, h = xyxy_to_xywh(bbox)
        
        # print(furniture.name, "xy:", (x, y), "owh", (furniture.width, furniture.height), "wh", (w, h), "or:", orientation, "side:", furniture.front)
        
        # Draw the furniture
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=furniture.color, edgecolor='black', linewidth=1))
        
        # Draw a line to indicate the front of the furniture
        LINE_COLOR = 'yellow'
        if furniture.front is not None:
            if orientation == Orientation.LEFT:
                ax.plot([x, x], [y, y + h], color=LINE_COLOR, linewidth=2, linestyle=':')
            elif orientation == Orientation.RIGHT:
                ax.plot([x + w, x + w], [y, y + h], color=LINE_COLOR, linewidth=2, linestyle=':')
            elif orientation == Orientation.BOTTOM:
                ax.plot([x, x + w], [y, y], color=LINE_COLOR, linewidth=2, linestyle=':')
            elif orientation == Orientation.TOP:
                ax.plot([x, x + w], [y + h, y + h], color=LINE_COLOR, linewidth=2, linestyle=':')
        
        # Draw the furniture name
        ax.text(x + w/2, y + h/2, furniture.name, ha='center', va='center', fontsize=8)

    # Set the axis limits and aspect ratio
    ax.set_xlim(0, room_width)
    ax.set_ylim(0, room_height)
    ax.set_aspect('equal')
    ax.set_title('Final Furniture Placement')
    plt.show()
    plt.savefig("final_furniture_placement.png")