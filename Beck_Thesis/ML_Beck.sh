#!/bin/bash
#SBATCH -n 24
#SBATCH -t 0-12:00:00 
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=beckdeyoung816@gmail.com

source ~/miniconda3/etc/profile.d/conda.sh
conda activate beck_env 

declare -a coasts=('NE_Atlantic_1' 'NE_Atlantic_2' 'NE_Pacific' 'Japan')

declare -a losses=('mse' \
                'Gumbel')

num_procs=6

declare -a pids=( )

for coast in "${!coasts[@]}"; do
    for loss in "${!losses[@]}"; do
        while (( ${#pids[@]} >= num_procs )); do
            sleep 0.2
            for pid in "${!pids[@]}"; do
                kill -0 "$pid" &>/dev/null || unset "pids[$pid]"
            done
        done
        python -W ignore ML_env_Coast.py ${coasts[$coast]} 'ALL' ${losses[$loss]} & pids["$!"]=1
done
done
wait
