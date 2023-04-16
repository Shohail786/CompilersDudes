from fractions import Fraction
from dataclasses import dataclass
from typing import Optional, NewType
from typing import List
import sys
# import pytest


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

# Define the token types.

@dataclass
class Num:
    n: int
@dataclass
class Bool:
    b: bool

@dataclass
class Keyword:
    word: str

@dataclass
class Identifier:
    word: str

@dataclass
class Operator:
    op: str


class EndOfTokens():
    pass

Token = Num | Bool | Keyword | Identifier | Operator | EndOfTokens


keywords = "if then else end while do done let is in letMut letAnd seq anth put get printing for ubool func funCall assign".split()
symbolic_operators = "+ - * / < > ≤ ≥ = ≠ ; , % ( )".split()
word_operators = "and or not quot rem".split()
whitespace = " \t\n"

def word_to_token(word):
    if word in keywords:
        return Keyword(word)
    if word in word_operators:
        return Operator(word)
    if word == "True":
        return Bool(True)
    if word == "False":
        return Bool(False)
    return Identifier(word)

class TokenError(Exception):
    pass

@dataclass
class Lexer:
    stream: Stream
    save: Token = None
    # an instance variable, named save of type Token with a default value of None.
    def from_stream(s):
        return Lexer(s)

    def next_token(self) -> Token:
        # returns the next token in the input stream
        try:
            match self.stream.next_char():
                # case ">":
                #     if self.stream.next_char()=="=":
                #         return Operator(">=")
                #     else:
                #         self.stream.unget()
                #         return Operator(">")
                case c if c in symbolic_operators: 
                    return Operator(c)
                
                case c if c.isdigit():
                    n = int(c)
                    while True:
                        try:
                            c = self.stream.next_char()
                            if c.isdigit():
                                n = n*10 + int(c)
                            else:
                                self.stream.unget()
                                return Num(n)
                        except EndOfStream:
                            return Num(n)
                case c if c.isalpha():
                    s = c
                    while True:
                        try:
                            c = self.stream.next_char()
                            if c.isalpha():
                                s = s + c
                            else:
                                self.stream.unget()
                                return word_to_token(s)
                        except EndOfStream:
                            return word_to_token(s)
                case c if c in whitespace:
                    return self.next_token()
        except EndOfStream:
            # raise EndOfTokens
            return EndOfTokens()

    def peek_token(self) -> Token:

# to look ahead in the stream to see the next token without 
# actually consuming it. 
        if self.save is not None:
            return self.save
        self.save = self.next_token()
        return self.save

    def advance(self):
        #  This method advances the stream to the next token.
        assert self.save is not None
        self.save = None

    def match(self, expected):
        # matches the current token with the expected token. 
        # If the current token matches the expected token,
        if self.peek_token() == expected:
            return self.advance()
        raise TokenError()

    def __iter__(self):
        #makes the Lexer class iterable
        # so you can use a for loop to iterate over the tokens.
        return self

    def __next__(self):
        # It calls next_token to get the next token
        return self.next_token()
        # try:
        #     return self.next_token()
        # # except EndOfTokens:
        #     raise StopIteration

@dataclass
class Parser:
    lexer: Lexer

    def from_lexer(lexer):
        return Parser(lexer)

    def parse_if(self):
        #The match method is called on the Lexer object to check that the 
        # next token in the stream
        self.lexer.match(Keyword("if"))
        c = self.parse_expr()
        self.lexer.match(Keyword("then"))
        t = self.parse_expr()
        self.lexer.match(Keyword("else"))
        f = self.parse_expr()
        self.lexer.match(Keyword("end"))
        return if_else(c, t, f)
    
    def parse_let(self):
        self.lexer.match(Keyword("let"))
        v=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e=self.parse_expr()
        self.lexer.match(Keyword("in"))
        b=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return Let(v,e,b)
    
    def parse_LetMut(self):
        self.lexer.match(Keyword("letMut"))
        v=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e=self.parse_expr()
        self.lexer.match(Keyword("in"))
        b=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return LetMut(v,e,b)
    
    def parse_LetAnd(self):
        self.lexer.match(Keyword("letAnd"))
        v1=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e1=self.parse_expr()
        self.lexer.match(Operator(";"))
        v2=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e2=self.parse_expr()
        self.lexer.match(Keyword("in"))
        b=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return LetAnd(v1,e1,v2,e2,b)
    
    def parse_Seq(self):
        self.lexer.match(Keyword("seq"))
        lst=[]
        #10
        while True:
            match self.lexer.peek_token():
                case Keyword("end"):
                    self.lexer.advance()
                    break
                case _:
                    while True:
                        lst.append(self.parse_expr())
                        match self.lexer.peek_token():
                            case Operator(";"):
                                self.lexer.advance()
                                continue
                            case _:
                                break
        #12
        # e1=self.parse_expr()
        # lst.append(e1)
        # self.lexer.match(Operator(";"))
        # e2=self.parse_expr()
        # lst.append(e2)
        # self.lexer.match(Keyword("end"))

        #13
        # print(" helloo ")
        # a=True
        # while a:
            
        #     e1=self.parse_expr()
        #     lst.append(e1)
        #     print(" helloo 123")
        #     self.lexer.match(Keyword(" "))
        #     if self.lexer.match(Keyword("end")):
        #         a=False
        return Seq(lst)

    def parse_put(self):
        self.lexer.match(Keyword("put"))
        v=self.parse_expr()
        self.lexer.match(Keyword("is"))
        e=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return Put(v,e)
    
    def parse_get(self):
        self.lexer.match(Keyword("get"))
        v=self.parse_expr()
        return Get(v)
    
    def parse_assign(self):
        self.lexer.match(Keyword("assign"))
        v1=self.parse_expr()
        self.lexer.match(Keyword("is"))
        v2=self.parse_expr()
        return Assign(v1,v2)

    def parse_printing(self):
        self.lexer.match(Keyword("printing"))
        v=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return Print(v)
    
    def parse_ubool(self):
        self.lexer.match(Keyword("ubool"))
        v=self.parse_expr()
        self.lexer.match(Keyword("end"))
        return UBoolOp(v)
    
    def parse_while(self):
        self.lexer.match(Keyword("while"))
        c = self.parse_expr()
        self.lexer.match(Keyword("do"))
        b = self.parse_expr()
        self.lexer.match(Keyword("done"))
        return while_loop(c, b)
    
    def parse_for(self):
        self.lexer.match(Keyword("for"))
        a=self.parse_expr()
        self.lexer.match(Keyword("is"))
        b=self.parse_expr()
        self.lexer.match(Operator(";"))
        c=self.parse_expr()
        self.lexer.match(Operator(";"))
        d=self.parse_expr()
        self.lexer.match(Operator(";"))
        e=self.parse_expr()
        self.lexer.match(Keyword("end"))
        
        return for_loop(a,b,c,d,e)

    def parse_LetFun(self):
        self.lexer.match(Keyword("func"))
        a=self.parse_expr()
        self.lexer.match(Operator("("))
        params=[]
        while True:
            match self.lexer.peek_token():
                case Operator(")"):
                    self.lexer.advance()
                    break
                case _:
                    while True:
                        params.append(self.parse_expr())
                        match self.lexer.peek_token():
                            case Operator(","):
                                self.lexer.advance()
                                continue
                            case _:
                                break    
            
        body=self.parse_expr()
        self.lexer.match(Operator(","))
        expr=self.parse_expr()
        return LetFun(a,params,body,expr)
    
    def parse_FunCall(self):
        self.lexer.match(Keyword("funCall"))
        a=self.parse_expr()
        self.lexer.match(Operator("("))
        params=[]
        while True:
            match self.lexer.peek_token():
                case Operator(")"):
                    self.lexer.advance()
                    break
                case _:
                    while True:
                        params.append(self.parse_expr())
                        match self.lexer.peek_token():
                            case Operator(","):
                                self.lexer.advance()
                                continue
                            case _:
                                break
        return FunCall(a,params)


    def parse_atom(self):
        # checks the type of the next token
        match self.lexer.peek_token():
            case Identifier(name):
                self.lexer.advance()
                return Variable(name)
            case Num(value):
                self.lexer.advance()
                return NumLiteral(value)
            case Bool(value):
                self.lexer.advance()
                return BoolLiteral(value)
            case Keyword("funCall"):     
                 return self.parse_FunCall()
    

    def parse_mult(self):
        left = self.parse_atom()
        while True:
            match self.lexer.peek_token():
                case Operator(op) if op in "*/%":
                    self.lexer.advance()
                    m = self.parse_atom()
                    left = BinOp(op, left, m)
                case _:
                    break
        return left

    def parse_add(self):
        left = self.parse_mult()
        while True:
            match self.lexer.peek_token():
                case Operator(op) if op in "+-":
                    self.lexer.advance()
                    m = self.parse_mult()
                    left = BinOp(op, left, m)
                case _:
                    break
        return left

    def parse_cmp(self):
        left = self.parse_add()
        match self.lexer.peek_token():
            case Operator(op) if op in "<>=":
                self.lexer.advance()
                right = self.parse_add()
                return BinOp(op, left, right)
        return left
    def parse_not(self):
        
        match self.lexer.peek_token():
            case Operator("not"):
                self.lexer.advance()
                right = self.parse_cmp()
                return UnOp("not",right)
            case _:
                return self.parse_cmp()
    def parse_or(self):
        left = self.parse_not()
        match self.lexer.peek_token():
            case Operator("or"):
                self.lexer.advance()
                right = self.parse_not()
                return BinOp("or", left, right)
        return left
    def parse_and(self):
        left = self.parse_or()
        match self.lexer.peek_token():
            case Operator("and"):
                self.lexer.advance()
                right = self.parse_or()
                return BinOp("and", left, right)
        return left


    def parse_simple(self):
        return self.parse_and()

    def parse_expr(self):
        #which handles the different cases for a valid expression: 
        # if-else, while loop or 
        # simple expression (a combination of basic mathematical operations 
        # like addition, subtraction, multiplication, and division and comparison operations like less than, greater than).
        match self.lexer.peek_token():
            case Keyword("if"):
                return self.parse_if()
            case Keyword("while"):
                return self.parse_while()
            case Keyword("for"):
                return self.parse_for()
            case Keyword("let"):
                return self.parse_let()
            case Keyword("letMut"):
                return self.parse_LetMut()
            case Keyword("put"):
                return self.parse_put()
            case Keyword("get"):
                return self.parse_get()
            case Keyword("assign"):
                return self.parse_assign()
            case Keyword("letAnd"):
                return self.parse_LetAnd()
            case Keyword("seq"):
                return self.parse_Seq()
            case Keyword("printing"):
                return self.parse_printing()
            case Keyword("ubool"):
                return self.parse_ubool()
            case Keyword("func"):
                return self.parse_LetFun()
            case Keyword("funCall"):
                return self.parse_FunCall()
            case _:
                return self.parse_simple()
            

@dataclass
class NumType:
    pass

@dataclass
class BoolType:
    pass
@dataclass
class StringType:
    pass

SimType = NumType | BoolType | StringType

@dataclass
#  The _init_ method takes any number of arguments and passes them to the Fraction constructor to create a new Fraction object, which is then stored in the value field.
class NumLiteral:
    value: Fraction
    type: SimType = NumType()
    def __init__(self, *args):
        self.value = Fraction(*args)


@dataclass
class StringLiteral:
    word : str 
    type: SimType = StringType()

@dataclass
class Integer:
    value:int
    type:SimType=NumType()

@dataclass
# this is kind of binary operation
class BinOp:                      
    operator: str      # '+' is the operator in addition
    # below are kind of two no. to be added
    left: 'AST'
    right: 'AST'

    type: Optional[SimType] = None


@dataclass
class Variable:
    name: str
    type: Optional[SimType] = None


@dataclass
class StringLiteral:
    word : str 
    type: SimType = StringType()


@dataclass
class Let:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'
    type: Optional[SimType] = None

@dataclass
class BoolLiteral:
    value: bool
    type: SimType = BoolType()


@dataclass
class if_else:
    expr: 'AST'
    et: 'AST'    #statement if expr is true
    ef: 'AST'    #statement if expr is false
    type: Optional[SimType] = None


@dataclass
class while_loop:
    condition: 'AST'
    body: 'AST'
    type: Optional[SimType] = None


@dataclass
class for_loop:
    var: 'AST'
    expr: 'AST'
    condition: 'AST'
    updt: 'AST'
    body: 'AST'
    type: Optional[SimType] = None


@dataclass
class Two_Str_concatenation:
    str1: 'AST'
    str2: 'AST'
    type: Optional[SimType] = None

@dataclass

class Str_slicing:
    str1: 'AST'
    start: 'AST'
    end: 'AST'
    type: Optional[SimType] = None


@dataclass
class LetMut:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'
    type: Optional[SimType] = None


@dataclass
class Seq:
    body: List['AST']
    type: Optional[SimType] = None


@dataclass
class Put:
    var: 'AST'
    e1: 'AST'
    type: Optional[SimType] = None

@dataclass

class Assign:
    var: 'AST'
    e1: 'AST'
    type: Optional[SimType] = None

@dataclass

class Get:
    var: 'AST'
    type: Optional[SimType] = None

@dataclass
class Print:
    e1: 'AST'
    type: Optional[SimType] = None


@dataclass
class LetFun:
    name:'AST'
    params:List['AST']
    body:'AST'
    expr:'AST'
    type: Optional[SimType] = None

@dataclass
class FunCall:
    fn:'AST'
    args: List['AST']
    type: Optional[SimType] = None

@dataclass
class FnObject:
    params: List['AST']
    body: 'AST'
    type: Optional[SimType] = None

@dataclass
class LetAnd:
    var1:'AST'
    expr1: 'AST'
    var2:'AST'
    expr2:'AST'
    expr3:'AST'
    type: Optional[SimType] = None
@dataclass
class UBoolOp:
    expr: 'AST' 
    type: Optional[SimType] = None
@dataclass 
class UnOp:
    operator: str 
    expr='AST'

AST = NumLiteral |BoolLiteral | StringLiteral | BinOp | Variable | Let | if_else | LetMut | Put | Get | Assign |Seq | Print | while_loop | FunCall | StringLiteral | UBoolOp | LetAnd
# TypedAST = NewType('TypedAST', AST)
class InvalidProgram(Exception):
    pass

# new code start
Value = Fraction | bool | str


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

    def check(self,name):
        for dict in reversed(self.env):
            if name in dict:
                return True
            else:
                return False
            
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


class TypeError(Exception):
    pass

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

        case StringLiteral(word):
            return word

        case Variable(name):
            return environment.get(name)
            
        case Put(Variable(name),e1): 
            environment.update(name,eval_(e1))
            return environment.get(name)
        
        case Get(Variable(name)):
            return environment.get(name)

        case Assign(Variable(name),e1):
            environment.add(name,eval_(e1))
            return name


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

        case Str_slicing(str1,start,end):
            result_str = StringLiteral("")
            i = Variable("i")
            i = start
            body1 = LetMut(i,Get(i),BinOp("+",i,NumLiteral(1)))
            body2 = LetMut(result_str,Get(result_str),Two_Str_concatenation(result_str,str1[Get(i)]))
            body = Seq([body1,body2])
            condition = BinOp("<",i,end)
            eval_(while_loop(condition,body))
            return result_str


        case LetAnd(Variable(name1),expr1,Variable(name2),expr2,expr3):
            v1=eval_(expr1)
            v2=eval_(expr2)
            environment.enter_scope()
            if environment.check(name1):
                environment.update(name1,v1)
                
            else:
               environment.add(name1,v1)

            if environment.check(name2):
                environment.update(name2,v2)
                
            else:
               environment.add(name2,v2)
            
            v3=eval_(expr3)
            environment.exit_scope()
            return v3

        case LetFun(Variable(name),params, body,expr):
            environment.enter_scope()
            environment.add(name, FnObject(params,body))
            v=eval_(expr)
            environment.exit_scope()
            return v
        
        
        case FunCall(Variable(name),args):
            fn=environment.get(name)
            argv=[]
            for arg in args:
                argv.append(eval_(arg))
            environment.enter_scope()
            for par,arg in zip(fn.params,argv):
                environment.add(par.name,arg)
            v=eval_(fn.body)
            environment.exit_scope()
            return v
            
        case UBoolOp(expr):
            if typecheck(expr).type==NumType():
                    v1=eval_(expr)
                    if v1 !=0:
                        
                        return True
                    else:
                        return False
            elif typecheck(expr).type==StringType():
                    v1=eval_(expr)
                    if v1 == "":
                        return False
                    else:
                        return True
            else:
                print("error")

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
        case BinOp("%", left, right):
            return eval_(left) % eval_(right)
        case BinOp(">",left,right):
            return eval_(left) > eval_(right)
        case BinOp("<", left,right):
            return eval_(left) < eval_(right)
        case BinOp("=", left,right):
            return eval_(left) == eval_(right)
        case BinOp ("or",left,right):
            return eval_(left) or eval_(right)
        case BinOp("and",left,right):
            return eval_(left) and eval_(right)
        case UnOp("not", expr):
            return not(eval_(expr))
        
        
        case if_else(expr,et,ef):
            v1 = eval_(expr)
            if v1 == True:
                return eval_(et)
            else:
                return eval_(ef)
                
        case while_loop(condition,e1):
            environment.enter_scope()
            vcond = eval_(condition)
            
            while(vcond):
                eval_(e1) 
                vcond=eval_(condition)
            environment.exit_scope()
            return None

        case for_loop(Variable(name),e1,condition,updt,body):
            environment.enter_scope()
            environment.add(name,eval_(e1))
            vcond=eval_(condition)
            while(vcond):
                v1=eval_(body)
                eval_(updt)
                vcond=eval_(condition)    
            environment.exit_scope()
            return v1
        
        case Print(e1):
            v1=eval_(e1)
            print(v1)
            return v1

    raise InvalidProgram()

#new code ends




def typecheck(program: AST, environment: Environment = None) -> AST:
    if environment is None:
        environment = Environment()
    def typecheck_(program):
        return typecheck(program, environment)
    match program:
        case NumLiteral() as t: # already typed.
            return t
        case BoolLiteral() as t: # already typed.
            return t
        case StringLiteral() as t:
            return t
        case Variable(name):
            t1=environment.get(name)
            tname=Variable(name)
            tname.type=t1
            return tname
        case Put(Variable(name),e1):
            v1=typecheck_(e1)
            t1=environment.get(name)
            print("v1 ", v1)
            print("t1 ",t1)
            tname=Variable(name)
            tname.type=t1
            v2=Put(tname,v1,tname.type)
            return v2
        case Get(Variable(name)):
            t1=environment.get(name)
            tname=Variable(name)
            tname.type=t1
            v2=Get(tname)
            return v2
        
        case Assign(Variable(name),e1):
            v1=typecheck_(e1)
            tname=Variable(name)
            tname.type=v1.type
            environment.add(name,tname.type)
            return Assign(tname,v1)

        case Seq(body):  
            newBody=[]
            for item in body:
                v1=typecheck_(item)
                newBody.append(v1)
            return Seq(newBody,v1.type)
        
        case Print(e1):
            v1=typecheck_(e1)
            print("e1 ",e1)
            print("v1 ",v1)
            return Print(v1,v1.type)

        case UBoolOp(expr):
            v1=typecheck_(expr)
            return UBoolOp(v1,BoolType())

        case BinOp(op, left, right) if op in "+*-/%":
            tleft = typecheck_(left)
            tright = typecheck_(right)
            if tleft.type != NumType() or tright.type != NumType():
                raise TypeError()
            return BinOp(op, tleft, tright, NumType())
        case BinOp("<", left, right):
            tleft = typecheck_(left)
            tright = typecheck_(right)
            if tleft.type != NumType() or tright.type != NumType():
                raise TypeError()
            return BinOp("<", tleft, tright, BoolType())
        case BinOp(">", left, right):
            tleft = typecheck_(left)
            tright = typecheck_(right)
            if tleft.type != NumType() or tright.type != NumType():
                raise TypeError()
            return BinOp(">", tleft, tright, BoolType())
        case BinOp("==", left, right):
            tleft = typecheck_(left)
            tright = typecheck_(right)
            if tleft.type != NumType() or tright.type != NumType():
                raise TypeError()
            return BinOp("==", tleft, tright, BoolType())
        
        case BinOp("=", left, right):
            tleft = typecheck_(left)
            tright = typecheck_(right)
            if tleft.type != tright.type:
                raise TypeError()
            return BinOp("=", tleft, tright, BoolType())
        case if_else(c, t, f): # We have to typecheck both branches.
            tc = typecheck_(c)
            if tc.type != BoolType():
                raise TypeError()
            tt = typecheck_(t)
            tf = typecheck_(f)
            if tt.type != tf.type: # Both branches must have the same type.
                raise TypeError()
            return if_else(tc, tt, tf, tt.type) # The common type becomes the type of the if-else.

        case while_loop(condition,e1):
            environment.enter_scope()
            condition1 = typecheck_(condition)
            exp1= typecheck_(e1) 
            environment.exit_scope()
            return while_loop(condition1,exp1,exp1.type)
        
        case for_loop(Variable(name),e1,condition,updt,body):
            tname=Variable(name)
            v1=typecheck_(e1)
            environment.enter_scope()
            environment.add(name,v1.type)
            vcond=typecheck_(condition)
            vbody=typecheck_(body)
            vupdt=typecheck_(updt)   
            environment.exit_scope()
            return for_loop(tname,v1,vcond,vupdt,vbody,vbody.type)
            
        case Let(Variable(name),exp1,exp2) | LetMut(Variable(name),exp1,exp2):
            tname=Variable(name)
            v1=typecheck_(exp1)
            tname.type=v1.type
            environment.enter_scope()
            environment.add(name,tname.type)
            v2=typecheck_(exp2)
            environment.exit_scope()
            v3=Let(tname,v1,v2,v2.type)
            return v3
        
        case LetAnd(Variable(name1),expr1,Variable(name2),expr2,expr3):
            newExp1=typecheck_(expr1)
            newExp2=typecheck_(expr2)
            tname1=Variable(name1)
            tname1.type=newExp1.type
            tname2=Variable(name2)
            tname2.type=newExp2.type
            environment.enter_scope()
            if environment.check(name1):
                environment.update(name1,newExp1.type)
                
            else:
               environment.add(name1,newExp1.type)

            if environment.check(name2):
                environment.update(name2,newExp2.type)
                
            else:
               environment.add(name2,newExp2.type)
            
            newExp3=typecheck_(expr3)
            environment.exit_scope()
            return LetAnd(tname1,newExp1,tname2,newExp2,newExp3, newExp3.type)
        
    raise TypeError()

# def test_typecheck():
#     import pytest
#     te = typecheck(BinOp("+", NumLiteral(2), NumLiteral(3)))
#     print("te: ",te)
#     assert te.type == NumType()
#     te = typecheck(BinOp("<", NumLiteral(2), NumLiteral(3)))
#     print("te: ",te)
#     assert te.type == BoolType()
#     with pytest.raises(TypeError):
#         typecheck(BinOp("+", BinOp("*", NumLiteral(2), NumLiteral(3)), BinOp("<", NumLiteral(2), NumLiteral(3))))

def test_parse():
    def parse(string):
        #First, the parse function creates a Stream object from the 
        # string argument and then creates a Lexer object from the Stream object.
        #The parse function then creates a Parser object from the Lexer object and calls the parse_expr method on the Parser object.
        return Parser.parse_expr (
            Parser.from_lexer(Lexer.from_stream(Stream.from_string(string)))
        )
    #10
    # x=input()
    # print(x)
    # y=parse(x)
    # print("y-> ",y)
    # print("ans-> ", eval(y))

    file=open(sys.argv[1],'r')
    #11
    # x=input()
    # x=file.read()
    # print(x)
    # y=parse(x)
    # print("y-> ",y)
    # z=typecheck(y)
    # print("z-> ",z)
    # print("ans-> ", eval(z))
    # print(z.type)

    #12
    # for line in file.readlines():
    #     x=line
    #     print(x)
    #     y=parse(x)
    #     print("y-> ",y)
    #     print("ans-> ",eval(y))
    13
    x=file.read()
    result = []
    parens = 0
    buff = ""
    for c in x:
        if c == "{":
            parens += 1
        if parens > 0:
            if c == "{":
                pass
            elif c == "}":
                pass
            else:
                buff += c
        if c == "}":
            parens -= 1
        if not parens and buff:
            result.append(buff)
            buff = ""
    for i, r in enumerate(result):
        print(i,r)
        y=parse(r)
        print("y-> ",y)
        print("ans-> ",eval(y))

    # You should parse, evaluate and see whether the expression produces the expected value in your tests.
    # print(parse("if a+b > 2*d then a*b - c + d else e*f/g end"))
    # print(parse("if 10*5 > 6*6 then 10*5 else 6*6 end"))
    # print(" eval ")
    # b=parse("if 10*5 > 6*6 then 10*5 else 6*6 end")
    # print("b ",b)
    # print(eval(b))
    # c=parse("let a is 5 in let b is 7 in a+b end end ")
    # print("c ",c)
    # print(eval(c))
    # code1.eval(parse("if a+b > 2*d then a*b - c + d else e*f/g end"))

# test_parse() # Uncomment to see the created ASTs.
print("parse  ",test_parse())
# print(test_typecheck())


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


def test_eval():
    e1 = NumLiteral(2)
    e2 = NumLiteral(7)
    e3 = NumLiteral(9)
    e4 = NumLiteral(5)
    e5 = BinOp("+", e2, e3)      
    e6 = BinOp("/", e5, e4)
    e7 = BinOp("*", e1, e6)
    assert eval(e7) == Fraction(32, 5)

# def test_string_slicing():
#     str1 = StringLiteral("abcdefg")
#     start = NumLiteral(0)
#     end = NumLiteral(4)
#     expr = Str_slicing(str1,start,end)
#     assert eval(expr) == 'abcd'
def test_string_slicing():
    program = Str_slicing(StringLiteral("Hello, world!"), NumLiteral(0), NumLiteral(5))
    # program = Str_slicing("Hello, world!", NumLiteral(0), NumLiteral(5))
    result = eval(program)
    assert eval(result) == 'Hello'

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
    print(e10)
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


def test_while_eval():
    a = Variable("a")
    e1=NumLiteral(10)
    e2 = LetMut(a, NumLiteral(2), while_loop(BinOp("<",Get(a),e1),Put(a, BinOp("+", Get(a), NumLiteral(2)))) )
    print(eval(e2))
    assert eval(e2)==10

def test_for_eval():
    a = Variable("a")
    e1=NumLiteral(10)
    i=Variable("i")
    e2=NumLiteral(0)
    e3=Put(i,BinOp("+",Get(i),NumLiteral(1)))
    e4=Put(a,BinOp("+",Get(i),Get(a)))
    e5=LetMut(a,e1, for_loop(i,e2,BinOp(">",e1,Get(i)),e3,e4))
    print(eval(e5))
    assert eval(e5)==55


def test_print():
    a=Variable("a")
    e1=NumLiteral(5)
    e2=LetMut(a,e1,Put(a,BinOp("+",Get(a),NumLiteral(6))))
    e3=Print(e2)
    assert eval(e3)==11

def test_str_concatenation():
    str1 = StringLiteral("ab")
    str2 = StringLiteral("cd")
    expr = Two_Str_concatenation(str1,str2)
    assert eval(expr) == 'abcd'



# print(test_eval())
# print(test_if_else_eval())
# print(test_let_eval())
# print(test_letmut_eg1())
# print(test_letmut_eg2())
# print(test_print())
# print(test_letmut())
# print(test_while_eval())

def test_Letfun1():
    a=Variable('a')
    b=Variable('b')
    f=Variable('f')
    e=LetFun(f,[a,b],BinOp("+",a,b),FunCall(f,[NumLiteral(15),NumLiteral(2)]))
    assert eval(e)==17 

def test_Letfun2():
    a = Variable("a")
    b = Variable("b")
    f = Variable("f")
    g = BinOp (
        "*",
        FunCall(f, [NumLiteral(15), NumLiteral(2)]),
        FunCall(f, [NumLiteral(12), NumLiteral(3)])
    )
    e = LetFun(
        f, [a, b], BinOp("+", a, b),
        g
    )
    assert eval(e) == (15+2)*(12+3)

def test_Letfun3():
    n = Variable("n")
    f = Variable("f")
    g = FunCall(f,[NumLiteral(5)])
    h=BinOp("=",n,NumLiteral(1))
    m=BinOp("-",n,NumLiteral(1))
    k=BinOp("*",n,FunCall(f,[m]))
    l=if_else(h,NumLiteral(1),k)
    e = LetFun(
        f, [n], l,
        g
    )
    print(eval(e))
    assert eval(e) == 120


def test_LetAnd():
    a=Variable('a')
    b=Variable('b')
    e1=NumLiteral(5)
    e2=BinOp("+",a,NumLiteral(1))
    e3=BinOp("+",a,b)
    e4=LetMut(a,e1,LetAnd(a,NumLiteral(3),b,e2,e3)) 
    assert eval(e4)==9

def test_UBoolOp1():
    a=Variable("a")
    e1=NumLiteral(0)
    e3=UBoolOp(e1)
    assert eval(e3)==False

def test_UBoolOp2():
    e1=StringLiteral("")
    e3=UBoolOp(e1)
    print(eval(e3))
    assert eval(e3)==False
#final code

def test_typecheck():
    t1=BinOp("-",NumLiteral(5),NumLiteral(3))
    t2=BinOp("+",t1,NumLiteral(2))
    t3=typecheck(t2)
    print("t2: ",t2)
    print("t3: ",t3)
    assert t3.type == NumType()

def test_typecheck1():
    t1=BinOp("-",NumLiteral(5),NumLiteral(3))
    t2=BinOp("+",t1,NumLiteral(2))
    t3=typecheck(t2)
    print("t2: ",t2)
    print("t3: ",t3)
    assert t3.type == NumType()

# print("test_eval(): ",test_eval())
# print("test_if_else_eval(): ", test_if_else_eval())
# print("test_let_eval(): ",test_let_eval())
# print("test_letmut_eg1(): ",test_letmut_eg1())
# print("test_letmut_eg2(): ",test_letmut_eg2())
# print("test_print(): ",test_print())
# print("test_letmut(): ",test_letmut())
# print("test_while_eval(): ",test_while_eval())
# print("test_for_eval(): ",test_for_eval())
# print("test_Letfun1(): ",test_Letfun1())
# print("test_Letfun2(): ",test_Letfun2())
# print("test_Letfun3(): ",test_Letfun3())
# print("test_LetAnd(): ",test_LetAnd())
# print("test_UBoolOp1(): ",test_UBoolOp1())
# print("test_UBoolOp2(): ",test_UBoolOp2())
# print("test_typecheck(): ",test_typecheck())
# print("test_list() ",test_list()) 