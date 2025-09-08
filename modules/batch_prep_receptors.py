# batch_prepare_receptors.py
import os
import glob
import subprocess
from pathlib import Path

# Configurations
mgltools_home = r"C:\Program Files (x86)\MGLTools-1.5.7"
mglpython     = os.path.join(mgltools_home, "Python.exe")
prep_res      = os.path.join(mgltools_home, "Lib", "site-packages",
                             "AutoDockTools", "Utilities24", "prepare_receptor4.py")

def main():
    res_folder = input("Enter the folder containing PDB files: ").strip()
    if not os.path.isdir(res_folder):
        print(f"Error: {res_folder} is not a valid directory")
        return

    # sanity checks
    if not os.path.exists(mglpython):
        print(f"Error: MGLTools Python not found at:\n  {MGLPYTHON}")
        return
    if not os.path.exists(prep_res):
        print(f"Error: prepare_receptor4.py not found at:\n  {PREP_RES}")
        return

    # collect receptors
    receptors = []    
    receptors += glob.glob(os.path.join(res_folder, "*.pdb"))
    receptors += glob.glob(os.path.join(res_folder, "*.PDB"))

    if not receptors:
        print("No .pdb files found.")
        return

    for res_path in receptors:
        res_path = Path(res_path)
        cwd      = str(res_path.parent)              # run from receptor folder
        in_name  = res_path.name                     # pass ONLY the filename
        out_name = res_path.with_suffix(".pdbqt").name

        print(f"Processing {in_name} → {out_name}")

        # -A hydrogens: add H if missing
        # -U nphs_lps: remove non-polar H and lone pairs (ADT convention)
        cmd = [
            mglpython, prep_res,
            "-r", in_name,
            "-o", out_name,
            "-A", "checkhydrogens",
            "-e", "TRUE"
            "-U", "nphs_lps_waters_nonstdres"
        ]

        try:
            subprocess.run(cmd, cwd=cwd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {in_name}: {e}")

    print("Batch receptor preparation complete.")
    
if __name__ == "__main__":
    main()
