/** @file */
#include <iostream>
#include <cstdio>
#include <random>
#include <chrono>
#include <string>
#include "triangulation.h"

using namespace std;

void save_routine(string outdir, vector<string> chkpts, int n_chkpt, Triangulation universe);

int main(int argc, char* argv[]) {
    
    if(argc < 1)
        throw logic_error("output folder not specified");
    else if (argc < 6)
        throw logic_error("too few arguments in function main()");
    
    /// @todo sarebbe bene che rientrasse nel log
    /// quindi andrebbe postposto dopo
    for(int i=0; i<7; i++)
        cout << argv[i] << endl;
    cout.flush();
    
    int run_num = stoi(argv[1]);
    double lambda = stod(argv[2]);
    string outdir = argv[3];
    int TimeLength = stoi(argv[4]);
    int last_step = stoi(argv[5]);
    string arg = argv[6]; /// @todo da sostituire il nome
    string last_chkpt = argv[7];
    
    float save_interval = 0.004;//15.; // in minutes
    int n_chkpt = 3;
    
    cerr << argv[7] << endl;
    
    vector<string> chkpts;
    chkpts.push_back("");
    for(int i=1; i<=n_chkpt; i++)
        chkpts.push_back(outdir + "/checkpoint/run" + to_string(run_num) + "_check" + to_string(i) + ".chkpt");
    
    // CHECK IF DEBUG MODE IS ACTIVATED
    /// @todo trasformare tutto in direttive preprocessor #ifndef
    bool debug_flag;
    
    const string True = "true";
    const string False = "false";
    if(arg == True)
        debug_flag = true;
    else if(arg == False)
        debug_flag = false;
    else
        throw logic_error("The 5th argument in function main() must be a bool (it is the \"debug_flag\")");
    
    // OPEN OUTPUT FILE
    
    string outfile = outdir + "/history/" + "simulation_output";
    ofstream output(outfile);
    if (!output)
        throw runtime_error("couldn't open 'simulation_output' for writing");
    
    string outfile1 = outfile + "_volumes";
    ofstream output1(outfile1);
    if (!output1)
        throw runtime_error("couldn't open 'simulation_output_volumes' for writing");
    
    // SETUP THE TRIANGULATION
    
    Triangulation universe(TimeLength,lambda);
//     if(false){
    if(run_num !=1){
        cerr << "ciao";
        string loadfile = outdir + "/checkpoint/" + last_chkpt;
        cout << loadfile;
        
        Triangulation aux_universe(loadfile);
        universe = aux_universe;
    }
    
    // MOVE
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> dice(1,4);
    
    int i=0;
    int j=0;
	auto time_ref = chrono::system_clock::now();
    
    
    // prima di cominciare faccio il primo salvataggio
    save_routine(outdir, chkpts, n_chkpt, universe);
    
    /// @todo devo decidere se fermarmi dopo un certo numero di mosse o se raggiungo una certa condizione (ad esempio: un certo numero di mosse termalizzate)
    
    while(i<last_step){
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
        i++;
        if(i % (last_step/1000) == 0)
            universe.print_space_profile(output);
        
        /// @todo mettere un #ifdef (copia da Giuseppe) anziché debug_flag
        universe.is_consistent(debug_flag);
        
        /** @todo ogni tot mosse deve
         *      - salvare il volume
         *      - salvare il profilo spaziale
         *      - fare un checkpoint (fa i check con il tempo)
         *          - i checkpoint ruotano su un numero x di file
         *            prima li rinomina tutti facendoli scorrere
         *            poi salva sull'ultimo che si è liberato
         */ 
		
        if(i % 100 == 0){
            /// @todo in realtà sarà la condizione logaritmica
            j++;
            output1 << i << ", " << universe.list2.size();
            if(j == 1){
                j=0;
                universe.print_space_profile(output);
            }
            chrono::duration<double> from_last = chrono::system_clock::now() - time_ref;
            if(from_last.count()/60 > save_interval){
                cerr << "ciao";
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
            save_routine(outdir, chkpts, n_chkpt, universe);
            }
        }
    }
    
    universe.print_space_profile('v');
}


void save_routine(string outdir, vector<string> chkpts, int n_chkpt, Triangulation universe){
    string logfile = outdir + "/" + "runs_log.txt";
    ofstream logput;
    logput.open (logfile, ofstream::out | ofstream::app);
    if (!logput)
        throw runtime_error("couldn't open 'logput' for writing");
    logput << "\nsto salvando... ";
    
    string tmp_chkpt = chkpts[n_chkpt] + ".tmp";
    universe.save(tmp_chkpt);
    
    logput << "COMPLETATO";
    
    char aux_cstr1[tmp_chkpt.size()+1];
    tmp_chkpt.copy(aux_cstr1, tmp_chkpt.size()+1);
    aux_cstr1[tmp_chkpt.size()] = '\0';
    
    char aux_cstr2[chkpts[n_chkpt].size()+1];
    chkpts[n_chkpt].copy(aux_cstr2, chkpts[n_chkpt].size()+1);
    aux_cstr2[chkpts[n_chkpt].size()] = '\0';
    
    rename(aux_cstr1, aux_cstr2);
}
