/*
 * <one line to give the program's name and a brief idea of what it does.>
 * Copyright (C) 2019  Alessandro Candido <email>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef TRIANGULATION_H
#define TRIANGULATION_H

#include <vector>
#include <string>
#include "label.h"
using namespace std;

/**
 * @todo write docs
 * @todo function create_vertex, create_triangle (e create_empty_triangle, che può essere una funzione indipendente o la stessa funzione create_triangle overloadata senza argomenti): le funzioni ritornano id
 * @todo usare ovunque, quindi per cominciare nel costruttore, le funzioni create_vertex e create_triangle anziché fare vertici a mano
 */
class Triangulation
{
public:
    /**
     * @param TimeLength the number of time slices
     */
    Triangulation(int TimeLength);

    /**
     * Destructor
     */
    ~Triangulation(){}

    
    // DATA
    
    /**
    * @brief the space-time volume of the triangulation
    * 
    */
    int volume;
    
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
    int num40;
    
    /**
    * @brief vert. coord. 4 patological
    * 
    * the number of vertices of coordination number 4 "patological", i.e. that belongs to patological time-slices (slices with only 3 vertices)
    * 
    */
    int num40p;
    
    /**
    * @brief the list of triangles in the triangulation
    * 
    */
    vector<Label> list2;
    
    /**
    * @brief list of 1st type transition
    * 
    * list of (1,2)-triangles that are right-members of cells for the move (2,2)
    * 
    * the advantage of using a vector of Label instead of a vector of positions in list2 (int) is that I don't have to update it when I do the moves (2,4)-(4,2) if I do these correctly
    */
    vector<Label> transition2112;
    
    /**
    * @brief list of 2nd type transition
    * 
    * list of (2,1)-triangles that are right-members of cells for the move (2,2)
    * 
    */
    vector<Label> transition1221;
    
    /**
    * @brief sizes of time slices
    * 
    * the list of spatial volumes of each slice in the triangulation
    * 
    */
    vector<int> spatial_profile;  
    
    
    // METHODS
    
    /**
    * @brief
    * 
    * @param Time
    * @param coordination_number
    * @param triangle
    * @return
    */
    int create_vertex(int Time, int coordination_number, Label triangle);
    
    /**
    * @brief
    * 
    * @return
    */
    int create_triangle();
    
    /**
    * @brief 
    * 
    * @param vertices 
    * @param adjacents_t 
    * @return int
    */
    int create_triangle(Label vertices[3], Label adjacents_t[3]);
    
    /**
    * @todo stampa il profilo spaziale (o stampando la sequenza di numeri oppure stampando tanti # su ogni riga)\n
    * dovrò farne due versioni:\n
    * - la versione senza input che stampa # su stdout\n
    * - la versione che prende in input un file e stampa su file\n
    *     (magari questa seconda versione può anche prendere un valore di un file una volta sola e stampare sempre su quello finché non gli viene detto diversamente)
    * 
    */
    void print_space_profile();
    
    /**
     * TODO initialization from file
     * 
     */ 
};

#endif // TRIANGULATION_H
