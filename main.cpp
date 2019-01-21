/** @file */
#include <iostream>
#include "triangulation.h"
#include "vertex.h"
#include "triangle.h"
#include <memory>

using namespace std;

int main() {
    Triangulation universe(10);
    
    Triangle* tri_lab = universe.list2[9].dync_triangle();
    /** @bug problemi con i vertici, le adiacenze sembrano perfette */
    
    cout << "(adjacent triangles) 0:" << tri_lab->adjacent_triangles()[0].dync_triangle()->position() << ", 1:" << tri_lab->adjacent_triangles()[1].dync_triangle()->position() << ", 2:" << tri_lab->adjacent_triangles()[2].dync_triangle()->position() << endl;
    cout << "(vertices) 0:" << tri_lab ->vertices()[0].dync_vertex()->position() << ", 1:" << tri_lab ->vertices()[1].dync_vertex()->position() << ", 2:" << tri_lab ->vertices()[2].dync_vertex()->position() << endl;
    cout << universe.list2.size();
}
