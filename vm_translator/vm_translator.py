def read_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines

def parse_lines(lines):
    parsed_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        line = line.split('//')[0].strip() # remove inline comments
        parsed_lines.append(line)
    return parsed_lines

class CodeWriter:
    def __init__(self, output_file):
        self.file = open(output_file, 'w')
        self.label_counter = 0

    def write_arithmetic(self, command):

        def unique_label():
            self.label_counter += 1
            return f"LABEL_{self.label_counter}"

        if command == "add":
            self.file.write('@SP\nAM=M-1\nD=M\nA=A-1\nM=M+D\n')
        elif command == "sub":
            self.file.write('@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n')
        elif command == "neg":
            self.file.write('@SP\nA=M-1\nM=-M\n')
        elif command == "eq":
            label_true = unique_label()
            label_end = unique_label()
            self.file.write(
                f'@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@{label_true}\nD;JEQ\n'
                f'@SP\nA=M-1\nM=0\n@{label_end}\n0;JMP\n'
                f'({label_true})\n@SP\nA=M-1\nM=-1\n({label_end})\n'
            )
        elif command == "gt":
            label_true = unique_label()
            label_end = unique_label()
            self.file.write(
                f'@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@{label_true}\nD;JGT\n'
                f'@SP\nA=M-1\nM=0\n@{label_end}\n0;JMP\n'
                f'({label_true})\n@SP\nA=M-1\nM=-1\n({label_end})\n'
            )
        elif command == "lt":
            label_true = unique_label()
            label_end = unique_label()
            self.file.write(
                f'@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@{label_true}\nD;JLT\n'
                f'@SP\nA=M-1\nM=0\n@{label_end}\n0;JMP\n'
                f'({label_true})\n@SP\nA=M-1\nM=-1\n({label_end})\n'
            )
        elif command == "and":
            self.file.write('@SP\nAM=M-1\nD=M\nA=A-1\nM=M&D\n')
        elif command == "or":
            self.file.write('@SP\nAM=M-1\nD=M\nA=A-1\nM=M|D\n')
        elif command == "not":
            self.file.write('@SP\nA=M-1\nM=!M\n')

    def write_push_pop(self, command, segment, index):
        index = int(index)
        if command == 'push':
            if segment == 'constant':
                self.file.write(f'@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
            elif segment in ('local', 'argument', 'this', 'that'):
                segment_base = {
                    'local': 'LCL',
                    'argument': 'ARG',
                    'this': 'THIS',
                    'that': 'THAT'
                }
                self.file.write(
                    f'@{segment_base[segment]}\nD=M\n@{index}\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                )
            elif segment == 'static':
                self.file.write(
                    f'@{self.file}.{index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                )
            elif segment == 'temp':
                self.file.write(
                    f'@{5+index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                )
            elif segment == 'pointer':
                if index == 0:
                    self.file.write(
                        f'@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                    )
                elif index == 1:
                    self.file.write(
                        f'@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                    )

        elif command == 'pop':
            if segment in ('local', 'argument', 'this', 'that'):
                segment_base = {
                    'local': 'LCL',
                    'argument': 'ARG',
                    'this': 'THIS',
                    'that': 'THAT'
                }
                self.file.write(
                    f'@{segment_base[segment]}\nD=M\n@{index}\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n'
                )
            elif segment == 'static':
                self.file.write(
                    f'@SP\nAM=M-1\nD=M\n@{self.file}.{index}\nM=D\n'
                )
            elif segment == 'temp':
                self.file.write(
                    f'@SP\nAM=M-1\nD=M\n@{5+index}\nM=D\n'
                )
            elif segment == 'pointer':
                if index == 0:
                    self.file.write(
                        f'@SP\nAM=M-1\nD=M\n@THIS\nM=D\n'
                    )
                elif index == 1:
                    self.file.write(
                        f'@SP\nAM=M-1\nD=M\n@THAT\nM=D\n'
                    )

    def write(self, lines):
        for line in lines:
            line = line.split()
            if len(line) == 1:
                self.write_arithmetic(line)
            else:
                self.write_push_pop(line[0], line[1], line[2])

    def close(self):
        self.file.close()

def main():
    import sys
    import os

    if len(sys.argv) != 2:
        print("Usage: python3 assembler.py filename.asm")
        return
    input_filename = sys.argv[1]
    basename = os.path.splitext(input_filename)[0]
    output_filename = basename + '.asm'
    lines = read_file(input_filename)
    parsed_lines = parse_lines(lines)
    code_writer = CodeWriter(output_filename)
    code_writer.write(parsed_lines)
    code_writer.close()

if __name__ == "__main__":
    main()