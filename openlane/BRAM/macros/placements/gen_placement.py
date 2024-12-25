import re
from array import *
import fileinput
import sys, getopt
import csv
import fabric_params

COL = fabric_params.col
ROW = fabric_params.row
REGFILE = fabric_params.regfile_col
DSP = fabric_params.DSP_col

LUT4AB_size = fabric_params.LUT4AB_size 
DSP_size = fabric_params.DSP_size
RegFile_size = fabric_params.RegFile_size
W_IO_size = fabric_params.W_IO_size 
RAM_IO_size = fabric_params.RAM_IO_size 
N_term_single_size = fabric_params.N_term_single_size 
N_term_single2_size = fabric_params.N_term_single2_size
N_term_RAM_IO_size = fabric_params.N_term_RAM_IO_size 
S_term_single_size = fabric_params.S_term_single_size 
S_term_single2_size = fabric_params.S_term_single2_size
S_term_RAM_IO_size = fabric_params.S_term_RAM_IO_size 
Space = fabric_params.Space
offset_WL = fabric_params.Offset_WL
offset_WR = fabric_params.Offset_WR
offset_H = fabric_params.Offset_H

LUT4AB_W = LUT4AB_size[0]
LUT4AB_H = LUT4AB_size[1]
DSP_W = DSP_size[0]
DSP_H = DSP_size[1]
RegFile_W = RegFile_size[0]
RegFile_H = RegFile_size[1]
N_term_H = N_term_single_size[1]
S_term_H = S_term_single_size[1]
W_IO_W = W_IO_size[0]
W_IO_H = W_IO_size[1]
RAM_IO_W = RAM_IO_size[0]
RAM_IO_H = RAM_IO_size[1]

#offset = 10
x_co = 0
y_co = 0
reg_count = 0
placement = ""
Tile_H = W_IO_H
if REGFILE[0] == 0:
   No_RegFile_col = 0
else:
   No_RegFile_col = len(REGFILE)
if DSP[0] == 0:
   No_DSP_col = 0
else:
   No_DSP_col = len(DSP)
No_LUT4AB_col = COL - No_RegFile_col - No_DSP_col

core_H = ROW*Tile_H + (ROW-1)*Space
core_W = No_LUT4AB_col*LUT4AB_W + No_DSP_col*DSP_W + No_RegFile_col*RegFile_W + (COL-1)*Space 
fabric_H = N_term_H + core_H + S_term_H + 2*Space + 2*offset_H
fabric_W = W_IO_W + core_W + RAM_IO_W + 2*Space + offset_WL + offset_WR

print ('column = ', COL)
print ('row = ', ROW)
print ('LUT4AB col = ', No_LUT4AB_col, 'DSP_col = ',No_DSP_col,'regfile col = ',No_RegFile_col)
print ('fabric_H = ', core_H)
print ('fabric_W = ', core_W)
print ('AREA (XY) = {} x {}'.format(fabric_W, fabric_H))

#try:
#    with open("sdc_template.sdc", 'r') as file :
#        placement = file.read()
#except IOError:
#    print("sdc_template.sdc is not accesstable")

for x in range(COL+2):
    if x==0:
         x_co = offset_WL
    else:
         x_co = offset_WL + W_IO_W + (x-reg_count-1)*LUT4AB_W + reg_count*RegFile_W + x*Space
         #print('x - reg_col -1 =',x-reg_count-1,'reg_count = ',reg_count)
    if REGFILE.count(x) == 1:
         reg_count += 1
         #print('reg col =',x,'reg_count = ',reg_count)

    for y in range(ROW+2):
         Tile = 'Inst_eFPGA.Tile_X'+str(x)+'Y'+str(y)
         if y==0: 
             y_co = fabric_H - N_term_H - offset_H
         elif y==ROW+1:
             y_co = fabric_H - N_term_H - core_H - 2*Space - S_term_H - offset_H
         else:
             y_co = fabric_H - N_term_H - y*Tile_H - y*Space - offset_H

         if x == 0 and y != 0 and y  <= ROW:
             placement += str(Tile)+'_W_IO '+str(x_co)+' '+str(y_co)+' N\n'
         if y == 0 and x != 0 and x <= COL:
             if REGFILE.count(x) == 1:
                 placement += str(Tile)+'_N_term_single2 '+str(x_co)+' '+str(y_co)+' N\n'
             elif DSP.count(x) == 1:
                 placement += str(Tile)+'_N_term_DSP '+str(x_co)+' '+str(y_co)+' N\n'
             else:
                 placement += str(Tile)+'_N_term_single '+str(x_co)+' '+str(y_co)+' N\n'
         if x >= 1 and y >= 1 and x <= COL and y <= ROW: 
             if REGFILE.count(x) == 1:
                 placement += str(Tile)+'_RegFile '+str(x_co)+' '+str(y_co)+' N\n'
             elif DSP.count(x) == 1 and y%2 == 0:
                 Tile = 'Inst_eFPGA.Tile_X'+str(x)+'Y'+str(y-1)+'_X'+str(x)+'Y'+str(y)
                 placement += str(Tile)+'_DSP_tile '+str(x_co)+' '+str(y_co)+' N\n'
             elif DSP.count(x) != 1:
                 placement += str(Tile)+'_LUT4AB '+str(x_co)+' '+str(y_co)+' N\n'
         if y == ROW+1 and x != 0 and x <= COL:
             if REGFILE.count(x) == 1:
                 placement += str(Tile)+'_S_term_single2 '+str(x_co)+' '+str(y_co)+' N\n'
             elif DSP.count(x) == 1:
                 placement += str(Tile)+'_S_term_DSP '+str(x_co)+' '+str(y_co)+' N\n'
             else:
                 placement += str(Tile)+'_S_term_single '+str(x_co)+' '+str(y_co)+' N\n'
         if x == COL+1 and y == 0:
             placement += str(Tile)+'_N_term_RAM_IO '+str(x_co)+' '+str(y_co)+' N\n'
         if x == COL+1 and y >= 1 and y <= ROW: 
             placement += str(Tile)+'_RAM_IO '+str(x_co)+' '+str(y_co)+' N\n'
         if x == COL+1 and y == ROW+1: 
             placement += str(Tile)+'_S_term_RAM_IO '+str(x_co)+' '+str(y_co)+' N\n'
     
if placement:
   with open("./macro_placement.cfg", 'w') as file:
        file.write(placement) 

