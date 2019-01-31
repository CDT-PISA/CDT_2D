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

int main(int argc, char* argv[]) {
// int main(){
//     int argc = 5;
//     string argv[6]={" ","output","0","51","10000","true"};
    
    if(argc < 1)
        throw logic_error("output folder not specified");
    else if (argc < 3)
        throw logic_error("too few arguments in function main()");
    
    // OPEN OUTPUT FILE
    
    string outdir = argv[1];
    string outfile = outdir + "/" + "simulation_output";
    ofstream output(outfile);
    if (!output)
        throw runtime_error("couldn't open 'simulation_output' for writing");
    
    // SETUP THE DEFAULT TRIANGULATION
    
    double lambda = stod(argv[2]);
    Triangulation universe(stoi(argv[3]),lambda);
    
    // MOVE
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> dice(3,4);
    
    int i=0;
    /**
     * @todo devo decidere se fermarmi dopo un certo numero di mosse o se raggiungo una certa condizione (ad esempio: un certo numero di mosse termalizzate)
     */ 
    while(i<stoi(argv[4])){
        cout << i << ") ";
        switch(dice(mt)){ // <-- è questa quella giusta, l'altra è solo per i test!!!!
//         switch(vec[i]){
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
        universe.print_space_profile(output);
        
        bool debug_flag;
        string arg = argv[5];
        const string True = "true";
        const string False = "false";
        if(arg == True)
            debug_flag = true;
        else if(arg == False)
            debug_flag = false;
        else
            throw logic_error("The 5th argument in function main() must be a bool (it is the \"debug_flag\")");
        universe.is_consistent(debug_flag);
    }
    universe.print_space_profile('v');
}
