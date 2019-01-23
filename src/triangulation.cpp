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

#include <iostream>
#include <iomanip>
#include <memory>
#include <stdexcept>
#include <random>
#include <cmath>
#include "triangulation.h"
/**
 * @todo Is a good practice to reinclude in the .cpp the header already included in the corresponding .h?
 */
#include "vertex.h"
#include "triangle.h"

using namespace std;

// ##### STARTING TRIANGULATION INITIALIZATION #####

/**
 * @todo comment: describe the structure at which is initialized and the way chosen to construct it (sotto @usage)
 * 
 * @note the whole function could be "extended" to reproduce the same configuration (time and translational invariant) for arbirtary values of the space volume at fixed time (instead of 3)\n
 * but there is no real reason to do it, because 3 is the minimal space volume for a given slice, but the other values are all the same --> so, at least for now, it remains fixed only to 3
 */ 
Triangulation::Triangulation(int TimeLength)
{
    if(TimeLength < 1)
        throw out_of_range("only positive time length are excepted for a triangulation");
    
    num40 = 0;
    num40p = 0;
    list0.clear();
    list2.clear();
    spatial_profile.clear();
    transition1221.clear();
    transition2112.clear();
    
    // ----- FIRST STRIP -----
    
    spatial_profile.push_back(3);
        
    for(int j=0;j<6;j++){   // initialize the 6 triangles in the first(zeroth) strip
        Label lab(new Triangle(list2.size())); // list2.size() has to be equal to j
        list2.push_back(lab);
        
        if(j<3){     // set transitions vectors
            lab.dync_triangle()->transition_id = transition1221.size();
            transition1221.push_back(lab);
        }
        else{
            lab.dync_triangle()->transition_id = transition2112.size();
            transition2112.push_back(lab);
        }
    }
    
    for(int j=0;j<3;j++){   // initialize the 3 vertices at time 1
        Label lab(new Vertex(list0.size(),1,6,list2[j]));    // list2.size() has to be equal to j
        list0.push_back(lab);
        list2[j].dync_triangle()->vertices()[2] = lab;
        
        int tri_id1 = j + 3;
        int tri_id2 = (j + 1)%3 + 3;
        list2[tri_id1].dync_triangle()->vertices()[1] = lab; /** @todo allegare disegni */
        list2[tri_id2].dync_triangle()->vertices()[0] = lab;
    }
    
    /* at the end of these first steps the only things missed are:\n
     * - related to the vertices at time 0, that will be initialize in the next section (Triangle::vertices)
     * - or the adjacency relations among triangles, that will be fixed in the final section (Triangle::adjacents_t)
     */ 
    
    // ----- INTERMEDIATE STRIPS -----
    
    for(int i=1;i<TimeLength;i++){
        spatial_profile.push_back(3);
        
        // STRIP TRIANGLES
        
        for(int j=0;j<6;j++){ // initialize the 6 triangles in the ith strip
            Label lab(new Triangle(list2.size())); // list2.size() has to be equal to (6*i + j)
            list2.push_back(lab);
            
            if(j<3){     // set transitions vectors
                lab.dync_triangle()->transition_id = transition1221.size();
                transition1221.push_back(lab);
            }
            else{
                lab.dync_triangle()->transition_id = transition2112.size();
                transition2112.push_back(lab);
            }
        }
        
        // VERTICES
            
        for(int j=0;j<3;j++){
            // Initialize the 3 vertices at time i+1
            
            int time = (i+1) % TimeLength;
            Label lab(new Vertex(list0.size(),time,6,list2[6*i+j]));    // list0.size() has to be equal to (3*i + j)
            list0.push_back(lab);
            
            // Now complete the vertices of the corresponding (2,1)-triangle (and fix his type)
            
            Triangle* tri_lab0 = list2[j + 6*i].dync_triangle();
            tri_lab0->type = TriangleType::_21;
            
            tri_lab0->vertices()[2] = lab;    // attach the current vertex to the triangle below it
            /* the vertices at time i (ones below the strip) are [3*(i-1),3*i) so for the triangle = 0 (mod 6) in the strip above:
             * - the down-left corner is the vertex = 2 (mod 3);
             * - the down-right corner is the vertex = 0 (mod 3)
             *
             * and so on for the other (2,1)-triangles in the strip
             */
            tri_lab0->vertices()[1] = list0[3*(i - 1) + j];   // attach the remaining two vertices
            tri_lab0->vertices()[0] = list0[3*(i - 1) + (j + 2)%3];
             
            
            // And now add the current vertex to the adjacent (1,2)-triangles in the strip
            
            Triangle* tri_lab3 = list2[j + 3 + 6*i].dync_triangle(); /** @todo allegare disegni */
            Triangle* tri_lab4 = list2[(j + 1)%3 + 3 + 6*i].dync_triangle();
            tri_lab3->vertices()[1] = lab;
            tri_lab4->vertices()[0] = lab;
            
            // Finally attach to the (1,2)-triangles vertices at the time i (the lower boundary of the strip")
            // and fix the type
            tri_lab3->type = TriangleType::_12;
            tri_lab4->vertices()[2] = list0[3*(i - 1) + j];
        }
        
        // TRIANGLE ADJACENCIES
        for(int j=0;j<3;j++){ /** @todo allegare disegni */
            Triangle* tri_labp = list2[j - 3 + 6*i].dync_triangle();    // triangle (1,2) in the previous strip
            Triangle* tri_lab0 = list2[j + 6*i].dync_triangle();    // triangle (2,1)
            Triangle* tri_lab3 = list2[j + 3 + 6*i].dync_triangle();    // triangle (1,2)
            
            tri_lab0->adjacent_triangles()[0] = list2[(j + 1)%3 + 3 + 6*i];
            tri_lab0->adjacent_triangles()[1] = list2[j + 3 + 6*i];
            tri_lab0->adjacent_triangles()[2] = list2[j - 3 + 6*i];
            
            tri_lab3->adjacent_triangles()[0] = list2[j + 6*i];
            tri_lab3->adjacent_triangles()[1] = list2[(j + 2)%3 + 6*i];
            
            tri_labp->adjacent_triangles()[2] = list2[j + 6*i];
        }
    }
    
    // ----- FINAL STEPS -----
    
    // Still have to fix the adjacencies in the first(zeroth) strip...
    for(int j=0;j<3;j++){ /** @todo allegare disegni */
        Triangle* tri_labp = list2[j - 3 + 6*TimeLength].dync_triangle();   // triangle (1,2) in the previous strip
        Triangle* tri_lab0 = list2[j].dync_triangle();    // triangle (2,1)
        Triangle* tri_lab3 = list2[j + 3].dync_triangle();    // triangle (1,2)
        
        tri_lab0->adjacent_triangles()[0] = list2[(j + 1)%3 + 3];
        tri_lab0->adjacent_triangles()[1] = list2[j + 3];
        tri_lab0->adjacent_triangles()[2] = list2[j - 3 + 6*TimeLength];
        
        tri_lab3->adjacent_triangles()[0] = list2[j];
        tri_lab3->adjacent_triangles()[1] = list2[(j + 2)%3];
        
        tri_labp->adjacent_triangles()[2] = list2[j];
        
    // ... and the types...
        tri_lab0->type = TriangleType::_21;
        tri_lab3->type = TriangleType::_12;
    }
    
    // ... and vertices of (2,1)-triangles (ones at time 0)
    for(int j=0;j<3;j++){
        Triangle* tri_lab0 = list2[j].dync_triangle();
        Triangle* tri_lab3 = list2[j+3].dync_triangle();
        
        tri_lab0->vertices()[0] = list0[(TimeLength - 1)*3 + (j + 2)%3];
        tri_lab0->vertices()[1] = list0[(TimeLength - 1)*3 + j];
        
        tri_lab3->vertices()[2] = list0[(TimeLength - 1)*3 + (j + 2)%3];
    }
}
 
// ##### SIMPLEX MANAGEMENT #####
 
int Triangulation::create_vertex(int Time, int coordination_number, Label triangle)
{
    int list_position=list0.size();
    Label lab(new Vertex(list_position, Time, coordination_number, triangle));
    
    list0.push_back(lab);
    
    return list_position;
}

int Triangulation::create_triangle()
{
    int list_position=list2.size();
    Label lab(new Triangle(list_position));
    
    list2.push_back(lab);
    
    return list_position;
}

int Triangulation::create_triangle(Label vertices[3], Label adjacents_t[3],TriangleType type)
{
    int list_position=list2.size();
    Label lab(new Triangle(list_position,vertices,adjacents_t,type));
    
    list2.push_back(lab);
    
    return list_position;
    
}

/** 
 * @todo migliorare gestione degli errori 
 * @todo devo controllare che non ci siano triangoli ancora attaccati o forse no? 
 * @todo controllare se ci sono altre cose da fare quando viene rimosso un vertice
 * 
 * @test verificare che funzioni regolarmente (magari anche dopo aver individuato esattamente come la uso nelle mossee e aver quindi definito cosa deve fare lei o cosa viene fatto esplicitamente nelle mosse)
 */
void Triangulation::remove_vertex(Label v_lab)
{
    try{        
        if(v_lab->id < (num40 - 1)){
            list0[v_lab->id] = list0[num40 - 1];
            list0[num40-1] = v_lab;
            
            v_lab->id = num40 - 1; 
            num40--;
        }
        if(v_lab->id < (num40p - 1)){
            list0[v_lab->id] = list0[num40p - 1];
            list0[num40p-1] = v_lab;
            
            v_lab->id = num40p - 1; 
            num40p--;
        }
        if(v_lab->id != list0.size() - 1){
            list0[v_lab->id] = list0[list0.size() - 1];
            list0[list0.size()-1] = v_lab;
            
            v_lab->id = list0.size() - 1;
        }
        
        spatial_profile[v_lab.dync_vertex()->time()]--;
        list0.pop_back();
    }
    catch(...){
        throw;
    }
}

/** 
 * @todo migliorare gestione degli errori 
 * @todo devo controllare che non ci siano triangoli adiacenti o vertici attaccati? 
 * @todo controllare se ci sono altre cose da fare quando viene rimosso un vertice
 * 
 * Triangulation::transition1221 e Triangulation::transition2112 vanno modificati direttamente nelle mosse, lì è troppo più facile (ho molta più informazione e non devo ricavarmela)
 * 
 * @test verificare che funzioni regolarmente (magari anche dopo aver individuato esattamente come la uso nelle mossee e aver quindi definito cosa deve fare lei o cosa viene fatto esplicitamente nelle mosse)
 */
void Triangulation::remove_triangle(Label tri_lab)
{
    try{
        if(tri_lab->id != list2.size() - 1){
            list2[tri_lab->id] = list2[list2.size() - 1];
            list2[list2.size()-1] = tri_lab;
            
            tri_lab->id = list2.size() - 1;
        }
        
        list2.pop_back();
    }
    catch(...){
        throw;
    }
}

// ##### MOVES #####

/**
 * Questa sarà la mossa
 * \code
 *     v3         v2         v3         v2
 *      * * * * * *           * * * * * *
 *      *        **           **        *
 *      *  1   *  *           *  *   1  *
 *    2 *    *    * 3  -->  2 *    *    * 3
 *      *  *   0  *           *  0   *  *
 *      **        *           *        **
 *      * * * * * *           * * * * * *
 *     v0         v1         v0         v1
 * \endcode
 * 
 * @todo allegare anche qualche altro disegno
 * 
 * @test devo fare i test per questa mossa (forse devo trovare un modo semplice di stampare tutta la triangolazione)
 */ 
void Triangulation::move_22_1()
{   
    long num_t = transition1221.size(); 
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> transition(0, num_t - 1);
    uniform_real_distribution<double> reject_trial(0.0,1.0);
    
    int tr = transition(mt);
//     static int tr = 3;
//     tr++;
    cout << "move_22_1 :" << tr << endl;
    
    /**
     * @todo cercare di capire l'errore "(SIGABRT) free(): double free detected in tcache 2"
     * l'errore si presentava con universe(10) tr scritto nel commento sopra
     * e soprattutto senza i lab_t e i lab_v, e al loro posto c'erano i tri_lab e v_lab
     * 
     * @todo lab_t e lab_v sono un po' ridondanti, quindi per ora credo siano solo temporanei
     * - o sostituisco i tri_lab e uso sempre dync_triangle (stessa cosa per i vertex)
     * - o non uso i lab_t e al loro posto metto sempre list2[tri_lab->position()]
     */ 
    // find triangles (they are needed to compute the reject ratio)
    Triangle* tri_lab0 = transition1221[tr].dync_triangle();
    Triangle* tri_lab1 = tri_lab0->adjacent_triangles()[1].dync_triangle();
    Triangle* tri_lab2 = tri_lab1->adjacent_triangles()[1].dync_triangle();
    Triangle* tri_lab3 = tri_lab0->adjacent_triangles()[0].dync_triangle();
    Label lab_t0 = transition1221[tr];
    Label lab_t1 = tri_lab0->adjacent_triangles()[1];
    Label lab_t2 = tri_lab1->adjacent_triangles()[1];
    Label lab_t3 = tri_lab0->adjacent_triangles()[0];
    
    
    // ----- REJECT RATIO -----
    int x = 1;
    if(tri_lab2->is21())
        x--;
    if(tri_lab3->is12())
        x--;
    
    double reject_ratio = min(1.0,static_cast<double>(num_t)/(num_t + x));
    
    if(reject_trial(mt) > reject_ratio)
        return; // if not rejected goes on, otherwise it returns with nothing done
    
    // ----- CELL "EVOLUTION" -----
    
    // find vertices
    /* it's sane to do it immediately, because first cell elements are recognized, and then modified
     * it is possible to do a mixed version, with some elements identified immediately and some other later, but according to me is really more messy
     */ 
    Vertex* v_lab0 = tri_lab0->vertices()[0].dync_vertex();
    Vertex* v_lab1 = tri_lab0->vertices()[1].dync_vertex();
    Vertex* v_lab2 = tri_lab0->vertices()[2].dync_vertex();
    Vertex* v_lab3 = tri_lab1->vertices()[0].dync_vertex();
    Label lab_v0 = tri_lab0->vertices()[0];
    Label lab_v1 = tri_lab0->vertices()[1];
    Label lab_v2 = tri_lab0->vertices()[2];
    Label lab_v3 = tri_lab1->vertices()[0];
    
    // modify triangles' adjacencies
    tri_lab0->adjacent_triangles()[0] = lab_t1;
    tri_lab0->adjacent_triangles()[1] = lab_t2;
    tri_lab1->adjacent_triangles()[0] = lab_t3;
    tri_lab1->adjacent_triangles()[1] = lab_t0;
    tri_lab2->adjacent_triangles()[0] = lab_t0;
    tri_lab3->adjacent_triangles()[1] = lab_t1;
    
    // modify triangles' vertices
    tri_lab0->vertices()[2] = lab_v3;
    tri_lab1->vertices()[2] = lab_v1;
    
    // modify vertices' near_t
    /** @todo pensare se c'è un modo più furbo di fare le assegnazioni */
    if(v_lab0->adjacent_triangle().dync_triangle() == tri_lab1)
        v_lab0->near_t = lab_t0;
    if(v_lab2->adjacent_triangle().dync_triangle() == tri_lab0)
        v_lab2->near_t = lab_t1;
    
    // modify vertices' coord_num
    v_lab0->coord_num--;
    v_lab2->coord_num--;
    v_lab1->coord_num++;
    v_lab3->coord_num++;
    
    // ----- AUXILIARY STRUCTURES -----
    
    // modify transitions list
    
    if(tri_lab2->is21()){
        /** @todo uno potrrebbe anche pensare di impacchettare queste modifiche delle transition list in dei metodi separati in modo da avere più garanzie sul fatto che gli invarianti siano rispettati */
        if(tri_lab0->transition_id != transition1221.size() - 1){
            Label lab_end = transition1221[transition1221.size() - 1];
            
            lab_end.dync_triangle()->transition_id = tri_lab0->transition_id;
            transition1221[tri_lab0->transition_id] = lab_end;
        }
        transition1221.pop_back();
        tri_lab0->transition_id = -1;
    }
    else{
        tri_lab1->transition_id = transition2112.size();
        transition2112.push_back(lab_t1);
    }
    if(tri_lab3->is12()){
        if(tri_lab3->transition_id != transition2112.size() - 1){
            Label lab_end = transition2112[transition2112.size() - 1];
            
            lab_end.dync_triangle()->transition_id = tri_lab3->transition_id;
            transition2112[tri_lab3->transition_id] = lab_end;
        }
        transition2112.pop_back();
        tri_lab3->transition_id = -1;
    }
    else{
        tri_lab3->transition_id = transition1221.size();
        transition1221.push_back(lab_t3);
    }
    
    /** @todo ripensare a questo errore */
    if(transition1221.size() != transition2112.size()){
        cout << "transition1221: " << transition1221.size() << " transition2112: " << transition2112.size();
        cout.flush();
        throw runtime_error("Not the same number of transitions of the two types");
    }
    
    // find vert. coord. 4 and patologies
    
    /* vertex 0,2 were not of coord. 4, and they could have become
     * vertex 1,3 could be of coord. 4, and now they are not
     */ 
    
    vector<Vertex*> vec;
    vec.push_back(v_lab0);
    vec.push_back(v_lab2);
    
    for(auto x : vec){
        if(x->coordination() == 4){
            Label lab = list0[x->position()];
            
            list0[x->position()] = list0[num40 + num40p];
            list0[x->position()].dync_vertex()->id = x->position();
            list0[num40 + num40p] = lab;
            list0[num40 + num40p].dync_vertex()->id = num40 + num40p;
            
            if(spatial_profile[x->time()] == 3){
                num40p++;
            }
            else{                
                list0[x->position()] = list0[num40];
                list0[x->position()].dync_vertex()->id = x->position();
                list0[num40] = lab;
                list0[num40].dync_vertex()->id = num40;
                
                num40++;
            }
        }        
    }
    
    vec.clear();
    vec.push_back(v_lab1);
    vec.push_back(v_lab3);
    
    for(auto x : vec){
        if(x->coordination() == 5){
            Label lab = list0[x->position()];

            if(spatial_profile[x->time()] == 3){
                num40p--;
            }
            else{
                num40--;
                
                list0[x->position()] = list0[num40];
                list0[x->position()].dync_vertex()->id = x->position();
                list0[num40] = lab;
                list0[num40].dync_vertex()->id = num40;
            }
            list0[x->position()] = list0[num40 + num40p];
            list0[x->position()].dync_vertex()->id = x->position();
            list0[num40 + num40p] = lab;
            list0[num40 + num40p].dync_vertex()->id = num40 + num40p;
        }        
    }
}

/**
 * Questa sarà la mossa
 * \code
 *     v3         v2         v3         v2
 *      * * * * * *           * * * * * *
 *      *        **           **        *
 *      *  1   *  *           *  *   1  *
 *    2 *    *    * 3  -->  2 *    *    * 3
 *      *  *   0  *           *  0   *  *
 *      **        *           *        **
 *      * * * * * *           * * * * * *
 *     v0         v1         v0         v1
 * \endcode
 */ 
void Triangulation::move_22_2()
{
}

/**
 * Questa sarà la mossa
 * \code
 *            v2                            v2
 *             *                             *       
 *            * *                          * * *      
 *        5  *   *  4                5   *   *   *   4
 *          *  0  *                    *  0  *  3  *  
 *         *       *                 *       *       *
 *     v0 * * * * * * v1   -->   v0 * * * * * * * * * * * v1
 *         *       *                 *       *       *
 *          *  1  *                    *  1  *  2  *    
 *        6  *   *  7                6   *   *   *   7   
 *            * *                          * * *      
 *             *                             *       
 *            v3                            v3
 * \endcode
 */
void Triangulation::move_24()
{
    // the number of points is equal to the number of space-links (space volume) that is equal to the number of triangles (spacetime volume)
    long volume = list2.size(); 
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> extracted_triangle(0, volume - 1);
    uniform_real_distribution<double> reject_trial(0.0,1.0);
    
    // ----- REJECT RATIO -----
    double reject_ratio = min(1.0,static_cast<double>(volume)/(num40+1));
    
    if(reject_trial(mt) > reject_ratio)
        return; // if not rejected goes on, otherwise it returns with nothing done
    
    // ----- CELL "EVOLUTION" -----
    int extr = extracted_triangle(mt);
//     static int tr = 3;
//     tr++;
    cout << "move_24 :" << extr << endl;
    
    if(list2[extr].dync_triangle()->is21())
    
}

/**
 * Questa sarà la mossa
 * \code
 *              v2                              v2        
 *               *                               *        
 *             * * *                            * *       
 *       5   *   *   *   4                  5  *   *  4   
 *         *  0  *  3  *                      *  0  *     
 *       *       *       *                   *       *    
 *   v0 * * * * * * * * * * * v1   -->   v0 * * * * * * v1
 *       *       *       *                   *       *    
 *         *  1  *  2  *                      *  1  *     
 *       6   *   *   *   7                  6  *   *  7   
 *             * * *                            * *       
 *               *                               *        
 *              v3                              v3        
 * \endcode
 */
void Triangulation::move_42()
{
}


// ##### USER INTERACTION METHODS #####

/** @todo implementare quella carina orizzontale*/
void Triangulation::print_space_profile()
{
    
}

void Triangulation::print_space_profile(char orientation)
{
    switch(orientation){
        case 'h':
        {
            print_space_profile();
            break;
        }   
        case 'v':
        {
            int max=3;
            for(auto x : spatial_profile){
                if(x > max)
                    max = x;
            }
                
            for(int i=0;i<spatial_profile.size();i++){
                cout << i << ": ";
                
                int length = (spatial_profile[i] * 100) / max;
                for(int j=0;j<length;j++)
                    cout << "#";
                
                cout << " " << setprecision(3) << length/100.0 << endl;
            }
            break;
        }
    }
}

// ##### SIMULATION RESULTS - SAVE METHODS #####

/** @todo quella importante sarà quella che stampa su file, e lo farà stampando i numeri*/
void Triangulation::print_space_profile(std::ofstream save_file, std::__cxx11::string filename)
{
}
