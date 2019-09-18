/** @file main.cpp
 * # CDT 2D - gaugefields
 * 
 * This is the simulation program that realises MCMC for CDT simulations
 * in the presence of gauge dynamics on the triangulation.
 * 
 * The algorithm used is a mixed one (Metropolis and heatbath).
 */
#include <iostream>
#include <cstdio>
#include <chrono>
#include <string>
#include <sstream>
#include <complex>
#include <sys/stat.h>
#include "triangulation.h"
#include "randomgenerator.h"
#include "edge.h"

using namespace std;


bool str_to_bool(string str, string error_msg = "");

/**
* @brief save wrapper for Triangulation's method
* 
* @param chkpts list of names for checkpoints
* @param n_chkpt checkpoint's name position in chkpts
* @param universe the triangulation
* @param i current number of iterations
*/
void save_routine(vector<string> chkpts, int n_chkpt, Triangulation& universe, long i);

string cx_to_str(complex<double> c){ stringstream s; s << real(c) << (imag(c) >= 0.0 ? "+" : "") 
                                                       << imag(c) << "i"; return s.str(); }
template <typename T>
void print_obs(T& time_ref,
               ofstream& volume_stream, ofstream& profile_stream, ofstream& gauge_stream, ofstream& torelons_stream,
               Triangulation& universe, long iter_from_beginning, long& i, bool adj_flag,
               int profile_ratio, int gauge_ratio, int adjacencies_ratio, int torelons_ratio,
               float save_interval, string run_id, int n_chkpt, vector<string>& chkpts,
               ofstream& acc_stream, ofstream& ph_stream,
               complex<double> GE_bef, complex<double> GE_aft, complex<double> Force);

int dice();
int dice(double move22, double move24);

int main(int argc, char* argv[]){
    
    // PARAMETERS
    
    string run_id = argv[1];
    double lambda = stod(argv[2]);
    double beta = stod(argv[3]);
    int TimeLength = stoi(argv[4]);
    string end_condition = argv[5];
    string debug_str = argv[6]; /// @todo da sostituire il nome
    string last_chkpt = argv[7];
    string linear_history_str = argv[8];
    string adj_str = argv[9];
    double move22 = stod(argv[10]);
    double move24 = stod(argv[11]);
    int max_volume = stoi(argv[12]);
    
    float save_interval = 0.05;//15.; // in minutes
    int n_chkpt = 3;
    
    string logfile = "runs.txt";
    ofstream logput;
    logput.open (logfile, ofstream::out | ofstream::app);
    if (!logput)
        throw runtime_error("couldn't open 'logput' for writing");
    
    logput << "\nSimulation Parameters:" << endl;
    logput << "\trun_id: " << run_id << endl;
    logput << "\tlambda: " << lambda << endl;
    logput << "\tbeta: " << beta << endl;
    logput << "\tTimeLength: " << TimeLength << endl;
    logput << "\tend_condition: " << end_condition << endl;
    logput << "\tdebug_flag: " << debug_str << endl; /// @todo da sostituire il nome
    logput << "\tlast_chkpt: " << last_chkpt << endl;
    logput << "\tlinear_history: " << linear_history_str << endl;
    logput << "\tadj_flag: " << adj_str << endl;
    logput << "\tmove22: " << move22 << endl;
    logput << "\tmove24: " << move24 << endl;
    logput << "\tmax_volume: " << max_volume << endl;
    logput.close();
    
    
    // CHECKPOINT NAMES
    /// @todo non sto usando last_chkpt
    
    vector<string> chkpts;
    chkpts.push_back("");
    for(int i=1; i<=n_chkpt; i++)
        chkpts.push_back("checkpoint/run" + run_id + "_check" + to_string(i) + ".chkpt");
    
    // CHECK IF DEBUG MODE IS ACTIVATED
    
    bool debug_flag = str_to_bool(debug_str, "The 6th argument in function main() must be a bool (it is the \"debug_flag\")");
    
    // CHECK IF ADJIACENCIES ARE TO BE PRINTED
    
    bool adj_flag = str_to_bool(adj_str, "The 9th argument in function main() must be a bool (it is the \"adj_flag\")");
    
    // END CONDITION
    
    char last_char = end_condition[end_condition.size()-1];
    bool limited_step = false;
    long last_step;
    long sim_duration;
    long end = stol(end_condition.substr(0, end_condition.size()-1));
    if(last_char == 't')        // number of seconds
        sim_duration = end;
    else if(last_char == 's'){  // pure number of steps
        limited_step = true;
        last_step = end;
    }
    else
        throw runtime_error("end_condition type not recognized");
    /*
    if(last_char == 'h')
        sim_duration = stoi(end_condition)*60*60; // stoi("10afk") == 10 !
    else if(last_char == 'm')
        sim_duration = stoi(end_condition)*60;
    else if(last_char == 's')
        sim_duration = stoi(end_condition);
    else{
        limited_step = true;
        last_step = stoi(end_condition);
        if(last_char == 'k')
            last_step *= 1e3;
        else if(last_char == 'M')
            last_step *= 1e6;
        else if(last_char == 'G')
            last_step *= 1e9L;
    }
    */
    
    // LINEAR HISTORY
    
    last_char = linear_history_str[linear_history_str.size()-1];
    long linear_history = stoi(linear_history_str);
    if(last_char == 'k')
        linear_history *= 1e3;
    else if(last_char == 'M')
        linear_history *= 1e6;
    else if(last_char == 'G')
        linear_history *= 1e9L;
    
    // OPEN OUTPUT FILES
    
    string profile_file = "history/profiles.txt";
    ofstream profile_stream(profile_file, ofstream::out | ofstream::app);
    if (!profile_stream)
        throw runtime_error("couldn't open 'profiles.txt' for writing");
    if (stod(run_id) == 1.)
        profile_stream << "# iteration[0] - profile[1:]" << endl << endl;
    
    string volume_file = "history/volumes.txt";
    ofstream volume_stream(volume_file, ofstream::out | ofstream::app);
    if (!volume_stream)
        throw runtime_error("couldn't open 'volumes.txt' for writing");
    if (stod(run_id) == 1.)
        volume_stream << "# iteration[0] - volume[1]" << endl << endl;
    
    string gauge_file = "history/gauge.txt";
    ofstream gauge_stream(gauge_file, ofstream::out | ofstream::app);
    if (!gauge_stream)
        throw runtime_error("couldn't open 'gauge.txt' for writing");
    if (stod(run_id) == 1.)
        gauge_stream << "# iteration[0] - action[1] - ch.top.[2] - av.contr.[3]" << endl << endl;
    
    string torelons_file = "history/toblerone.txt";
    ofstream torelons_stream(torelons_file, ofstream::out | ofstream::app);
    if (!torelons_stream)
        throw runtime_error("couldn't open 'toblerone.txt' for writing");
    if (stod(run_id) == 1.)
        torelons_stream << "# iteration[0] - torelons[1:]" << endl << endl;
    
    string acc_file = "history/glink_update.txt";
    ofstream acc_stream(acc_file, ofstream::out | ofstream::app);
    if (!acc_stream)
        throw runtime_error("couldn't open 'glink_update.txt' for writing");
    if (stod(run_id) == 1.)
        acc_stream << "# iteration[0] - GaugeElement_bef[1] - GaugeElement_aft[2] - Force_abs[2] - Force_arg[3]" << endl << endl;
    
    string ph_file = "history/phases.txt";
    ofstream ph_stream(ph_file, ofstream::out | ofstream::app);
    if (!ph_stream)
        throw runtime_error("couldn't open 'phases.txt' for writing");
    if (stod(run_id) == 1.)
        ph_stream << "# iteration[0] - phases[1:]" << endl << endl;
    
    // ratios
    
    int profile_ratio = 4;
    int gauge_ratio = 16;
    int adjacencies_ratio = 128;
    int torelons_ratio = gauge_ratio;
    
    // SETUP THE TRIANGULATION
    // and output parameters
    
    Triangulation universe(TimeLength, lambda, beta);
    
    if(stod(run_id) != 1.){
        string loadfile = "checkpoint/" + last_chkpt;
        
        universe.load(loadfile);
    }
    
    // randomize the generator
    RandomGen r;
    r.really_rand();
    
    // FIRST SAVE, then begin
    save_routine(chkpts, n_chkpt, universe, 0);
    auto time_ref = chrono::system_clock::now();
    auto start_time = time_ref;
    
    // and a first check
    if(debug_flag)
        universe.is_consistent();
    
    /// @todo aggiungere il supporto per riconosciuta termalizzazione
    
    long i = 0;
    double acceptance = 0.;
    double dS_g = 0.;
    complex<double> GE_bef;
    complex<double> GE_aft;
    complex<double> Force;
    
    while(((limited_step and i<last_step) or not limited_step) and universe.list2.size() < max_volume){        
        chrono::duration<double> elapsed = chrono::system_clock::now() - start_time;
        if(elapsed.count() > sim_duration)
            break;
            
        if(debug_flag){
            cout << i << ") ";
        }
        
        switch(dice(move22, move24)){
            case 1:
            case 2:
            {
                vector<double> v = universe.move_22(debug_flag);
                if(v.size() == 2){
                    acceptance = v[0];
                    dS_g = v[1];
                }
                break;
            }
            case 3:
            {
                universe.move_24(debug_flag);
                break;   
            }
            case 4:
            {
                universe.move_42(debug_flag);
                break;
            }
            case 5:
            {
                vector<complex<double>> v = universe.move_gauge(debug_flag);
                GE_bef = v[0];
                GE_aft = v[1];
                Force = v[2];
                break;
            }
        }
        
        if(debug_flag)
            universe.is_consistent();
        
        //
        
        long iter_from_beginning = universe.iterations_done + i;
        if(linear_history > 0){
            if((iter_from_beginning) % linear_history == 0)
                print_obs(time_ref, volume_stream, profile_stream, gauge_stream, torelons_stream, universe,
                          iter_from_beginning, i, adj_flag,
                          profile_ratio, gauge_ratio, adjacencies_ratio, torelons_ratio,
                          save_interval, run_id, n_chkpt, chkpts,
                          acc_stream, ph_stream, GE_bef, GE_aft, Force);
        }
        else{
            if((iter_from_beginning) % universe.volume_step == 0){
                universe.steps_done++;
                if(universe.steps_done == 512){
                        universe.volume_step *= 2;
                        universe.steps_done = 0;
                }
                print_obs(time_ref, volume_stream, profile_stream, gauge_stream, torelons_stream, universe,
                          iter_from_beginning, i, adj_flag,
                          profile_ratio, gauge_ratio, adjacencies_ratio, torelons_ratio,
                          save_interval, run_id, n_chkpt, chkpts,
                          acc_stream, ph_stream, GE_bef, GE_aft, Force);
            }
        }
        
        if((iter_from_beginning) % int(2e4) == 0){
            struct stat buffer;
            if(stat("stop", &buffer) == 0){
                ofstream logput;
                logput.open (logfile, ofstream::out | ofstream::app);
                if (!logput)
                    throw runtime_error("couldn't open 'logput' for writing");
                logput << "\t[STOPPED at iteration " << universe.iterations_done + i << "]" << endl;
                logput.close();
                
                break;
            }
        }
        
        i++;
    }
    
    // LAST SAVE, before quit
    
    remove(chkpts[1].c_str());
    
    for(int j=1; j<n_chkpt; j++)                        
        rename(chkpts[j+1].c_str(), chkpts[j].c_str());
    
    save_routine(chkpts, n_chkpt, universe, i);
    
    // check for MAX VOLUME REACHING
    
    if(universe.list2.size() >= max_volume){
        ofstream iter("max_volume_reached");
        iter << universe.iterations_done + i;
        iter.close();
    }
    
    // COMPLETION MESSAGE
    
    logput.open(logfile, ofstream::out | ofstream::app);
    if (!logput)
        throw runtime_error("couldn't open 'logput' for writing");
    logput << "\nSimulation Run --> COMPLETED" << endl;
    logput << "Last step was: " + to_string(universe.iterations_done + i) << endl;
    
    return 0;
}


bool str_to_bool(string str, string error_msg)
{
    const string True = "true";
    const string False = "false";
    
    if(str == True)
        return true;
    else if(str == False)
        return false;
    else
        throw logic_error(error_msg);
}

void save_routine(vector<string> chkpts, int n_chkpt, Triangulation& universe, long i)
{
    static int count=-1;
    count++;
    universe.iterations_done += i;
    
    
    string logfile = "runs.txt";
    ofstream logput;
    logput.open(logfile, ofstream::out | ofstream::app);
    if (!logput)
        throw runtime_error("couldn't open 'logput' for writing");
    
    if(count % 4 == 0)
        logput << endl;
    else
        logput << ", ";    
    logput << "saving... ";
    
    string tmp_chkpt = chkpts[n_chkpt] + ".tmp";
    universe.save(tmp_chkpt);
    universe.iterations_done -= i;  // tiene il conto dal checkpoint precedente, 
                                    // quindi deve rimanere fisso
    
    logput << "COMPLETED";
    
    rename(tmp_chkpt.c_str(), chkpts[n_chkpt].c_str());
    
    ofstream iter("iterations_done");
    iter << universe.iterations_done + i;
    iter.close();
}

template <typename T>
void print_obs(T& time_ref,
               ofstream& volume_stream, ofstream& profile_stream, ofstream& gauge_stream, ofstream& torelons_stream,
               Triangulation& universe, long iter_from_beginning, long& i, bool adj_flag,
               int profile_ratio, int gauge_ratio, int adjacencies_ratio, int torelons_ratio,
               float save_interval, string run_id, int n_chkpt, vector<string>& chkpts,
               ofstream& acc_stream, ofstream& ph_stream,
               complex<double> GE_bef, complex<double> GE_aft, complex<double> Force)
{
    static int j = 0;
    static int k = 0;
    static int h = 0;
    static int n = 0;
    static int l = 0;
    
    j++;
    k++;
    h++;
    l++;
    volume_stream << iter_from_beginning << " " << universe.list2.size() << endl;
    acc_stream << iter_from_beginning << " " << arg(GE_bef) << " " << arg(GE_aft)
               << " " << abs(Force) << " " << arg(Force) << endl;

    if(j == profile_ratio){
        j = 0;
        profile_stream << iter_from_beginning << " ";
        universe.print_space_profile(profile_stream);
    }
    if(k == gauge_ratio){
        k = 0;
        vector<double> v = universe.gauge_action_top_charge();
        double av_contr = 6 * v[0] / ((universe.beta * universe.N) * universe.list0.size());
        gauge_stream << iter_from_beginning << " " << v[0] << " " << v[1] << " " << av_contr << endl;
    }
//     if(h == 16*gauge_ratio){
//         h = 0;
//         
//         vector<double> phases;
//         for(auto x: universe.list1)
//             phases.push_back(arg(x.dync_edge()->gauge_element()[0][0]));        
//         
//         ph_stream << iter_from_beginning << " ";
//         for(auto x: phases)
//             ph_stream << x << " ";
//         ph_stream << endl;
//     }
    if(adj_flag && (h == adjacencies_ratio)){
        h = 0;
        universe.text_adjacency_and_observables("history/adjacencies/adj" + to_string(n) + "_run" + run_id + ".json",
                                                iter_from_beginning);
        n++;
    }
//     if(l == torelons_ratio){
//         l = 0;
//         torelons_stream << iter_from_beginning << " ";
//         vector<complex<double>> torelons = universe.toleron();
//         for(auto x: torelons)
//             torelons_stream << x << " ";
//         torelons_stream << endl;
//     }
    chrono::duration<double> from_last = chrono::system_clock::now() - time_ref;
    if(from_last.count()/60 > save_interval){
        time_ref = chrono::system_clock::now();
        
        remove(chkpts[1].c_str());
        
        for(int j=1; j<n_chkpt; j++)                        
            rename(chkpts[j+1].c_str(), chkpts[j].c_str());
        
        save_routine(chkpts, n_chkpt, universe, i);
    }
}

int dice()
{
    return dice(0.1, 0.2);
}

int dice(double move22, double move24)
{
    static RandomGen r;
    int dice = 0;
    
    double extraction = r.next();
    if(extraction < move22)
        dice = 1;
    else if(extraction < 2*move22)
        dice = 2;
    else if(extraction < move24 + 2*move22)
        dice = 3;
    else if(extraction < 2*move24 + 2*move22)
        dice = 4;
    else
        dice = 5;
    
    return dice;
}
