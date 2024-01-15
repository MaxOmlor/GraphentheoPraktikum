import ast

string = "(.5,.1,1)"
ast.literal_eval(string.replace(" ", ""))