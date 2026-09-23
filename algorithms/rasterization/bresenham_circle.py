def bresenham_circle(cx, cy, radius):
    points = []

    cx = round(cx)
    cy = round(cy)
    radius = round(abs(radius))

    x = 0
    y = radius
    decision = 3 - (2 * radius)

    while x <= y:
        symmetric_points = [
            (cx + x, cy + y),
            (cx - x, cy + y),
            (cx + x, cy - y),
            (cx - x, cy - y),
            (cx + y, cy + x),
            (cx - y, cy + x),
            (cx + y, cy - x),
            (cx - y, cy - x),
        ]

        for point in symmetric_points:
            if point not in points:
                points.append(point)

        if decision < 0:
            decision += (4 * x) + 6
        else:
            decision += (4 * (x - y)) + 10
            y -= 1

        x += 1

    return points