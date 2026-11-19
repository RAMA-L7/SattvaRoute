# FDE-005 golden Tcl template. ARM_SCRIPT and VIA_FLAGS are substituted only.
read_db ARM_SCRIPT
set block [ord::get_db_block]
set zero [$block findNet zero_]
if {$zero ne "NULL"} { $zero setSpecial }
set_debug_level DRT pin_access 1
pin_access VIA_FLAGS
exit
