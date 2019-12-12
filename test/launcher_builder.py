from sys import argv, exit
from os import system, popen

if(len(argv)<2):
    print("usage: python3 ",argv[0], " <input file>")
    exit(1)

fname = argv[1]
fname_launcher = fname+"_launcher.sh"
try:
    inputfile = open(fname+".txt","r")
    exec(inputfile.read())
except IOError:
    raise IOError("Input file '%s' doesn't exists" % (inputfile+".txt"))

if len(params)>48:
    print("Unsupported more than 48 cores")

partition = "skl_usr_dbg"
account = "INF19_npqcd_0"

timestring="23:59:59"
if partition[-3:]=="dbg":
    timestring = "00:29:59"

#  
#  usage:
#  ./main  <num slices> <lambda> <beta> [--main_dir =simulation] [--confname =conf] [--w_22 =0.1] [--w_24 =0.2] [--max_iters =-1] [--walltime =-1] [--meas_Vprofile =-1] [--meas_Qcharge =-1] [--meas_plaquette =-1] [--meas_torelon =-1] 
#  

with open(fname_launcher,"w") as f:
    f.write("#!/bin/bash\n"
              "#SBATCH --partition=%s\n"
              "#SBATCH --account=%s\n"
              "#SBATCH --nodes=1\n"
              "#SBATCH --time=%s\n"
              "#SBATCH --job-name=CDT2DU1-%s\n"
              "#SBATCH --output=log_%s.out\n" % (partition,account,timestring,fname,fname))
    f.write('\nmodule load intel\nmodule load mkl\n# opzione per ottimizzare per skl su icc: -xMIC-AVX512\n')

    f.write("\nif [ -t %s ];then exit 1;fi\n" % (fname+"/diverging_points"))
    f.write("\nrm -f %s %s\n" % (fname+"/all_fine",fname+"/stop"))

    f.write('\nnparams=%d\n'% len(params))

    for i in range(len(params)):
        f.write('mkdir -p %s\n' % (fname+"/sim_"+str(i)))

    for i in range(len(params)):
        f.write('./main %d %f %f --main_dir %s --walltime %d --w_22 %f --w_24 %f --max_V %d --meas_V %d --meas_Vprofile %d --meas_Qcharge %d --meas_plaquette %d --meas_torelon %d > %s &\n' %(Tslices,params[i,0],params[i,1],fname+"/sim_"+str(i),walltime,w_22,w_24,max_V,meas_V,meas_Vprofile,meas_Qcharge,meas_plaquette, meas_torelon, fname+"/sim_"+str(i)+"/log"))
	
    f.write('wait\n')

    if resub:
        f.write("var=$(ls %s/*/all_fine | wc -l)\n"%(fname))
        f.write("stp=$(ls %s/*/stop | wc -l)\n"%(fname))
        f.write("if [ $var -gt $((($nparams*2)/3)) ];then touch %s; if [ $stp -eq $nparams ];then sbatch $0;fi ;else echo $var > %s ;fi" % (fname+"/all_fine", fname+"/diverging_points"))
    

system('chmod +x %s' % fname_launcher)
#    os.system('chmod +x %s/sub_%s.sh'%(dname,runflag))  

