# HACK VM translator

## Overview

This project is part of the NAND2Tetris course, which aims to build a complete computer system from the ground up. The Hack VM translator translates Hack VM language programs into Hack assembly language.

## Features

* Translates Hack VM language to Hack assembly language.
* Supports arithmetic and logical commands.
* Handles memory access commands.
* Processes branching and looping commands.
* Manages function calls and returns.

## Requirements

* Python 3.x

## Usage

**Input**: The VM translator expects either a text file containing Hack VM code or a directory containing a set of such files. Each line can be a command or a comment.

**Output**: The output is a single text file containing the HACK assembly code. The generated .asm file can be found in the same directory as the input file/directory.

### Running the assembler:

```bash
python3 vm_translator.py path/to/file.vm
```
OR
```bash
python3 vm_translator.py path/to/directory/
```

## Implementation Details

### Files

* `vm_translator.py`: The main VM translator script.


### Functions

* **read_file(filename)**: reads the current VM file
* **handle_file(abs_path)**: generates the assembly code for a single file
* **handle_dir(abs_path)**: generates a single assembly file (.asm) for all VM files in the directory
* **parse_lines(lines)**: creates a dictionary, mapping the VM file to its corresponding VM commands, after removing the comments and whitespaces

### `CodeWriter` class

* **_write_bootstrap()**: adds bootstrap code
* **_write_arithmetic(command)**: handles arithmetic and logical VM commands - `add`, `sub`, `neg`, `and`, `or`, `not`, `eq`, `gt` and `lt`
* **_write_push_pop(command, segment, index, file_name)**: handles `push` and `pop` commands for all memory segments - `local`, `argument`, `this`, `that`, `static`, `temp`, `pointer` and `constant`.
* **_write_label(label)**: generates assembly code to add a label
* **_write_goto(label)**: handles unconditional jump commands
* **_write_if_goto(label)**: handles conditional jump commands
* **_write_call(function_name, num_args)**: pushes required data to the stack and jumps to the called function
* **_write_function()**: generates assembly for function declarations
* **_write_return()**: restores the previous state and continues execution from where it left off
* **write(parsed_lines)**: This is the only public method in `CodeWriter` class. Writes the HACK assembly code in the output file.

## Error Handling

This VM translator does NOT check for any errors in the VM code. It is assumed that the VM code is generated by the HACK compiler and is error-free.

## Testing

The VM translator has been thoroughly tested with various VM codes:
* Simple programs that include stack testing, arithmetic and logical commands and various memory access commands.
* Programs with branching and looping commands.
* Complex programs with recursive function calls.
* Complex programs with more than one user-defined classes.

The tests can be reproduced using the supplied CPU Emulator in the Nand2Tetris course, following the instructions provided in the course materials.