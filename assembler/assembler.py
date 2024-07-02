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

def first_pass(lines):

    symbol_table = {"RAM addresses":
        {
            'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7, 
            'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
            'SCREEN': 16384, 'KBD': 24576, 'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4
        }, "ROM addresses": {}
    }

    rom_address = 0
    for line in lines:
        if line.startswith('(') and line.endswith(')'):
            label = line[1:-1]
            symbol_table['ROM addresses'][label] = rom_address
        else: # only increase the line number/rom address if it is an instruction (not a whitespace or label)
            rom_address += 1
    return symbol_table

def second_pass(lines, symbol_table):
    next_variable_address = 16 # variables refer to an address in the RAM
    binary_code = []

    def translate_a_instruction(line):
        nonlocal next_variable_address
        symbol = line[1:]
        if symbol.isdigit():
            address = int(symbol)
        else:
            if symbol in symbol_table["RAM addresses"]:
                address = symbol_table["RAM addresses"][symbol]
            elif symbol in symbol_table["ROM addresses"]:
                address = symbol_table["ROM addresses"][symbol]
            else: # symbol is a variable
                symbol_table["RAM addresses"][symbol] = next_variable_address
                next_variable_address += 1
                address = symbol_table["RAM addresses"][symbol]
        address = format(address, '016b')
        return address
    
    def translate_c_instruction(instruction):
        comp_table = {
            '0':   '0101010', '1':   '0111111', '-1':  '0111010',
            'D':   '0001100', 'A':   '0110000', '!D':  '0001101', '!A':  '0110001',
            '-D':  '0001111', '-A':  '0110011', 'D+1': '0011111', 'A+1': '0110111',
            'D-1': '0001110', 'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
            'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
            'M':   '1110000', '!M':  '1110001', '-M':  '1110011', 'M+1': '1110111',
            'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000111',
            'D&M': '1000000', 'D|M': '1010101'
        }

        dest_table = {
            None: '000', 'M': '001', 'D': '010', 'MD': '011', 'A': '100', 'AM': '101',
            'AD': '110', 'AMD': '111'
        }

        jump_table = {
            None: '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100',
            'JNE': '101', 'JLE': '110', 'JMP': '111'
        }

        dest, comp, jump = None, None, None
        if '=' in instruction:
            parts = instruction.split('=')
            dest = parts[0].strip()
            instruction = parts[1].strip()
        if ';' in instruction:
            parts = instruction.split(';')
            comp = parts[0].strip()
            jump = parts[1].strip()
        else:
            comp = instruction.strip()
        
        dest_bits = dest_table.get(dest, '000')
        comp_bits = comp_table[comp]
        jump_bits = jump_table.get(jump, '000')
        return ('111' + comp_bits + dest_bits + jump_bits)

    for line in lines:
        if line.startswith('(') and line.endswith(')'):
            continue
        if line.startswith('@'):
            binary_code.append(translate_a_instruction(line))
        else:
            binary_code.append(translate_c_instruction(line))
    return binary_code

def write_file(filename, binary_code):
    with open(filename, 'w') as file:
        for line in binary_code:
            file.write(line + '\n')

def main():
    import sys
    import os

    if len(sys.argv) != 2:
        print("Usage: python3 assembler.py filename.asm")
        return
    input_filename = sys.argv[1]
    basename = os.path.splitext(input_filename)[0]
    output_filename = basename + '.hack'
    lines = read_file(input_filename)
    parsed_lines = parse_lines(lines)
    symbol_table = first_pass(parsed_lines)
    binary_code = second_pass(parsed_lines, symbol_table)
    write_file(output_filename, binary_code)

if __name__ == "__main__":
    main()