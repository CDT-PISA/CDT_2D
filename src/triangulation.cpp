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

#include "triangulation.h"
#include <memory>
/**
 * @todo Is a good practice to reinclude in the .cpp the header already included in the corresponding .h?
 */
#include "vertex.h"
#include "triangle.h"


Triangulation::Triangulation(int TimeLength)
{
    num40 = TimeLength;
    
    for(int i=0;i<TimeLength;i++){
        for(int t=0;t<3;t++){
//             Vertex v(i,);
            num40++;
//             list0.push_back(v);
        }
    }

}

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

int Triangulation::create_triangle(Label vertices[3], Label adjacents_t[3])
{
    int list_position=list2.size();
    Label lab(new Triangle(list_position,vertices,adjacents_t));
    
    list2.push_back(lab);
    
    return list_position;
    
}



