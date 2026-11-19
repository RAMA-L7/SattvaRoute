#!/bin/bash
cd "/mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/experiment_b" || exit 9
/usr/local/bin/openroad -no_init -exit "/mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/experiment_b/pin_access_b.tcl" > "/mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/logs/experiment_b.log" 2>&1
rc=$?
echo "$rc" > "/mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/evidence/experiment_b.rc"
echo "ARM_B_RC=$rc"
