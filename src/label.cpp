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

#include "label.h"
#include "vertex.h"
#include "triangle.h"

Label::Label(Simplex* s) : shared_ptr<Simplex>(s){}

/**
* @todo migliorare il cast e completare con errore (ramo else)
*/
Vertex* Label::dync_vertex()
{
    if(Vertex* v_ptr = dynamic_cast<Vertex*>(&**this)){
        return v_ptr;
    }
    else{
        return nullptr;
    }
}

/**
* @todo migliorare il cast e completare con errore (ramo else)
*/
Triangle* Label::dync_triangle()
{
    if(Triangle* t_ptr = dynamic_cast<Triangle*>(&**this)){
        return t_ptr;
    }
    else{
        return nullptr;
    }
}
