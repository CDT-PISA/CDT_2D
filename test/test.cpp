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
    int max_iters = args.max_iters;
    int walltime_seconds = args.walltime;
    int meas_Vprofile = args.meas_Vprofile;
    int meas_Qcharge = args.meas_Qcharge;
    int meas_plaquette = args.meas_plaquette;


    Triangulation uni(T, lambda, beta);
    RandomGen r;

    string measure_folder = main_dir + "/measures";
    string Vprofile_fname = measure_folder + "/Vprofile";
    string Qcharge_fname = measure_folder + "/Qcharge";
    string plaquette_fname = measure_folder + "/plaquette";
    FILE * meas_file;

    system(("mkdir -p "+measure_folder).c_str());
    

    auto t_start = std::chrono::high_resolution_clock::now();
    auto t_end = t_start;
    double secs_passed; // = (1./1000.)*std::chrono::duration<double, std::milli>(t_end-t_start).count();
    bool hit_walltime = false;
    for(int i=1; (max_iters<0 | i<max_iters) & !hit_walltime; ++i){
 
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
//         cout<<i<<" "<<uni.topological_charge()<<endl;     
//        for(int s = 0; s < 10; ++s){
// //        cout<<10*i+s<<" "<<uni.topological_charge()<<endl;     
//            uni.move_gauge();
//        }
        
         //FIXME: magic number
        if(i%100==0){
            t_end = std::chrono::high_resolution_clock::now();
            secs_passed = std::chrono::duration<double>(t_end-t_start).count();
            hit_walltime = secs_passed>walltime_seconds;
        }

        // check and perform measures
        // TODO: optimizable
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

            fprintf(meas_file, "%ld %lg\n", uni.iterations_done, uni.topological_charge());

            fclose(meas_file);
        }
        if(i%meas_plaquette==0 and meas_plaquette>0){
            meas_file = fopen(plaquette_fname.c_str(),"a");

            fprintf(meas_file, "%ld %lg\n", uni.iterations_done, uni.average_plaquette());

            fclose(meas_file);
        }
     }


    return 0;
}
