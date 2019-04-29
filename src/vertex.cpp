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
#include "gaugeelement.h"

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

GaugeElement Vertex::looparound(Vertex edge_v[2])
{
    GaugeElement Loop;
    
    ///@todo
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
