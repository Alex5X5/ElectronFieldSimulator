import tkinter
import random
import math


class Field:
    MAX_LIFETIME: int = 20
    INITIAL_FIELD_STRENGTH: float = 10.0
    LIGHT_SPEED: float = 0.7
    FIELD_DECAY: float = 0.9

    def __init__(self, x: int, y: int, row: int, column: int):
        self.x = x
        self.y = y
        self.row = row
        self.column = column
        self.lifetime = 0
        self.alive:bool = True

    @property
    def radius(self):
        return self.lifetime * Field.LIGHT_SPEED

    def tick(self, rects):
        self.lifetime += 1
        if self.lifetime>Field.MAX_LIFETIME:
            self.alive = False
        if not self.alive:
            return
        for row in rects:
            for rect in row:
                delta_x = self.row - rect.row
                delta_y = self.column - rect.column
                dist = math.sqrt(delta_x * delta_x + delta_y * delta_y)
                if dist <= self.radius:
                    # add = Field.INITIAL_FIELD_STRENGTH / ( self.radius * self.radius * Field.FIELD_DECAY )
                    # print(add)
                    dist_ = min(max(dist, 0.01), 10.0)
                    rect.intensity += Field.INITIAL_FIELD_STRENGTH / (dist_ * dist_ * Field.FIELD_DECAY)


class Rect:
    
    def __init__(self, x, y, row:int, column:int, width, height, canvas, color=(100, 100, 100)):
        self.__canvas = canvas
        self.__x:int = x
        self.__y:int = y
        self.row = row
        self.column = column
        self.__width:int = width
        self.__height:int = height
        self.__intensity:float = 0.0
        self.__color = color
        self.__handle:int = self.__canvas.create_rectangle(self.x, self.y, self.width, self.height, width=0, fill=self.color_hex)
    
    def __str__(self):
        return f"Rect[x:{self.x} y:{self.y} w:{self.width}, h:{self.height}, i:{self.intensity}]"
    
    @property
    def x(self) -> int:
        return self.__x
    
    @x.setter
    def x(self, value):
        self.__x = value
    
    @property
    def x2(self) -> int:
        return self.__x + self.__width
    
    @property
    def y(self) -> int:
        return self.__y
    
    @y.setter
    def y(self, value):
        self.__y = value
    
    @property
    def y2(self) -> int:
        return self.__y + self.__height
    
    @property
    def width(self) -> int:
        return self.__width
    
    @width.setter
    def width(self, value):
        self.__width = value
    
    @property
    def height(self) -> int:
        return self.__height
    
    @height.setter
    def height(self, value):
        self.__height = value
    
    @property
    def color(self) -> tuple[int, int, int]:
        return self.__color
    
    @color.setter
    def color(self, value):
        self.__color = value
    
    @property
    def color_hex(self) -> str:
        return "#%02x%02x%02x" % self.color
    
    @property
    def intensity(self) -> float:
        return self.__intensity
    
    @intensity.setter
    def intensity(self, value):
        value_ = min(10.0, max(0.01, float(value)))
        self.__intensity = value_
        col:float = 1.0 - 1.0 / ( value_ / 10.0 + 1.0)
        col_inv = 1.0 - col
        red = int(255 * col)
        green = int(255 * col_inv)
        blue = int(0)
        print(f"setting color to {col} {col_inv}")
        self.color=(red, green, blue)
    
    def mesh(self):
        self.__canvas.coords(self.__handle, self.x, self.y, self.x2, self.y2)
        self.__canvas.itemconfigure(self.__handle, fill=self.color_hex)


class CustomCanvas(tkinter.Canvas):

    REFRESH_RATE:int = 30
    REFRESH_INTERVAL:int = int(1000/REFRESH_RATE)
    
    @property
    def rows(self) -> int:
        return 50
    
    @property
    def columns(self) -> int:
        return 50
        
    @property
    def width(self) -> int:
        return self.winfo_width()
    
    @property
    def height(self) -> int:
        return self.winfo_height()
    
    @property
    def segment_width(self) -> int:
        return int(self.width / self.columns)
    
    @property
    def segment_height(self) -> int:
        return int(self.height / self.rows)
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rectangles:list[list[Rect]] = []
        self.fields:list[Field] = []
        
        self.is_left_down:bool = False
        self.is_right_down:bool = False
        
        self.__mouse_x:int = 0
        self.__mouse_y:int = 0
        
        self.bind('<ButtonPress-1>', self.on_left_mouse_down)
        self.bind('<ButtonRelease-1>', self.on_left_mouse_up)
        self.bind('<Motion>', self.on_mouse_moved)
        self.load()
        self.after(CustomCanvas.REFRESH_INTERVAL, self.loop)
    
    def get_rect_at_pos(self, x:int, y:int):
        column = int(math.floor(x / self.segment_width))
        row = int(math.floor(y / self.segment_height))
        if row < 0:
            return None
        if row > len(self.rectangles) - 1:
            return None
        if column < 0:
            return None
        if column > len(self.rectangles[row]) - 1:
            return None
        return self.rectangles[row][column]
    
    def on_left_mouse_down(self, event):
        self.is_left_down = True
        
    def on_left_mouse_up(self, event):
        self.is_left_down = False
    
    def on_mouse_moved(self, event):
        self.__mouse_x = event.x
        self.__mouse_y = event.y
        
    def load(self):
        print("load!") 
        for row in range(self.rows):
            self.rectangles.append([])
            for column in range(self.columns):
                self.rectangles[row].append(Rect(50, 50, row, column, 50, 50, self, (100, 100, 100)))
    
    def logic_loop(self):
        if self.is_left_down:
            rect = self.get_rect_at_pos(self.__mouse_x, self.__mouse_y)
            if rect.__class__ == Rect:
                self.fields.append(Field(rect.x, rect.y, rect.row, rect.column))
        for row in self.rectangles:
            for rect in row:
                rect.intensity = 0.0
        for field in self.fields:
            field.tick(self.rectangles)
        for field in filter(lambda x: not x.alive,self.fields):
            self.fields.remove(field)
    
    def graphics_loop(self):
        for row_index, row in enumerate(self.rectangles):
            for column_index, rect in enumerate(row):
                rect.x = column_index * self.segment_width
                rect.y = row_index * self.segment_height
                rect.width = self.segment_width
                rect.height = self.segment_height
                rect.mesh()

    #runs the simulation and updates the gui
    #periodically called by the canvas
    def loop(self):
        self.logic_loop()
        self.graphics_loop()
        self.after(CustomCanvas.REFRESH_INTERVAL, self.loop)


root:tkinter.Tk = tkinter.Tk()
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
canvas = CustomCanvas(root, width=600, height=600)
canvas.grid(row=0, column=0, sticky="nswe")
canvas.pack()

root.mainloop()
