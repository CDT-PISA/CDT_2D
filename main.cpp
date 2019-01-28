/** @file */
#include <iostream>
#include <iomanip>
#include "triangulation.h"
#include <random>
#include <string>
#include <vector>
// #include <memory>

// #include "label.h"
// #include "simplex.h"
// #include "vertex.h"
// #include "triangle.h"

using namespace std;

// int main(int argc, char* argv[]) {
int main(){
    int argc = 4;
    string argv[5]={" ","output","0","31","10000"};
    if(argc < 1)
        throw logic_error("output folder not specified");
    else if (argc < 3)
        throw logic_error("too few arguments in function main()");
    string outdir = argv[1];
    string outfile = outdir + "/" + "simulation_output";
    ofstream output(outfile);
    if (!output)
        throw runtime_error("couldn't open 'simulation_output' for writing");
    
    double lambda = stod(argv[2]);
    Triangulation universe(stoi(argv[3]),lambda);
    
    // MOVE
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> dice(3,4);
    
    int i=0;
    /**
     * @todo devo poter contare in qualche modo le mosse fatte effettivamente, quindi o metto una variabile che lo fa, oppure devo poterle contare a posteriori ad esempio dalle righe di salvataggio di spatial_profile
     * per ora infatti l'argomento del while dice quanti tentativi vengono fatti, non quante mosse davvero
     * forse per questa cosa sarebbe sensato CHIEDERE A GIUSEPPE O D'ELIA
     */ 
    while(i<stoi(argv[4])){
        cout << i << ") ";
        switch(dice(mt)){ // <-- è questa quella giusta, l'altra è solo per i test!!!!
//         switch(i){
            case 1:
            {
                universe.move_22_1();
                break;
            }
            case 2:
            {
                universe.move_22_2();
                break;
            }
            case 3:
            {
                universe.move_24();
                break;   
            }
            case 4:
            {
                universe.move_42();
                break;
            }
        }
        i++;
        /**
         * @todo I'm saving and printing also the failed attempts, I think that this will be wrong at the end, and when it all works I'll have to watch only to the steps done, and not also to those failed
         */ 
        universe.print_space_profile(output);
    }
    universe.print_space_profile('v');
    
    /** @todo scegliere se far terminare dopo un numero fissato di mosse o scegliere una condizione per terminare\n
     * quella della condizione è un'idea, ma potrebbe essere non banale perché la triangolazione è una struttura complessa e le osservabili non sono chiare
     */
}
