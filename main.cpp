/** @file */
#include <iostream>
#include <cstdio>
#include <chrono>
#include <string>
#include <sys/stat.h>
#include "triangulation.h"
#include "randomgenerator.h"

using namespace std;

void save_routine(vector<string> chkpts, int n_chkpt, Triangulation universe, long i);

int dice();

int main(int argc, char* argv[]){
    
    // PARAMETERS
    
    string run_id = argv[1];
    double lambda = stod(argv[2]);
    double g_ym = stod(argv[3]);
    int TimeLength = stoi(argv[4]);
    string end_condition = argv[5];
    string debug_str = argv[6]; /// @todo da sostituire il nome
    string last_chkpt = argv[7];
    string linear_history_str = argv[8];
    
    float save_interval = 0.1;//15.; // in minutes
    int n_chkpt = 3;
    
    string logfile = "runs.txt";
    ofstream logput;
    logput.open (logfile, ofstream::out | ofstream::app);
    if (!logput)
        throw runtime_error("couldn't open 'logput' for writing");
    
    logput << "\nSimulation Parameters:" << endl;
    logput << "\trun_id: " << run_id << endl;
    logput << "\tlambda: " << lambda << endl;
    logput << "\tg_ym: " << g_ym << endl;
    logput << "\tTimeLength: " << TimeLength << endl;
    logput << "\tend_condition: " << end_condition << endl;
    logput << "\tdebug_flag: " << debug_str << endl; /// @todo da sostituire il nome
    logput << "\tlast_chkpt: " << last_chkpt << endl;
    logput << "\tlinear_history: " << linear_history_str<< endl;
    logput.close();
    
    
    // CHECKPOINT NAMES
    
    vector<string> chkpts;
    chkpts.push_back("");
    for(int i=1; i<=n_chkpt; i++)
        chkpts.push_back("checkpoint/run" + run_id + "_check" + to_string(i) + ".chkpt");
    
    
    // CHECK IF DEBUG MODE IS ACTIVATED
    /// @todo trasformare tutto in direttive preprocessor #ifndef
    
    bool debug_flag;
    
    const string True = "true";
    const string False = "false";
    if(debug_str == True)
        debug_flag = true;
    else if(debug_str == False)
        debug_flag = false;
    else
        throw logic_error("The 5th argument in function main() must be a bool (it is the \"debug_flag\")");
    
    
    // END CONDITION
    
    char last_char = end_condition[end_condition.size()-1];
    bool limited_step = false;
    long last_step;
    long sim_duration;
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
    
    
    // SETUP THE TRIANGULATION
    // and output parameters
    
    Triangulation universe(TimeLength,lambda, g_ym);
    
    int profile_ratio = 4;
    
    if(stod(run_id) != 1.){
        string loadfile = "checkpoint/" + last_chkpt;
        
        Triangulation aux_universe(loadfile);
        universe = aux_universe;
    }
    
    
    // FIRST SAVE, then begin
    save_routine(chkpts, n_chkpt, universe, 0);
    auto time_ref = chrono::system_clock::now();
    auto start_time = time_ref;
    
    
    /// @todo aggiungere il supporto per riconosciuta termalizzazione
    
    long i=0;
    long j=0;
    
    while(((limited_step and i<last_step) or not limited_step) and universe.list2.size() < 1e6){
        
        chrono::duration<double> elapsed = chrono::system_clock::now() - start_time;
        if(elapsed.count() > sim_duration)
            break;
            
        if(debug_flag){
            cout << i << ") ";
        }
        
        switch(dice()){
            case 1:
            {
                universe.move_22_1(debug_flag);
                break;
            }
            case 2:
            {
                universe.move_22_2(debug_flag);
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
                universe.move_gauge(debug_flag);
                break;
            }
        }
        
        /// @todo mettere un #ifdef (copia da Giuseppe) anziché debug_flag
        if(debug_flag)
            universe.is_consistent();
        
        //
        if(linear_history > 0){
            if((universe.iterations_done + i) % linear_history == 0){
                volume_stream << universe.iterations_done + i << " " << universe.list2.size() << endl;
                
                chrono::duration<double> from_last = chrono::system_clock::now() - time_ref;
                if(from_last.count()/60 > save_interval){
                    time_ref = chrono::system_clock::now();
                    
                    remove(chkpts[1].c_str());
                    
                    for(int j=1; j<n_chkpt; j++)                        
                        rename(chkpts[j+1].c_str(), chkpts[j].c_str());
                    
                    save_routine(chkpts, n_chkpt, universe, i);
                }               
            }
        }
        else{
            if((universe.iterations_done + i) % universe.volume_step == 0){
                universe.steps_done++;
                if(universe.steps_done == 512){
                        universe.volume_step *= 2;
                        universe.steps_done = 0;
                }
                j++;
                volume_stream << universe.iterations_done + i << " " << universe.list2.size() << endl;
                if(j == profile_ratio){
                    j=0;
                    profile_stream << universe.iterations_done + i << " ";
                    universe.print_space_profile(profile_stream);
                }
                chrono::duration<double> from_last = chrono::system_clock::now() - time_ref;
                if(from_last.count()/60 > save_interval){
                    time_ref = chrono::system_clock::now();
                    
                    remove(chkpts[1].c_str());
                    
                    for(int j=1; j<n_chkpt; j++)                        
                        rename(chkpts[j+1].c_str(), chkpts[j].c_str());
                    
                    save_routine(chkpts, n_chkpt, universe, i);
                }
            }
        }
        
        if((universe.iterations_done + i) % int(2e5) == 0){
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
    
    // COMPLETION MESSAGE
    
    logput.open(logfile, ofstream::out | ofstream::app);
    if (!logput)
        throw runtime_error("couldn't open 'logput' for writing");
    logput << "\nSimulation Run --> COMPLETED" << endl;
    logput << "Last step was: " + to_string(universe.iterations_done + i) << endl;
}


void save_routine(vector<string> chkpts, int n_chkpt, Triangulation universe, long i){
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

int dice(){
    static RandomGen r;
    int dice = 0;
    
    double extraction = r.next();
    if(extraction < 0.1)
        dice = 1;
    else if(extraction < 0.2)
        dice = 2;
    else if(extraction < 0.3)
        dice = 3;
    else if(extraction < 0.4)
        dice = 4;
    else
        dice = 5;
    
    return extraction;
}
