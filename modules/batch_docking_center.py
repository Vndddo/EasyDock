# batch_docking_center.py
import os
import re
import glob
import pandas as pd

# Paths
pair_file = os.path.join("..", "input", "pair.txt")
pdb_folder = os.path.join("..", "input", "receptor_ori")
output_file = os.path.join("..", "output", "docking_centers.txt")

def list_pdb_files(root_folder):
    """Recursively list all .pdb/.PDB files under root_folder."""
    files = []
    for pattern in ("**/*.pdb", "**/*.PDB"):
        files.extend(glob.glob(os.path.join(root_folder, pattern), recursive=True))
    return files

def build_file_index(root_folder):
    """Return list of (basename_lower, fullpath)."""
    pdb_files = list_pdb_files(root_folder)
    index = [(os.path.basename(p).lower(), p) for p in pdb_files]
    return index

def find_pdb_file(pdb_id, file_index):
    """Find a pdb file whose basename contains pdb_id (case-insensitive)."""
    pid = str(pdb_id).strip().lower()
    for base, full in file_index:
        if pid in base:
            return full
    return None

def parse_ligand_list(value):
    """Support Nat_Ligand cells like 'NAG', 'NAG; MG', 'NAG,MG', 'NAG / MG'."""
    if value is None:
        return []
    s = str(value).strip()
    if not s or s.lower() in {"na", "not available", "none"}:
        return []
    # split on common separators
    parts = re.split(r"[;,/|]+", s)
    return [p.strip().upper() for p in parts if p.strip()]

def get_ligand_center(pdb_file, ligand_resname):
    """
    Get the geometric center of the FIRST ligand occurrence in the PDB.
    Collect atoms only until residue (chain + resid) changes.
    """
    ligand_resname = ligand_resname.strip().upper()
    coords = []
    collecting = False
    current_chain = None
    current_resid = None

    with open(pdb_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not (line.startswith(("HETATM", "ATOM")) and len(line) >= 54):
                continue

            resname = line[17:20].strip().upper()
            chain   = line[21].strip()
            resid   = line[22:26].strip()

            if not collecting:
                if resname == ligand_resname:
                    collecting = True
                    current_chain = chain
                    current_resid = resid
                else:
                    continue

            # If we moved past the first ligand residue → stop completely
            if (resname != ligand_resname or 
                chain != current_chain or 
                resid != current_resid):
                break

            # Collect atom coordinates
            try:
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                coords.append((x, y, z))
            except ValueError:
                continue

    if coords:
        xs, ys, zs = zip(*coords)
        return (sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs))

    return None

def main():
    # Read pair file (tab-separated). If that fails, try any whitespace.
    try:
        df = pd.read_csv(pair_file, sep="\t", dtype=str)
    except Exception:
        df = pd.read_csv(pair_file, delim_whitespace=True, dtype=str)

    # Normalize columns (support some common header variants)
    cols = {c.lower(): c for c in df.columns}
    if "pdb" not in cols:
        print(f"Error: 'PDB' column not found in {PAIR_FILE}. Found columns: {list(df.columns)}")
        return
    pdb_col = cols["pdb"]

    ligand_col = None
    for cand in ["nat_ligand", "ligand", "native_ligand"]:
        if cand in cols:
            ligand_col = cols[cand]
            break
    if ligand_col is None:
        print(f"Error: 'Nat_Ligand' (or 'Ligand'/'Native_Ligand') column not found in {PAIR_FILE}. Found columns: {list(df.columns)}")
        return

    # Index PDB files once
    file_index = build_file_index(PDB_FOLDER)
    if not file_index:
        print(f"Error: No PDB files found under {PDB_FOLDER}")
        return
    print(f"Indexed {len(file_index)} PDB files under: {PDB_FOLDER}")

    results = ["PDB\tLigand\tX\tY\tZ"]
    missing = 0

    for _, row in df.iterrows():
        pdb_id_raw = (row[pdb_col] or "").strip()
        if not pdb_id_raw:
            continue
        pdb_id = pdb_id_raw.upper()

        # find matching file
        pdb_file = find_pdb_file(pdb_id, file_index)
        if not pdb_file:
            print(f"[!] PDB file not found for {pdb_id}")
            results.append(f"{pdb_id}\t\tNot Found\tNot Found\tNot Found")
            missing += 1
            continue

        ligands = parse_ligand_list(row[ligand_col])
        if not ligands:
            print(f"[!] No ligand specified for {pdb_id} in pair.txt")
            results.append(f"{pdb_id}\t\tNot Found\tNot Found\tNot Found")
            continue

        # try each ligand in order until one is found in the PDB
        center = None
        used_lig = None
        for lig in ligands:
            center = get_ligand_center(pdb_file, lig)
            if center is not None:
                used_lig = lig
                break

        if center is None:
            print(f"[!] None of the ligands {ligands} found in {os.path.basename(pdb_file)}")
            results.append(f"{pdb_id}\t{','.join(ligands)}\tNot Found\tNot Found\tNot Found")
        else:
            x, y, z = center
            print(f"[+] {pdb_id} {used_lig} center = {x:.3f}, {y:.3f}, {z:.3f}")
            results.append(f"{pdb_id}\t{used_lig}\t{x:.3f}\t{y:.3f}\t{z:.3f}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(results))

    print(f"\nSaved results to {OUTPUT_FILE}")
    if missing:
        print(f"Note: {missing} PDB IDs had no matching file. Check folder path and filenames.")

if __name__ == "__main__":
    main()
