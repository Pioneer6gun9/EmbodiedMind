#!/usr/bin/env bash
set -e
python evaluation/ablation.py --episodes 100 --out runs/table1_ablation.json
