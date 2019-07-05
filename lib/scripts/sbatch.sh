#!/bin/bash
#SBATCH --partition=skl_usr_dbg
#SBATCH --account=INF19_npqcd_0
#SBATCH --nodes=1
#SBATCH --time 00:29:30
#SBATCH --job-name={jobname}
#SBATCH --error=stderr{i}_{time}.txt
#SBATCH --output=stdout{i}_{time}.txt

# module load intel
# module load mkl

# mkdir -p /marconi_scratch/userexternal/gclement/CDTRk/cdt4d-r2/grid_V8kS_g2m1.0/logs

module load python

declare -a points_strings={points}

for p in "${{points_strings[@]}}"
do
    eval $p
    cd $point_dir
    python3 $make
    nohup python3 $PWD/$launch &
    cd ..
done

# if [ ! -f /marconi_scratch/userexternal/gclement/CDTRk/cdt4d-r2/grid_V8kS_g2m1.0/data_0/stopfile.txt ]
# then 
#   sbatch $0
# fi 
