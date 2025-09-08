# EasyDock

**EasyDock** is a lightweight batch-automation toolkit for **AutoDock Vina**.  
It streamlines receptor/ligand preparation, defines docking grids, and runs batch docking with summary reports.

---

## Project Overview
Molecular docking is a key method in structure-based drug discovery.  
This toolkit streamlines four essential stages of docking with natural products or synthetic ligands:

1. Ligand Preparation** with MGLTools (`prepare_ligand4.py`)  
2. **Receptor Preparation** with MGLTools (`prepare_receptor4.py`)  
3. **Docking Center Detection** from native ligand coordinates  
4. **Batch Docking Execution** with AutoDock Vina, including global results summary

---

## Installation
Clone the repository:
```bash
git clone https://github.com/yourusername/EasyDock.git
cd EasyDock
pip install -r requirements.txt
```

---

## How to Use
### Ligand Preparation
- **Purpose**: Automates the ligand preparation process (costumisable) to `.pdbqt` files. 
- **Input**: Folder containing ligand files (`.pdb`, `.mol`, or other structural format).
- **Output**: Prepared ligand `.pdbqt` files.
- **Usage**:
```bash
python modules/batch_prep_ligands.py
```

### Receptor Preparation
- **Purpose**: Automates the receptor preparation process (costumisable) to `.pdbqt` files. 
- **Input**: Folder containing receptor files downloaded from PDB.
- **Output**: Prepared receptor `.pdbqt` files.
- **Usage**:
```bash
python modules/batch_prep_receptors.py
```

### Docking Center Detection
- **Purpose**: Automates the docking center detection based on native ligand's coordinate. 
- **Input**: Receptor of interest downloaded from PDB and PDB–Ligand associations (pair.txt).
- **Output**: `.docking_centers.txt` with coordinates.
- **Usage**:
```bash
python modules/batch_docking_center.py
```

### Batch Docking Execution
- **Purpose**: Automates docking of receptor–ligand combinations using predefined docking centers (customisable). 
- **Input**: 
  - Prepared receptor `.pdbqt` files  
  - Prepared ligand `.pdbqt` files  
  - `docking_centers.txt` file (grid centers per receptor)  
  - `combination.txt` file (pairs of receptor–ligand) 
- **Output**:
  - Per-receptor folders with docked `.pdbqt` files and logs  
  - `docking_summary.csv` with best binding scores for all pairs
- **Usage**:
```bash
python modules/batch_autodock.py
```

---

## Requirements:
- Python 3.8+
- pandas
- AutoDock Vina installed
- MGLTools installed (for preparation)

