import flet as ft
import flet.canvas as cv

from qureed_gui.logic import ConnectionManager

CM = ConnectionManager()

class Canvas(ft.Container):
    def __init__(self):
        super().__init__()
        self.top=0
        self.left=0
        self.expand = True
        self.canvas=cv.Canvas()
        self.content=self.canvas
        CM.register_canvas(self)

    def clear_canvas(self):
        self.canvas.shapes = []
        self.update()

    def create_connection(self, loc1, loc2, adjust=True):
        if adjust:
            factor = 5000
        else:
            factor = 0
        point1 = [x + factor for x in loc1]
        point2 = [x + factor for x in loc2]
        strength = 0.9
        conn = cv.Path(
            [
                cv.Path.MoveTo(point1[0], point1[1]),
                cv.Path.CubicTo(
                    point1[0] + strength * (point2[0] - point1[0]),
                    point1[1],
                    point1[0] + (1 - strength) * (point2[0] - point1[0]),
                    point2[1],
                    point2[0],
                    point2[1],
                ),
            ],
            paint=ft.Paint(
                stroke_width=3,
                style=ft.PaintingStyle.STROKE,
            ),
        )

        self.canvas.shapes.append(conn)
        self.canvas.update()
    
        
