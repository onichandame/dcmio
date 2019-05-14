# dcmio

A simple DICOM input/output toolkit. Currently only supports Python 3.X

## Author

Xiao Zhang

Special thanks given to:

- **Pei-Yi Lee** for doing the validation

- **Wei-Lin Chen** for leading the project and firing the motivation

## Goal&Motivation

The motivation comes from the development of a proprietary software in the company I work in. The final goal of this toolkit is to support the proprietary software

## Current Status

This project has been frozen because a toolkit which better suits out situation was found. Everyone is welcome to clone from, contribute to and redistribute it in any form so long as my comapny does not hold it back.

## Instruction

This section describes the basic structure and the designated usage of **dcmio**

### Read DICOM

#### Linux

To run **dcmio**, you need to install python 3.X

```bash
./test.py -i <input DICOM path(with filename)> -o <output csv path(without filename)> <-p> <-t>
```

This command will always output header file as a *.csv* table.

Add `-p` if you want to output pixel data together with the DICOM header

Add `-t` if you want to save the tree view diagram in *<input filename>-treeview.txt* in the output path

To do:
- read from multiple DICOM files in directories of customized levels.
- write to DICOM RT-Structure

#### Windows

Don't know yet

### Basic Structure

The returned object by calling `dcm_read` is a DTree instance. The structure of DTree is basically a table (in the context of database). For more details, see <https://en.wikipedia.org/wiki/Table_(database)>.

Keeping the concept of columns and rows of databases in mind, each row in DTree represents an attribute in DICOM IOD. For the definition of attribute, see <http://dicom.nema.org/medical/dicom/current/output/html/part01.html#chapter_3>

The DTree has 5 branches of type DBranch: tag(xxxx,xxxx), VR(xx), VM(x), name, value. Each branch is filled with the values of the type indicated by the name of the branch.

### Example Usage

The designated use cases where **dcmio** will be called is reading from and writing to DICOM files.

The example of reading from a DICOM file has been given above. The example code used to write a DTree instance into a DICOM file has been give in the test.py code
