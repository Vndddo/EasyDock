# batch_prepare_ligand.py
import os
import glob
import subprocess
from pathlib import Path

# Configurations
mgltools_home = r"C:\Program Files (x86)\MGLTools-1.5.7"
mglpython     = os.path.join(mgltools_home, "Python.exe")
prep_lig      = os.path.join(mgltools_home, "Lib", "site-packages",
                             "AutoDockTools", "Utilities24", "prepare_ligand4.py")

def main():
    lig_folder = input("Enter the folder containing ligand files (.pdb or .mol2): ").strip()
    if not os.path.isdir(lig_folder):
        print(f"Error: {lig_folder} is not a valid directory")
        return

    # sanity checks
    if not os.path.exists(mglpython):
        print(f"Error: MGLTools Python not found at:\n  {MGLPYTHON}")
        return
    if not os.path.exists(prep_lig):
        print(f"Error: prepare_ligand4.py not found at:\n  {PREP_LIG}")
        return

    # collect ligands
    ligands = []
    ligands += glob.glob(os.path.join(lig_folder, "*.pdb"))
    ligands += glob.glob(os.path.join(lig_folder, "*.PDB"))
    ligands += glob.glob(os.path.join(lig_folder, "*.mol2"))
    ligands += glob.glob(os.path.join(lig_folder, "*.MOL2"))

    if not ligands:
        print("No .pdb or .mol2 files found.")
        return

    for lig_path in ligands:
        lig_path = Path(lig_path)
        cwd      = str(lig_path.parent)              # run from ligand folder
        in_name  = lig_path.name                     # pass ONLY the filename
        out_name = lig_path.with_suffix(".pdbqt").name

        print(f"Processing {in_name} → {out_name}")

        # -A hydrogens: add H if missing
        # -U nphs_lps: remove non-polar H and lone pairs (ADT convention)
        cmd = [
            mglpython, prep_lig,
            "-l", in_name,
            "-o", out_name,
            "-A", "hydrogens",
            "-U", "nphs_lps",
        ]

        try:
            subprocess.run(cmd, cwd=cwd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {in_name}: {e}")

    print("Batch ligand preparation complete.")
    
if __name__ == "__main__":
    main()
