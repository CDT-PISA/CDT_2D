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

#ifndef SIMPLEX_H
#define SIMPLEX_H

/**
 * @todo write docs
 */
class Simplex
{
public:
    virtual ~Simplex() {}
    
    /// DATA
    
    /**
    * @brief index in list of simplices
    * 
    * TODO come lo gestisco in modo sensato?
    * 
    * il suo senso credo sia risalire al Label che lo possiede, in modo da includerlo in altre strutture (qui solo i triangoli)
    */
    int id;
    
    
    /// METHODS

    /** 
     * @param other the triangle I'm comparing with
     * @return the equality truth value of the Simplex::id of the two
     */
    bool operator== ( const Simplex& other ) const;

    /** 
     * @param other the triangle I'm comparing with
     * @return the  truth value of the Simplex::id of the two
     */
    bool operator!= ( const Simplex& other ) const;
};

#endif // SIMPLEX_H
