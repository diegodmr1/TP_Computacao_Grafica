def liang_barsky(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    dx = x2 - x1
    dy = y2 - y1

    p = [
        -dx,
        dx,
        -dy,
        dy
    ]

    q = [
        x1 - xmin,
        xmax - x1,
        y1 - ymin,
        ymax - y1
    ]

    u1 = 0.0
    u2 = 1.0

    for pi, qi in zip(p, q):

        if pi == 0:
            if qi < 0:
                return None
            continue

        u = qi / pi

        if pi < 0:
            if u > u2:
                return None

            if u > u1:
                u1 = u

        else:
            if u < u1:
                return None

            if u < u2:
                u2 = u

    clipped_x1 = x1 + u1 * dx
    clipped_y1 = y1 + u1 * dy

    clipped_x2 = x1 + u2 * dx
    clipped_y2 = y1 + u2 * dy

    return (
        clipped_x1,
        clipped_y1,
        clipped_x2,
        clipped_y2
    )