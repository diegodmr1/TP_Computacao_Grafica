def boundary_fill(
    start_x,
    start_y,
    get_color,
    set_color,
    boundary_colors,
    fill_color,
    width,
    height,
):
    start_x = round(start_x)
    start_y = round(start_y)

    if not (
        0 <= start_x < width
        and 0 <= start_y < height
    ):
        return

    stack = [(start_x, start_y)]
    visited = set()

    while stack:
        x, y = stack.pop()

        if not (
            0 <= x < width
            and 0 <= y < height
        ):
            continue

        if (x, y) in visited:
            continue

        visited.add((x, y))

        current_color = get_color(x, y)

        if current_color in boundary_colors:
            continue

        if current_color == fill_color:
            continue

        set_color(x, y, fill_color)

        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))