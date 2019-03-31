/** @file */
#include <iostream>
#include <cstdio>
#include <random>
#include <chrono>
#include <string>
#include "triangulation.h"

using namespace std;

void save_routine(vector<string> chkpts, int n_chkpt, Triangulation universe, int i);

int main(int argc, char* argv[]){
    
    // PARAMETERS
    
    int run_num = stoi(argv[1]);
    double lambda = stod(argv[2]);
    int TimeLength = stoi(argv[3]);
    string end_condition = argv[4];
    string debug_str = argv[5]; /// @todo da sostituire il nome
    string last_chkpt = argv[6];
    string linear_history_str = argv[7];
    
    float save_interval = 0.1;//15.; // in minutes
    int n_chkpt = 3;
    
    string logfile = "runs.txt";
    ofstream logput;
    logput.open (logfile, ofstream::out | ofstream::app);
    if (!logput)
        throw runtime_error("couldn't open 'logput' for writing");
    
    logput << "\nSimulation Parameters:" << endl;
    logput << "\trun_num: " << run_num << endl;
    logput << "\tlambda: " << lambda << endl;
    logput << "\tTimeLength: " << TimeLength << endl;
    logput << "\tend_condition: " << end_condition << endl;
    logput << "\tdebug_flag: " << debug_str << endl; /// @todo da sostituire il nome
    logput << "\tlast_chkpt: " << last_chkpt << endl;
    logput.close();
    
    // CHECKPOINT NAMES
    
    vector<string> chkpts;
    chkpts.push_back("");
    for(int i=1; i<=n_chkpt; i++)
        chkpts.push_back("checkpoint/run" + to_string(run_num) + "_check" + to_string(i) + ".chkpt");
    
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
    int sim_duration;
    if(last_char == 'h')
        sim_duration = stoi(end_condition)*60*60;
    else if(last_char == 'm')
        sim_duration = stoi(end_condition)*60;
    else if(last_char == 's')
        sim_duration = stoi(end_condition);
    else{
        limited_step = true;
        if(isdigit(last_char))
            last_step = stoi(end_condition);
        else{
            last_step = stoi(end_condition.substr(0,end_condition.size()-2));
            
            if(last_char == 'k')
                last_step *= 1e3;
            else if(last_char == 'M')
                last_step *= 1e6;
            else if(last_char == 'G')
                last_step *= 1e9L;
        }
    }
    
    // LINEAR HISTORY
    
    last_char = linear_history_str[linear_history_str.size()-1];
    long linear_history;
    if(isdigit(last_char)) 
        linear_history = stoi(linear_history_str);
    else{
        linear_history = stoi(linear_history_str.substr(0,linear_history_str.size()-2));
        
        if(last_char == 'k')
            linear_history *= 1e3;
        else if(last_char == 'M')
            linear_history *= 1e6;
        else if(last_char == 'G')
            linear_history *= 1e9L;
    }
    
    // OPEN OUTPUT FILE
    
    string profile_file = "history/profiles.txt";
    ofstream profile_stream(profile_file, ofstream::out | ofstream::app);
    if (!profile_stream)
        throw runtime_error("couldn't open 'profiles.txt' for writing");
    if (run_num == 1)
        profile_stream << "# iteration[0] - profile[1:]" << endl << endl;
    
    string volume_file = "history/volumes.txt";
    ofstream volume_stream(volume_file, ofstream::out | ofstream::app);
    if (!volume_stream)
        throw runtime_error("couldn't open 'volumes.txt' for writing");
    if (run_num == 1)
        volume_stream << "# iteration[0] - volume[1]" << endl << endl;
    
    // SETUP THE TRIANGULATION
    // and output parameters
    
    Triangulation universe(TimeLength,lambda);
    
    int profile_ratio = 4;
    
    if(run_num !=1){
        string loadfile = "checkpoint/" + last_chkpt;
        
        Triangulation aux_universe(loadfile);
        universe = aux_universe;
    }
    
    // MOVE
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> dice(1,4);
    
    // FIRST SAVE, then begin
    save_routine(chkpts, n_chkpt, universe, 0);
    auto time_ref = chrono::system_clock::now();
    auto start_time = time_ref;
    
    /// @todo aggiungere il supporto per riconosciuta termalizzazione
    
    int i=0;
    int j=0;
    
    while(((limited_step and i<last_step) or not limited_step) and universe.list2.size() < 1e6){
        
        chrono::duration<double> elapsed = chrono::system_clock::now() - start_time;
        if(elapsed.count() > sim_duration)
            break;
        
        if(debug_flag){
            cout << i << ") ";
        }
        
        switch(dice(mt)){
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
        }
        
        /// @todo mettere un #ifdef (copia da Giuseppe) anziché debug_flag
        universe.is_consistent(debug_flag);
        
        //
        if(linear_history > 0){
            if((universe.iterations_done + i) % linear_history == 0){
                volume_stream << universe.iterations_done + i << " " << universe.list2.size() << endl;
                
                chrono::duration<double> from_last = chrono::system_clock::now() - time_ref;
                if(from_last.count()/60 > save_interval){
                    time_ref = chrono::system_clock::now();
                    
                    char aux_cstr[chkpts[1].size()+1];
                    chkpts[1].copy(aux_cstr, chkpts[1].size()+1);
                    aux_cstr[chkpts[1].size()] = '\0';
                    
                    remove(aux_cstr);
                    
                    for(int j=1; j<n_chkpt; j++){
                        char aux_cstr1[chkpts[j].size()+1];
                        chkpts[j].copy(aux_cstr1, chkpts[j].size()+1);
                        aux_cstr1[chkpts[j].size()] = '\0';
                        
                        char aux_cstr2[chkpts[j+1].size()+1];
                        chkpts[j+1].copy(aux_cstr2, chkpts[j+1].size()+1);
                        aux_cstr2[chkpts[j+1].size()] = '\0';
                        
                        rename(aux_cstr2, aux_cstr1);
                    }
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
                    
                    char aux_cstr[chkpts[1].size()+1];
                    chkpts[1].copy(aux_cstr, chkpts[1].size()+1);
                    aux_cstr[chkpts[1].size()] = '\0';
                    
                    remove(aux_cstr);
                    
                    for(int j=1; j<n_chkpt; j++){
                        char aux_cstr1[chkpts[j].size()+1];
                        chkpts[j].copy(aux_cstr1, chkpts[j].size()+1);
                        aux_cstr1[chkpts[j].size()] = '\0';
                        
                        char aux_cstr2[chkpts[j+1].size()+1];
                        chkpts[j+1].copy(aux_cstr2, chkpts[j+1].size()+1);
                        aux_cstr2[chkpts[j+1].size()] = '\0';
                        
                        rename(aux_cstr2, aux_cstr1);
                    }
                    save_routine(chkpts, n_chkpt, universe, i);
                }
            }
        }
        i++;
    }
    
    // LAST SAVE, before quit
    
    char aux_cstr[chkpts[1].size()+1];
    chkpts[1].copy(aux_cstr, chkpts[1].size()+1);
    aux_cstr[chkpts[1].size()] = '\0';
    
    remove(aux_cstr);
    
    for(int j=1; j<n_chkpt; j++){
        char aux_cstr1[chkpts[j].size()+1];
        chkpts[j].copy(aux_cstr1, chkpts[j].size()+1);
        aux_cstr1[chkpts[j].size()] = '\0';
        
        char aux_cstr2[chkpts[j+1].size()+1];
        chkpts[j+1].copy(aux_cstr2, chkpts[j+1].size()+1);
        aux_cstr2[chkpts[j+1].size()] = '\0';
        
        rename(aux_cstr2, aux_cstr1);
    }
    save_routine(chkpts, n_chkpt, universe, i);
    
    // COMPLETION MESSAGE
    
    logput.open(logfile, ofstream::out | ofstream::app);
    if (!logput)
        throw runtime_error("couldn't open 'logput' for writing");
    logput << "\nSimulation Run --> COMPLETED" << endl;
    logput << "Last step was: " + to_string(universe.iterations_done + i) << endl;
}


void save_routine(vector<string> chkpts, int n_chkpt, Triangulation universe, int i){
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
    
    char aux_cstr1[tmp_chkpt.size()+1];
    tmp_chkpt.copy(aux_cstr1, tmp_chkpt.size()+1);
    aux_cstr1[tmp_chkpt.size()] = '\0';
    
    char aux_cstr2[chkpts[n_chkpt].size()+1];
    chkpts[n_chkpt].copy(aux_cstr2, chkpts[n_chkpt].size()+1);
    aux_cstr2[chkpts[n_chkpt].size()] = '\0';
    
    rename(aux_cstr1, aux_cstr2);
}
