# batch_autodock.py
import os
import subprocess
from datetime import datetime
import pandas as pd

# Configuration
vina_exe = r"C:\Program Files (x86)\The Scripps Research Institute\Vina\vina.exe"
exhaustiveness = 50

# Paths
receptor_folder = os.path.join("..", "input", "receptor_ori")
ligand_folder   = os.path.join("..", "input", "test_comp")
output_folder   = os.path.join("..", "output")
coord_file      = os.path.join("..", "docking_centers.txt")
combo_file      = os.path.join("..", "combination.txt")
summary_file    = os.path.join(output_folder, "docking_summary.csv")

# Functions
def load_coordinates(coord_file):
    """Reads coordinate .txt file into dataframe"""
    return pd.read_csv(coord_file, sep=r"\s+")

def load_combinations(combo_file):
    """Reads receptor-ligand combinations"""
    return pd.read_csv(combo_file, sep=r"\t+")

def parse_vina_log(log_file):
    """Extract best binding energy from vina log file"""
    best_score = None
    try:
        with open(log_file, "r") as f:
            for line in f:
                if line.strip().startswith("1 "):  # first docking mode
                    parts = line.split()
                    if len(parts) >= 2:
                        best_score = float(parts[1])
                        break
    except Exception as e:
        print(f"[WARNING] Could not parse {log_file}: {e}")
    return best_score

def run_vina(receptor, ligand, x, y, z):
    """Run AutoDock Vina for receptor-ligand pair with given coordinates"""

    # Make receptor-specific subfolder
    receptor_out_dir = os.path.join(output_folder, receptor)
    os.makedirs(receptor_out_dir, exist_ok=True)

    receptor_file = os.path.join(receptor_folder, receptor + ".pdbqt")
    ligand_file   = os.path.join(ligand_folder, ligand + ".pdbqt")

    if not os.path.exists(receptor_file):
        print(f"[ERROR] Receptor file not found: {receptor_file}")
        return None
    if not os.path.exists(ligand_file):
        print(f"[ERROR] Ligand file not found: {ligand_file}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{receptor}_{ligand}_{timestamp}"
    out_file = os.path.join(receptor_out_dir, out_name + ".pdbqt")
    log_file = os.path.join(receptor_out_dir, out_name + ".log")

    vina_cmd = [
        vina_exe,
        "--receptor", receptor_file,
        "--ligand", ligand_file,
        "--center_x", str(x),
        "--center_y", str(y),
        "--center_z", str(z),
        "--size_x", "40",
        "--size_y", "40",
        "--size_z", "40",
        "--exhaustiveness", str(exhaustiveness),
        "--out", out_file,
        "--log", log_file
    ]

    print(f"[INFO] Running Vina for {receptor} and {ligand} ...")
    subprocess.run(vina_cmd)

    # Parse best score
    score = parse_vina_log(log_file)
    return {"Receptor": receptor, "Ligand": ligand, "Score": score, "LogFile": log_file}

def main():
    df_coords = load_coordinates(coord_file)
    df_combos = load_combinations(combo_file)

    results = []

    for i, row in df_combos.iterrows():
        receptor = row["Receptor"].strip()
        ligand   = row["Ligand"].strip()

        # Look up coordinates for this receptor
        if receptor not in df_coords["PDB"].values:
            print(f"[WARNING] No coordinates found for {receptor}, skipping...")
            continue

        coords = df_coords[df_coords["PDB"] == receptor].iloc[0]
        x, y, z = coords["X"], coords["Y"], coords["Z"]

        # Run docking
        res = run_vina(receptor, ligand, x, y, z)
        if res:
            results.append(res)

    # Save summary table
    if results:
        df_summary = pd.DataFrame(results)
        df_summary.to_csv(summary_file, index=False)
        print(f"[INFO] Docking summary saved to {summary_file}")
    else:
        print("[INFO] No results to summarize.")

if __name__ == "__main__":
    main()
