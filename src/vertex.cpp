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

Triangle Vertex::next(Triangle current, int& previous_idx){
    Triangle next;
    
    int bond_idx = current.find_element(owner->list0[this->position()], SimplexType::_vertex);
    
    int next_idx = 0;
    // I'd want to consider previous_idx == 0
    // to do this I translate to that reference frame 
    // to interpret the result I translate back in the original frame
    if((bond_idx - previous_idx) % 3 == 1)
        next_idx = (2 + previous_idx) % 3;
    else if((bond_idx - previous_idx) % 3 == 2)
        next_idx = (1 + previous_idx) % 3;
    
    next = *current.adjacent_triangles()[next_idx].dync_triangle();
    previous_idx = (4 - next_idx) % 3; // is the `opposite` function: 1 <--> 0, 2 <--> 2
    
    return next;
}

GaugeElement Vertex::looparound()
{
    GaugeElement Plaquette;
    Vertex bond = *this;
    Triangle start = *(bond.near_t.dync_triangle());
    
    Triangle previous;
    int previous_idx;
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
    
    Triangle current = start;
    bool first_round = true;
    while(current != start || first_round){
        first_round = false;
        
        GaugeElement current_previous = current.edges()[previous_idx].dync_edge()->gauge_element();
        Plaquette *= current_previous.dagger();
        // to be multiplied correctly the element has to be taken in the direction of travel
        // I took the inverse, therefore I add the dagger
        
        previous = current;
        current = next(current, previous_idx);
    }
    
    return Plaquette;
}

GaugeElement Vertex::looparound(Triangle edge_t[2])
{
    GaugeElement Staple;
    Vertex bond = *this;
    Triangle start = edge_t[1];
    
    Triangle previous = edge_t[0];
    int previous_idx = start.find_element(owner->list2[previous.position()], SimplexType::_triangle);
    
    Triangle current = start;
    bool first_round = true;
    while(current != start || first_round){
        first_round = false;
        
        if(current != start){
            GaugeElement current_previous = current.edges()[previous_idx].dync_edge()->gauge_element();
            Staple *= current_previous.dagger();
            // to be multiplied correctly the element has to be taken in the direction of travel
            // I took the inverse, therefore I add the dagger
        }
        
        previous = current;
        current = next(current, previous_idx);
    }
    
    return Staple;
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
