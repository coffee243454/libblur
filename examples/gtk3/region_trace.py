import cairo
from dataclasses import dataclass


@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int

# A way to get the blur region from a widget with cairo
def trace_widget_regions(widget, accuracy: int = 10, alpha_threshold: int = 10) -> list[Rect]:
    alloc = widget.get_allocation()
    w, h = alloc.width, alloc.height

    if w <= 0 or h <= 0:
        return []

    surface = cairo.ImageSurface(cairo.Format.ARGB32, w, h)
    cr = cairo.Context(surface)
    widget.draw(cr)
    data   = surface.get_data()
    stride = surface.get_stride()
    raw: list[Rect] = []
    for y in range(0, h, accuracy):
        step_h = min(accuracy, h - y)
        x = 0
        while x < w:
            alpha = data[y * stride + x * 4 + 3]
            if alpha > alpha_threshold:
                start_x = x
                while x < w and data[y * stride + x * 4 + 3] > alpha_threshold:
                    x += 1
                raw.append(Rect(start_x, y, x - start_x, step_h))
            else:
                x += 1
    merged: list[Rect] = []
    for rect in raw:
        found = False
        for m in reversed(merged):
            if (m.x == rect.x and
                m.width == rect.width and
                m.y + m.height == rect.y):
                m.height += rect.height
                found = True
                break
        if not found:
            merged.append(Rect(rect.x, rect.y, rect.width, rect.height))

    return merged


def trace_widget_regions_as_dicts(widget, accuracy: int = 10,
                                  alpha_threshold: int = 10) -> list[dict]:
    return [
        {"x": r.x, "y": r.y, "width": r.width, "height": r.height}
        for r in trace_widget_regions(widget, accuracy, alpha_threshold)
    ]