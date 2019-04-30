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

#include "edge.h"
#include "vertex.h"
#include "triangle.h"

Edge::Edge(const int& list_position)
{   
    id = list_position;
}

Edge::Edge(const int& list_position, const Label (&vertices)[2], const Label& triangle, const EdgeType& e_type)
{
    id = list_position;
    near_t = triangle;
    type = e_type;
    
    for(int i=0;i<2;i++){
        v[i] = vertices[i];
    }    
}

GaugeElement Edge::gauge_element(){ return U; }

Label Edge::adjacent_triangle(){ return near_t; }

Label* Edge::vertices(){ return v; }

bool Edge::is_space()
{
    if(type == EdgeType::_space)
        return true;
    else if(type == EdgeType::_time)
        return false;
    else
        throw runtime_error("EdgeType not recognized");
}

bool Edge::is_time(){ return not is_space(); }

// ##### GAUGE #####

GaugeElement Edge::force()
{
    GaugeElement Force;
    Force = 0;
    Triangle edge_t[2];
    
    edge_t[0] = *near_t.dync_triangle();
    
    // find the vertex opposite to this edge in near_t
    int i;
    for(i=0; i<3; i++){
        for(int j=0; j<2 && v[j]!=near_t.dync_triangle()->vertices()[i]; j++)
        if(j == 2)
            break;
    }
    edge_t[1] = *near_t.dync_triangle()->adjacent_triangles()[i].dync_triangle();
    
    for(auto x: v){
        Force += x.dync_vertex()->looparound();
    }
    
    return Force;
}

// ##### FILE I/O #####

void Edge::write(std::ostream& output)
{
    output.write((char*)&id, sizeof(id));
    output.write((char*)&type, sizeof(type));
    U.write(output);
    
    int pos = near_t->position();
    output.write((char*)&pos, sizeof(pos));
    
    for(auto x : v){
        int pos = x->position();
        output.write((char*)&pos, sizeof(pos));
    }
}

void Edge::read(std::istream& input, const vector<Label>& List0, const vector<Label>& List1, const vector<Label>& List2)
{
    input.read((char*)&id, sizeof(id));
    input.read((char*)&type, sizeof(type));
    U.read(input, List1);
    
    int pos = 0;
    input.read((char*)&pos, sizeof(pos));
    near_t = List2[pos];
    
    for(auto& x : v){
        int pos = 0;
        input.read((char*)&pos, sizeof(pos));
        x = List0[pos];
    }
}
