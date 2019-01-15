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

/**
 * @todo write docs
 */
class Triangle
{
public:
    /**
     * Default constructor
     */
    Triangle();

    /**
     * Copy constructor
     *
     * @param other TODO
     */
    Triangle ( const Triangle& other );

    /**
     * Destructor
     */
    ~Triangle();

    /**
     * Assignment operator
     *
     * @param other TODO
     * @return TODO
     */
    Triangle& operator= ( const Triangle& other );

    /**
     * @todo write docs
     *
     * @param other TODO
     * @return TODO
     */
    bool operator== ( const Triangle& other ) const;

    /**
     * @todo write docs
     *
     * @param other TODO
     * @return TODO
     */
    bool operator!= ( const Triangle& other ) const;

    /**
    * @brief index in list2
    * 
    */
    int id;
    
    /**
    * @brief labels of owned Vertices
    * 
    */
    Label v[3];
    
    /**
    * @brief labels of adjacent Triangles;
    * 
    */
    Label t[3];
    
};

#endif // TRIANGLE_H
