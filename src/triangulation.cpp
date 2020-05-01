/** @file triangulation.cpp
 * 
 * In this file are present only the general methods, while
 * other methods with specific purposes are collected and 
 * stored in following files:
 * - **moves.cpp**: 
 * - **adjacency.cpp**:
 * - **debug.cpp**:
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
#include <algorithm>
#include <unordered_set>
#include <unordered_map>
#include "randomgenerator.h"
#include "triangulation.h"
#include "vertex.h"
#include "edge.h"
#include "triangle.h"
#include "label.h"
#include "gaugeelement.h"

using namespace std;

// ##### STARTING TRIANGULATION INITIALIZATION #####
//

/**
 * @todo comment: describe the structure at which is initialized and the way chosen to construct it (sotto @usage)
 * 
 * @note the whole function could be "extended" to reproduce the same configuration (time and translational invariant) for arbirtary values of the space volume at fixed time (instead of 3)\n
 * but there is no real reason to do it, because 3 is the minimal space volume for a given slice, but the other values are all the same --> so, at least for now, it remains fixed only to 3
 */
void Triangulation::initialize(int TimeLength, double Lambda, double Beta, int waist, bool debug_flag)
{
    (void)debug_flag; // since it is unused here
    volume_step = 16;
    steps_done = -512;
    iterations_done = 0;

    if(TimeLength%2!=0){
        throw std::runtime_error("ERROR: incompatible zero twist with odd number of slices");
    }
    int twist = TimeLength/2;
    
    if(TimeLength < 1)
        throw out_of_range("only positive time length are accepted for a triangulation");
 
    lambda = Lambda;
    beta = Beta;
    isBetaZero = (Beta==0.0);
    
    num40 = 0;
    num40p = 0;
    list0.clear();
    list1.clear();
    list2.clear();
    spatial_profile.clear();
    transition1221.clear();
    transition2112.clear();
    edge_uset.clear();
    
    // ----- FIRST STRIP -----
    spatial_profile.push_back(waist);
        
    for(int j=0;j<2*waist;j++){   // initialize the 2*waist triangles in the first(zeroth) strip
        Label lab(new Triangle(list2.size())); // list2.size() has to be equal to j
        list2.push_back(lab);
        
        if(j<waist){     // set transitions vectors
            lab.dync_triangle()->transition_id = transition1221.size();
            transition1221.push_back(lab);
        }else{
            lab.dync_triangle()->transition_id = transition2112.size();
            transition2112.push_back(lab);
        }
    }
    
    for(int j=0;j<waist;j++){   // initialize the 'waist' vertices at time 1
        Label lab(new Vertex(list0.size(),1,6,list2[j]));    // list2.size() has to be equal to j
        list0.push_back(lab);
        list2[j].dync_triangle()->vertices()[2] = lab;
        
        int tri_id1 = j + waist;
        int tri_id2 = (j + 1)%waist + waist;
        list2[tri_id1].dync_triangle()->vertices()[1] = lab; /** @todo allegare disegni */
        list2[tri_id2].dync_triangle()->vertices()[0] = lab;
    }
    for(int j=0;j<waist;j++){   // initialize the waist edges at time 1
        Label vertices[] = {list0[(j + waist-1)%waist], list0[j]};
        Label lab(new Edge(list1.size(), vertices, list2[j+waist], EdgeType::_space));
        list1.push_back(lab);
        
        list2[j+waist].dync_triangle()->e[2] = lab;
    }
    
    /* at the end of these first steps the only things missed are:\n
     * - related to the vertices at time 0, that will be initialize in the next section (Triangle::vertices)
     * - or the adjacency relations among triangles, that will be fixed in the final section (Triangle::adjacents_t)
     */
    
    // ----- INTERMEDIATE STRIPS -----
    
    for(int i=1;i<TimeLength;i++){
        spatial_profile.push_back(waist);
        
        // STRIP TRIANGLES
        
        for(int j=0;j<2*waist;j++){ // initialize the 2*waist triangles in the ith strip
            Label lab(new Triangle(list2.size())); // list2.size() has to be equal to (2*waist*i + j)
            list2.push_back(lab);
            
            if(j<waist){     // set transitions vectors
                lab.dync_triangle()->transition_id = transition1221.size();
                transition1221.push_back(lab);
            }else{
                lab.dync_triangle()->transition_id = transition2112.size();
                transition2112.push_back(lab);
            }
        }
        
        // VERTICES
            
        for(int j=0;j<waist;j++){
            // Initialize the waist vertices at time i+1
            
            int time = (i+1) % TimeLength;
            Label lab(new Vertex(list0.size(),time,6,list2[2*waist*i+j]));    // list0.size() has to be equal to (waist*i + j)
            list0.push_back(lab);
            
            // Now complete the vertices of the corresponding (2,1)-triangle (and fix his type)
            
            Triangle* tri_lab0 = list2[j + 2*waist*i].dync_triangle();
            tri_lab0->type = TriangleType::_21;
            
            tri_lab0->vertices()[2] = lab;    // attach the current vertex to the triangle below it
            /* the vertices at time i (ones below the strip) are [waist*(i-1),waist*i) so for the triangle = 0 (mod 2*waist) in the strip above:
             * - the down-left corner is the vertex = 2 (mod waist);
             * - the down-right corner is the vertex = 0 (mod waist)
             *
             * and so on for the other (2,1)-triangles in the strip
             */
            tri_lab0->vertices()[1] = list0[waist*(i - 1) + j];   // attach the remaining two vertices
            tri_lab0->vertices()[0] = list0[waist*(i - 1) + (j + waist-1)%waist];
             
            
            // And now add the current vertex to the adjacent (1,2)-triangles in the strip
            
            Triangle* tri_lab3 = list2[j + waist + 2*waist*i].dync_triangle(); /** @todo allegare disegni */
            Triangle* tri_lab4 = list2[(j + 1)%waist + waist + 2*waist*i].dync_triangle();
            tri_lab3->vertices()[1] = lab;
            tri_lab4->vertices()[0] = lab;
            
            // Finally attach to the (1,2)-triangles vertices at the time i (the lower boundary of the strip")
            // and fix the type
            tri_lab3->type = TriangleType::_12;
            tri_lab4->vertices()[2] = list0[waist*(i - 1) + j];
        }
        
        // EDGES
        
        for(int j=0;j<waist;j++){
            // time-like ones
            Label vertices_s1[] = {list0[(j + waist-1)%waist + waist*(i-1)], list0[j + waist*i]};
            Label lab_s1(new Edge(list1.size(), vertices_s1, list2[j + waist + 2*waist*i], EdgeType::_time));
            list1.push_back(lab_s1);
            
            list2[j + waist + 2*waist*i].dync_triangle()->e[0] = lab_s1;
            list2[j + 2*waist*i].dync_triangle()->e[1] = lab_s1;
            
            Label vertices_s2[] = {list0[j + waist*(i-1)], list0[j + waist*i]};
            Label lab_s2(new Edge(list1.size(), vertices_s2, list2[j + 2*waist*i], EdgeType::_time));
            list1.push_back(lab_s2);
            
            list2[j + 2*waist*i].dync_triangle()->e[0] = lab_s2;
            list2[(j + 1)%waist + waist + 2*waist*i].dync_triangle()->e[1] = lab_s2;
        }
        for(int j=0;j<waist;j++){
            // space-like ones
            Label vertices_t[] = {list0[(j + waist-1)%waist + waist*i], list0[j + waist*i]};
            Label lab_t(new Edge(list1.size(), vertices_t, list2[j + waist + 2*waist*i], EdgeType::_space));
            list1.push_back(lab_t);
            
            list2[j + waist + 2*waist*i].dync_triangle()->e[2] = lab_t;
            list2[j + 2*waist*i].dync_triangle()->e[2] = list1[j + 3*waist*(i - 1)]; // initialized on the previous slice
        }
        
        // TRIANGLE ADJACENCIES
        for(int j=0;j<waist;j++){ /** @todo allegare disegni */
            Triangle* tri_labp = list2[j - waist + 2*waist*i].dync_triangle();    // triangle (1,2) in the previous strip
            Triangle* tri_lab0 = list2[j + 2*waist*i].dync_triangle();    // triangle (2,1)
            Triangle* tri_lab3 = list2[j + waist + 2*waist*i].dync_triangle();    // triangle (1,2)
            
            tri_lab0->adjacent_triangles()[0] = list2[(j + 1)%waist + waist + 2*waist*i];
            tri_lab0->adjacent_triangles()[1] = list2[j + waist + 2*waist*i];
            tri_lab0->adjacent_triangles()[2] = list2[j - waist + 2*waist*i];
            
            tri_lab3->adjacent_triangles()[0] = list2[j + 2*waist*i];
            tri_lab3->adjacent_triangles()[1] = list2[(j + waist-1)%waist + 2*waist*i];
            
            tri_labp->adjacent_triangles()[2] = list2[j + 2*waist*i];
        }
    }
    
    // ----- FINAL STEPS -----
    
    // Still have to fix the adjacencies in the first(zeroth) strip...
    for(int j=0;j<waist;j++){ /** @todo allegare disegni */
        Triangle* tri_labp = list2[(j+twist)%waist - waist + 2*waist*TimeLength].dync_triangle();   // triangle (1,2) in the previous strip
        Triangle* tri_lab0 = list2[j].dync_triangle();    // triangle (2,1)
        Triangle* tri_lab3 = list2[j + waist].dync_triangle();    // triangle (1,2)
        
        tri_lab0->adjacent_triangles()[0] = list2[(j + 1)%waist + waist];
        tri_lab0->adjacent_triangles()[1] = list2[j + waist];
        tri_lab0->adjacent_triangles()[2] = list2[(j+twist)%waist - waist + 2*waist*TimeLength];
        
        tri_lab3->adjacent_triangles()[0] = list2[j];
        tri_lab3->adjacent_triangles()[1] = list2[(j + waist-1)%waist];
        
        tri_labp->adjacent_triangles()[2] = list2[j];
        
        // ... and the types...
        tri_lab0->type = TriangleType::_21;
        tri_lab3->type = TriangleType::_12;
    }
    
    // ... and some edges and their adjacencies ...
    for(int j=0;j<waist;j++){
        // missing time-like edges
        Label vertices_t1[] = {list0[(j + twist + waist-1)%waist + waist*(TimeLength-1)], list0[j]};
        Label lab_t1(new Edge(list1.size(), vertices_t1, list2[j + waist], EdgeType::_time));
        list1.push_back(lab_t1);
        
        list2[j + waist].dync_triangle()->e[0] = lab_t1;
        list2[j].dync_triangle()->e[1] = lab_t1;
        
        Label vertices_t2[] = {list0[(j + twist)%waist + waist*(TimeLength-1)], list0[j]};
        Label lab_t2(new Edge(list1.size(), vertices_t2, list2[j], EdgeType::_time));
        list1.push_back(lab_t2);
        
        list2[j].dync_triangle()->e[0] = lab_t2;
        list2[(j + 1)%waist + waist].dync_triangle()->e[1] = lab_t2;
        
        // missing time-like adjacencies (space-like edges)
        list2[j].dync_triangle()->e[2] = list1[(j + twist)%waist + 3*waist*(TimeLength-1)];
    }
    
    // ... and vertices of (2,1)-triangles (ones at time 0)
    for(int j=0;j<waist;j++){
        Triangle* tri_lab0 = list2[j].dync_triangle();
        Triangle* tri_lab3 = list2[j+waist].dync_triangle();
        
        tri_lab0->vertices()[0] = list0[(TimeLength - 1)*waist + (j + twist + waist-1)%waist];
        tri_lab0->vertices()[1] = list0[(TimeLength - 1)*waist + (j + twist)%waist];
        
        tri_lab3->vertices()[2] = list0[(TimeLength - 1)*waist + (j + twist + waist-1)%waist];
    }

    for(auto v: list0)
        v.dync_vertex()->owner = this;
    for(auto e: list1){
        e.dync_edge()->owner = this;
        e.dync_edge()->U.base_edge = list1[e->id];
    }
    for(auto t: list2)
        t.dync_triangle()->owner = this;

    fill_edge_uset();
    
    N = list1[0].dync_edge()->gauge_element().N;
}

Triangulation::Triangulation(int TimeLength, double Lambda, double Beta, int waist, bool debug_flag){
    initialize(TimeLength, Lambda, Beta, waist, debug_flag);
}

/// @todo I NOMI alle variabili
Triangulation::Triangulation(string filename)
{
    load(filename);
}

Triangulation::~Triangulation()
{
    transition1221.clear();
    transition2112.clear();
    edge_uset.clear();
    
    Label lab(nullptr);
        
    for(auto x = list0.rbegin(); x != list0.rend(); x++){
        Vertex* v_lab = x->dync_vertex();
        
        v_lab->near_t = lab;
        
        list0.pop_back();
    }
    for(auto x = list1.rbegin(); x != list1.rend(); x++){
        Edge* e_lab = x->dync_edge();
        
        for(int i=0; i<2; i++){
            e_lab->v[i] = lab;
        }
        e_lab->near_t = lab;
        e_lab->U.base_edge = lab;
        
        list1.pop_back();
    }
    for(auto x = list2.rbegin(); x != list2.rend(); x++){
        Triangle* tri_lab = x->dync_triangle();
        
        for(int i=0; i<3; i++){
            tri_lab->v[i] = lab;
            tri_lab->e[i] = lab;
            tri_lab->t[i] = lab;
        }
        
        list2.pop_back();
    }
}
void Triangulation::fill_edge_uset(){
    for(size_t i=0; i<list1.size(); i++){        
        // fills edge hash set
        Label *lab_v_arr = list1[i].dync_edge()->v;
        Vertex* v0=lab_v_arr[0].dync_vertex();
        Vertex* v1=lab_v_arr[1].dync_vertex();
        edge_uset.emplace(v0,v1);
    }
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
    
    list1.push_back(lab);
    e_lab->U.base_edge = list1[e_lab->id];
    
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
        if(lab_v->id != (int)list0.size() - 1){
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
        if(lab_e->id != (int)list1.size() - 1){
            list1[lab_e->id] = list1[list1.size() - 1];
            list1[lab_e->id]->id = lab_e->id;
        }
        
        Label lab(nullptr);
        Edge* e_lab = lab_e.dync_edge();
        for(int i=0; i<2; i++){
            e_lab->v[i] = lab;
        }
        e_lab->near_t = lab;
        e_lab->U.base_edge = lab;
        
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
        if(lab_t->id != (int)list2.size() - 1){
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

void Triangulation::unitarize()
{
    for(auto e_lab : list1)
        e_lab.dync_edge()->U.unitarize();
}

// ##### MOVES #####
// and their auxiliary functions
#include "triangulation/moves.cpp"

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
                
            for(int i=0;i<(int)spatial_profile.size();i++){
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
void Triangulation::print_space_profile(ostream& output)
{
    for(auto x : spatial_profile)
        output << x << " ";
    output << endl;
}

double Triangulation::average_plaquette(bool debug_flag)
{
    double S=0.0;
    for(auto lab_v: list0){
        if(debug_flag)
            cout << "lab_v->position() = "<<lab_v->position() << "\n"; cout.flush();
        
        double contrib = lab_v.dync_vertex()->ReTr_plaquette(debug_flag);
        
        S += contrib;
    }
    
    return S/(double)list0.size();
}

double Triangulation::total_gauge_action(bool debug_flag)
{
    double S = 0;
    for(auto lab_v: list0){
        if(debug_flag)
            cout << lab_v->position() << "\n"; cout.flush();
        
        double contrib = lab_v.dync_vertex()->gauge_action_contrib(debug_flag);
        
        if(debug_flag)
            cout << lab_v->position() << "ciao\n"; cout.flush();
        
        S += - beta * N * contrib;
    }
    
    return S;
}

double Triangulation::average_gauge_action_contribute(bool debug_flag)
{
    double action = total_gauge_action(debug_flag);
    
    return 6 * action / ((beta * N) * list0.size());
}

constexpr double pi() { return atan(1)*4; }

double Triangulation::topological_charge(bool debug_flag)
{
    // currently implented only for U(1)
    double charge = 0;
    
    for(auto lab_v: list0){
        GaugeElement Plaquette = lab_v.dync_vertex()->looparound(debug_flag);
        
        charge += arg(Plaquette.tr()) / (2 * pi());
    }
    
    return charge;
}

GaugeElement Triangulation::space_loop(Triangle* start, bool debug_flag)
{
    //loop around a spatial slice
    // if I go to the right I'm following the direction of GaugeElements
    // and t[0] means going to the right
    Triangle* current = start->t[0].dync_triangle();
    GaugeElement Loop;
    
    while(current != start){
        Loop *= current->e[1].dync_edge()->gauge_element();
        current = current->t[0].dync_triangle();
    }
    Loop *= current->e[1].dync_edge()->gauge_element();
    
    return Loop;
}

vector<complex<double>> Triangulation::toleron(bool debug_flag)
{
    int TimeLength = spatial_profile.size();
    vector<Triangle*> starting_triangles(TimeLength, nullptr);
    
    int i = 0;
    for(auto x: list2){
        int t = x.dync_triangle()->slab_index();
        if(starting_triangles[t] == nullptr){
            starting_triangles[t] = x.dync_triangle();
            i++;
        }
        if(i == TimeLength)
            break;
    }
    
    vector<complex<double>> tolerons(TimeLength, 0.);
    
    for(int i=0; i<TimeLength; i++){
        if( N == 1 || N == 2)
            tolerons[i] = space_loop(starting_triangles[i], debug_flag).tr();
        else
            throw runtime_error("Toleron not implemented");
    }
    
    return tolerons;
}

vector<double> Triangulation::gauge_action_top_charge(bool debug_flag)
{
    double S = 0;
    double charge = 0;
    
    for(auto lab_v: list0){
        if(debug_flag)
            cout << lab_v->position() << endl;
        vector<double> v_vert = lab_v.dync_vertex()->gauge_action_top_charge_densities(debug_flag);
        
        S += - (beta * N) * v_vert[0];
        charge += v_vert[1];
    }
    
    vector<double> v;
    
    v.push_back(S);
    v.push_back(charge);
    
    return v;
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
    RandomGen r;
    uint64_t rng_state = r.get_state();
    output.write((char*)&rng_state,sizeof(rng_state));
    
    output.write((char*)&lambda, sizeof(lambda));
    output.write((char*)&beta, sizeof(beta));
    output.write((char*)&N, sizeof(N));
    
    output.write((char*)&num40, sizeof(num40));
    output.write((char*)&num40p, sizeof(num40p));
    
    int n_v = list0.size();
    output.write((char*)&n_v, sizeof(n_v));

    int n_e = list1.size();
    output.write((char*)&n_e, sizeof(n_e));
    
    int n_tri = list2.size();
    output.write((char*)&n_tri, sizeof(n_tri));
    
    for(auto lab_v : list0)
        lab_v.dync_vertex()->write(output);
    
    for(auto lab_e : list1)
        lab_e.dync_edge()->write(output);
        
    for(auto lab_tri : list2)
        lab_tri.dync_triangle()->write(output);

    size_t tr1221_size = transition1221.size();
    output.write((char*)&tr1221_size,sizeof(tr1221_size));
    size_t tr2112_size = transition2112.size();
    output.write((char*)&tr2112_size,sizeof(tr2112_size));
    
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
    isBetaZero = (beta==0.0);
    input.close();
}

void Triangulation::load(ifstream& input)
{
    list0.clear();
    list1.clear();
    list2.clear();
    edge_uset.clear();
    
    input.read((char*)&volume_step, sizeof(volume_step));
    input.read((char*)&steps_done, sizeof(steps_done));
    input.read((char*)&iterations_done, sizeof(iterations_done));
    uint64_t rng_state;
    input.read((char*)&rng_state,sizeof(rng_state));
    RandomGen r;
    r.set_state(rng_state);
    
    input.read((char*)&lambda, sizeof(lambda));
    input.read((char*)&beta, sizeof(beta));
    input.read((char*)&N, sizeof(N));
    
    input.read((char*)&num40, sizeof(num40));
    input.read((char*)&num40p, sizeof(num40p));
    
    int n_v = 0;
    input.read((char*)&n_v, sizeof(n_v));
    int n_e = 0;
    input.read((char*)&n_e, sizeof(n_e));
    int n_tri = 0;
    input.read((char*)&n_tri, sizeof(n_tri));
    
    // 1st list: empty Triangles
    
    for(int i=0; i<n_tri; i++){
        Label lab(new Triangle(i));
        list2.push_back(lab);
    }
    
    // 2nd list: initialized Vertices
    
    for(int i=0; i<n_v; i++){        
        Label lab(new Vertex(i));
        list0.push_back(lab);
        
        lab.dync_vertex()->read(input, list2);
    }
    
    // 3nd list: initialized Edges
    
    for(int i=0; i<n_e; i++){        
        Label lab(new Edge(i));
        list1.push_back(lab);
        
        lab.dync_edge()->read(input, list0, list1, list2);

    }

    fill_edge_uset();

    
    // 4th list: Triangle initialization
    
    for(int i=0; i<n_tri; i++)
        list2[i].dync_triangle()->read(input, list0, list1, list2);

    size_t tr1221_size, tr2112_size;
    input.read((char*)&tr1221_size,sizeof(tr1221_size));
    input.read((char*)&tr2112_size,sizeof(tr2112_size));
    
    // FURTHER STRUCTURES RECOSTRUCTION
    
//r.set_state(rng_state);
    
    int TimeLength;
    input.read((char*)&TimeLength, sizeof(TimeLength));
    
    // space profile
    spatial_profile.clear();
    spatial_profile.resize(TimeLength);
    fill(spatial_profile.begin(), spatial_profile.end(), 0);

    for(auto x : list0){
        Vertex v = *x.dync_vertex();
        spatial_profile[v.time()]++;
    }
    
    // transition lists
    transition1221.clear();
    transition2112.clear();
    transition1221.resize(tr1221_size);
    transition2112.resize(tr2112_size);
    
    for(auto x : list2){
        Triangle tri = *x.dync_triangle();
        
        if(tri.is12() and tri.adjacent_triangles()[1].dync_triangle()->is21()){
            transition2112[x.dync_triangle()->transition_id]=x;
        }else if(tri.is21() and tri.adjacent_triangles()[1].dync_triangle()->is12()){
            transition1221[x.dync_triangle()->transition_id]=x;
        }
    }
     
    // set ownership
    
//    cout << *this << endl;
    
    for(auto x : list0){
        x->owner = this;
    }
    for(auto x : list1){
        x->owner = this;
    }
    for(auto x : list2){
        x->owner = this;
    }
    
}


struct pair_hash{
        template <class T1, class T2>
                std::size_t operator() (const std::pair<T1, T2> &pair) const{
                            return (std::hash<T1>()(pair.first) << 8) ^ std::hash<T2>()(pair.second);
                                }
};

typedef std::unordered_set<std::pair<int,int>,pair_hash> PairSet;

template <typename T> inline
std::pair<T,T> make_sorted_pair(const T& a, const T& b){
        return (a>b) ? std::make_pair(b,a) : std::make_pair(a,b);
}

void Triangulation::save_abscomp(ofstream& of)
{
    int dim, nverts, nlinks, nsimpx;
    std::unordered_map<std::pair<uint,uint>,double,pair_hash> links_sqlen_map;
    int simpx_nverts, simpx_nlinks;
    std::vector<std::vector<uint>> simpx_verts;     

    dim = 2;
    simpx_nverts = dim+1;
    simpx_nlinks = (dim*dim+dim)/2;
    nverts = list0.size();
    nlinks = list1.size();
    nsimpx = 0;
    double unit_len = 1.0;
    
    for(int ti=0; ti<list2.size(); ++ti){
        Triangle* tri = list2[ti].dync_triangle();
        std::vector<uint> tri_verts = {static_cast<uint>(tri->v[0]->id), static_cast<uint>(tri->v[1]->id), static_cast<uint>(tri->v[2]->id)};
        std::sort(tri_verts.begin(),tri_verts.end());
        simpx_verts.push_back(tri_verts);

        for(int rvi=0; rvi<simpx_nverts-1; ++rvi){
            uint vi = tri_verts[rvi];
            for(int rvj=rvi+1; rvj<simpx_nverts; ++rvj){
                uint vj = tri_verts[rvj];
                auto vivj = make_sorted_pair(vi,vj);
                links_sqlen_map[vivj]=unit_len;
            }
        }
        nsimpx++;
    } 

    if(nlinks!=links_sqlen_map.size()){
        cout<<"nlinks="<<nlinks<<", sqlen_mapsize="<<links_sqlen_map.size()<<endl;
        cout<<"Check if there are links in list1, which are not present in map"<<endl;
        for(int li=0; li<list1.size(); ++li){
            Edge* edge = list1[li].dync_edge();
            uint v0 = static_cast<uint>(edge->v[0]->id); 
            uint v1 = static_cast<uint>(edge->v[1]->id); 
            if(v0>v1) swap(v0,v1);
            bool found=false;
            for(auto& it : links_sqlen_map){
                if(v0==(it.first.first) and v1==(it.first.second)){
                    found=true;
                    break;
                }
            }
            if(!found){
                cout<<"Not found link "<<li<<endl;
                throw std::runtime_error("ERROR: not found link in structures");
            }
        }
        cout<<"All links found, are there copies in list1?"<<endl;

        bool found=false;
        for(int li=0; li<list1.size(); ++li){
            Edge* ei = list1[li].dync_edge();
            uint eiv0=ei->v[0]->id; 
            uint eiv1=ei->v[1]->id; 
            if(eiv0==eiv1){
                cout<<"link "<<li<<" connect the vertex "<<eiv0<<" with itself"<<endl;
                found=true;
                break;
            }

            if(eiv0>eiv1) std::swap(eiv0,eiv1);

            if(ei->id!=li){
                cout<<"Index in structure "<<ei->id<<" do not coincides with index in list1 "<<li<<endl;
                found=true;
                break;
            }

            for(int lj=li+1; lj<list1.size(); ++lj){
                Edge* ej = list1[lj].dync_edge();
                uint ejv0=ej->v[0]->id; 
                uint ejv1=ej->v[1]->id; 

                if(ejv0>ejv1) std::swap(ejv0,ejv1);

                if(eiv0==ejv0 and eiv1==ejv1){
                    cout<<"links "<<li<<" and "<<lj<<" appear to have the same vertices"<<endl;
                    found=true;
                }
           } 
            if(found)
                break;
        }
        if(!found){
            cout<<"Not found copies in list1 and all references are correct"<<endl;
        }
    }
    assert(nlinks==links_sqlen_map.size());
    assert(nsimpx==simpx_verts.size());

    of.write((char*)&dim,sizeof(dim));
    of.write((char*)&nverts,sizeof(nverts));
    of.write((char*)&nlinks,sizeof(nlinks));
    of.write((char*)&nsimpx,sizeof(nsimpx));

//    if(verbose){
//        std::cout<<"dim = "<<dim<<std::endl;
//        std::cout<<"nverts = "<<nverts<<std::endl;
//        std::cout<<"nlinks = "<<nlinks<<std::endl;
//        std::cout<<"nsimpx = "<<nsimpx<<std::endl;
//        std::cout<<"simpx_nverts = "<<simpx_nverts<<std::endl;
//        std::cout<<"simpx_nlinks = "<<simpx_nlinks<<std::endl;
//    }

    for(int si = 0; si <nsimpx; ++si){
        of.write((char*)&(simpx_verts[si][0]), simpx_nverts*sizeof(uint));
//        if(verbose){
//            std::cout<<"\nsimpx_verts["<<si<<"]: ";
//            for(int i = 0; i< simpx_nverts; ++i){
//                std::cout<<simpx_verts[si][i]<<" ";
//            }
//            std::cout<<std::endl;
//        }
    }
     
}

bool Triangulation::test(){
    // checking links
    bool found=false;
    for(int li=0; li<list1.size(); ++li){
        Edge* ei = list1[li].dync_edge();
        uint eiv0=ei->v[0]->id; 
        uint eiv1=ei->v[1]->id; 
        if(eiv0==eiv1){
            cout<<"link "<<li<<" connect the vertex "<<eiv0<<" with itself"<<endl;
            found=true;
            break;
        }

        if(eiv0>eiv1) std::swap(eiv0,eiv1);

        if(ei->id!=li){
            cout<<"Index in structure "<<ei->id<<" do not coincides with index in list1 "<<li<<endl;
            found=true;
            break;
        }

        for(int lj=li+1; lj<list1.size(); ++lj){
            Edge* ej = list1[lj].dync_edge();
            uint ejv0=ej->v[0]->id; 
            uint ejv1=ej->v[1]->id; 

            if(ejv0>ejv1) std::swap(ejv0,ejv1);

            if(eiv0==ejv0 and eiv1==ejv1){
                cout<<"links "<<li<<" and "<<lj<<" appear to have the same vertices ("<<eiv0<<" and "<<eiv1<<")"<<endl;
                found=true;
            }
       } 
        if(found)
            break;
    }
    return found;

}


// ##### ADJACENCY LIST #####

#include "triangulation/adjacency.cpp"

// ##### DEBUG #####

#include "triangulation/debug.cpp"
