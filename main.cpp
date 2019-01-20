/** @file */
#include <iostream>
#include "triangulation.h"
#include "vertex.h"
#include "triangle.h"
#include <memory>

using namespace std;

int main() {
    Triangulation universe(2);
    
    for(int i=0;i<20;i++)
        cout << universe.create_triangle() << endl;
    universe.create_vertex(0,6,universe.list2[0]);
    
    cout << universe.list2.size() << endl;
    cout << universe.list2[14]->position() << endl;
//     cout << "triangolo adiacente al vertice[0]:" << ((dynamic_cast<Vertex*>(universe.list0[0]))->adjacent_triangle()).position();
    
    cout << universe.list0[0].dync_vertex()->adjacent_triangle().dync_triangle()->position();
}
