#include <string>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <type_traits>

using namespace std;

struct arg_list{
    // fixed
    int T = 0;
    double lambda = 0.0;
    double beta = 0.0;

    // floating valued
    string main_dir = "simulation";
    string confname = "conf";
    double w_22 = 0.1;
    double w_24 = 0.2;
    int init_waist = 3;
    int max_V = -1;
    int max_iters = -1;
    int walltime = -1;
    int seed = -1;
    int meas_V= -1;
    int meas_Vprofile = -1;
    int meas_Qcharge = -1;
    int meas_plaquette = -1;
    int meas_torelon = -1;
    int fix_V = -1;
    double fix_V_rate = 1e-5;
    int fix_V_each = 10;
//    double w_gauge = 0.7;
    
    friend ostream& operator<<(ostream& o, const arg_list& al);
};

ostream& operator<<(ostream& o, const arg_list& al){
    o<<"T: "<<al.T<<endl;
    o<<"lambda: "<<al.lambda<<endl;
    o<<"beta: "<<al.beta<<endl;
    o<<"main_dir: "<<al.main_dir<<endl;
    o<<"confname: "<<al.confname<<endl;
    o<<"w_22: "<<al.w_22<<endl;
    o<<"w_24: "<<al.w_24<<endl;
    o<<"init_waist: "<<al.init_waist<<endl;
    o<<"max_V: "<<al.max_V<<endl;
    o<<"max_iters: "<<al.max_iters<<endl;
    o<<"walltime: "<<al.walltime<<endl;
    o<<"seed: "<<al.seed<<endl;
    o<<"meas_V: "<<al.meas_V<<endl;
    o<<"meas_Vprofile: "<<al.meas_Vprofile<<endl;
    o<<"meas_Qcharge: "<<al.meas_Qcharge<<endl;
    o<<"meas_plaquette: "<<al.meas_plaquette<<endl;
    o<<"meas_torelon: "<<al.meas_torelon<<endl;
    o<<"fix_V: "<<al.fix_V<<endl;
    o<<"fix_V_rate: "<<al.fix_V_rate<<endl;
    o<<"fix_V_each: "<<al.fix_V_each<<endl;
//    o<<"w_gauge: "<<al.w_gauge<<endl;
    return o;
}

string args_string(){

  string ret= " ";
  ret += "<num slices> ";
  ret += "<lambda> ";
  ret += "<beta> ";
  ret += "\n";
  ret += "[--main_dir (simulation)] \n";
  ret += "[--confname (conf)] \n";
  ret += "[--w_22 (0.1)] \n";
  ret += "[--w_24 (0.2)] \n";
  ret += "[--init_waist (3)] \n";
  ret += "[--max_V (-1)] \n";
  ret += "[--max_iters (-1)] \n";
  ret += "[--walltime (-1)] \n";
  ret += "[--seed (-1)] \n";
  ret += "[--meas_V (-1)] \n";
  ret += "[--meas_Vprofile (-1)] \n";
  ret += "[--meas_Qcharge (-1)] \n";
  ret += "[--meas_plaquette (-1)] \n";
  ret += "[--meas_torelon (-1)] \n";
  ret += "[--fix_V (-1)] \n";
  ret += "[--fix_V_rate (1e-5)] \n";
  ret += "[--fix_V_each (10)] \n";
  return ret;
}

template <typename T>
void parse_flag_valued_term(T& var, string var_name, int argc, int fixed_args, map<string,int>& argmap, map<int,string>& argmap_inv){
    int tmp_idx = argmap[var_name];
    if(tmp_idx>=fixed_args){
       if(tmp_idx+1>= argc)
           throw std::runtime_error(("ERROR: set value after '"+var_name+"' flag").c_str()); 
       
       
       if constexpr(std::is_same<T,string>::value){
           var = argmap_inv[tmp_idx+1]; 
       }else if constexpr(std::is_same<T,double>::value){
           var = stod(argmap_inv[tmp_idx+1].c_str(),NULL); 
       }else if constexpr(std::is_same<T,int>::value){
           var = atoi(argmap_inv[tmp_idx+1].c_str()); 
       }else{
           throw std::logic_error(("ERROR: unsupported type of '"+var_name+"' flag in parser").c_str()); 
       }
    }
}

int parse_arguments(arg_list& args, int argc, char** argv){
    int fixed_args = 3;
    map<string,int> argmap;
    map<int,string> argmap_inv;
//    char *end;
//    int base_strtoull = 10;

    if(argc<=fixed_args){
      cout<<"usage:\n"<<argv[0]<<" "<<args_string()<<endl;
      return 1;
    }

    // fixed arguments
    args.T = atoi(argv[1]);
    args.lambda = stod(argv[2],NULL);
    args.beta = stod(argv[3],NULL);

    // collect floating arguments
    for(int i = fixed_args+1; i < argc; ++i){
        argmap[argv[i]]=i;
        argmap_inv[i]=argv[i];
    }
//
////
////// flagged arguments without value
////
//

//
////
////// flagged arguments with value
////
//
    
    // (string) main_dir
    parse_flag_valued_term(args.main_dir, "--main_dir", argc, fixed_args, argmap, argmap_inv);

    // (string) confname
    parse_flag_valued_term(args.confname, "--confname", argc, fixed_args, argmap, argmap_inv);
    
    // (double) w_22
    parse_flag_valued_term(args.w_22, "--w_22", argc, fixed_args, argmap, argmap_inv);
        
    // (double) w_24
    parse_flag_valued_term(args.w_24, "--w_24", argc, fixed_args, argmap, argmap_inv);

    // (int) init_waist
    parse_flag_valued_term(args.init_waist, "--init_waist", argc, fixed_args, argmap, argmap_inv);

    // (int) max_V
    parse_flag_valued_term(args.max_V, "--max_V", argc, fixed_args, argmap, argmap_inv);

    // (int) max_iters
    parse_flag_valued_term(args.max_iters, "--max_iters", argc, fixed_args, argmap, argmap_inv);

    // (int) walltime
    parse_flag_valued_term(args.walltime, "--walltime", argc, fixed_args, argmap, argmap_inv);

    // (int) seed
    parse_flag_valued_term(args.walltime, "--seed", argc, fixed_args, argmap, argmap_inv);

    // (int) meas_V
    parse_flag_valued_term(args.meas_V, "--meas_V", argc, fixed_args, argmap, argmap_inv);

    // (int) meas_Vprofile
    parse_flag_valued_term(args.meas_Vprofile, "--meas_Vprofile", argc, fixed_args, argmap, argmap_inv);

    // (int) meas_Qcharge
    parse_flag_valued_term(args.meas_Qcharge, "--meas_Qcharge", argc, fixed_args, argmap, argmap_inv);

    // (int) meas_plaquette
    parse_flag_valued_term(args.meas_plaquette, "--meas_plaquette", argc, fixed_args, argmap, argmap_inv);

    // (int) meas_torelon
    parse_flag_valued_term(args.meas_torelon, "--meas_torelon", argc, fixed_args, argmap, argmap_inv);

    // (int) fix_V
    parse_flag_valued_term(args.fix_V, "--fix_V", argc, fixed_args, argmap, argmap_inv);

    // (double) fix_V_rate
    parse_flag_valued_term(args.fix_V_rate, "--fix_V_rate", argc, fixed_args, argmap, argmap_inv);

    // (int) fix_V_each
    parse_flag_valued_term(args.fix_V_each, "--fix_V_each", argc, fixed_args, argmap, argmap_inv);


    // argument checking
    if(args.T <= 0){
        throw "ERROR: argument <T> invalid";
    }

    if(args.beta <= 0.0){
        throw "ERROR: argument <beta> invalid";
    }

    if(args.init_waist <= 2){
        throw "ERROR: argument <init_waist> invalid";
    }
    return 0;
}
