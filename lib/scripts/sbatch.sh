#!/bin/bash
#SBATCH --partition={arch}_usr_{queue}
#SBATCH --account={account}
#SBATCH --nodes=1
#SBATCH --time {qtime}:30
#SBATCH --job-name={jobname}

# #SBATCH --error=stderr{i}_{time_}.txt
# #SBATCH --output=stdout{i}_{time_}.txt
# module load intel
# module load mkl

# mkdir -p /marconi_scratch/userexternal/gclement/CDTRk/cdt4d-r2/grid_V8kS_g2m1.0/logs

module load python/3.6.4
module load gnu/7.3.0

declare -a points_strings={points}

for p in "${{points_strings[@]}}"
do
    cd ..
    eval $p
    cd $point_dir
    # python3 $make
    nohup python3 $PWD/$launch &
done

cd ../{sbatch_dir}

wait

# if [ ! -f /marconi_scratch/userexternal/gclement/CDTRk/cdt4d-r2/grid_V8kS_g2m1.0/data_0/stopfile.txt ]
# then
#   sbatch $0
# fi
