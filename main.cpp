/** @file */
#include <iostream>
#include <iomanip>
#include "triangulation.h"
#include <random>

// #include "vertex.h"
// #include "triangle.h"

using namespace std;

int main() {
    Triangulation universe(10);    
    
    // MOVE
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int>  dice(1, 4);
    
    int i=0;
    while(i<5){
//         switch(dice(mt)){
        switch(1){
            case 1:
            {
                cout << "Hello";
                universe.move_22_1();
                break;
            }
            case 2:
            {
                break;
            }
            case 3:
            {
                break;   
            }
            case 4:
            {
                break;   
            }
        }
        i++;
    }
    /** @todo scegliere se far terminare dopo un numero fissato di mosse o scegliere una condizione per terminare\n
     * quella della condizione è un'idea, ma potrebbe essere non banale perché la triangolazione è una struttura complessa e le osservabili non sono chiare
     */
        
}
