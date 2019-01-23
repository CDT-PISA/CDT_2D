/** @file */
#include <iostream>
#include <iomanip>
#include "triangulation.h"
#include <random>

#include "label.h"
// #include "vertex.h"
#include "triangle.h"

using namespace std;

int main() {
    Triangulation universe(100);    
    
    // MOVE
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int>  dice(1, 4);
    
    int i=0;
    /**
     * @todo devo poter contare in qualche modo le mosse fatte effettivamente, quindi o metto una variabile che lo fa, oppure devo poterle contare a posteriori ad esempio dalle righe di salvataggio di spatial_profile
     */ 
    while(i<10000){
        cout << i << ") ";
//         switch(dice(mt)){ // <-- è questa quella giusta, l'altra è solo per i test!!!!
        switch(1){
            case 1:
            {
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
    Triangle* tri_lab = universe.list2[7].dync_triangle();
    /** @todo scegliere se far terminare dopo un numero fissato di mosse o scegliere una condizione per terminare\n
     * quella della condizione è un'idea, ma potrebbe essere non banale perché la triangolazione è una struttura complessa e le osservabili non sono chiare
     */
}
