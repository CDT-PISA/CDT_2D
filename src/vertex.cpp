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

#include <complex>
#include "vertex.h"
#include "edge.h"
#include "triangle.h"
#include "triangulation.h"
#include "gaugeelement.h"

Vertex::Vertex()
{   
    id = -1;
}

Vertex::Vertex(int list_position)
{   
    id = list_position;
}

Vertex::Vertex(int list_position, int Time, int coordination_number, Label triangle)
{   
    id = list_position;
    t_slice = Time;
    coord_num = coordination_number;
    near_t = triangle;
}

int Vertex::time(){ return t_slice; }

int Vertex::coordination(){ return coord_num; }

Label Vertex::adjacent_triangle(){ return near_t; }
    
// ##### GAUGE #####

bool Vertex::orientation_convention(const Triangle& pointed, int from)
{
    return from == 1 || (from == 2 && pointed.is21());
}

Triangle* Vertex::next(Triangle* current, int& previous_idx, bool debug_flag){
    if(debug_flag){
        cout << "vertex: " << this->position() << endl;
        cout << "previous_idx: " << previous_idx << endl;
        cout << "current: " << current->position() << endl;
    }

    int bond_idx = current->find_element(owner->list0[this->position()], SimplexType::_vertex);
    
    if(debug_flag)
        cout << "bond: " << bond_idx << endl;
    
    int next_idx = 0;
    while(next_idx == bond_idx or next_idx == previous_idx)
        next_idx++; 
    

    if(debug_flag)
        cout << "next: " << next_idx << endl;
    
    Triangle *next = current->adjacent_triangles()[next_idx].dync_triangle();
    
//    previous_idx = 0;
//    while(next->adjacent_triangles()[previous_idx].dync_triangle()!=current) 
//        previous_idx++; 
    previous_idx = (4 - next_idx) % 3; // is the `opposite` function: 1 <--> 0, 2 <--> 2
    
    if(debug_flag){
        next->print_elements();
    }
    
    return next;
}

GaugeElement Vertex::looparound(bool debug_flag)
{
    vector<int> v;
    v.push_back(-1);
    
    return looparound(v, debug_flag);
}

GaugeElement Vertex::looparound(vector<int>& triangle_list, bool debug_flag)
{   
    /**
     * @image html RotLoop.png "Loop orientations" width=500cm
     */ 
    if(debug_flag){
        cout << endl << endl;
        cout << "+---------------------+" << endl;
        cout << "|PLAQUETTE CALCULATION|" << endl;
        cout << "+---------------------+" << endl;
        cout << "bond: " << this->position() << endl;
        cout << endl;
    }
    
    int initial_size = triangle_list.size();
    if(initial_size > 1)
        throw runtime_error("looparound: triangle_list is supposed to be an empty vector");
    
    GaugeElement Plaquette;
    Vertex bond = *this;
    Triangle *start = bond.near_t.dync_triangle();
    
    if(debug_flag)
        cout << "start: " << start->position() << endl;
    
    int previous_idx;
    
    Label lab_bond = owner->list0[bond.position()];
    int bond_idx = start->find_element(lab_bond, SimplexType::_vertex);
    
    // the purpose of the followng `shift` is to guarantee that plaquettes are
    // traversed counter-clockwise (is needed for topological charge computation)
    int shift;
    if(start->is21())
        shift = 2;
    else
        shift = 1;
    previous_idx = (bond_idx + shift) % 3;
    
    Triangle *previous = start->adjacent_triangles()[previous_idx].dync_triangle();
    /*
    if(*(start.vertices()[0].dync_vertex()) == bond){
        // if 0 is `bond` 1, 2 are triangles adjacent to `start` and `bond`
        previous = *(start.adjacent_triangles()[1].dync_triangle());
        previous_idx = 1;
    }
    else{
        // if 0 is not `bond` 0 is a triangle adjacent to `start` and `bond`
        // because triangle 0 is opposite to vertex 0
        // so both vertex 1 and 2 are adjacents to triangle 0
        previous = *(start.adjacent_triangles()[0].dync_triangle());
        previous_idx = 0;
    }
    */
    
    Triangle* current = start;
    bool first_round = true;
    while(*current != *start || first_round){
        first_round = false;
        
        if(debug_flag){
            cout << "\t previous: " << current->t[previous_idx]->id;
            cout << " current: " << current->position() << endl;
        }
        
        if(initial_size == 0)
            triangle_list.push_back(current->id);
        
        GaugeElement current_previous = current->edges()[previous_idx].dync_edge()->gauge_element();
        
        // ORIENTAZIONE
        ///@todo
        if(orientation_convention(*current, previous_idx))
            current_previous = current_previous.dagger();
        
        //check unitarity
#if NC == 2
	if(abs(current_previous.det() - 1.) > 1e-8){
	    throw runtime_error("looparound plaquette: link is not special unitary:\n\tdet link -1  = (" + to_string(real(current_previous.det()) - 1.) + ", " + to_string(imag(current_previous.det())) + ")\n\t|link| - 1 = " + to_string(abs(current_previous.det()) - 1));
	}
#endif
        
        Plaquette *= current_previous.dagger();
        // to be multiplied correctly the element has to be taken in the direction of travel
        // I took the inverse, therefore I add the dagger
        
        if(debug_flag){
//             cout << current_previous << endl;
        }
        
        previous = current;
        current = next(current, previous_idx);
    }

    if(debug_flag){
        cout << Plaquette << endl;
        cout << "END PLAQUETTE CALCULATION" << endl << endl;
    }
 
    //check unitarity
#if NC == 2    
    if(abs(Plaquette.det() - 1.) > 1e-8){
        throw runtime_error("looparound: plaquette is not unitary:\n\tdet plaq - 1 = (" + to_string(real(Plaquette.det()) - 1) + ", " + to_string(imag(Plaquette.det())) + ")\n\t|plaq| - 1 = " + to_string(abs(Plaquette.det()) - 1));
    }
#endif
    
    return Plaquette;
}

GaugeElement Vertex::looparound(Triangle* edge_t[2], bool debug_flag)
{
    if(debug_flag){
        cout << endl << endl;
        cout << "+------------------+" << endl;
        cout << "|STAPLE CALCULATION|" << endl;
        cout << "+------------------+" << endl;
        cout << "bond: " << this->position() << endl;
        cout << endl;
    }
    
    // initialize base_edge to a random edge in order not to have 
    // GaugeElements with missing base_edges
    // (so that each GaugeElement has a reference to the structure
    // that owns it)
    GaugeElement Staple(this->owner->list1[0]);
    Vertex bond = *this;
    Triangle* start = edge_t[1];
    Triangle* previous = edge_t[0];
    int previous_idx = start->find_element(owner->list2[previous->position()], SimplexType::_triangle, debug_flag);
    
    if(not orientation_convention(*start, previous_idx)){
        Triangle* aux = start;
        start = previous;
        previous = aux;
        previous_idx = (4 - previous_idx) % 3; // is the `opposite` function: 1 <--> 0, 2 <--> 2
    }                        
    
    if(debug_flag){
        cout << "---------------" << endl;
        cout << "start: " << start->position() << endl;
        start->print_elements();
    }
    
    if(debug_flag){
        cout << "previous: " << previous_idx << endl;
        previous->print_elements();
        cout << "---------------" << endl;
    }


    Triangle *current = next(start,previous_idx);
    while(current != start){
        
        if(debug_flag){
            cout << "\t previous: " << current->t[previous_idx]->id;
            cout << " current: " << current->position() << endl;
//             owner->list2[current->position()].dync_triangle()->print_elements();
        }
        
//        if(*current != *start){
        GaugeElement current_previous = current->edges()[previous_idx].dync_edge()->gauge_element();
        
        // ORIENTAZIONE
        ///@todo
        if(orientation_convention(*current, previous_idx))
            current_previous = current_previous.dagger();
        
        //check unitarity
#if NC == 2
	if(abs(current_previous.det() - 1.0) > 1e-8){
	    throw runtime_error("looparound: link is not special unitary:\n\t det link - 1 = (" + to_string(real(current_previous.det()) - 1.0) + " ," + to_string(imag(current_previous.det())) + ")\n\t|link| = " + to_string(abs(current_previous.det()) - 1));
	}
#endif

        Staple *= current_previous.dagger();
            // to be multiplied correctly the element has to be taken in the direction of travel
            // I took the inverse, therefore I add the dagger
//        }
        
        current = next(current, previous_idx);
        
        if(debug_flag){
//             cout << current_previous << endl;
        }
    }
 
    //check unitarity
#if NC == 2
    if(abs(abs(Staple.det()) - 1) > 1e-8){
        throw runtime_error("looparound: staple is not special unitary:\n\t det Staple - 1 = (" + to_string(real(Staple.det()) - 1.0) + " ," + to_string(imag(Staple.det())) + ")\n\t|staple| = " + to_string(abs(Staple.det()) - 1));
    }
#endif
    
    if(debug_flag){
        cout << Staple << endl;
        cout << "END STAPLE CALCULATION" << endl << endl;
    }
    
    return Staple;
}

double Vertex::ReTr_plaquette(bool debug_flag)
{
    GaugeElement Plaquette = this->looparound(debug_flag);
    return real(Plaquette.tr());
}

double Vertex::Pi_tilde(bool debug_flag)
{
    GaugeElement Plaquette = this->looparound(debug_flag);
    return real(Plaquette.tr()) / Plaquette.N - 1;
}

double Vertex::gauge_action_contrib(bool debug_flag)
{
    return Pi_tilde(debug_flag) / coord_num;
}

constexpr double pi() { return atan(1)*4; }

double Vertex::topological_charge_density(bool debug_flag)
{
    GaugeElement Plaquette = this->looparound(debug_flag);
    return arg(Plaquette.tr()) / (2 * pi());
}

vector<double> Vertex::gauge_action_top_charge_densities(bool debug_flag)
{
    vector<int> v;
    v.push_back(-1);
    
    return gauge_action_top_charge_densities(v, debug_flag);
}

vector<double> Vertex::gauge_action_top_charge_densities(vector<int>& triangle_list, bool debug_flag)
{
    GaugeElement Plaquette = this->looparound(triangle_list, debug_flag);
    double gauge_action_density;
    double charge_density;
    
    gauge_action_density = ( real(Plaquette.tr()) / Plaquette.N - 1 ) / coord_num;
    charge_density = arg(Plaquette.tr()) / (2 * pi());
    
    vector<double> v;
    v.push_back(gauge_action_density);
    v.push_back(charge_density);
    
    return v;
}

// ##### FILE I/O #####

void Vertex::write(ostream& output)
{
    output.write((char*)&id, sizeof(id));
    output.write((char*)&t_slice, sizeof(t_slice));
    output.write((char*)&coord_num, sizeof(coord_num));
    
    int pos = near_t->position();
    output.write((char*)&pos, sizeof(pos));
}

void Vertex::read(istream& input, const vector<Label>& List2)
{
    input.read((char*)&id, sizeof(id));
    input.read((char*)&t_slice, sizeof(t_slice));
    input.read((char*)&coord_num, sizeof(coord_num));
    
    int pos = 0;
    input.read((char*)&pos, sizeof(pos));
    near_t = List2[pos];
}

// ##### DEBUG FACILITIES #####
    
void Vertex::print_elements(std::ostream& os)
{
    os << endl << "v[" << position() << "]:     (time: " << t_slice << ")" << endl;
    
    os << "near_t: " << near_t.dync_triangle()->position() << endl;
    os << "coord_num: " << coord_num << endl;
}
