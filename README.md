# dcmio

A simple yet actively developing DICOM input/output toolkit. Currently only supports Python 3.X

## Author

Xiao Zhang

## Goal&Motivation

The motivation comes from the development of NeuboronPlan. The final goal of this toolkit is to support the NeuboronPlan project

## Instruction

This section describes the basic structure and designated usage of **dcmio**

### Read DICOM

#### Linux

To run **dcmio**, you need to install python 3.X

```bash
./test.py -i <input DICOM path(with filename)> -o <output csv path(without filename)> <-p> <-t>
```

Add `-p` if you want to output pixel data instead of DICOM header

Add `-t` if you want to save the tree view diagram in *treeview.txt* in the output path

#### Windows

Don't know yet

### Basic Structure

The returned object by calling `dcmRead` is a list of attributes. For definition of attribute, see <http://dicom.nema.org/medical/dicom/current/output/html/part01.html#chapter_3>

Each attribute consists of a `tag` object and a `value` object

#### tag

|   code  | VR | VM | name |
| -------- | -- | -- | ---- |
| \<8-digit hex number\> | \<2-char\> | \<1-digit decimal(1-4)\> | \<string\> |

#### value

The type of value depends on the VR of the corresponding tag. Python normally disregards type so the user may read the value regardless of the type. But you need to KNOW what the type it should be in case you need to manipulate the `attribute` object directly
