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

#ifndef TRIANGLE_H
#define TRIANGLE_H

#include "simplex.h"
#include "label.h"
using namespace std;

/**
 * @todo check docs
 */
class Triangle : public Simplex
{
private:
    /**
    * Default constructor
    * 
    * @usage I use this to construct an "empty Triangle", i.e. a region of spacetime "outside" the Universe (but inside the Triangulation, it acquires immediatly the id field). This will be useful for make changements in the Universe (initialize it, or make a move), but when they are created they have to be put as soon as possible inside the Universe.
    * 
    * To limit the chances of outsider simplices I make it possible only to have "empty Triangle"s, but not "empty Vertex"s, because they are not needed.
    * 
    */
    Triangle(int list_position);
    
    /**
     * 
     * The "good" constructor
     * 
     * @param vertices the three vertices of the Triangle
     * @param adjacents_t the three Triangles adjacent to this one
     */
    Triangle(int list_position, Label vertices[3], Label adjacents_t[3]);

    /**
     * Destructor
     */
    ~Triangle(){}
    
    
    // DATA
    
    /**
    * @var labels of owned Vertices
    * 
    */
    Label v[3]={};
    
    /**
    * @var labels of adjacent Triangles;
    * 
    */
    Label t[3]={};
    
    friend class Triangulation;
    
public:
    
    /**
    * @brief method interface
    * 
    * @return v[3]
    */
    Label* vertices();
    
    /**
    * @brief method interface
    * 
    * @return t[3]
    */
    Label* adjacent_triangles();
};

#endif // TRIANGLE_H
