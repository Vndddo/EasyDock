# EasyDock

**EasyDock** is a lightweight batch-automation toolkit for **AutoDock Vina**.  
It streamlines receptor/ligand preparation, defines docking grids, and runs batch docking with summary reports.

---

## Features
- Batch ligand preparation (MGLTools `prepare_ligand4.py`)
- Batch receptor preparation (MGLTools `prepare_receptor4.py`)
- Automatic docking center detection from native ligands
- Batch docking for receptor–ligand combinations
- Global summary CSV with best binding scores

---

## Installation
Clone the repository:
```bash
git clone https://github.com/yourusername/EasyDock.git
cd EasyDock
pip install -r requirements.txt
