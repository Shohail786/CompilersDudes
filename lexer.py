import re

# input code file in c
f = open('inputt.c', 'r')
Program = f.read()
# for the 
#  god 239adf
# // this is a comment
# nitin

# tokens will be pushed into corresponding categories
Identifiers = []
Keywords = []
Symbols = []
Operators = []
Numerals = []
Headers = []

# this function will remove right and left extra spaces
def SpaceRemover(Program):
    ScannedProgram = []
    for line in Program:
        if (line.strip() != ''):
            ScannedProgram.append(line.strip())
    return ScannedProgram

# comments remover
def CommentRemover(Program):
    ProgramMultiCommentsRemoved = re.sub("/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", Program)
    ProgramSingleCommentsRemoved = re.sub("//.*", "", ProgramMultiCommentsRemoved)
    ProgramCommentsRemoved = ProgramSingleCommentsRemoved
    return ProgramCommentsRemoved

# this function will return a list of tokens yet to be categorized
def Tokenizer(str):
    symbol = re.findall(r"[!#%&()*+/:;<=>@\\^`{|}~\t-]+", str)
    # print(symbol)
    res = re.findall(r"[\w]+", str)
    for i in symbol:
        res.append(i)
    # print(res)
    return res

ReservedKeyWords = "auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|main|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while|string|class|struc|include"
ReservedOperators = "(\++)|(-)|(=)|(\*)|(/)|(%)|(--)|(<=)|(>=)"
ReservedNumerals = "^(\d+)$"
ReservedSpecialChars = "[\[@&~!#$\^\|{}\]:;<>?,\.']|\(\)|\(|\)|{}|\[\]|\""
ReservedIdentifiers = "^[a-zA-Z_]+[a-zA-Z0-9_]*"
ReservedHeaders = "([a-zA-Z]+\.[h])"


ProgramCommentsRemoved = CommentRemover(Program)
# for the 
#  god 239adf

# nitin


ProgramString = ProgramCommentsRemoved.split('\n')
# ['for the ', ' god 239adf', '', 'nitin']


ScannedProgram = SpaceRemover(ProgramString)
# ['for the', 'god 239adf', 'nitin']

# it doesn't consider #input...
# print(ScannedProgram)
for line in ScannedProgram:
    tokens = Tokenizer(line)
    # first token will be ['for', 'the']
    
    for token in tokens:
        if(re.findall(ReservedKeyWords, token)):
            Keywords.append(token)
        elif(re.findall(ReservedHeaders,token)):
            Headers.append(token)
        elif(re.findall(ReservedOperators, token)):
            Operators.append(token)
        elif(re.findall(ReservedNumerals,token)):
            Numerals.append(token)
        elif (re.findall(ReservedSpecialChars, token)):
            Symbols.append(token)
        elif (re.findall(ReservedIdentifiers, token)):
            Identifiers.append(token)


IdentifiersOutput = []
[IdentifiersOutput.append(x) for x in Identifiers if x not in IdentifiersOutput]
KeywordsOutput = []
[KeywordsOutput.append(x) for x in Keywords if x not in KeywordsOutput]
SymbolsOutput = []
[SymbolsOutput.append(x) for x in Symbols if x not in SymbolsOutput]
OperatorsOutput = []
[OperatorsOutput.append(x) for x in Operators if x not in OperatorsOutput]
NumeralsOutput = []
[NumeralsOutput.append(x) for x in Numerals if x not in NumeralsOutput]
HeadersOutput = []
[HeadersOutput.append(x) for x in Headers if x not in HeadersOutput]

print("There Are ",len(KeywordsOutput),"Keywords: ",KeywordsOutput)
print("\n")
print("There Are ",len(IdentifiersOutput),"Identifiers: ",IdentifiersOutput)
print("\n")
print("There Are ",len(HeadersOutput),"Header Files: ",HeadersOutput)
print("\n")
print("There Are",len(SymbolsOutput),"Symbols:",SymbolsOutput)
print("\n")
print("There Are ",len(NumeralsOutput),"Numerals:",NumeralsOutput)
print("\n")

