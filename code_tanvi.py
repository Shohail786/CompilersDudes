from dataclasses import dataclass
from fractions import Fraction
from typing import Union, Mapping  #Union is used to specify that a variable can have one of several types and Mapping is a type hint for dictionaries or mappings.
from typing import List


@dataclass
#  The _init_ method takes any number of arguments and passes them to the Fraction constructor to create a new Fraction object, which is then stored in the value field.
class NumLiteral:
    value: Fraction
    def __init__(self, *args):
        self.value = Fraction(*args)

@dataclass
# this is kind of binary operation
class BinOp:                      
    operator: str      # '+' is the operator in addition
    # below are kind of two no. to be added
    left: 'AST'
    right: 'AST'

@dataclass
class Variable:
    name: str


@dataclass
class Let:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'

@dataclass
class BoolLiteral:
    value: bool

@dataclass
class if_else:
    expr: 'AST'
    et: 'AST'    #statement if expr is true
    ef: 'AST'    #statement if expr is false



@dataclass
class while_loop:
    condition: 'AST'
    body: 'AST'


@dataclass
class for_loop:
    var: 'AST'
    start_expr: 'AST'
    end_expr: 'AST'
    condition: 'AST'
    body: 'AST'
    
@dataclass
class Two_Str_concatenation:
    str1: 'AST'
    str2: 'AST'

@dataclass
class LetMut:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'


@dataclass
class Seq:
    body: List['AST']

@dataclass
class LetMut:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'

@dataclass
class Put:
    var: 'AST'
    e1: 'AST'

@dataclass
class Get:
    var: 'AST'

@dataclass
class Print:
    e1: 'AST'

# Original defination
# cons adds an item to the beginning of the list. If the list is empty, it creates a new list with the item as its only element. Otherwise, it creates a new list with the item as the first element and the rest of the original list as the remaining elements.
# is-empty? returns true if the list is empty and false otherwise.
# head returns the first element of the list.
# tail returns a new list containing all elements of the original list except for the first one.

# My defination
#Introduced a dataclass for lists with cons, is_empty, head, and tail.
# cons - Adding an element in the list
# is_empty - checks if a list is empty or not
# head - First element in the list using indexing
# tail - Creates a list of elements except the first one using indexing

@dataclass
class List:
    def __init__(self, elements=None):
        self.elements = elements or []

    def cons(self, element):
        self.elements.append(element)

    def is_empty(self):
        return not bool(self.elements)

    def head(self):
        if self.is_empty():
            return None
        return self.elements[0]

    def tail(self):
        if self.is_empty():
            return None
        return self.elements[1:]

class Environment:
    env: List

    def __init__(self):
        self.env=[{}]

    def enter_scope(self):
        self.env.append({})

    def exit_scope(self):
        assert self.env
        self.env.pop()

    def add(self,name,value):
        assert name not in self.env[-1]
        self.env[-1][name]=value

    def get(self,name):
        for dict in reversed(self.env):
            if name in dict:
                return dict[name]
        raise KeyError()
    
    def update(self,name,value):
        for dict in reversed(self.env):
            if name in dict:
                dict[name]=value
                return
        raise KeyError()

AST = NumLiteral | BinOp | Variable | Let | if_else | LetMut | Put | Get |Seq | Print | while_loop


# The AST type is defined as a union of several classes, including NumLiteral, BinOp, Variable, Let, and If_else.


Value = Fraction | bool

# The InvalidProgram exception is defined. This exception will be raised when an invalid program is encountered during evaluation.
class InvalidProgram(Exception):
    pass

# environment is a mapping of variable names to their values and is used to keep track of the state of the program during evaluation. 
# The function returns the final value of the program.
def eval(program: AST, environment: Environment = None) -> Value:
    if environment is None:
        environment = Environment()

    def eval_(program):
        return eval(program, environment) 
       
    match program:
        case NumLiteral(value):
            return value
        case BoolLiteral(value):
            return value
        
        case Variable(name):
            return environment.get(name)
            
        case Put(Variable(name),e1): 
            environment.update(name,eval_(e1))
            return environment.get(name)
        
        case Get(Variable(name)):
            return environment.get(name)
        
        case Let(Variable(name), e1, e2) | LetMut(Variable(name),e1, e2):

            v1 = eval_(e1)
            environment.enter_scope()
            environment.add(name,v1)
            v2=eval_(e2)
            environment.exit_scope()
            return v2
        
        case Two_Str_concatenation(str1,str2):
            result_str = eval_(str1) + eval_(str2)
            return result_str
     
        
        case Seq(body):
            v1=None
            for item in body:
                v1=eval_(item)
            return v1    

        case BinOp("+", left, right):
            return eval_(left) + eval_(right)
        case BinOp("-", left, right):
            return eval_(left) - eval_(right)
        case BinOp("*", left, right):
            return eval_(left) * eval_(right)
        case BinOp("/", left, right):
            return eval_(left) / eval_(right)
        case BinOp(">",left,right):
            return eval_(left) > eval_(right)
        case BinOp("<", left,right):
            return eval_(left) < eval_(right)
        case BinOp("==", left,right):
            return eval_(left) == eval_(right)
        # case ListLiteral()

        case if_else(expr,et,ef):
            v1 = eval_(expr)
            if v1 == True:
                return eval_(et)
            else:
                return eval_(ef)
                
        case while_loop(condition,e1):
            v1 = eval_(condition)
            
            if v1 == True:
                eval_(e1) 
                eval_(while_loop(condition,e1))
            
            return None

        case Print(e1):
            v1=eval_(e1)
            print(v1)
            return v1

    raise InvalidProgram()




# def eval_list(lst, env):
#     result = []
#     for i in range(len(lst.elements)):
#         result.append(eval(lst.elements[i], env))
#     return List(result)

# Let(Variable("my_list"), List([NumLiteral(1), NumLiteral(2), NumLiteral(3)]))

# v = eval_list(List([NumLiteral(1), NumLiteral(2), NumLiteral(3)]), env)
# environment.add("my_list", v)


# Define the environment
environment = Environment()

# Define the 'eval_list' function
def eval_list(lst, env):
    result = []
    for i in range(len(lst.elements)):
        result.append(eval(lst.elements[i], env))
    return List(result)

# Create a list and evaluate it
my_list = List([NumLiteral(1), NumLiteral(2), NumLiteral(3)])
v = eval_list(my_list, environment)

# Add the result to the environment
environment.add("my_list", v)

# Define the 'is_empty' operation for the List class
def is_empty(lst):
    return len(lst.elements) == 0

# Define the 'head' operation for the List class
def head(lst):
    if is_empty(lst):
        raise Exception("List is empty")
    return lst.elements[0]

# Define the 'tail' operation for the List class
def tail(lst):
    if is_empty(lst):
        raise Exception("List is empty")
    return List(lst.elements[1:])


# Test the operations
print(is_empty(my_list))   # False
print(head(my_list))      # NumLiteral(1)
print(tail(my_list))      # List([NumLiteral(2), NumLiteral(3)])

def test_eval():
    e1 = NumLiteral(2)
    e2 = NumLiteral(7)
    e3 = NumLiteral(9)
    e4 = NumLiteral(5)
    e5 = BinOp("+", e2, e3)      
    e6 = BinOp("/", e5, e4)
    e7 = BinOp("*", e1, e6)
    assert eval(e7) == Fraction(32, 5)

def test_let_eval():
    a  = Variable("a")
    e1 = NumLiteral(5)
    e2 = BinOp("+", a, a)
    e  = Let(a, e1, e2)
    assert eval(e) == 10
    e  = Let(a, e1, Let(a, e2, e2))
    assert eval(e) == 20
    e  = Let(a, e1, BinOp("+", a, Let(a, e2, e2)))
    assert eval(e) == 25
    e  = Let(a, e1, BinOp("+", Let(a, e2, e2), a))
    assert eval(e) == 25
    e3 = NumLiteral(6); 
    e  = BinOp("+", Let(a, e1, e2), Let(a, e3, e2))
    assert eval(e) == 22

def test_letmut():
    # a = Variable("a")
    b = Variable("b")
    e1 = LetMut(b, NumLiteral(2), Put(b, BinOp("+",Get(b), NumLiteral(1))))
    # e2 = LetMut(a, NumLiteral(1), Seq([e1, Get(a)]))
    assert eval(e1) == 3


def test_while_eval():
    a = Variable("a")
    e1=NumLiteral(10)
    e2 = LetMut(a, NumLiteral(2), while_loop(BinOp("<",Get(a),e1),Put(a, BinOp("+", Get(a), NumLiteral(2)))) )
    assert eval(e2)==None

def test_if_else_eval():
    e1=NumLiteral(10)
    e2=NumLiteral(5)
    e3=NumLiteral(6)
    e4=NumLiteral(6)
    e5=BinOp("*",e2,e1)
    e6=BinOp("*",e3,e4)
    e7=BinOp(">",e5,e6)
    e10=if_else(e7,e5,e6)
    assert eval(e10) == 50

def test_letmut_eg1():
    a=Variable("a")
    e1=NumLiteral(5)
    e2=LetMut(a,e1,Put(a,BinOp("+",Get(a),NumLiteral(6))))
    assert eval(e2)==11


def test_letmut_eg2():
    a=Variable("a")
    e1=NumLiteral(5)
    b=Variable("b")
    e2=NumLiteral(4)
    e3=Put(a,BinOp("+",Get(a),Get(b)))
    e4=Put(b,BinOp("+",Get(a),Get(b)))
    e5=LetMut(b,e2,Seq([e3,e4]))
    e6=LetMut(a,e1,Seq([e5,Get(a)]))
    assert eval(e6)==9

def test_print():
    a=Variable("a")
    e1=NumLiteral(5)
    e2=LetMut(a,e1,Put(a,BinOp("+",Get(a),NumLiteral(6))))
    e3=Print(e2)
    assert eval(e3)==11

def test_print1():
    e1=NumLiteral(5)
    # Need error in this line itself.
    e2=BinOp("+",e1,BinOp(">",NumLiteral(5),NumLiteral(6)))
    e3=Print(e2)
    # assert eval(e3)==11

# Input list is empty or not
# def is_list_empty(list_to_check):
#     return list_to_check == []


# Creating a empty list and adding elements to it using cons function
def test_list():
    lst = List()
    lst.cons(1)
    lst.cons(2)
    lst.cons(3)

    print(lst.is_empty()) # False
    print(lst.head()) # 1
    print(lst.tail()) # [2, 3]

# Using For loop to ietrate over lists.
def test_list1():
    lst = List()
    lst.cons(1)
    lst.cons(2)
    lst.cons(3)

    print(lst.is_empty()) # False
    print(lst.head()) # 1
    print(lst.tail()) # [2, 3]

    # empty_list = []
    # non_empty_list = [1, 2, 3]
    # print(is_list_empty(empty_list)) # True 
    # print(is_list_empty(non_empty_list)) # False

    # list1=[]
    # if (list1[0]!=None):
    #     print("Empty string")
    # else:
    #     e1=NumLiteral(list[1])
    #     e2=NumLiteral(list[2])
    #     e5=BinOp("*",e2,e1)
    #     e6=BinOp("+",e2,e1)
    #     e7=BinOp("/",e2,e1)
    #     e8=BinOp("-",e2,e1)
    #     assert eval(e5) == 6    
    #     assert eval(e6) == 5
    #     assert eval(e7) == 0.66
    #     assert eval(e8) == -1

    # print(list1[1])


print(test_eval())
print(test_if_else_eval())
print(test_let_eval())
print(test_letmut_eg1())
print(test_letmut_eg2())
print(test_print())
print(test_print1())
print(test_letmut())
print(test_while_eval())
print(test_list()) 