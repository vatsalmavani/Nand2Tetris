import re

pattern = r'(".*?"|\b\w+\b|[{}()\[\].,;+\-*/&|<>=~]|//.*\n)'
string = '''hello

world   /*
fuck

this comment // is this deleted
// too?

*/
how
"hello how are you" {} // fuck this comment

are you
)'''
string = re.sub(r'//.*\n', '', string)
string = re.sub(r'/\*.*\*/', '', string, flags=re.DOTALL)
matches = re.findall(pattern, string)
print(matches)