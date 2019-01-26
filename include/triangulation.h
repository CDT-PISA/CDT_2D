/** @file */
#ifndef TRIANGULATION_H
#define TRIANGULATION_H

#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include "label.h"
#include "triangle.h"
using namespace std;

/**
 * @todo write docs
 * @todo function create_vertex, create_triangle (e create_empty_triangle, che può essere una funzione indipendente o la stessa funzione create_triangle overloadata senza argomenti): le funzioni ritornano id
 * @todo usare ovunque, quindi per cominciare nel costruttore, le funzioni create_vertex e create_triangle anziché fare vertici a mano
 */
class Triangulation
{
public: /// @todo magari la metterò ogni tanto a public per fare dei test ma alla fine deve essere private
    // DATA
    
    /**
    * @brief the space-time volume of the triangulation
    * 
    * @todo perché devo tenermi Triangulation::volume se è = list2.size() ? per ora non lo uso... così non devo tenerlo aggiornato
    */
//     long volume;
    
    /**
     * @todo per ogni vector creare una funzione che elimina l'elemento faccendo uno o più swap e portandolo in fondo e poi fa pop_back\n
     * uno più perché nel caso di un vector con più segmenti per portarlo in fondo e mantenerlo ordinato devo fare swap e portarlo in fondo al primo segmento, poi al secondo e così via\n
     * (inoltre è bene che sia un metodo così ogni volta che scambio qualche elemento gli aggiusto Simplex::id in modo che rimanga coerente)
     */ 
    /**
    * @brief the list of vertices in the triangulation
    * 
    * It has three segments:
    * - [0,num40-1] vert. coord. 4
    * - [num40,num40+num40p-1] vert. coord. 4 patological (see Triangulation::num40p)
    * - [num40+num40p,num0] all other vert.
    * 
    */
    vector<Label> list0;
    
    /**
    * @brief vert. coord. 4 
    * 
    * the number of vertices of coordination number 4 in the triangulation
    * 
    */
    long num40;
    
    /**
    * @brief vert. coord. 4 patological
    * 
    * the number of vertices of coordination number 4 "patological", i.e. that belongs to patological time-slices (slices with only 3 vertices)
    * 
    */
    long num40p;
    
    /**
    * @brief the list of triangles in the triangulation
    * 
    */
    vector<Label> list2;
    
    /**
    * @brief list of 1st type transition
    * 
    * list of (2,1)-triangles that are right-members of cells for the move (2,2)
    * \code
    *         * * * * * *
    * (1,2)-> *        **
    *         *      ****
    *         *    ******
    *         *  ********
    *         *********** <-(2,1)
    *         ***********
    * \endcode
    * the colored triangle is the one of which the label is saved in Triangulation::transition2112
    */
    vector<Label> transition1221;
    
    /**
    * @brief list of 2nd type transition
    * 
    * list of (1,2)-triangles that are right-members of cells for the move (2,2)
    * \code
    *         ***********
    *         *********** <-(1,2)
    *         *  ********
    *         *    ******
    *         *      ****
    * (2,1)-> *        **
    *         * * * * * *
    * \endcode
    * the colored triangle is the one of which the label is saved in Triangulation::transition1221
    * 
    * the advantage of using a vector of Label instead of a vector of positions in list2 (int) is that I don't have to update it when I do the moves (2,4)-(4,2) if I do these correctly
    */
    vector<Label> transition2112;
    
    /**
    * @brief sizes of time slices
    * 
    * the list of spatial volumes of each slice in the triangulation
    * 
    */
    vector<long> spatial_profile;
    
    double lambda;
    
public:
    // ##### STARTING TRIANGULATION INITIALIZATION #####
    
    /** @todo initialization from file */ 
    
    /**
     * @param TimeLength the number of time slices
     */
    Triangulation(int TimeLength, double Lambda);
    
    /**
     * Destructor
     */
    ~Triangulation(){}
    
    // ##### SIMPLEX MANAGEMENT #####
    
    /**
    * @brief
    * 
    * @param Time
    * @param coordination_number
    * @param triangle
    * @return
    */
    Label create_vertex(int Time, int coordination_number, Label triangle);
    
    /**
    * @brief
    * 
    * @return
    */
    Label create_triangle();
    
    /**
    * @brief 
    * 
    * @param vertices 
    * @param adjacents_t 
    * @return Label
    */
    Label create_triangle(Label vertices[3], Label adjacents_t[3], TriangleType type);
    
    void remove_vertex(Label v_lab);
    
    void remove_triangle(Label tri_lab);
    
    // ##### MOVES #####
    
    /** @todo pensare magari a nomi migliori per le mosse */
    
    /**
    * @todo allegare disegno per distinguere la 22_1 dalla 22_2 (e magari nomi più espliciti, forse 22_sx e 22_dx o boh)
    */
    void move_22_1();
    
    void move_22_2();
    
    void move_24();
    
    void move_42();
    
    // auxiliary functions (for moves)
    
    /**
    * @brief find the Triangle 0 in the cell of the move 2 -> 4
    * 
    * @param extr_lab the label of the extracted triangle
    * @return Label of the Triangle 0 of the cell
    */
    Label move_24_find_t0(Label extr_lab);
    
    /**
    * @brief find the Triangle 0 in the cell of the move 4 -> 2
    * 
    * @param extr_lab the label of the extracted triangle
    * @return Label of the Triangle 0 of the cell
    */
    Label move_42_find_t0(Label extr_lab);
    
    // ##### USER INTERACTION METHODS #####
    
    /**
    * @todo stampa il profilo spaziale (o stampando la sequenza di numeri oppure stampando tanti # su ogni riga)\n
    * dovrò farne due versioni:\n
    * - la versione senza input che stampa # su stdout\n
    * - la versione che prende in input un file e stampa su file\n
    *     (magari questa seconda versione può anche prendere un valore di un file una volta sola e stampare sempre su quello finché non gli viene detto diversamente)
    * 
    */
    /**
    * @brief print space profile graphically
    * 
    * @usage this function is the default one, and print the space horizzontally, that is more understable
    */
    void print_space_profile();
    
    /**
    * @brief print space profile graphically
    * 
    * @usage this function let the user specify the orientation, so that is possible to choose the vertical orientation (useful for big TimeLenght)
    * @param orientation could be either 'h' or 'v'
    */
    void print_space_profile(char orientation);
    
    // ##### SIMULATION RESULTS - SAVE METHODS #####
    
    /**
     * @todo dovrebbe poter scegliere il file anche una volta sola e poi usare sempre quello
     * - usare qualcosa static (o qualche cosa del genere per tenere il file aperto)
     * - aprire in append e stampare una riga intera alla volta
     */ 
    void print_space_profile(ofstream& output);
    
};

#endif // TRIANGULATION_H
