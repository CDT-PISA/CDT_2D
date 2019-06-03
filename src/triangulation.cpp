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
#include <fstream>
#include <iomanip>
#include <memory>
#include <stdexcept>
#include <random>
#include <cmath>
#include <complex>
#include <string>
#include "randomgenerator.h"
#include "triangulation.h"
#include "vertex.h"
#include "edge.h"
#include "triangle.h"
#include "label.h"
#include "gaugeelement.h"

using namespace std;

// ##### STARTING TRIANGULATION INITIALIZATION #####

/**
 * @todo comment: describe the structure at which is initialized and the way chosen to construct it (sotto @usage)
 * 
 * @note the whole function could be "extended" to reproduce the same configuration (time and translational invariant) for arbirtary values of the space volume at fixed time (instead of 3)\n
 * but there is no real reason to do it, because 3 is the minimal space volume for a given slice, but the other values are all the same --> so, at least for now, it remains fixed only to 3
 */ 
Triangulation::Triangulation(int TimeLength, double Lambda, double G_ym)
{
    volume_step = 16;
    steps_done = -512;
    iterations_done = 0;
    
    if(TimeLength < 1)
        throw out_of_range("only positive time length are excepted for a triangulation");
 
    lambda = Lambda;
    g_ym = G_ym;
    
    num40 = 0;
    num40p = 0;
    list0.clear();
    list1.clear();
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
    
    for(int j=0;j<3;j++){   // initialize the 3 edges at time 1
        Label vertices[] = {list0[(j + 2)%3], list0[j]};
        Label lab(new Edge(list1.size(), vertices, list2[j+3], EdgeType::_space));
        list1.push_back(lab);
        
        list2[j+3].dync_triangle()->e[2] = lab;
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
        
        // EDGES
        
        for(int j=0;j<3;j++){
            // time-like ones
            Label vertices_s1[] = {list0[(j + 2)%3 + 3*(i-1)], list0[j + 3*i]};
            Label lab_s1(new Edge(list1.size(), vertices_s1, list2[j + 3 + 6*i], EdgeType::_time));
            list1.push_back(lab_s1);
            
            list2[j + 3 + 6*i].dync_triangle()->e[0] = lab_s1;
            list2[j + 6*i].dync_triangle()->e[1] = lab_s1;
            
            Label vertices_s2[] = {list0[j + 3*(i-1)], list0[j + 3*i]};
            Label lab_s2(new Edge(list1.size(), vertices_s2, list2[j + 6*i], EdgeType::_time));
            list1.push_back(lab_s2);
            
            list2[j + 6*i].dync_triangle()->e[0] = lab_s2;
            list2[(j + 1)%3 + 3 + 6*i].dync_triangle()->e[1] = lab_s2;
        }
        for(int j=0;j<3;j++){
            // space-like ones
            Label vertices_t[] = {list0[(j + 2)%3 + 3*i], list0[j + 3*i]};
            Label lab_t(new Edge(list1.size(), vertices_t, list2[j + 3 + 6*i], EdgeType::_space));
            list1.push_back(lab_t);
            
            list2[j + 3 + 6*i].dync_triangle()->e[2] = lab_t;
            list2[j + 6*i].dync_triangle()->e[2] = list1[j + 9*(i - 1)]; // initialized on the previous slice
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
    
    // ... and some edges and their adjacencies ...
    for(int j=0;j<3;j++){
        // missing time-like edges
        Label vertices_t1[] = {list0[(j + 2)%3 + 3*(TimeLength-1)], list0[j]};
        Label lab_t1(new Edge(list1.size(), vertices_t1, list2[j + 3], EdgeType::_time));
        list1.push_back(lab_t1);
        
        list2[j + 3].dync_triangle()->e[0] = lab_t1;
        list2[j].dync_triangle()->e[1] = lab_t1;
        
        Label vertices_t2[] = {list0[j + 3*(TimeLength-1)], list0[j]};
        Label lab_t2(new Edge(list1.size(), vertices_t2, list2[j], EdgeType::_time));
        list1.push_back(lab_t2);
        
        list2[j].dync_triangle()->e[0] = lab_t2;
        list2[(j + 1)%3 + 3].dync_triangle()->e[1] = lab_t2;
        
        // missing time-like adjacencies (space-like edges)
        list2[j].dync_triangle()->e[2] = list1[j + 9*(TimeLength-1)];
    }
    
    // ... and vertices of (2,1)-triangles (ones at time 0)
    for(int j=0;j<3;j++){
        Triangle* tri_lab0 = list2[j].dync_triangle();
        Triangle* tri_lab3 = list2[j+3].dync_triangle();
        
        tri_lab0->vertices()[0] = list0[(TimeLength - 1)*3 + (j + 2)%3];
        tri_lab0->vertices()[1] = list0[(TimeLength - 1)*3 + j];
        
        tri_lab3->vertices()[2] = list0[(TimeLength - 1)*3 + (j + 2)%3];
    }
    
    for(auto v: list0)
        v.dync_vertex()->owner = this;
    for(auto e: list1){
        e.dync_edge()->owner = this;
        e.dync_edge()->U.base_edge = list1[e->id];
    }
    for(auto t: list2)
        t.dync_triangle()->owner = this;
}

/// @todo I NOMI alle variabili
Triangulation::Triangulation(string filename)
{
    load(filename);
}

// ##### SIMPLEX MANAGEMENT #####
 
Label Triangulation::create_vertex(const int& Time, const int& coordination_number, const Label& adjacent_triangle)
{
    int list_position=list0.size();
    Label lab(new Vertex(list_position, Time, coordination_number, adjacent_triangle));
    Vertex* v_lab = lab.dync_vertex();
    
    v_lab->owner = this;
    
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
    int list_position = list2.size();
    Label lab(new Triangle(list_position));
    Triangle* tri_lab = lab.dync_triangle();
    
    tri_lab->owner = this;
    
    list2.push_back(lab);
    
    return lab;
}

Label Triangulation::create_triangle(const Label (&vertices)[3], const Label (&edges)[3], const Label (&adjacents_t)[3], const TriangleType& type)
{
    /** @todo gestire errore, almeno con un messaggio, se vertices e adjacents_t vengono scambiati
     * poiché sono dello stesso tipo il compilatore non da errore se li inverto, ma l'errore me lo becco a runtime
     */ 
    
    int list_position=list2.size();
    Label lab(new Triangle(list_position, vertices, edges, adjacents_t, type));
    Triangle* tri_lab = lab.dync_triangle();
    
    tri_lab->owner = this;
    
    list2.push_back(lab);
    
    return lab;
}

Label Triangulation::create_edge(const Label (&vertices)[2], const Label& triangle, const EdgeType& e_type)
{    
    int list_position=list1.size();
    Label lab(new Edge(list_position, vertices, triangle, e_type));
    Edge* e_lab = lab.dync_edge();    
    
    e_lab->owner = this;
    e_lab->U = 1.;
    e_lab->U.base_edge = list1[e_lab->id];
    
    list1.push_back(lab);
    
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
        if(lab_v->id < num40){
            list0[lab_v->id] = list0[num40 - 1];
            list0[lab_v->id]->id = lab_v->id;
            list0[num40 - 1] = lab_v;
            lab_v->id = num40 - 1; 
            
            num40--;
            if(lab_v->id < num40 + num40p)
                num40p++;
        }
        if(lab_v->id < num40 + num40p){
            list0[lab_v->id] = list0[num40 + num40p - 1];
            list0[lab_v->id]->id = lab_v->id;
            list0[num40 + num40p - 1] = lab_v;            
            lab_v->id = num40 + num40p - 1; 
            
            num40p--;
        }
        if(lab_v->id != list0.size() - 1){
            list0[lab_v->id] = list0[list0.size() - 1];            
            list0[lab_v->id]->id = lab_v->id;
        }
        
        // ___ update spatial_profile ___
        spatial_profile[lab_v.dync_vertex()->time()]--;
        
        Vertex* v_lab = lab_v.dync_vertex();
        Label lab(nullptr);
        v_lab->near_t = lab;
        
        list0.pop_back();
    }
    catch(...){
        throw;
    }
}

void Triangulation::remove_edge(Label lab_e)
{
    try{
        if(lab_e->id != list1.size() - 1){
            list1[lab_e->id] = list1[list1.size() - 1];
            list1[lab_e->id]->id = lab_e->id;
        }
        
        Label lab(nullptr);
        Edge* e_lab = lab_e.dync_edge();
        for(int i=0; i<2; i++){
            e_lab->v[i] = lab;
        }
        e_lab->near_t = lab;
        
        list1.pop_back();
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
void Triangulation::remove_triangle(Label lab_t)
{
    try{
        if(lab_t->id != list2.size() - 1){
            list2[lab_t->id] = list2[list2.size() - 1];
            list2[lab_t->id]->id = lab_t->id;
        }
        
        Label lab(nullptr);
        Triangle* tri_lab = lab_t.dync_triangle();
        for(int i=0; i<3; i++){
            tri_lab->v[i] = lab;
            tri_lab->e[i] = lab;
            tri_lab->t[i] = lab;
        }
        
        list2.pop_back();
    }
    catch(...){
        throw;
    }
}

// ##### MOVES #####
// and their auxiliary functions
#include "moves/moves.cpp"

// ##### USER INTERACTION METHODS #####

/** @todo implementare quella carina orizzontale */
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

// ##### OBSERVABLES #####

/** @todo quella importante sarà quella che stampa su file, e lo farà stampando i numeri*/
void Triangulation::print_space_profile(ofstream& output)
{
    for(auto x : spatial_profile)
        output << x << " ";
    output << endl;
}

double Triangulation::total_gauge_action(bool debug_flag)
{
    double S = 0;
    for(auto lab_v: list0){
        if(debug_flag)
            cout << lab_v->position() << "\n"; cout.flush();
        
        GaugeElement plaq = lab_v.dync_vertex()->looparound();
        
        if(debug_flag)
            cout << lab_v->position() << "ciao\n"; cout.flush();
        
        S += (2/pow(g_ym,2))*real(-(plaq - 1).tr());
    }
    
    return S;
}

constexpr double pi() { return atan(1)*4; }

double Triangulation::topological_charge()
{
    // currently implented only for U(1)
    double charge = 0;
    
    for(auto lab_v: list0){
        GaugeElement plaq = lab_v.dync_vertex()->looparound();
        
        charge += arg(plaq.tr()) / (2 * pi());
    }
    
    return charge;
}


// ##### FILE I/O #####

void Triangulation::save(string filename)
{
    ofstream of(filename, ios::binary | ios::out);
	save(of);
    of.close();
}

void Triangulation::save(ofstream& output)
{   
    output.write((char*)&volume_step, sizeof(volume_step));
    output.write((char*)&steps_done, sizeof(steps_done));
    output.write((char*)&iterations_done, sizeof(iterations_done));
    
    output.write((char*)&lambda, sizeof(lambda));
    output.write((char*)&num40, sizeof(num40));
    output.write((char*)&num40p, sizeof(num40p));
    
    int n_tri = list2.size();
    output.write((char*)&n_tri, sizeof(n_tri));
    
    int n_v = list0.size();
    output.write((char*)&n_v, sizeof(n_v));
    
    int n_e = list1.size();
    output.write((char*)&n_e, sizeof(n_e));
    
    for(auto lab_v : list0)
        lab_v.dync_vertex()->write(output);
    
    for(auto lab_e : list1)
        lab_e.dync_edge()->write(output);
        
    for(auto lab_tri : list2)
        lab_tri.dync_triangle()->write(output);
    
    int TimeLength = spatial_profile.size();
    output.write((char*)&TimeLength, sizeof(TimeLength));
}

void Triangulation::load(string filename)
{
    /** @todo aggiungere come documentazione:
     *
     * leggere id, transition_id e type è facile
     * 
     * per leggere i label invece devo ricostruirle, e per farlo è necessario andare nello stesso ordine del setup di default:
     *      - creo la lista dei triangoli vuoti 
     *      - creo i vertici attaccati ai triangoli
     *      - ripasso sulla lista dei triangoli vuoti e carico i vertici e i triangoli
     * per farlo dovrò creare un array temporaneo parallelo a quello dei triangoli con i t[3] e i v[3]
     */
    
    ifstream input(filename, ios::binary | ios::in);
    load(input);
    input.close();
}

void Triangulation::load(ifstream& input)
{
    list0.clear();
    list1.clear();
    list2.clear();
    
    input.read((char*)&volume_step, sizeof(volume_step));
    input.read((char*)&steps_done, sizeof(steps_done));
    input.read((char*)&iterations_done, sizeof(iterations_done));
    
    input.read((char*)&lambda, sizeof(lambda));
    input.read((char*)&num40, sizeof(num40));
    input.read((char*)&num40p, sizeof(num40p));
    
    // 1st list: empty Triangles
    
    int n_tri = 0;
    input.read((char*)&n_tri, sizeof(n_tri));
    
    for(int i=0; i<n_tri; i++){
        Label lab(new Triangle(i));
        list2.push_back(lab);
    }
    
    // 2nd list: initialized Vertices
    
    int n_v = 0;
    input.read((char*)&n_v, sizeof(n_v));
    
    for(int i=0; i<n_v; i++){        
        Label lab(new Vertex(i));
        list0.push_back(lab);
        
        lab.dync_vertex()->read(input, list2);
    }
    
    // 3nd list: initialized Edges
    
    int n_e = 0;
    input.read((char*)&n_e, sizeof(n_e));
    
    for(int i=0; i<n_e; i++){        
        Label lab(new Edge(i));
        list1.push_back(lab);
        
        lab.dync_edge()->read(input, list0, list1, list2);
    }
    
    // 4th list: Triangle initialization
    
    for(int i=0; i<n_tri; i++)
        list2[i].dync_triangle()->read(input, list0, list1, list2);
    
    // further structures recostruction
    
    int TimeLength;
    input.read((char*)&TimeLength, sizeof(TimeLength));
    
    spatial_profile.resize(TimeLength);
    
    
    // space profile
    for(auto x : list0){
        Vertex v = *x.dync_vertex();
        spatial_profile[v.time()]++;
    }
    
    // transition lists
    for(auto x : list2){
        Triangle tri = *x.dync_triangle();
        
        if(tri.is12()){
            if(tri.adjacent_triangles()[1].dync_triangle()->is21()){
                x.dync_triangle()->transition_id = transition2112.size();
                transition2112.push_back(x);
            }
            else
                x.dync_triangle()->transition_id = -1;
        }
        else{
            if(tri.adjacent_triangles()[1].dync_triangle()->is12()){
                x.dync_triangle()->transition_id = transition1221.size();
                transition1221.push_back(x);
            }
            else
                x.dync_triangle()->transition_id = -1;
        }
    }
        
}

#include "debug/debug.cpp"
