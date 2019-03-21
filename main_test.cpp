/** @file */
#include <iostream>
#include <random>
#include "triangulation.h"

using namespace std;

int main() {
    
    string outdir = "output/run";
    double lambda = -1.56;
    int TimeLength = 10;
    long last_step = 50000;
    string ciao = outdir + "/checkpoint/ciao.triangulation"; /// @todo da sostituire il nome
    
    // OPEN OUTPUT FILE
    
    string outfile = outdir + "/" + "simulation_output";
    ofstream output(outfile);
    if (!output)
        throw runtime_error("couldn't open 'simulation_output' for writing");
    
    // SETUP THE TRIANGULATION
    
    Triangulation universe(TimeLength,lambda);
    Triangulation universe1(TimeLength,lambda);    
    
    for(int i=0; i<1000;i++){
        universe.move_24(false);
    }
    
    universe1 = universe;
    universe.save(ciao);
    
    if(true){//not (ciao == "new_run")){
        Triangulation aux_universe(ciao);
        universe = aux_universe;
    }
    
    for(int i=0; i<universe.transition2112.size(); i++){
        if(universe.transition2112[i]->position() != universe1.transition2112[i]->position())
            cout << "ciao" << endl;
    }
    
    for(int i=0; i<universe.transition1221.size(); i++){
        if(universe.transition1221[i]->position() != universe1.transition1221[i]->position())
            cout << i << endl;
    }

    universe.print_space_profile('v');
    
    // MOVE
    /*
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> dice(1,4);
    
    int i=0;
    */
    /**
     * @todo devo decidere se fermarmi dopo un certo numero di mosse o se raggiungo una certa condizione (ad esempio: un certo numero di mosse termalizzate)
     */ 
    /*
    while(i<last_step){
        
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
    }
    
    universe.print_space_profile('v');*/
}

