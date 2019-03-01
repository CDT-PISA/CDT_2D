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
#include <memory>

Label::Label(Simplex* s_ptr)
{
    sh_ptr_simplex.reset(s_ptr);
}


Simplex& Label::operator*()
{
    return *sh_ptr_simplex;
}

Simplex* Label::operator->()
{
    return &*sh_ptr_simplex;
}

bool Label::operator==(Label lab)
{
    return this->sh_ptr_simplex->position() == lab.sh_ptr_simplex->position();
}

bool Label::operator!=(Label lab)
{
    return not(*this == lab);
}

/**
* @todo migliorare il cast e completare con errore (throw nel ramo else)
*/
Vertex* Label::dync_vertex()
{
    if(Vertex* v_ptr = dynamic_cast<Vertex*>(&*sh_ptr_simplex)){
        return v_ptr;
    }
    else{
        return nullptr;
    }
}

/**
* @todo migliorare il cast e completare con errore (throw nel ramo else)
*/
Triangle* Label::dync_triangle()
{
    if(Triangle* t_ptr = dynamic_cast<Triangle*>(&*sh_ptr_simplex)){
        return t_ptr;
    }
    else{
        return nullptr;
    }
}
