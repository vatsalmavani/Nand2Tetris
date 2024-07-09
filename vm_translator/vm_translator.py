import os, sys
from collections import defaultdict

def read_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines

def parse_lines(lines):
    parsed_lines = defaultdict(list)
    for k,v in lines.items():
        for line in v:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            line = line.split('//')[0].strip() # remove inline comments
            parsed_lines[k].append(line)
    return parsed_lines

class CodeWriter:
    def __init__(self, output_file):
        self.file = open(output_file, 'w')
        self.label_counter = 0
    
    def _write_bootstrap(self):
        self.file.write('// bootstrap code\n')
        self.file.write('@256\nD=A\n@SP\nM=D\n') # set stack pointer to 256
        self._write_call('Sys.init', '0')

    def _write_arithmetic(self, command):
        
        self.file.write(f'// {command}\n')

        def unique_label():
            self.label_counter += 1
            return f"LABEL_{self.label_counter}"

        if command == "add":
            self.file.write('@SP\nAM=M-1\nD=M\nA=A-1\nM=M+D\n')
        elif command == "sub":
            self.file.write('@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n')
        elif command == "and":
            self.file.write('@SP\nAM=M-1\nD=M\nA=A-1\nM=M&D\n')
        elif command == "or":
            self.file.write('@SP\nAM=M-1\nD=M\nA=A-1\nM=M|D\n')
        elif command == "not":
            self.file.write('@SP\nA=M-1\nM=!M\n')
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

    def _write_push_pop(self, command, segment, index, file_name):
        index = int(index)
        self.file.write(f'// {command} {segment} {index}\n')
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
                    f'@{file_name}.{index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
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
                    f'@SP\nAM=M-1\nD=M\n@{file_name}.{index}\nM=D\n'
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

    def _write_label(self, label):
        self.file.write(f'// label {label}\n')
        self.file.write(f'({label})\n')

    def _write_goto(self, label):
        self.file.write(f'// goto {label}\n')
        self.file.write(f'@{label}\n0;JMP\n')

    def _write_if_goto(self, label):
        self.file.write(f'// if-goto {label}\n')
        self.file.write(f'@SP\nAM=M-1\nD=M\n@{label}\nD;JNE\n')

    def _write_call(self, function_name, num_args):
        num_args = int(num_args)
        return_address = f'{function_name}$ret.{self.label_counter}'
        self.label_counter += 1
        self.file.write(f'// call {function_name} {num_args}\n')
        self.file.write(f'@{return_address}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n') # push return address
        self.file.write('@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n') # push LCL
        self.file.write('@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n') # push ARG
        self.file.write('@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n') # push THIS
        self.file.write('@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n') # push THAT
        self.file.write(f'@{num_args}\nD=A\n@5\nD=D+A\n@SP\nD=M-D\n@ARG\nM=D\n') # ARG = SP - 5 - nargs
        self.file.write('@SP\nD=M\n@LCL\nM=D\n') # LCL = SP
        self._write_goto(function_name)
        self._write_label(return_address)

    def _write_function(self, function_name, num_vars):
        self.file.write(f'// function {function_name} {num_vars}\n')
        self._write_label(function_name)
        for _ in range(int(num_vars)):
            self._write_push_pop('push', 'constant', '0', '')

    def _write_return(self):
        self.file.write('// return\n')
        self.file.write('@LCL\nD=M\n@R13\nM=D\n') # end_frame (R13) = LCL
        self.file.write('@5\nA=D-A\nD=M\n@R14\nM=D\n') # return_address (R14) = *(end_frame - 5)
        self.file.write('@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n') # *ARG = pop()
        self.file.write('@ARG\nD=M+1\n@SP\nM=D\n') # SP = ARG + 1
        self.file.write('@R13\nAM=M-1\nD=M\n@THAT\nM=D\n') # THAT = *(end_frame - 2)
        self.file.write('@R13\nAM=M-1\nD=M\n@THIS\nM=D\n') # THIS = *(end_frame - 1)
        self.file.write('@R13\nAM=M-1\nD=M\n@ARG\nM=D\n') # ARG = *(end_frame - 3)
        self.file.write('@R13\nAM=M-1\nD=M\n@LCL\nM=D\n') # LCL = *(end_frame - 4)
        self.file.write('@R14\nA=M\n0;JMP\n') # goto return_address

    def write(self, parsed_lines):
        self._write_bootstrap()
        for file, lines in parsed_lines.items():
            for line in lines:
                line = line.split()
                if len(line) == 1:
                    command = line[0]
                    if command == 'return':
                        self._write_return()
                    else:
                        self._write_arithmetic(command)
                elif len(line) == 2:
                    command, label = line[0], line[1]
                    if command == 'label':
                        self._write_label(label)                    
                    elif command == 'goto':
                        self._write_goto(label)
                    else:
                        self._write_if_goto(label)
                else:
                    command, func_or_seg, val = line[0], line[1], line[2]
                    if command == 'function':
                        self._write_function(func_or_seg, val)
                    elif command == 'call':
                        self._write_call(func_or_seg, val)
                    else:
                        self._write_push_pop(command, func_or_seg, val, file)

    def close(self):
        self.file.close()

def handle_file(abs_path):
    basename = os.path.basename(abs_path).split('.')[0]
    output_filename = os.path.splitext(abs_path)[0] + '.asm'
    lines = {basename: read_file(abs_path)}
    parsed_lines = parse_lines(lines)
    code_writer = CodeWriter(output_filename)
    code_writer.write(parsed_lines)
    code_writer.close()

def handle_dir(abs_path):
    basename = os.path.basename(abs_path)
    output_filename = abs_path + '/' + basename + '.asm'
    file_list = os.listdir(abs_path) # list of all the files in this folder
    files = [(abs_path + '/' + file) for file in file_list if file.endswith('.vm')]
    lines = defaultdict(list)
    for file in files:
        temp_lines = read_file(file)
        file_basename = os.path.basename(file).split('.')[0]
        lines[file_basename].extend(temp_lines)
    parsed_lines = parse_lines(lines)
    code_writer = CodeWriter(output_filename)
    code_writer.write(parsed_lines)
    code_writer.close()


def main():
    if len(sys.argv) != 2:
        print("Usage:\npython3 vm_translator.py filename.asm\nOR\npython3 vm_translator.py path/to/folder")
        return
    ipt = sys.argv[1]
    abs_path = os.path.abspath(ipt)
    if os.path.isfile(abs_path):
        handle_file(abs_path)
    elif os.path.isdir(abs_path):
        handle_dir(abs_path)
    else:
        print(f"no file or folder found: {ipt}")


if __name__ == "__main__":
    main()