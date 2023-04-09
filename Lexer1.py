from fractions import Fraction
from dataclasses import dataclass
from typing import Optional, NewType
from typing import List
import sys


# A minimal example to illustrate typechecking.

class EndOfStream(Exception):
    pass



@dataclass
# This defines a class named Stream, which will store information 
# about a character stream
class Stream:
    # Stream contains the string and positon
    source: str  
    # This is an instance variable of the class, which stores the string data of the stream.
    pos: int
    #  stores the current position in the stream.
    def from_string(s):
        return Stream(s, 0)
    # create stream object
    def next_char(self):
    #gets the next char from the stream
        if self.pos >= len(self.source):
            raise EndOfStream()
        self.pos = self.pos + 1
        return self.source[self.pos - 1]

    def unget(self):
    #  move the position of the stream back by one character
        assert self.pos > 0
        self.pos = self.pos - 1
