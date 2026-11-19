# FDE-005 golden Tcl template. /mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/scratch/arm_a/4_cts.odb and  are substituted only.
read_db /mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/scratch/arm_a/4_cts.odb
set block [ord::get_db_block]
set zero [$block findNet zero_]
if {$zero ne "NULL"} { $zero setSpecial }
set_debug_level DRT pin_access 1
pin_access 
exit
