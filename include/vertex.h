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

#ifndef VERTEX_H
#define VERTEX_H

#include "simplex.h"
#include "label.h"
#include "triangulation.h"
#include <memory>
using namespace std;

/**
 * @todo check docs
 * @todo how to link in Doxygen class data members? e.g. how to link t_slice in time() description?
 */
class Vertex : public Simplex
{
private:    
    /**
     * @brief Constructor
     * 
     * @param list_position the Simplex::id, that is the position in Triangulation::list0
     * @param Time the time slice to which the Vertex belongs
     * @param coordination_number the number of adjacent triangles
     * @param triangle the label of an adjacent triangle
     */
    Vertex(int list_position, int Time, int coordination_number, Label triangle);


    
    // DATA
    
    /**
    * @var time label of the slice
    * 
    */
    int t_slice;
    
    /**
    * @var number of adjacent Triangles
    * 
    */
    int coord_num;
    
    /**
    * @var label of a neighbouring Triangle
    * 
    */
    Label near_t;
    
    /** 
    * @todo Appena scopro a che serve lo aggiungo
    * int r; 
    */
    
    friend class Triangulation;
    friend class shared_ptr<Vertex>;
    
public:

     /**
     * Destructor
     */
    ~Vertex(){}

    
    /**
    * @brief interface method
    * 
    * @return t_slice
    */
    int time();

    /**
    * @brief interface method
    * 
    * @return coord_num
    */
    int coordination();

    /**
    * @brief interface method
    * 
    * @return near_t
    */
    Label adjacent_triangle();

};

#endif // VERTEX_H
