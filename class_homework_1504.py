import warnings
class Rectangle:
    def __init__(self, top_left_x, top_left_y, length, height):
        self.abs = top_left_x
        self.ord = top_left_y
        self.l = length
        self.h = height

    def set_new_length(self, length_n):
        if length_n < 0:
            warnings.warn('One of the parameters is below zero', UserWarning)
        elif length_n == 0:
            raise ValueError('One of the parameters is zero')
        else: self.l = length_n

    def get_square(self):
        return self.l * self.h

    def is_square(self):
        if self.l == self.h:
            return True


    def horizontal(self):
        if self.l > self.h:
            return True
        else: return False


    def in_start(self):
        zeros = []
        if self.abs == 0:
            zeros.append('start_x')
        if self.ord - self.h == 0:
            zeros.append('start_y')
        return zeros

    def dot_inside(self, coord_x, coord_y):
        if coord_x > self.abs and coord_x < self.abs + self.l:
            if coord_y < self.ord and coord_y > self.ord - self.h:
                return 'Yes'
            else: return 'No'
        else: return 'No'

