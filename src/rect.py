import tkinter as tk
from typing import Iterable

class Rect:
    """
    A Rect class for tkinter

    You can construct a Rect object in the following ways:
    - `Rect(x, y, width, height)`: Creates a rectangle with its top-left corner at (x, y), a width of `width`, and a height of `height`.
    - `Rect((x, y), (width, height))`: Creates a rectangle with its top-left corner at (x, y), a width of `width`, and a height of `height`.
    - `Rect(rect_object)`: Creates a rectangle with the same position and dimensions as the given `rect` object.
    - `Rect(tk.Widget)`: Generates a Rect object for the specified Widget.


    Attributes:
        x, y(left, top): The x, y position of top and left side
        w, h(width, height): The width/height of the rect
        right: The x position of the right side
        bottom: The y position of the bottom side
        centerx, centery : The x/y position of the rect center
        center = (centerx, centery)
        size = (w, h)
        topleft = (left, top)
        topright = (right, top)
        bottomright = (right, bottom)
        bottomleft = (left, bottom)
        midleft = (left, centery)
        midright = (right, centery)
        midtop = (centerx, top)
        midbottom = (centerx, bottom)

    Examples:
        >>> r = Rect(10, 20, 30, 40)
        >>> r.x, r.y, r.w, r.h
        (10, 20, 30, 40)
        >>> r.left, r.top, r.right, r.bottom
        (10, 20, 40, 60)
        >>> r.width = 30
        >>> r.height = 30
        >>> r.size
        (30, 30)
        >>> r.topleft = (5, 10)
        >>> r.bottomright
        (35, 40)
        >>> r.center = (20, 30)
        >>> r.topleft
        (5, 15)
        >>> r2 = r.copy()
        >>> r2.move(10, 10) #doctest: +ELLIPSIS
        <Rect(10, 10, 55, 65) at ...>
        >>> r2.move_ip(15, 25)
        >>> r2.topleft
        (15, 25)
    """

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Rect):
            rect = args[0]
            self.x, self.y, self.w, self.h = rect.x, rect.y, rect.w, rect.h
        elif len(args) == 4:
            self.x, self.y, self.w, self.h = args
        elif len(args) == 2 and isinstance(args[0], Iterable) and isinstance(args[1], Iterable):
            self.x, self.y = args[0]
            self.w, self.h = args[1]
        elif len(args) == 1 and isinstance(args[0], tk.Widget):
            widget = args[0]
            self.x, self.y = widget.winfo_x(), widget.winfo_y()
            self.w, self.h = widget.winfo_reqwidth(), widget.winfo_reqheight()
        else:
            raise TypeError("Invalid arguments for Rect")

    @property
    def width(self):
        return self.w

    @width.setter
    def width(self, value):
        self.w = value

    @property
    def height(self):
        return self.h

    @height.setter
    def height(self, value):
        self.h = value

    @property
    def size(self):
        return self.w, self.h

    @size.setter
    def size(self, value):
        self.w, self.h = value[0], value[1]

    @property
    def left(self):
        return self.x

    @left.setter
    def left(self, value):
        self.x = value

    @property
    def top(self):
        return self.y

    @top.setter
    def top(self, value):
        self.y = value

    @property
    def right(self):
        return self.x + self.w

    @right.setter
    def right(self, value):
        self.x = value - self.w

    @property
    def bottom(self):
        return self.y + self.h

    @bottom.setter
    def bottom(self, value):
        self.y = value - self.h

    @property
    def centerx(self):
        return self.x + self.w // 2

    @centerx.setter
    def centerx(self, value):
        self.x = value - self.w // 2

    @property
    def centery(self):
        return self.y + self.h // 2

    @centery.setter
    def centery(self, value):
        self.y = value - self.h // 2

    @property
    def center(self):
        return self.centerx, self.centery

    @center.setter
    def center(self, value):
        cx, cy = value
        self.centerx = cx
        self.centery = cy

    @property
    def topleft(self):
        return self.left, self.top

    @topleft.setter
    def topleft(self, value):
        self.left, self.top = value[0], value[1]

    @property
    def topright(self):
        return self.right, self.top

    @topright.setter
    def topright(self, value):
        self.right, self.top = value[0], value[1]

    @property
    def bottomleft(self):
        return self.left, self.bottom

    @bottomleft.setter
    def bottomleft(self, value):
        self.left, self.bottom = value[0], value[1]

    @property
    def bottomright(self):
        return self.right, self.bottom

    @bottomright.setter
    def bottomright(self, value):
        self.right, self.bottom = value[0], value[1]

    @property
    def midleft(self):
        return self.left, self.centery

    @midleft.setter
    def midleft(self, value):
        self.left, self.centery = value[0], value[1]

    @property
    def midright(self):
        return self.right, self.centery

    @midright.setter
    def midright(self, value):
        self.right, self.centery = value[0], value[1]

    @property
    def midtop(self):
        return self.centerx, self.top

    @midtop.setter
    def midtop(self, value):
        self.centerx, self.top = value[0], value[1]

    @property
    def midbottom(self):
        return self.centerx, self.bottom

    @midbottom.setter
    def midbottom(self, value):
        self.centerx, self.bottom = value[0], value[1]

    def move(self, x: int, y: int) -> "Rect":
        """Move the rect and return the rect
        >>> r = Rect(10, 20, 30, 40)
        >>> r2 = r.move(5, 5)
        >>> r2.topleft
        (5, 5)
        >>> r2.bottomright
        (35, 45)
        """
        return Rect(x, y, self.w, self.h)

    def move_ip(self, x: int, y: int) -> None:
        """Move the rect in situ
        >>> r = Rect(10, 20, 30, 40)
        >>> r.move_ip(5, 5)
        >>> r.topleft
        (5, 5)
        """
        self.x, self.y = x, y

    def copy(self) -> "Rect":
        """Copy the self Rect
        >>> r = Rect(10, 20, 30, 40)
        >>> r2 = r.copy()
        >>> r2.topleft == r.topleft
        True
        >>> r2.bottomright == r.bottomright
        True
        """
        return Rect(self.x, self.y, self.w, self.h)

    def pack_widget(self, widget: tk.Widget) -> None:
        """
        Put the widget in the corresponding position on the Rect
        :param widget: The tk widget to be placed
        """
        widget.place(x=self.x, y=self.y)

    def __repr__(self):
        return f"<Rect({self.x}, {self.y}, {self.w}, {self.h}) at {hex(id(self))}>"

    def __eq__(self, other):
        if not isinstance(other, Rect):
            return False
        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h

    def __hash__(self):
        return hash((self.x, self.y, self.w, self.h))

    def __add__(self, other):
        if not isinstance(other, Rect):
            return NotImplemented
        return Rect(self.x + other.x, self.y + other.y, self.w + other.w, self.h + other.h)

    def __sub__(self, other):
        if not isinstance(other, Rect):
            return NotImplemented
        return Rect(self.x - other.x, self.y - other.y, self.w - other.w, self.h - other.h)

    def __mul__(self, scalar):
        return Rect(self.x * scalar, self.y * scalar, self.w * scalar, self.h * scalar)

    def __truediv__(self, scalar):
        return Rect(self.x / scalar, self.y / scalar, self.w / scalar, self.h / scalar)

    def __iadd__(self, other):
        if not isinstance(other, Rect):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        self.w += other.w
        self.h += other.h
        return self

    def __isub__(self, other):
        if not isinstance(other, Rect):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
        self.w -= other.w
        self.h -= other.h
        return self

    def __imul__(self, scalar):
        self.x *= scalar
        self.y *= scalar
        self.w *= scalar
        self.h *= scalar
        return self

    def __itruediv__(self, scalar):
        self.x /= scalar
        self.y /= scalar
        self.w /= scalar
        self.h /= scalar
        return self

if __name__ == "__main__":
    import doctest
    doctest.testmod()