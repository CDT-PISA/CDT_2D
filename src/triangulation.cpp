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
#include <string>
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
Triangulation::Triangulation(int TimeLength, double Lambda)
{
    if(TimeLength < 1)
        throw out_of_range("only positive time length are excepted for a triangulation");
 
    lambda = Lambda;
    
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
 
Label Triangulation::create_vertex(int Time, int coordination_number, Label adjacent_triangle)
{
    int list_position=list0.size();
    Label lab(new Vertex(list_position, Time, coordination_number, adjacent_triangle));
    Vertex* v_lab = lab.dync_vertex();
    
    list0.push_back(lab);
    
    // ___ update list0 ___
    if(v_lab->coordination() == 4){
        list0[v_lab->position()] = list0[num40+num40p];
        list0[v_lab->position()]->id = v_lab->position();
        if(num40p != 0){
            list0[num40+num40p] = list0[num40];
            list0[num40+num40p]->id = num40+num40p;
        }
        list0[num40] = lab;
        list0[num40]->id = num40;
        num40++;
    }
    
    // ___ update spatial_profile ___
    spatial_profile[v_lab->time()]++;
    
    return lab;
}

Label Triangulation::create_triangle()
{
    int list_position=list2.size();
    Label lab(new Triangle(list_position));
    
    list2.push_back(lab);
    
    return lab;
}

Label Triangulation::create_triangle(Label vertices[3], Label adjacents_t[3],TriangleType type)
{
    /** @todo gestire errore, almeno con un messaggio, se vertices e adjacents_t vengono scambiati
     * poiché sono dello stesso tipo il compilatore non da errore se li inverto, ma l'errore me lo becco a runtime
     */ 
    
    int list_position=list2.size();
    Label lab(new Triangle(list_position,vertices,adjacents_t,type));
    
    list2.push_back(lab);
    
    return lab;
}

/** 
 * @todo migliorare gestione degli errori 
 * @todo devo controllare che non ci siano triangoli ancora attaccati o forse no? 
 * @todo controllare se ci sono altre cose da fare quando viene rimosso un vertice
 * 
 * @test verificare che funzioni regolarmente (magari anche dopo aver individuato esattamente come la uso nelle mossee e aver quindi definito cosa deve fare lei o cosa viene fatto esplicitamente nelle mosse)
 */
void Triangulation::remove_vertex(Label lab_v)
{
    try{        
        if(lab_v->id < (num40 - 1)){
            list0[lab_v->id] = list0[num40 - 1];
            list0[lab_v->id]->id = lab_v->id;
            list0[num40-1] = lab_v;
            lab_v->id = num40 - 1; 
            
            num40--;
        }
        if(lab_v->id < (num40 + num40p - 1)){
            list0[lab_v->id] = list0[num40 + num40p - 1];
            list0[lab_v->id]->id = lab_v->id;
            list0[num40 + num40p-1] = lab_v;            
            lab_v->id = num40 + num40p - 1; 
            
            num40p--;
        }
        if(lab_v->id != list0.size() - 1){
            list0[lab_v->id] = list0[list0.size() - 1];            
            list0[lab_v->id]->id = lab_v->id;
            list0[list0.size()-1] = lab_v;            
            lab_v->id = list0.size() - 1;
        }
        
        // ___ update spatial_profile ___
        spatial_profile[lab_v.dync_vertex()->time()]--;
        
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
            list2[tri_lab->id]->id = tri_lab->id;
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
    cout << "move_22_1 :" << transition2112[tr]->position() << " " << transition1221[tr].dync_triangle()->vertices()[1]->position() << " ";
    
    /**
     * @todo cercare di capire l'errore "(SIGABRT) free(): double free detected in tcache 2"
     * l'errore si presentava con universe(10) tr scritto nel commento sopra
     * e soprattutto senza i lab_t e i lab_v, e al loro posto c'erano i tri_lab e v_lab
     * POSSIBILE SOLUZIONE: tutto questo succede per colpa del triangolo x (da scoprire, nell'esempio credo sia l'11):
     * - la prima volta viene assegnato come adiacenza ... = tri_labx (in questo modo il label diventa uno shared_ptr che non conosce gli altri shared_ptr, quindi anomalo e convinto di essere l'unico shared_ptr che punta quell'oggetto)
     * - la seconda volta viene sovrascritto e quindi deleta l'oggetto (labx = tri_laby, con labx derivante da qualche array di label, tipo tri_labz->adjacent_triangles()[n])
     * - la terza volta (intercambiabile con la seconda) un altro lato diventa uno shared_ptr solitario con ... = tri_lab_x
     * - alla quarta succede quello che è successo alla seconda, solo che l'oggetto puntato già non esiste più e quindi quando prova a deletarlo non ci riesce e torna l'errore
     * tutto questo è possibile che accada IN SOLE DUE MOSSE
     * 
     * 
     * @todo lab_t e lab_v sono un po' ridondanti, quindi per ora credo siano solo temporanei
     * - o sostituisco i tri_lab e uso sempre dync_triangle (stessa cosa per i vertex)
     * - o non uso i lab_t e al loro posto metto sempre list2[tri_lab->position()]
     */ 
    // ___ find triangles (they are needed to compute the reject ratio) ___
    Label lab_t0 = transition1221[tr];
    Label lab_t1 = lab_t0.dync_triangle()->adjacent_triangles()[1];
    Label lab_t2 = lab_t1.dync_triangle()->adjacent_triangles()[1];
    Label lab_t3 = lab_t0.dync_triangle()->adjacent_triangles()[0];
    Triangle* tri_lab0 = lab_t0.dync_triangle();
    Triangle* tri_lab1 = lab_t1.dync_triangle();
    Triangle* tri_lab2 = lab_t2.dync_triangle();
    Triangle* tri_lab3 = lab_t3.dync_triangle();
    
    cout << tri_lab1->vertices()[0]->position() << endl;
    
    
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
    
    // ___ find vertices ___
    /* it's sane to do it immediately, because first cell elements are recognized, and then modified
     * it is possible to do a mixed version, with some elements identified immediately and some other later, but according to me is really more messy
     */ 
    Label lab_v0 = tri_lab0->vertices()[0];
    Label lab_v1 = tri_lab0->vertices()[1];
    Label lab_v2 = tri_lab0->vertices()[2];
    Label lab_v3 = tri_lab1->vertices()[0];
    Vertex* v_lab0 = lab_v0.dync_vertex();
    Vertex* v_lab1 = lab_v1.dync_vertex();
    Vertex* v_lab2 = lab_v2.dync_vertex();
    Vertex* v_lab3 = lab_v3.dync_vertex();
    
    // ___ modify triangles' adjacencies ___
    tri_lab0->adjacent_triangles()[0] = lab_t1;
    tri_lab0->adjacent_triangles()[1] = lab_t2;
    tri_lab1->adjacent_triangles()[0] = lab_t3;
    tri_lab1->adjacent_triangles()[1] = lab_t0;
    tri_lab2->adjacent_triangles()[0] = lab_t0;
    tri_lab3->adjacent_triangles()[1] = lab_t1;
    
    // ___ modify triangles' vertices ___
    tri_lab0->vertices()[2] = lab_v3;
    tri_lab1->vertices()[2] = lab_v1;
    
    // ___ modify vertices' near_t ___
    /** @todo pensare se c'è un modo più furbo di fare le assegnazioni */
    v_lab0->near_t = lab_t0;
    v_lab2->near_t = lab_t1;
    
    // ___ modify vertices' coord_num ___
    v_lab0->coord_num--;
    v_lab2->coord_num--;
    v_lab1->coord_num++;
    v_lab3->coord_num++;
    
    // ----- AUXILIARY STRUCTURES -----
    
    // ___ modify transitions list ___
    
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
        /* we have to do this only in the case in which t2 is of the type such that a transition between t2 and t1 was not allowed before, indeed otherwise t1 was already a transition-cell right-member, but the transition  doesn't store the value of the left-member, so is not relevant that is changed: t1 was a transition right-member and still is */
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
    
    // ___ find vert. coord. 4 and patologies ___
    
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
            list0[x->position()]->id = x->position();
            list0[num40 + num40p] = lab;
            list0[num40 + num40p]->id = num40 + num40p;
            
            if(spatial_profile[x->time()] == 3){
                num40p++;
            }
            else{                
                list0[x->position()] = list0[num40];
                list0[x->position()]->id = x->position();
                list0[num40] = lab;
                list0[num40]->id = num40;
                
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
                list0[x->position()]->id = x->position();
                list0[num40] = lab;
                list0[num40]->id = num40;
            }
            list0[x->position()] = list0[num40 + num40p];
            list0[x->position()]->id = x->position();
            list0[num40 + num40p] = lab;
            list0[num40 + num40p]->id = num40 + num40p;
        }        
    }
    
    // ----- END MOVE -----
}

/**
 * Questa sarà la mossa
 * \code
 *     v3         v2            v3         v2 
 *      * * * * * *             * * * * * *  
 *      **        *             *        **  
 *      *  *   1  *             *  1   *  *  
 *    2 *    *    * 3   -->   2 *    *    * 3
 *      *  0   *  *             *  *   0  *  
 *      *        **             **        *  
 *      * * * * * *             * * * * * *  
 *     v0         v1            v0         v1 
 * \endcode
 */ 
void Triangulation::move_22_2()
{
       
    long num_t = transition2112.size(); 
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> transition(0, num_t - 1);
    uniform_real_distribution<double> reject_trial(0.0,1.0);
    
    int tr = transition(mt);
    cout << "move_22_2 :" << transition2112[tr]->position() << " " << transition2112[tr].dync_triangle()->vertices()[1]->position() << " ";
    
    // ___ find triangles (they are needed to compute the reject ratio) ___
    Label lab_t0 = transition2112[tr];
    Label lab_t1 = lab_t0.dync_triangle()->adjacent_triangles()[1];
    Label lab_t2 = lab_t1.dync_triangle()->adjacent_triangles()[1];
    Label lab_t3 = lab_t0.dync_triangle()->adjacent_triangles()[0];
    Triangle* tri_lab0 = lab_t0.dync_triangle();
    Triangle* tri_lab1 = lab_t1.dync_triangle();
    Triangle* tri_lab2 = lab_t2.dync_triangle();
    Triangle* tri_lab3 = lab_t3.dync_triangle();
    
    cout << tri_lab0->vertices()[0]->position() << endl;
    
    
    // ----- REJECT RATIO -----
    int x = 1;
    if(tri_lab2->is12())
        x--;
    if(tri_lab3->is21())
        x--;
    
    double reject_ratio = min(1.0,static_cast<double>(num_t)/(num_t + x));
    
    if(reject_trial(mt) > reject_ratio)
        return; // if not rejected goes on, otherwise it returns with nothing done
    
    // ----- CELL "EVOLUTION" -----
    
    // ___ find vertices ___
    /* it's sane to do it immediately, because first cell elements are recognized, and then modified
     * it is possible to do a mixed version, with some elements identified immediately and some other later, but according to me is really more messy
     */ 
    Label lab_v0 = tri_lab1->vertices()[0];
    Label lab_v1 = tri_lab1->vertices()[1];
    Label lab_v2 = tri_lab0->vertices()[1];
    Label lab_v3 = tri_lab1->vertices()[2];
    Vertex* v_lab0 = lab_v0.dync_vertex();
    Vertex* v_lab1 = lab_v1.dync_vertex();
    Vertex* v_lab2 = lab_v2.dync_vertex();
    Vertex* v_lab3 = lab_v3.dync_vertex();
    
    // ___ modify triangles' adjacencies ___
    tri_lab0->adjacent_triangles()[0] = lab_t1;
    tri_lab0->adjacent_triangles()[1] = lab_t2;
    tri_lab1->adjacent_triangles()[0] = lab_t3;
    tri_lab1->adjacent_triangles()[1] = lab_t0;
    tri_lab2->adjacent_triangles()[0] = lab_t0;
    tri_lab3->adjacent_triangles()[1] = lab_t1;
    
    // ___ modify triangles' vertices ___
    tri_lab0->vertices()[2] = lab_v0;
    tri_lab1->vertices()[2] = lab_v2;
    
    // ___ modify vertices' near_t ___
    /** @todo pensare se c'è un modo più furbo di fare le assegnazioni */
    v_lab1->near_t = lab_t1;
    v_lab3->near_t = lab_t0;
    
    // ___ modify vertices' coord_num ___
    v_lab1->coord_num--;
    v_lab3->coord_num--;
    v_lab0->coord_num++;
    v_lab2->coord_num++;
    
    // ----- AUXILIARY STRUCTURES -----
    
    // ___ modify transitions list ___
    
    if(tri_lab2->is12()){
        /** @todo uno potrrebbe anche pensare di impacchettare queste modifiche delle transition list in dei metodi separati in modo da avere più garanzie sul fatto che gli invarianti siano rispettati */
        if(tri_lab0->transition_id != transition2112.size() - 1){
            Label lab_end = transition2112[transition2112.size() - 1];
            
            lab_end.dync_triangle()->transition_id = tri_lab0->transition_id;
            transition2112[tri_lab0->transition_id] = lab_end;
        }
        transition2112.pop_back();
        tri_lab0->transition_id = -1;
    }
    else{
        /* see the corresponding comment in move_22_1 */
        tri_lab1->transition_id = transition1221.size();
        transition1221.push_back(lab_t1);
    }
    if(tri_lab3->is21()){
        if(tri_lab3->transition_id != transition1221.size() - 1){
            Label lab_end = transition1221[transition1221.size() - 1];
            
            lab_end.dync_triangle()->transition_id = tri_lab3->transition_id;
            transition1221[tri_lab3->transition_id] = lab_end;
        }
        transition1221.pop_back();
        tri_lab3->transition_id = -1;
    }
    else{
        tri_lab3->transition_id = transition2112.size();
        transition2112.push_back(lab_t3);
    }
    
    /** @todo ripensare a questo errore */
    if(transition1221.size() != transition2112.size()){
        cout << "transition1221: " << transition1221.size() << " transition2112: " << transition2112.size();
        cout.flush();
        throw runtime_error("Not the same number of transitions of the two types");
    }
    
    // ___ find vert. coord. 4 and patologies ___
    
    /* vertex 1,3 were not of coord. 4, and they could have become
     * vertex 0,2 could be of coord. 4, and now they are not
     */ 
    
    vector<Vertex*> vec;
    vec.push_back(v_lab1);
    vec.push_back(v_lab3);
    
    for(auto x : vec){
        if(x->coordination() == 4){
            Label lab = list0[x->position()];
            
            list0[x->position()] = list0[num40 + num40p];
            list0[x->position()]->id = x->position();
            list0[num40 + num40p] = lab;
            list0[num40 + num40p]->id = num40 + num40p;
            
            if(spatial_profile[x->time()] == 3){
                num40p++;
            }
            else{                
                list0[x->position()] = list0[num40];
                list0[x->position()]->id = x->position();
                list0[num40] = lab;
                list0[num40]->id = num40;
                
                num40++;
            }
        }        
    }
    
    vec.clear();
    vec.push_back(v_lab0);
    vec.push_back(v_lab2);
    
    for(auto x : vec){
        if(x->coordination() == 5){
            Label lab = list0[x->position()];

            if(spatial_profile[x->time()] == 3){
                num40p--;
            }
            else{
                num40--;
                
                list0[x->position()] = list0[num40];
                list0[x->position()]->id = x->position();
                list0[num40] = lab;
                list0[num40]->id = num40;
            }
            list0[x->position()] = list0[num40 + num40p];
            list0[x->position()]->id = x->position();
            list0[num40 + num40p] = lab;
            list0[num40 + num40p]->id = num40 + num40p;
        }        
    }
    
    // ----- END MOVE -----
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
 *     v0 * * * * * * v1   -->   v0 * * * * v4* * * * * * v1
 *         *       *                 *       *       *
 *          *  1  *                    *  1  *  2  *    
 *        6  *   *  7                6   *   *   *   7   
 *            * *                          * * *      
 *             *                             *       
 *            v3                            v3
 * \endcode
 * 
 * @todo check if there is something more to be done by the move_24
 * @test check if it works
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
    double reject_ratio = min(1.0,((exp(-2*lambda)*volume)/2)/(num40+1));
    
    if(reject_trial(mt) > reject_ratio)
        return; // if not rejected goes on, otherwise it returns with nothing done
    
    // ----- CELL "EVOLUTION" -----
    
    int extr = extracted_triangle(mt);
//     int extr = ;
    
    cout << "move_24: " << extr;
    
    // ___ cell recognition ___
    
    Label lab_t0 = move_24_find_t0(list2[extr]);
    Label lab_t1 = lab_t0.dync_triangle()->adjacent_triangles()[2];
    Triangle* tri_lab0 = lab_t0.dync_triangle();
    Triangle* tri_lab1 = lab_t1.dync_triangle();
    
    Label lab_v0 = tri_lab0->vertices()[0];
    Label lab_v1 = tri_lab0->vertices()[1];
    Label lab_v2 = tri_lab0->vertices()[2];
    Label lab_v3 = tri_lab1->vertices()[2];
    Vertex* v_lab0 = lab_v0.dync_vertex();
    Vertex* v_lab1 = lab_v1.dync_vertex();
    Vertex* v_lab2 = lab_v2.dync_vertex();
    Vertex* v_lab3 = lab_v3.dync_vertex();
    
    cout << " (time " << v_lab0->time() << ")" << endl;
    
    // ___ create new Triangles and vertex, and put already in them the right values ___
    Label lab_v4 = create_vertex(v_lab0->time(),4,lab_t0);
    Vertex* v_lab4 = lab_v4.dync_vertex();
    
    Label t2_adjancencies[3];
    Label t3_adjancencies[3];
    Label t2_vertices[3];
    Label t3_vertices[3];
    t2_adjancencies[0] = tri_lab1->adjacent_triangles()[0];
    t2_adjancencies[1] = lab_t1;
    t2_adjancencies[2] = lab_t0;    // actually wrong, is lab_t3, but is still to be created
    t2_vertices[0] = lab_v4;
    t2_vertices[1] = lab_v1;
    t2_vertices[2] = lab_v3;
    t3_adjancencies[0] = tri_lab0->adjacent_triangles()[0];
    t3_adjancencies[1] = lab_t0;
    t3_adjancencies[2] = lab_t1;    // actually wrong, is lab_t3, but is still to be created
    t3_vertices[0] = lab_v4;
    t3_vertices[1] = lab_v1;
    t3_vertices[2] = lab_v2;
    
    Label lab_t2 = create_triangle(t2_vertices,t2_adjancencies,TriangleType::_12);
    Label lab_t3 = create_triangle(t3_vertices,t3_adjancencies,TriangleType::_21);
    Triangle* tri_lab2 = lab_t2.dync_triangle();
    Triangle* tri_lab3 = lab_t3.dync_triangle();
    tri_lab2->adjacent_triangles()[2] = lab_t3;
    tri_lab3->adjacent_triangles()[2] = lab_t2;
    
    // ___ update adjancencies and vertices of the initial triangles ___
    tri_lab0->adjacent_triangles()[0] = lab_t3;
    tri_lab1->adjacent_triangles()[0] = lab_t2;
    tri_lab3->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] = lab_t3;
    tri_lab2->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] = lab_t2;
    
    tri_lab0->vertices()[1] = lab_v4;
    tri_lab1->vertices()[1] = lab_v4;
    
    // ___ update already existing vertex properties ___
    // coordination number
    v_lab2->coord_num++;
    v_lab3->coord_num++;
    
    // the adjacency of vertex 1
    /* (the other ones have still the same adjacencies of before, plus the new triangles, but not less) */
    v_lab1->near_t = lab_t3;
    
    // ___ update list0 (pathologies) ___
    
    if(spatial_profile[v_lab4->time()] == 4){ // 4 because the update of spatial_profile is directly in create_vertex
        /* vert. coord. 4 in the time slice of v4 previously pathological no longer are */
        if(v_lab0->coordination() == 4){
            list0[v_lab0->position()] = list0[num40];
            list0[v_lab0->position()]->id = v_lab0->position();
            list0[num40] = lab_v0;
            list0[num40]->id = num40;
            num40++;
            num40p--;
        }
        if(v_lab1->coordination() == 4){
            list0[v_lab1->position()] = list0[num40];
            list0[v_lab1->position()]->id = v_lab1->position();
            list0[num40] = lab_v1;
            list0[num40]->id = num40;
            num40++;
            num40p--;
        }
        
        // then find the third vertex
        /* the third, respect to vertex 1 and  0, already in the time slice of vertex 4 */
        Label current_triangle = tri_lab3->adjacent_triangles()[0];
        while(current_triangle.dync_triangle()->is12()){
            current_triangle = current_triangle.dync_triangle()->adjacent_triangles()[0];
        }
        Label third_vertex = current_triangle.dync_triangle()->vertices()[1]; 
        if(third_vertex.dync_vertex()->coordination() == 4){
            list0[third_vertex->position()] = list0[num40];
            list0[third_vertex->position()]->id = third_vertex->position();
            list0[num40] = third_vertex;
            list0[num40]->id = num40;
            num40++;
            num40p--;
        }
    }
    /* vertex 2 and 3 couldn't be of coord. 4 before, because they have more than one time link toward the same time slice */ 
    
    // ----- END MOVE -----
    
    /* notice that transition list has not to be updated (no need because of the choices made in move construction, in particular because of triangles are inserted on the right, and transitions are represented by right members of the cell) */
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
 *   v0 * * * * v4* * * * * * v1   -->   v0 * * * * * * v1
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
    // the number of points is equal to the number of space-links (space volume) that is equal to the number of triangles (spacetime volume)
    
    if((num40 == 0) && (num40p == 0))
        return;
    
    random_device rd;
    mt19937_64 mt(rd());
    uniform_int_distribution<int> extracted_vertex(0, num40 + num40p - 1);
    uniform_real_distribution<double> reject_trial(0.0,1.0);
    
    // ----- REJECT RATIO -----
    int volume = list2.size();
    double reject_ratio = min(1.0,(exp(2*lambda)*num40)/(volume/2-1));
    
    if(reject_trial(mt) > reject_ratio)
        return; // if not rejected goes on, otherwise it returns with nothing done
    
    // ----- CELL "EVOLUTION" -----
    int extr = extracted_vertex(mt);
    
    if(extr > num40 - 1)
        return;
    
    cout << "move_42: " << extr << " " << list0[extr]->position();
    cout.flush();
    
    // ___ cell recognition ___
    
    Label lab_t0 = move_42_find_t0(list0[extr]);
    Label lab_t1 = lab_t0.dync_triangle()->adjacent_triangles()[2];
    Label lab_t2 = lab_t1.dync_triangle()->adjacent_triangles()[0];
    Label lab_t3 = lab_t0.dync_triangle()->adjacent_triangles()[0];
    Triangle* tri_lab0 = lab_t0.dync_triangle();
    Triangle* tri_lab1 = lab_t1.dync_triangle();
    Triangle* tri_lab2 = lab_t2.dync_triangle();
    Triangle* tri_lab3 = lab_t3.dync_triangle();
    
    Label lab_v0 = tri_lab0->vertices()[0];
    Label lab_v1 = tri_lab2->vertices()[1];
    Label lab_v2 = tri_lab0->vertices()[2];
    Label lab_v3 = tri_lab1->vertices()[2];
    Label lab_v4 = list0[extr];
    Vertex* v_lab0 = lab_v0.dync_vertex();
    Vertex* v_lab1 = lab_v1.dync_vertex();
    Vertex* v_lab2 = lab_v2.dync_vertex();
    Vertex* v_lab3 = lab_v3.dync_vertex();
    Vertex* v_lab4 = lab_v4.dync_vertex();
    
    cout << " (time " << v_lab0->time() << ")" << endl;
    
    // ___ update adjacencies of persisting simplexes ___
    //triangles
    tri_lab0->adjacent_triangles()[0] = tri_lab3->adjacent_triangles()[0];
    tri_lab1->adjacent_triangles()[0] = tri_lab2->adjacent_triangles()[0];
    tri_lab0->vertices()[1] = tri_lab3->vertices()[1];
    tri_lab1->vertices()[1] = tri_lab2->vertices()[1];
    
    tri_lab3->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] = tri_lab3->adjacent_triangles()[1];
    tri_lab2->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] = tri_lab2->adjacent_triangles()[1];
    /* there is no need to update also the vertices for these two because they are already connected to the right one, because it will be vertex 4 that will be removed, and vertex 1 (the one they are already connected to) will remain */
    
    //vertices
    v_lab1->adjacent_triangle() = lab_t0;
    v_lab2->adjacent_triangle() = lab_t0;
    v_lab3->adjacent_triangle() = lab_t1;
    v_lab2->coord_num--;
    v_lab3->coord_num--;
    
    // ___ remove triangles 2 and 3, and vertex 4 ___
    remove_triangle(lab_t2);
    remove_triangle(lab_t3);
    remove_vertex(lab_v4);
    
    // ___ update list0 (pathologies) ___
    
    if(spatial_profile[v_lab4->time()] == 3){// 3 because the update of spatial_profile is directly in remove_vertex
        /* vert. coord. 4 in the time slice of v4 previously were not pathological, now they are */
        if(v_lab0->coordination() == 4){
            list0[v_lab0->position()] = list0[num40-1];
            list0[v_lab0->position()]->id = v_lab0->position();
            list0[num40-1] = lab_v0;
            list0[num40-1]->id = num40-1;
            num40--;
            num40p++;
        }
        if(v_lab1->coordination() == 4){
            list0[v_lab1->position()] = list0[num40-1];
            list0[v_lab1->position()]->id = v_lab1->position();
            list0[num40-1] = lab_v1;
            list0[num40-1]->id = num40-1;
            num40--;
            num40p++;
        }
        
        // then find the third vertex
        /* the third, respect to vertex 1 and  0, already in the time slice of vertex 4 */
        Label current_triangle = tri_lab0->adjacent_triangles()[0];
        while(current_triangle.dync_triangle()->is12()){
            current_triangle = current_triangle.dync_triangle()->adjacent_triangles()[0];
        }
        Label third_vertex = current_triangle.dync_triangle()->vertices()[1]; 
        if(third_vertex.dync_vertex()->coordination() == 4){
            list0[third_vertex->position()] = list0[num40-1];
            list0[third_vertex->position()]->id = third_vertex->position();
            list0[num40-1] = third_vertex;
            list0[num40-1]->id = num40-1;
            num40--;
            num40p++;
        }
    }
    
    /* vertex 2 and 3 cannot become of coord. 4, because they have more than one time link toward the same time slice */ 

    // ----- END MOVE -----
    
    /* notice that transition list has not to be updated (no need because of the choices made in move construction, in particular because of triangles are removed on the right, and transitions are represented by right members of the cell) */
}

// +++++ auxiliary functions (for moves) +++++

Label Triangulation::move_24_find_t0(Label extr_lab)
{
    Triangle* tri_lab = extr_lab.dync_triangle();
    
    if(tri_lab->is21())
        return extr_lab;
    else
        return tri_lab->adjacent_triangles()[2];
}

/**
* @test da verificare
*/
Label Triangulation::move_42_find_t0(Label extr_lab)
{
    Vertex* v_lab = extr_lab.dync_vertex();
    Label  lab_t = v_lab->adjacent_triangle();
    Triangle* tri_lab = lab_t.dync_triangle();
    
    if(tri_lab->is21()){
        if(tri_lab->vertices()[1] == extr_lab)
            return lab_t;
        else if(tri_lab->vertices()[0] == extr_lab)
            return tri_lab->adjacent_triangles()[1];
        else{
            cout << "ciao";
            cout.flush();
            throw runtime_error("Triangulation inconsistency: in cell (4,2) triangle 21 adjacent to the central vertex doesn't own it neither as v[0] nor as v[1]");
        }
    }
    else{
        if(tri_lab->vertices()[1] == extr_lab)
            return tri_lab->adjacent_triangles()[2];
        else if(tri_lab->vertices()[0] == extr_lab)
            return tri_lab->adjacent_triangles()[2].dync_triangle()->adjacent_triangles()[1];
        else{
            cout << "ciao";
            cout.flush();
            throw runtime_error("Triangulation inconsistency: in cell (4,2) triangle 12 adjacent to the central vertex doesn't own it neither as v[0] nor as v[1]");
        }
    }
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
                cout << right << setw(ceil(log10(spatial_profile.size()))) << i << ": ";
                
                int length = (spatial_profile[i] * 100) / max;
                for(int j=0;j<length;j++)
                    cout << "#";
                
                cout << " " << setprecision(3) << length/100.0 << endl;
            }
            cout << "normalization: " << max << endl;
            break;
        }
    }
}

// ##### SIMULATION RESULTS - SAVE METHODS #####

/** @todo quella importante sarà quella che stampa su file, e lo farà stampando i numeri*/
void Triangulation::print_space_profile(ofstream& output)
{
    for(auto x : spatial_profile)
        output << x << " ";
    output << endl;
}

// ##### DEBUG #####

void Triangulation::is_consistent(bool debug_flag)
{
    if(not debug_flag)
        return;
        
    // check list0: Vertices, num40, num40p
    
    for(int i=0; i < list0.size(); i++){
        Label lab = list0[i];
        Vertex* v_lab = lab.dync_vertex();
        
        // id
        
        if(i != lab->id)
            throw runtime_error("Vertex identifier wrong: Vertex in position "+to_string(i)+" in list0, while its identifier points to "+to_string(lab->id));
        
        // near_t
         
        if(not find_vertex_in_triangle(v_lab->near_t.dync_triangle(),lab->id))
            throw runtime_error("Error in Vertex ["+to_string(i)+"]: adjacent Triangle ["+to_string(v_lab->near_t->id)+"] does not include it");
        
        // coordination_number
        
        /*
        if(v_lab->coordination() != count_adjacents(v_lab))
            throw runtime_error("Error in Vertex ["+to_string(i)+"]: number of adjacents triangles is not equal to coordination number stored");
        */
        
    }
    
    // check list2: Triangles
    
    for(int i=0; i < list2.size(); i++){
        Label lab = list2[i];
        Triangle* tri_lab = lab.dync_triangle();
        
        // id
        
        if(i != lab->id)
            throw runtime_error("Triangle identifier wrong: Triangle in position ["+to_string(i)+"] in list2, while its identifier points to ["+to_string(lab->id)+"]");
        
        // TriangleType
        
        if(not (tri_lab->type == TriangleType::_12 or tri_lab->type == TriangleType::_21))
            throw range_error("Error in Triangle ["+to_string(i)+"]: TriangleType not recognized");
        
        // adjacent_triangles: they share a couple of vertices
        
        if(tri_lab->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] != lab)
            throw runtime_error("Error in Triangle: The _right_ adjacent of Triangle ["+to_string(i)+"] is Triangle ["+to_string(tri_lab->adjacent_triangles()[0].dync_triangle()->id)+"], but its _left_ adjacent is not ["+to_string(i)+"] itself");
        /**
         * @todo shared vertices
        bool find_shared_vertices(Triangle* tri_lab,Triangle* ->adjacent_triangles()[0].dync_triangle());
         *
        if(not find_shared_vertices(tri_lab,tri_lab->adjacent_triangles()[0].dync_triangle(),found))
            throw runtime_error("Error in Triangle ["+to_string(i)+"]: is adjacent with Triangle ["+to_string(i)+"] but they don't share two vertices");
        */
        
        if(tri_lab->adjacent_triangles()[1].dync_triangle()->adjacent_triangles()[0] != lab)
            throw runtime_error("Error in Triangle: The _left_ adjacent of Triangle ["+to_string(i)+"] is Triangle ["+to_string(tri_lab->adjacent_triangles()[1].dync_triangle()->id)+"], but its _right_ adjacent is not ["+to_string(i)+"] itself");
        
        if(tri_lab->adjacent_triangles()[2].dync_triangle()->adjacent_triangles()[2] != lab)
            throw runtime_error("Error in Triangle: The _time_ adjacent of Triangle ["+to_string(i)+"] is Triangle ["+to_string(tri_lab->adjacent_triangles()[2].dync_triangle()->id)+"], but its _time_ adjacent is not ["+to_string(i)+"] itself");
        
        // vertices 0 and 1 on the same t_slice, coherent with the TriangleType (vertex 2 on adjacent slice)
        
        if(tri_lab->vertices()[0].dync_vertex()->time() == tri_lab->vertices()[1].dync_vertex()->time()){
            int t_slice0 = tri_lab->vertices()[0].dync_vertex()->time();
            int t_slice2 = tri_lab->vertices()[2].dync_vertex()->time();
            if(tri_lab->is21()){
                if(t_slice2 != ((t_slice0 + 1) % spatial_profile.size()))
                    throw runtime_error("Error in Triangle ["+to_string(tri_lab->id)+"]: vertex 2 in wrong time slice");
            }
            else{
                if(t_slice0 == 0)
                    t_slice0 += spatial_profile.size();
                if(t_slice2 != (t_slice0-1))
                    throw runtime_error("Error in Triangle ["+to_string(tri_lab->id)+"]: vertex 2 in wrong time slice");
            }
        }
        else
            throw runtime_error("Error in Triangle["+to_string(i)+"]: vertices 0 and 1 of the triangle are not on the same time slice");
        
        // transition_id
        
        if(tri_lab->transition_id != -1){ // if is -1 and it's wrong it will be verified in transition lists checks
            if(tri_lab->is12()){
                if(transition2112[tri_lab->transition_id] != lab)
                    throw runtime_error("Error in Triangle ["+to_string(i)+"]: wrong transition_id");
            }
            else{
                if(transition1221[tri_lab->transition_id] != lab)
                    throw runtime_error("Error in Triangle ["+to_string(i)+"]: wrong transition_id");
                
            }
        }
    }
    
    // check space_profile
    
    /**
     * @todo devo trovare il modo di contare i vertici per fare il confronto
     */
    
    // check transitions
    
    for(int i=0; i < transition1221.size(); i++){
        Label lab = transition1221[i];
        Triangle* tri_lab = lab.dync_triangle();
        
        if(tri_lab->transition_id != i)
            throw runtime_error("Error in transition list: in transition1221 element ["+to_string(i)+"] has transition identifier"+to_string(tri_lab->transition_id));
        
        if(not tri_lab->is21())
            throw runtime_error("Error in transition list: in transition1221 right member Triangle ["+to_string(lab->id)+"] is not of type (2,1)");
        if(not tri_lab->adjacent_triangles()[1].dync_triangle()->is12())
            throw runtime_error("Error in transition list: in transition1221 left member Triangle ["+to_string(tri_lab->adjacent_triangles()[1]->id)+"] is not of type (1,2)");
    }
    for(int i=0; i < transition2112.size(); i++){
        Label lab = transition2112[i];
        Triangle* tri_lab = lab.dync_triangle();
        
        if(tri_lab->transition_id != i)
            throw runtime_error("Error in transition list: in transition2112 element ["+to_string(i)+"] has transition identifier"+to_string(tri_lab->transition_id));
        
        if(not tri_lab->is12())
            throw runtime_error("Error in transition list: in transition2112 right member Triangle ["+to_string(lab->id)+"] is not of type (1,2)");
        if(not tri_lab->adjacent_triangles()[1].dync_triangle()->is21())
            throw runtime_error("Error in transition list: in transition2112 left member Triangle ["+to_string(tri_lab->adjacent_triangles()[1]->id)+"] is not of type (1,2)");
    }
}

int Triangulation::count_adjacents(Vertex* v_lab){
    Triangle* initial_triangle = v_lab->near_t.dync_triangle();
    Triangle* current_triangle = initial_triangle;
    int adjacencies = 1;
    bool same_strip = true;
    
    while(same_strip){
        current_triangle = current_triangle->adjacent_triangles()[1].dync_triangle();
        if(not find_vertex_in_triangle(current_triangle,v_lab->id))
            same_strip = false;
        else
            adjacencies++;
    }
    same_strip = true;
    current_triangle = current_triangle->adjacent_triangles()[2].dync_triangle();
    adjacencies++;
    while(same_strip){
        current_triangle = current_triangle->adjacent_triangles()[0].dync_triangle();
        if(not find_vertex_in_triangle(current_triangle,v_lab->id))
            same_strip = false;
        else
            adjacencies++;
    }
    current_triangle = current_triangle->adjacent_triangles()[2].dync_triangle();
    adjacencies++;
    while(current_triangle->id != initial_triangle->id){
        current_triangle = current_triangle->adjacent_triangles()[1].dync_triangle();
        adjacencies++;
    }
    return adjacencies;
}

bool Triangulation::find_vertex_in_triangle(Triangle* adjacent_triangle, int v_id){
    if(v_id == adjacent_triangle->vertices()[0]->id){
        return true;
    }
    else if(v_id == adjacent_triangle->vertices()[1]->id){
        return true;
    }
    else if(v_id == adjacent_triangle->vertices()[2]->id){
        return true;
    }
    else{
        return false;
    }
}
