# Cyberpunk-Red-Net-Architecture-generator
A generator used to generate NET-Architectures for the Tabletop Game Cyberpunk Red

## Requirements
if you have python installed, you can just run this out of the box, no other packages necessary

## How to run
### Windows
Download the latest windows release [here](https://github.com/benjo121ben/Cyberpunk-Red-Net-Arch-generator/releases) unzip and run `net_arch_gen_2.0.exe`
### Linux and Mac
You will have to download [net_arch_gen.py](./net_arch_gen_2.0.py) and run it with python by yourself.

## Credit 
The program was inspired by and is loosely based on MildarAA's NET-Generator, which I decided to completely redo because of the way the branches were printed.
And while the prints are still not perfect, I prefer it this way.\
My version reuses none of the code, but the input text display is basically a streamlined version of his.

## Foot Note
This algorithm does not use the one outlined in the Rulebook, it is slightly tweaked.\
I've experienced, that ingame, most architectures aren't even close to 10 floors, so the maximum of 18 is usually way too much. To fix this issue, I opted for the possibility to choose the range of floor sizes and I also 
increase the chance of branches on higher floor counts, to spread out the floors more. Though huge gauntlets of death are still possible if you so wish.
