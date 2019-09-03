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
#include "vertex.h"
#include "edge.h"
#include "gaugeelement.h"
#include <iostream>

using namespace std;

Triangle::Triangle()
{
    id = -1;
}

Triangle::Triangle(const int& list_position)
{
    id = list_position;
}

Triangle::Triangle(const int& list_position, const Label (&vertices)[3], const Label (&edges)[3], const Label (&adjacents_t)[3], const TriangleType& t_type)
{
    id = list_position;
    type = t_type;
    
    for(int i=0;i<3;i++){
        v[i] = vertices[i];
        e[i] = edges[i];
        t[i] = adjacents_t[i];
    }    
}

bool Triangle::is12() const
{
    if(type == TriangleType::_12)
        return true;
    else if(type == TriangleType::_21)
        return false;
    else
        throw runtime_error("TriangleType not recognized");
}

bool Triangle::is21() const
{
    return not is12();
}

bool Triangle::is_transition()
{
    if(transition_id == -1)
        return false;
    else
        return true;
}

int Triangle::slab_index()
{
    if(is12())
        return v[2].dync_vertex()->time();
    else
        return v[0].dync_vertex()->time();
}

/**
* @todo in questi metodi (Triangle::vertices Triangle::adjacent_triangles) devo inserire un controllo degli errori più stringente:\n
* gli "empty triangle" possiedono solo liste vuote, per cui se provo a fare l'accesso a quelle devo comunicare che c'è un errore, perché il triangolo è in costruzione (o faccio fallire l'esecuzione, o come minimo stampo un log)
*/
Label* Triangle::vertices(){ return v; }

Label* Triangle::edges(){ return e; }

Label* Triangle::adjacent_triangles(){ return t; }

int Triangle::find_element(Label lab_Element, SimplexType type, bool debug_flag)
{
    int pos;
    int lab_id = lab_Element->id;
    if(type == SimplexType::_vertex){
//        pos = distance(v,find(v,v+3,lab_Element));
        for(pos=0; pos<3; ++pos){
            if(lab_id==v[pos]->id)
                break;
        }
    }else if(type == SimplexType::_edge){
//        pos = distance(e,find(e,e+3,lab_Element));
        for(pos=0; pos<3; ++pos){
            if(lab_id==e[pos]->id)
                break;
        }
    }else if(type == SimplexType::_triangle){
//        pos = distance(t,find(t,t+3,lab_Element));
        for(pos=0; pos<3; ++pos){
            if(lab_id==t[pos]->id)
                break;
        }
    }else{
        throw runtime_error("SimplexType not recognized");
    }
        
    if(pos == 3)
        throw runtime_error("Element not found in triangle " + to_string(this->id));
    
    return pos;
}

int Triangle::opposite(int i){
    // is the `opposite` function: 1 <--> 0, 2 <--> 2
    
    return (4 - i) % 3;
}

// ##### GAUGE #####

void Triangle::gauge_transform(GaugeElement G, bool debug_flag)
{    
    if(debug_flag){
        cout << "╔═══════════════════════╗" << endl;
        cout << "║    GAUGE TRANSFORM    ║" << endl;
        cout << "╚═══════════════════════╝" << endl;
        cout << G << endl;
    }
    
    e[0].dync_edge()->U *= G.dagger();
    e[1].dync_edge()->U *= G;
    if(this->is12())
        e[2].dync_edge()->U *= G;
    else
        e[2].dync_edge()->U *= G.dagger();
    
    for(auto &e_lab : e)
        e_lab.dync_edge()->U.unitarize();
}

// ##### FILE I/O #####

void Triangle::write(ostream& output)
{
    output.write((char*)&id, sizeof(id));
    output.write((char*)&transition_id, sizeof(transition_id));
    output.write((char*)&type, sizeof(type));
    
    for(auto x : v){
        int pos = x->position();
        output.write((char*)&pos, sizeof(pos));
    }    
    for(auto x : e){
        int pos = x->position();
        output.write((char*)&pos, sizeof(pos));
    }
    for(auto x : t){
        int pos = x->position();
        output.write((char*)&pos, sizeof(pos));
    }
}

void Triangle::read(istream& input, const vector<Label>& List0, const vector<Label>& List1, const vector<Label>& List2)
{
    input.read((char*)&id, sizeof(id));
    input.read((char*)&transition_id, sizeof(transition_id));
    input.read((char*)&type, sizeof(type));
    
    
    for(auto& x : v){
        int pos = 0;
        input.read((char*)&pos, sizeof(pos));
        x = List0[pos];
    }
    for(auto& x : e){
        int pos = 0;
        input.read((char*)&pos, sizeof(pos));
        x = List1[pos];
    }
    for(auto& x : t){
        int pos = 0;
        input.read((char*)&pos, sizeof(pos));
        x = List2[pos];
    }   
}

// ##### DEBUG FACILITIES #####

void Triangle::print_elements(std::ostream& os)
{
    print_elements(false, os);
}

void Triangle::print_elements(bool trans, ostream& os)
{
    os << endl << "t[" << this->position() << "]:   (type";
    if(this->is12())
        os << "12)";
    else
        os << "21)";
    os << endl << "v: ";
    for(int j=0; j<3; j++)
        os << this->v[j]->position() << " ";
    os << endl << "e: ";
    for(int j=0; j<3; j++)
        os << this->e[j]->position() << " ";
    os << endl << "t: ";
    for(int j=0; j<3; j++)
        os << this->t[j]->position() << " ";
    if(trans)
        os << endl << "transition_id: " << transition_id;
    os << endl;
}
