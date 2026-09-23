def flood_fill(
    start_x,
    start_y,
    get_color,
    set_color,
    fill_color,
    width,
    height,
):
    start_x = round(start_x)
    start_y = round(start_y)

    if (
        start_x < 0
        or start_x >= width
        or start_y < 0
        or start_y >= height
    ):
        return

    target_color = get_color(start_x, start_y)

    if target_color == fill_color:
        return

    stack = [(start_x, start_y)]
    visited = set()

    while stack:
        x, y = stack.pop()

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        if (x, y) in visited:
            continue

        visited.add((x, y))

        if get_color(x, y) != target_color:
            continue

        set_color(x, y, fill_color)

        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))