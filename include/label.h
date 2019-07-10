/** @file */
#ifndef LABEL_H
#define LABEL_H

#include <memory>

#include "simplex.h"
using namespace std;

class Vertex;
class Edge;
class Triangle;

class Label{
private:
    shared_ptr<Simplex> sh_ptr_simplex;
public:
    // Constructors
    Label(): sh_ptr_simplex(nullptr) {}
    Label(Simplex*);
    
    /*
    // Copy & Move
    Label(const Label&);
    Label(Label&&);
    Label& operator=(const Label&);
    Label& operator=(Label&&);
    */
    
    ~Label(){}
    
    // Operators
    Simplex& operator*();
    Simplex* operator->();
    
    bool operator==(Label);
    bool operator!=(Label);
    
    // Recast
    Vertex* dync_vertex();
    Edge* dync_edge();
    Triangle* dync_triangle();
    
};

#endif // LABEL_H
