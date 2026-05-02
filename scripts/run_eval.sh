#!/usr/bin/env bash
set -e
python evaluation/run_eval.py --config configs/eval_red_block_blue_box.yaml --episodes 100
