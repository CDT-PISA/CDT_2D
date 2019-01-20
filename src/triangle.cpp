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

#include "triangle.h"

Triangle::Triangle(int list_position)
{
    id = list_position;
}

Triangle::Triangle(int list_position, Label vertices[3], Label adjacents_t[3])
{
    id = list_position;
    
    for(int i=0;i<3;i++){
        v[i] = vertices[i];
        t[i] = adjacents_t[i];
    }
    
}


/**
* @todo in questi metodi (Triangle::vertices Triangle::adjacent_triangles) devo inserire un controllo degli errori più stringente:\n
* gli "empty triangle" possiedono solo liste vuote, per cui se provo a fare l'accesso a quelle devo comunicare che c'è un errore, perché il triangolo è in costruzione (o faccio fallire l'esecuzione, o come minimo stampo un log)
*/
Label* Triangle::vertices(){ return v; }

Label * Triangle::adjacent_triangles(){ return t; }


