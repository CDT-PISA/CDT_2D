#include <iostream>
#include "label.h"
#include "edge.h"
#include "vertex.h"
#include "triangle.h"
#include "gaugeelement.h"
#include "triangulation.h"
#include "randomgenerator.h"
#include <cmath>
#include <complex>
#include "parser.hpp"
#include <chrono>
#include <unistd.h>


using namespace std;


double move22;
double move24;

int dice(){
    static RandomGen r;
    int dice = 0;
    
    
    double extraction = r.next();
    if(extraction < move22/2.)
        dice = 1;
    else if(extraction < move22)
        dice = 2;
    else if(extraction < move24/2. + move22)
        dice = 3;
    else if(extraction < move24 + move22)
        dice = 4;
    else
        dice = 5;
    
    return dice;
}

arg_list args;

int main(int argc, char* argv[]){

    int ret = parse_arguments(args, argc, argv);
    if(ret==1){
      exit(1);
    }

    cout<<"arguments:\n"<<args<<endl;
    int T = args.T;
    double lambda = args.lambda;
    double beta = args.beta;
    string main_dir = args.main_dir;
    string confname = args.confname;
    move22 = args.w_22;
    move24 = args.w_24;
    int init_waist = args.init_waist;
    int max_V = args.max_V;
    int max_iters = args.max_iters;
    int walltime_seconds = args.walltime;
    int meas_V = args.meas_V;
    int meas_Vprofile = args.meas_Vprofile;
    int meas_Qcharge = args.meas_Qcharge;
    int meas_plaquette = args.meas_plaquette;
    int meas_torelon = args.meas_torelon;
    int fix_V = args.fix_V;
    double fix_V_rate = args.fix_V_rate;
    uint mean_V_items = args.fix_V_each;
    vector<uint> aver_V;
    uint idx_last_V=0;

    string confs_folder = main_dir + "/confs";
    string conf_filename = confs_folder+ "/"+confname;
    string confbkp_filename = confs_folder+ "/"+confname+"_bkp";

    string measure_folder = main_dir + "/measures";
    string lambda_fname = measure_folder + "/lambda";
    string V_fname = measure_folder + "/Volume";
    string Vprofile_fname = measure_folder + "/Vprofile";
    string Qcharge_fname = measure_folder + "/Qcharge";
    string plaquette_fname = measure_folder + "/plaquette";
    string torelon_fname = measure_folder + "/torelon";
    FILE * meas_file;


    system(("mkdir -p "+measure_folder).c_str());
    system(("mkdir -p "+confs_folder).c_str());

    system(("rm -rf "+(main_dir + "/max_V_reached")).c_str());
    system(("rm -rf "+(main_dir + "/all_fine")).c_str());

    
    Triangulation uni;

    if(access( conf_filename.c_str(), F_OK ) != -1){
        uni.load(conf_filename);
        uni.save(confbkp_filename);
    }else{
        uni.initialize(T, lambda, beta, init_waist);
        uni.save(conf_filename);
        uni.save(confbkp_filename);
    }
    cout<<uni<<endl;
    exit(0);
    
    RandomGen r;

    auto t_start = std::chrono::high_resolution_clock::now();
    auto t_end = t_start;
    double secs_passed; // = (1./1000.)*std::chrono::duration<double, std::milli>(t_end-t_start).count();
    bool hit_walltime = false;
    int i=1;
    for(i=1; (max_iters<0 | i<max_iters) and !hit_walltime and (uni.list2.size()<(uint)max_V); ++i){
 
         switch(dice()){
             case 1:{
                 uni.move_22();
                 break;
             }
             case 2:{
                 uni.move_22();
                 break;
             }
             case 3:{
                 uni.move_24();
                 break;   
             }
             case 4:{
                 uni.move_42();
                 break;
             }
             case 5:{
                 uni.move_gauge();
                 break;
             }
        }

        uni.iterations_done++;

        if(i%1000==0){ //FIXME: magic number
            t_end = std::chrono::high_resolution_clock::now();
            secs_passed = std::chrono::duration<double>(t_end-t_start).count();
            hit_walltime = secs_passed>walltime_seconds;
            if(access( (main_dir + "/stop").c_str(), F_OK ) != -1){
                hit_walltime = true;
            }
        }

        // check and perform measures
        // TODO: optimizable
        if(i%meas_V==0 and meas_V>0){
            uint vol_meas = uni.list2.size();
            meas_file = fopen(V_fname.c_str(),"a");
            fprintf(meas_file, "%ld %u\n", uni.iterations_done, vol_meas);
            fclose(meas_file);

            if(fix_V>0){
                if(aver_V.size()<mean_V_items){
                    aver_V.push_back(vol_meas);
                }else{
                    aver_V[idx_last_V]=vol_meas;
                    idx_last_V = (idx_last_V +1)%mean_V_items;
                    double mean_V = 0.0;
                    for(uint jj=0U; jj<mean_V_items; ++jj){
                        mean_V+=aver_V[jj];
                    }
                    mean_V/=(double)mean_V_items;
                    if(mean_V > fix_V*1.2){
                        uni.lambda += fix_V_rate*pow(abs(mean_V-fix_V),1.3);
                    }else if(mean_V < fix_V/1.2){
                        uni.lambda -= fix_V_rate*pow(abs(mean_V-fix_V),1.8);
                    }
                    meas_file = fopen(lambda_fname.c_str(),"a");
                    fprintf(meas_file, "%ld %u %lg\n", uni.iterations_done, vol_meas, uni.lambda);
                    fclose(meas_file);
                }
            }
        }
        if(i%meas_Vprofile==0 and meas_Vprofile>0){
            meas_file = fopen(Vprofile_fname.c_str(),"a");
            
            fprintf(meas_file, "%ld %zu ", uni.iterations_done, uni.spatial_profile.size());
            for(const auto& sl_vol : uni.spatial_profile){
                fprintf(meas_file, "%ld ", sl_vol);
            }
            fprintf(meas_file, "\n");

            fclose(meas_file);
        }
        if(i%meas_Qcharge==0 and meas_Qcharge>0){
            meas_file = fopen(Qcharge_fname.c_str(),"a");

            double qval = uni.topological_charge();
            if(abs(qval)<1e-10) qval=0;
            fprintf(meas_file, "%ld %ld %lg\n", uni.iterations_done, uni.list2.size(), qval);

            fclose(meas_file);
        }
        if(i%meas_plaquette==0 and meas_plaquette>0){
            meas_file = fopen(plaquette_fname.c_str(),"a");

            fprintf(meas_file, "%ld %lg\n", uni.iterations_done, uni.average_plaquette());

            fclose(meas_file);
        }
        if(i%meas_torelon==0 and meas_torelon>0){
            meas_file = fopen(torelon_fname.c_str(),"a");

            auto profile = uni.spatial_profile;
            auto torelon = uni.toleron();
            fprintf(meas_file, "%ld %ld %zu ", uni.iterations_done, uni.list2.size(), profile.size());
            for(uint ei=0; ei<profile.size(); ++ei){
                fprintf(meas_file, "%ld %lg %lg ", profile[ei], real(torelon[ei]), imag(torelon[ei]));
            }
            fprintf(meas_file, "\n");

            fclose(meas_file);
        }
    }
    
    cout<<"saving configuration in "<<conf_filename<<endl;
    uni.save(conf_filename);

    if(uni.list2.size()>=(uint)max_V){
        cout<<"Max volume threshold saturated!!"<<endl;
        meas_file = fopen((main_dir + "/max_V_reached").c_str(),"w");
        fprintf(meas_file, "MAX V REACHED: %zu\n", uni.list2.size());
        fclose(meas_file);
    }else{
        meas_file = fopen((main_dir + "/all_fine").c_str(),"w");
        fprintf(meas_file, "ciao");
        fclose(meas_file);
    }

    t_end = std::chrono::high_resolution_clock::now();
    secs_passed = (1./1000)*std::chrono::duration<double, std::milli>(t_end-t_start).count();
    cout<<"All [DONE] in "<<secs_passed<<" seconds"<<endl;
    cout<<"\niterations done = "<<i<<endl;
    cout<<"total run iterations = "<<uni.iterations_done<<endl<<endl;


    cout<<"Program ended"<<endl;


    return 0;
}
