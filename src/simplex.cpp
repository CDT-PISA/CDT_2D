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

#include "simplex.h"
#include "label.h"

bool Simplex::operator==(const Simplex& other) const
{
    return id == other.id;
}

bool Simplex::operator!= ( const Simplex& other ) const
{
    return not (*this == other);
}

int Simplex::position()
{
    return id;
}

Triangulation* Simplex::get_owner()
{
    return owner;
}

ostream& operator<<(ostream& os, Simplex& s){
    s.print_elements(os);
    
    return os;
}
