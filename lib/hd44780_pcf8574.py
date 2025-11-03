__version__ = "1.0.0"

from ticle import (
    utime,
    micropython,
)
from machine import I2C

class HD44780_PCF8574:
    def __init__(self, scl:int, sda:int, *, addr:int=0x3f, freq:int=400_000, cols:int=16, rows:int=2):
        self.__i2c = I2C(sda=sda, scl=scl, freq=freq)

        self.__addr = addr

        self.__cols = int(cols)
        self.__rows = int(rows)

        self.__display = True
        self.__cursor = False
        self.__blink = False
        self.__x = 0
        self.__y = 0
        self.__dwidth = 40  # DDRAM width
        self.__shift = 0
        self.__ax = 0
        self.__ay = 0
        self.__tx4 = bytearray(4)

        self.__gw = self.__cols * 5
        self.__gh = self.__rows * 8
        self.__gfb = bytearray(self.__gw * self.__gh)

        self.__i2c.writeto(self.__addr, bytes([0x00]))
        utime.sleep_us(20_000)
        for _ in range(3):
            self.__i2c.writeto(self.__addr, bytes((0x30 | 0x04, 0x30)))  # EN pulse packed
            utime.sleep_us(5_000)
        self.__i2c.writeto(self.__addr, bytes((0x20 | 0x04, 0x20)))
        utime.sleep_us(1_000)

        self.__cmd(0x20 | (0x08 if self.__rows > 1 else 0x00))
        self.set_display(False)
        self.clear()
        self.__cmd(0x04 | 0x02)
        
        self.set_display(True, cursor=False, blink=False)

    def deinit(self):
        self.set_display(cursor=False, blink=False)
        self.clear()

    def __write(self, data: int, rs: int):
        b0 = ((rs & 0x01) | (data & 0xF0))
        b1 = ((rs & 0x01) | ((data & 0x0F) << 4))
        tx = self.__tx4
        tx[0] = b0 | 0x04
        tx[1] = b0
        tx[2] = b1 | 0x04
        tx[3] = b1
        self.__i2c.writeto(self.__addr, tx)

        if rs == 0 and data <= 3:
            utime.sleep_us(5_000)

    def __cmd(self, c: int):
        self.__write(c & 0xFF, 0)

    def __data(self, d: int):
        self.__write(d & 0xFF, 0x01)

    def __move_to(self, x:int, y:int):
        ROW_ADDR = (0x00, 0x40, 0x14, 0x54)
        x = max(0, min(self.__cols-1, int(x)))
        y = max(0, min(self.__rows-1, int(y)))
        self.__x, self.__y = x, y
        real_col = (self.__shift + x) % self.__dwidth
        pos = 0x80 | (ROW_ADDR[y] + real_col)
        self.__cmd(pos)

    @micropython.native
    def clear(self):
        self.__cmd(0x01)
        self.__x = self.__ax = 0
        self.__y = self.__ay = 0
        self.__shift = 0

    def home(self):
        self.__cmd(0x02)
        self.__x = self.__ax = 0
        self.__y = self.__ay = 0
        self.__shift = 0

    def set_display(self, on: bool|None = None, cursor: bool|None = None, blink: bool|None = None):
        if on is None: on = self.__display
        else: self.__display = on
        if cursor is None: cursor = self.__cursor
        else: self.__cursor = cursor
        if blink is None: blink = self.__blink
        else: self.__blink = blink
        self.__cmd(0x08 | (0x04 if on else 0) | (0x02 if cursor else 0) | (0x01 if blink else 0))

    def text(self, text: str|bytes, x: int|None = None, y: int|None = None, *, wrap: bool = False):
        ROW_ADDR = (0x00, 0x40, 0x14, 0x54)
        if isinstance(text, (bytes, bytearray)):
            text = text.decode()
        if x is not None and y is not None:
            self.__move_to(x, y)
            if not wrap:
                self.__ay = y
                self.__ax = (self.__shift + x) % self.__dwidth
        for ch in str(text):
            if ch == '\n':
                self.__ay = (self.__ay + 1) % self.__rows
                self.__ax = 0
                self.__move_to(0, self.__ay)
                continue
            oc = ord(ch)
            if wrap:
                self.__data(oc)
                self.__x += 1
                if self.__x >= self.__cols:
                    self.__x = 0
                    self.__y = (self.__y + 1) % self.__rows
                    self.__move_to(self.__x, self.__y)
            else:
                if self.__ax < self.__dwidth:
                    real_col = self.__ax % self.__dwidth
                    pos = 0x80 | (ROW_ADDR[self.__ay] + real_col)
                    self.__cmd(pos)
                    self.__data(oc)
                    if self.__ax < self.__cols:
                        self.__x = self.__ax; self.__y = self.__ay
                    else:
                        self.__x = self.__cols - 1; self.__y = self.__ay
                    self.__ax += 1
                else:
                    break

    def scroll_left(self, n:int=1):
        for _ in range(max(1, n)):
            self.__cmd(0x10 | 0x08 | 0x00)
            self.__shift = (self.__shift + 1) % self.__dwidth

    def scroll_right(self, n:int=1):
        for _ in range(max(1, n)):
            self.__cmd(0x10 | 0x08 | 0x04)
            self.__shift = (self.__shift - 1) % self.__dwidth