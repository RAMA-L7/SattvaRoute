#!/usr/bin/env python3
"""
Failure Case 1: Missing macro timing-view configuration diagnostic.

Diagnoses the case where the macro .lib file is missing or incompatible,
based on actual ORFS error patterns observed during floorplan stage.
"""
import re, sys, os

# ---- Configuration ----
LEF_PATH = "/mnt/d/SattvaRoute/benchmark/design/sattva_sram/macro/sram_x4x4x1.lef"
LIB_PATH = "/mnt/d/SattvaRoute/benchmark/design/sattva_sram/macro/sram_x4x4x1.lib"
CONFIG_PATH = "/mnt/d/SattvaRoute/benchmark/design/sattva_sram/config.mk"

def check_file(path, label):
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    return {"exists": exists, "path": path, "label": label, "size": size}

def main():
    results = {}

    # Check LEF
    results["le"] = check_file(LEF_PATH, "sram_x4x4x1.lef")

    # Check LIB
    results["lib"] = check_file(LIB_PATH, "sram_x4x4x1.lib")

    # Check config.mk for ADDITIONAL_LIBS
    config_lib_ref = None
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            for line in f:
                m = re.search(r'ADDITIONAL_LIBS.*?(lib/[^\s]+)', line)
                if m:
                    config_lib_ref = m.group(1)
                    break
        # Also search more broadly
        if config_lib_ref is None:
            with open(CONFIG_PATH) as f:
                content = f.read()
                m = re.search(r'ADDITIONAL_LIBS.*?(\S+\.lib)', content)
                if m:
                    config_lib_ref = m.group(1)

    results["config_lib_ref"] = config_lib_ref

    # Report
    print("=== Failure Case 1: Missing macro timing-view configuration ===")
    print()
    print(f"LEF file: {results['le']['path']}")
    print(f"  Exists: {results['le']['exists']}, Size: {results['le']['size']} bytes")
    print()
    print(f"Liberty (.lib) file: {results['lib']['path']}")
    print(f"  Exists: {results['lib']['exists']}, Size: {results['lib']['size']} bytes")
    print()
    print(f"Config.mk ADDITIONAL_LIBS reference: {results['config_lib_ref']}")
    print()
    
    # Diagnosis
    if not results["le"]["exists"]:
        print("DIAGNOSIS: LEF file missing — macro geometry unavailable")
        print("  RECOMMENDATION: Restore sram_x4x4x1.lef to benchmark/design/sattva_sram/macro/")
    elif not results["lib"]["exists"]:
        print("DIAGNOSIS: Liberty file missing — macro timing arcs unavailable")
        print("  RECOMMENDATION: Restore sram_x4x4x1.lib to benchmark/design/sattva_sram/macro/")
        print("  or correct the ADDITIONAL_LIBS path in config.mk")
    elif config_lib_ref and results["lib"]["exists"]:
        # Check if the config reference matches the actual file
        actual_basename = os.path.basename(LIB_PATH)
        if actual_basename not in config_lib_ref:
            print("DIAGNOSIS: Liberty path mismatch between config.mk and filesystem")
            print(f"  Config references: {config_lib_ref}")
            print(f"  Actual file: {LIB_PATH}")
            print("  RECOMMENDATION: Fix ADDITIONAL_LIBS in config.mk to match actual .lib path")
        else:
            print("DIAGNOSIS: All macro view files present and properly referenced")
            print("  RECOMMENDATION: No action needed")
    else:
        print("DIAGNOSIS: Unable to determine — check file paths and config.mk")

    print()
    print("Evidence: LEF=" + str(results["le"]["exists"]) + 
          ", LIB=" + str(results["lib"]["exists"]) + 
          ", config_ref=" + str(results["config_lib_ref"]))

if __name__ == "__main__":
    main()