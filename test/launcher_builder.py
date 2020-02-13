from sys import argv, exit
from os import system, popen, getcwd

if(len(argv)<2):
    print("usage: python3 ",argv[0], " <input file>")
    exit(1)

fname = argv[1].replace(".txt","")
fname_launcher = fname+"_launcher.sh"
fname_stopper = fname+"_stopper.sh"

# default values
init_waist=3
max_iters=-1
walltime=-1
w_22=0.05
w_24=0.1
max_V=50000
meas_V=-1
meas_Vprofile=-1
meas_Qcharge=-1
meas_plaquette=-1
meas_torelon=-1
fix_V=-1
fix_V_rate=1e-8
fix_V_each=10

seeds=[]

try:
    inputfile = open(fname+".txt","r")
    exec(inputfile.read())
except IOError:
    raise IOError("Input file '%s' doesn't exists" % (inputfile+".txt"))

pwd=getcwd()+"/"
if(len(seeds)==0):
    seeds = 100+np.random.choice(1000000,size=len(params),replace=False)

launch_command="bash"
if machine == "marco":
    if len(params)>48:
        print("Unsupported more than 48 cores")
        sys.exit(1)

    partition = "skl_usr_dbg"
    account = "INF20_npqcd"

    timestring="23:59:59"
    if partition[-3:]=="dbg":
        timestring = "00:29:59"
    
    launch_command="sbatch"

elif machine == "pierone":
    if len(params)>40:
        print("Unsupported more than 48 cores")
        sys.exit(1)

    partition = "workq"

    timestring="23:59:59"
    launch_command="echo cannot relaunch" #"qsub"
    

system("mkdir -p %s" % fname)
np.savetxt("%s/params.txt" % fname, params)

with open(fname_launcher,"w") as f:
    f.write("#!/bin/bash\n")
    if machine=="marco":
        f.write( "#SBATCH --partition=%s\n"
                  "#SBATCH --account=%s\n"
                  "#SBATCH --nodes=1\n"
                  "#SBATCH --time=%s\n"
                  "#SBATCH --job-name=CDT2DUN%s\n"
                  "#SBATCH --output=log_%s.out\n" % (partition,account,timestring,fname,fname))
        f.write('\nmodule load intel\nmodule load mkl\n# opzione per ottimizzare per skl su icc: -xMIC-AVX512\n')
    elif machine=="pierone":
        f.write(  "#PBS -q %s\n"
                  "#PBS -l walltime=%s\n"
                  "#PBS -l select=1:ncpus=%d\n"
                  "#PBS -N %s\n"
                  "#PBS -k oe\n" % (partition,timestring,len(params),fname))

    f.write("\ncd %s\n" % pwd)

    f.write("\nif [ -t %s ];then exit 1;fi\n" % (fname+"/diverging_points"))
    f.write("\nrm -f %s/all_fine %s/*/stop\n" % (fname,pwd+fname))

    f.write('\nnparams=%d\n'% len(params))

    f.write('mkdir -p %s/sim_{%d..%d}\n\n' % (fname,0,len(params)-1))

    for i in range(len(params)):
       f.write('./main %d %s %s --main_dir %s --init_waist %d --max_iters %d --walltime %d --seed %d --w_22 %s --w_24 %s --max_V %d --meas_V %d --meas_Vprofile %d --meas_Qcharge %d --meas_plaquette %d --meas_torelon %d --fix_V %d --fix_V_rate %s --fix_V_each %d >> %s &\n' %(Tslices,'{:.16}'.format(params[i,0]),'{:.16}'.format(params[i,1]),fname+"/sim_"+str(i),init_waist,max_iters,walltime,seeds[i],'{:.16}'.format(w_22),'{:.16}'.format(w_24),max_V,meas_V,meas_Vprofile,meas_Qcharge,meas_plaquette, meas_torelon, fix_V, fix_V_rate, fix_V_each, fname+"/sim_"+str(i)+"/log"))
        
    f.write('wait\n\n')

    if resub:
        f.write("var=$(ls %s/*/all_fine | wc -l)\n"%(fname))
        f.write("stp=$(ls %s/*/stop | wc -l)\n"%(fname))

        f.write("date\n")
        f.write("echo all fine: $var, stop files: $stp, nparams: $nparams\n")
        f.write("if [ $var -gt $((($nparams*2)/3)) ];then touch %s; if [ $stp -ne $nparams ];then %s $0;fi ;else echo $var > %s ;fi"
                % (fname+"/all_fine", launch_command, fname+"/diverging_points"))
    

system('chmod +x %s' % fname_launcher)

with open(fname_stopper,"w") as f:
    f.write("#!/bin/bash\n")
    
    f.write("if [ $# -lt 1 ]\nthen\n\tfor i in $(seq 0 1 %d)\n\tdo\n\t\ttouch %s/sim_\"$i\"/stop\n\tdone\nelse\n\tfor i in $@\n\tdo\n\t\ttouch %s/sim_\"$i\"/stop\n\tdone\nfi\n" % (len(params)-1,fname,fname))
system('chmod +x %s' % fname_stopper)
