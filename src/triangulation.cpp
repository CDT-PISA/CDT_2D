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
#include <stdexcept>
/**
 * @todo Is a good practice to reinclude in the .cpp the header already included in the corresponding .h?
 */
#include "vertex.h"
#include "triangle.h"

using namespace std;

Triangulation::Triangulation(int TimeLength)
{
    if(TimeLength < 1)
        throw out_of_range("only positive time length are excepted for a triangulation");
    
    num40 = 0;
    num40p = 0;
    list0.clear();
    list2.clear();
    spatial_profile.clear();
    transition1221.clear();
    transition2112.clear();
    
    // FIRST STRIP
        
    for(int j=0;j<6;j++){   // initialize the 6 triangles in the first(zeroth) strip
        Label lab(new Triangle(list2.size())); // list2.size() has to be equal to j
        list2.push_back(lab);
    }
    
    for(int j=0;j<3;j++){   // initialize the 3 vertices at time 1
        Label lab(new Vertex(list0.size(),1,6,list2[j]));    // list2.size() has to be equal to j
        list0.push_back(lab);
        list2[j].dync_triangle()->vertices()[2] = lab;
        
        int tri_id1 = j + 3;
        int tri_id2 = (j + 1)%3 + 3;
        list2[tri_id1].dync_triangle()->vertices()[1] = lab; /** @todo allegare disegni */
        list2[tri_id2].dync_triangle()->vertices()[0] = lab;
    }
    
    /* at the end of these first steps the only things missed are:\n
     * - related to the vertices at time 0, that will be initialize in the next section (Triangle::vertices)
     * - or the adjacency relations among triangles, that will be fixed in the final section (Triangle::adjacents_t)
     */ 
    
    // INTERMEDIATE STRIPS
    
    for(int i=1;i<TimeLength;i++){
        spatial_profile.push_back(3);
        
        // STRIP TRIANGLES
        
        for(int j=0;j<6;j++){ // initialize the 6 triangles in the ith strip
            Label lab(new Triangle(list2.size())); // list2.size() has to be equal to (6*i + j)
            list2.push_back(lab);
        }
        
        // VERTICES
            
        for(int j=0;j<3;j++){
            // Initialize the 3 vertices at time i+1
            
            int time = (i+1) % TimeLength;
            Label lab(new Vertex(list0.size(),time,6,list2[6*i+j]));    // list0.size() has to be equal to (3*i + j)
            list0.push_back(lab);
            
            // Now complete the vertices of the corresponding (2,1)-triangle
            
            Triangle* tri_lab0 = list2[j + 6*i].dync_triangle();
            tri_lab0->vertices()[2] = lab;    // attach the current vertex to the triangle below it
            /* the vertices at time i (ones below the strip) are [3*(i-1),3*i) so for the triangle = 0 (mod 6) in the strip above:
             * - the down-left corner is the vertex = 2 (mod 3);
             * - the down-right corner is the vertex = 0 (mod 3)
             *
             * and so on for the other (2,1)-triangles in the strip
             */
            tri_lab0->vertices()[0] = list0[3*(i - 1) + j];   // attach the remaining two vertices
            tri_lab0->vertices()[1] = list0[3*(i - 1) + (j + 2)%3];
             
            
            // And now add the current vertex to the adjacent (1,2)-triangles in the strip
            
            Triangle* tri_lab1 = list2[j + 3 + 6*i].dync_triangle(); /** @todo allegare disegni */
            Triangle* tri_lab2 = list2[(j + 1)%3 + 3 + 6*i].dync_triangle();
            tri_lab1->vertices()[1] = lab;
            tri_lab2->vertices()[0] = lab;
            
            // Finally attach to the (1,2)-triangles vertices at the time i (the lower boundary of the strip")
            tri_lab2->vertices()[2] = list0[3*(i - 1) + j];
        }
        
        // TRIANGLE ADJACENCIES
        for(int j=0;j<3;j++){ /** @todo allegare disegni */
            Triangle* tri_labp = list2[j - 3 + 6*i].dync_triangle();    // triangle (1,2) in the previous strip
            Triangle* tri_lab0 = list2[j + 6*i].dync_triangle();    // triangle (2,1)
            Triangle* tri_lab3 = list2[j + 3 + 6*i].dync_triangle();    // triangle (1,2)
            
            tri_lab0->adjacent_triangles()[0] = list2[(j + 1)%3 + 3 + 6*i];
            tri_lab0->adjacent_triangles()[1] = list2[j + 3 + 6*i];
            tri_lab0->adjacent_triangles()[2] = list2[j - 3 + 6*i];
            
            tri_lab3->adjacent_triangles()[0] = list2[j + 6*i];
            tri_lab3->adjacent_triangles()[1] = list2[(j + 2)%3 + 6*i];
            
            tri_labp->adjacent_triangles()[2] = list2[j + 6*i];
        }
    }
    
    // FINAL STEPS
    
    // Still have to fix the adjacencies in the first(zeroth) strip...
    for(int j=0;j<3;j++){ /** @todo allegare disegni */
        Triangle* tri_labp = list2[j - 3 + 6*TimeLength].dync_triangle();   // triangle (1,2) in the previous strip
        Triangle* tri_lab0 = list2[j].dync_triangle();    // triangle (2,1)
        Triangle* tri_lab3 = list2[j + 3].dync_triangle();    // triangle (1,2)
        
        tri_lab0->adjacent_triangles()[0] = list2[(j + 1)%3 + 3];
        tri_lab0->adjacent_triangles()[1] = list2[j + 3];
        tri_lab0->adjacent_triangles()[2] = list2[j - 3 + 6*TimeLength];
        
        tri_lab3->adjacent_triangles()[0] = list2[j];
        tri_lab3->adjacent_triangles()[1] = list2[(j + 2)%3];
        
        tri_labp->adjacent_triangles()[2] = list2[j];
    }
    
    // ... and vertices of (2,1)-triangles (ones at time 0)
    for(int j=0;j<3;j++){
        Triangle* tri_lab = list2[j].dync_triangle();
        
        tri_lab->vertices()[0] = list0[TimeLength - 3 + (j + 2)%3];
        tri_lab->vertices()[1] = list0[TimeLength - 3 + j];
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
