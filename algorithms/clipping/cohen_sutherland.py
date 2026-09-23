INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def compute_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE

    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT

    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP

    return code


def cohen_sutherland(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    while True:

        # Os dois pontos estão dentro da janela
        if code1 == 0 and code2 == 0:
            return x1, y1, x2, y2

        # Os dois pontos estão fora na mesma região
        if code1 & code2:
            return None

        code_out = code1 if code1 != 0 else code2

        if code_out & TOP:
            if y2 == y1:
                return None

            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax

        elif code_out & BOTTOM:
            if y2 == y1:
                return None

            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin

        elif code_out & RIGHT:
            if x2 == x1:
                return None

            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax

        else:
            if x2 == x1:
                return None

            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin

        if code_out == code1:
            x1 = x
            y1 = y
            code1 = compute_code(
                x1, y1,
                xmin, ymin,
                xmax, ymax
            )

        else:
            x2 = x
            y2 = y
            code2 = compute_code(
                x2, y2,
                xmin, ymin,
                xmax, ymax
            )