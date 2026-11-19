#!/bin/bash
cd "/mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/experiment_a" || exit 9
/usr/local/bin/openroad -no_init -exit "/mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/experiment_a/pin_access_a.tcl" > "/mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/logs/experiment_a.log" 2>&1
rc=$?
echo "$rc" > "/mnt/d/SattvaRoute/experiments/FDE-005/FDE-005-20261119T135453Z-4d06/evidence/experiment_a.rc"
echo "ARM_A_RC=$rc"
