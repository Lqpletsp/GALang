class Keyword: 
    def __init__(self) -> None:
        self.__Keywords:list = ["out","in","inc","dec", "decl","varchar","int","bool"
                                ,"set"]
        self.__OneVariableCommand:list = ["in"]
        self.__TwoOrMoreVariableCommand:list = ["out","inc","dec","decl","set"]
        self.__Datatypes:list = ["varchar","int","bool"]

    def GetKeywords(self) -> list:return self.__Keywords
    def GetOneVariableCommand(self) -> list: return self.__OneVariableCommand
    def GetTwoOrMoreVariableCommand(self) -> list: return self.__TwoOrMoreVariableCommand
    def GetDataTypes(self) -> list: return self.__Datatypes

class Error: 
    def OutError(self, ErrorType, ErrorLine) -> None:
        print(f"ERROR[{ErrorLine}] : {ErrorType}")
        exit()
    
class Tokenizer:
    def Tokenize(self,line,linenumber) -> list:
        token,Storetokens = "", []
        line = line.rstrip()
        if not line: return None
        inquotation,incomments = False,False
        count = 0
        while count < len(line):
            ch = line[count]

            if ch == '"' and not inquotation:
                inquotation = True
                token += '"'
                count += 1
                continue

            if ch == '"' and inquotation:
                token += '"'
                Storetokens.append(token)
                token = ""
                inquotation = False
                count += 1
                continue

            if inquotation:
                token += ch
                count += 1
                continue

            if ch == '|' and not incomments:
                incomments = True
                count += 1 
                continue
            if ch == '|' and incomments: 
                incomments = False
                count += 1 
                continue
            if incomments:
                count += 1 
                continue

            if ch == " " or ch == ",":
                if token != "":
                    Storetokens.append(token)
                    token = ""
                count += 1 
                continue
            if ch == ";":
                if Storetokens != "":Storetokens.append(token)
                Storetokens.append(";")
                break

            else: 
                token += ch 
                count += 1
        return Storetokens

class Interpreter():
    def __init__(self) -> None: self.__memory = []

    def storevariables(self,val) -> None:
        try:
            self.__memory.append(val)
        except MemoryError:
            print("Memory full, write unsucessful")
            exit()

    def searchvariables(self, VariableName):
        for each in self.__memory: 
            if each[1] == VariableName: return each
        return []

    def out(self,outtoken):
        for iter1 in range(len(outtoken)):
            outputval = ""
            if outtoken[iter1].isdigit():print(outtoken[iter1])
            elif outtoken[iter1][0] == '"' and outtoken[iter1][-1] == '"':print(outtoken[iter1].strip('"'),end="")
            elif outtoken[iter1][0] != '"' and outtoken[iter1][-1] != '"':
                for each in self.__memory:
                    if each[1]==outtoken[iter1]:outputval = each[2]
                if outputval:print(outputval.strip('"'), end="")
                else: return -1,f"Undeclared variable, {outtoken[iter1]}"
            elif outtoken[iter1][0] == '"' and outtoken[iter1][-1]!= '"' or (outtoken[iter1][0] != '"' and outtoken[iter1] == '"'):
                return -1, "Incorrect representation of string"
        print()
        return 1,""

    def inp(self,inpvariable,storedata): #inp because it is a keyword in python... but this is for the in function 
        for iter1 in range(len(self.__memory)): 
            if self.__memory[iter1][1] == inpvariable:
                try:self.__memory[iter1][2] = storedata
                except:self.__memory[iter1].append(storedata)
                return True, ""
        return False, "Varaible not found"

    def set(self,inpvariable,storedata): 
        for iter1 in range(len(self.__memory)): 
            if self.__memory[iter1][1] == inpvariable and self.determinedatatype(storedata) == self.__memory[iter1][0]:
                print(self.determinedatatype(storedata))
                try:self.__memory[iter1][2] = storedata
                except: self.__memory[iter1].append(storedata)
                return True, ""
            elif self.__memory[iter1][1] == inpvariable and not self.determinedatatype(storedata):
                variablestore = self.searchvariables(storedata)
                if not variablestore: return False, "Variable not found"
                elif variablestore[0] == self.__memory[iter1][0]: 
                    try:self.__memory[iter1][2] = variablestore[2]
                    except:self.__memory[iter1].append(variablestore[2])
                    return True, ""
                elif variablestore[0] != self.__memory[iter1][0]: return False, "Incorrect datatype. Cannot store in the said variable"
        return False, "Varaible not found"

    def inc(self,tokens):pass
    def dec(self,tokens):pass

    def decl(self,tokens):
        if not tokens[0].isdigit() and tokens[1].strip('"') in Keyword().GetDataTypes():
            self.storevariables([tokens[1],tokens[0]])
            return True, "" 
        elif tokens[0].isdigit(): return False, "Invalid variable name"
        elif tokens[1] not in Keyword().GetDataTypes(): 
            return False, "Invalid Datatype"

    def determinedatatype(self,value) -> str: #Right now this function is quite useless
        if (value[0] == '"' and value[-1] =='"'): return "varchar"
        elif value.isdigit() and int(value) == float(value): return "int"
        elif value.isdigit() and int(value) != float(value): return "float"
        else: return ""

    def Interpret(self, code) -> None:
        lines,tokenizedcode = code.split("\n"),[]
        for iter1 in range(len(lines)):
            tokenizedline = Tokenizer().Tokenize(lines[iter1],iter1)

            if tokenizedline: 
                if tokenizedline[-1] != ";":
                    Error().OutError("Malformed line. Each line must end with ';'", iter1)

                tokenizedline = [each for each in tokenizedline if each != "" and each != ";"]

                if tokenizedline[0] not in Keyword().GetKeywords():Error().OutError("Every line must begin with a command/funciton, none found", iter1)
                elif tokenizedline[0] in Keyword().GetOneVariableCommand() and (len(tokenizedline) > 2  or len(tokenizedline) < 2):
                    Error().OutError("Length of line does not support one variable command", iter1)
                elif tokenizedline[0] in Keyword().GetTwoOrMoreVariableCommand() and len(tokenizedline)<2:
                    Error().OutError("Length of line does not support two or more tokens command", iter1)

                if tokenizedline[0] == "out":
                    returnval, returnstate = self.out(tokenizedline[1:]) #Put variable name and data
                    if returnval == -1 and returnstate:Error().OutError(returnstate, iter1) #If malformed line for out Keyword
                elif tokenizedline[0] == "in":
                    sudostore = input("")
                    returnval, returnstate = self.inp(tokenizedline[1],sudostore)
                    if not returnval:
                        Error().OutError(returnstate,iter1)
                elif tokenizedline[0] == "inc": pass #Ignore for now... first code a way to assign values and declare variables. 
                elif tokenizedline[0] == "decl":
                    returnval, returnstate = self.decl(tokenizedline[1:])
                    if not returnval: Error().OutError(returnstate, iter1)
                elif tokenizedline[0] == "set": 
                    if len(tokenizedcode)>3: Error.OutError("Malformed line for 'set'", iter1)
                    returnval, returnstate = self.set(tokenizedline[1],tokenizedline[2])
                    if not returnval: Error().OutError(returnstate, iter1)

Code = '''
decl variable1 varchar;
decl variable2 varchar;
decl variable3 int; 
set variable1 "Hello";
out variable1;
set variable2 variable1;
out variable2; 
'''
Interpreter().Interpret(Code)
