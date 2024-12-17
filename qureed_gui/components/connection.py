import flet as ft
import flet.canvas as cv


class Connection:

    def __init__(self, port_a, port_b, canvas, signal):
        self.port_a = port_a
        self.port_b = port_b
        self.signal = signal
        self._start_point = list(port_a.location)
        print("THE PORT CONNECTIONS")
        print(port_a.location)
        print(port_b.location)
        self._end_point = list(port_b.location)
        self.canvas = canvas
        

    def draw(self):
        self.connection = cv.Path(
            [
                cv.Path.MoveTo(self._start_point[0], self._start_point[1]),
                cv.Path.LineTo(
                    (self._start_point[0] + self._end_point[0]) / 2,
                    self._start_point[1],
                ),
                cv.Path.LineTo(
                    (self._start_point[0] + self._end_point[0]) / 2, self._end_point[1]
                ),
                cv.Path.LineTo(self._end_point[0], self._end_point[1]),
            ],
            paint=ft.Paint(
                stroke_width=3,
                style=ft.PaintingStyle.STROKE,
            ),
        )
        self.canvas.shapes.append(self.connection)
        self.canvas.update()

    def redraw(self):
        """
        Removes the connection path and creates a new on
        """
        self.canvas.shapes.remove(self.connection)
        self.draw()

    def move(self, port, delta_x, delta_y):
        """
        Handles the change of the connection
        when any device is moved
        """
        if port == self.port_a:
            self._start_point[0] = self._start_point[0] + delta_x
            self._start_point[1] = self._start_point[1] + delta_y
        if port == self.port_b:
            self._end_point[0] = self._end_point[0] + delta_x
            self._end_point[1] = self._end_point[1] + delta_y
        self.redraw()

    def remove(self):
        self.canvas.shapes.remove(self.connection)
        self.canvas.update()
