/** @file */
#ifndef TRIANGLE_H
#define TRIANGLE_H

#include "simplex.h"
#include "label.h"
#include <iostream>
#include <fstream>
#include <stdexcept>
#include <vector>
#include <algorithm>
using namespace std;

class Vertex;
class Edge;
class GaugeElement;

enum class TriangleType {_12, _21 };

/**
 * @todo check docs
 */
class Triangle : public Simplex
{
private:
    /**
    * Auxiliary Triangle: not in list2
    * 
    */
    Triangle();
    
    /**
    * Default constructor
    * 
    * @usage I use this to construct an "empty Triangle", i.e. a region of spacetime "outside" the Universe (but inside the Triangulation, it acquires immediatly the id field). This will be useful for make changements in the Universe (initialize it, or make a move), but when they are created they have to be put as soon as possible inside the Universe.
    * 
    * To limit the chances of outsider simplices I make it possible only to have "empty Triangle"s, but not "empty Vertex"s, because they are not needed.
    * 
    */
    Triangle(const int& list_position);
    
    /**
     * 
     * The "good" constructor
     * 
     * @param vertices the three vertices of the Triangle
     * @param adjacents_t the three Triangles adjacent to this one
     */
    Triangle(const int &list_position, const Label (&vertices)[3], const Label (&edges)[3], const Label (&adjacents_t)[3], const TriangleType& t_type);
    
    // DATA
    
    /**
    * @var labels of owned Vertices
    * 
    */
    Label v[3]={};
        
    /**
    * @var labels of adjacent Edges;
    * 
    */
    Label e[3]={};
    
    /**
    * @var labels of adjacent Triangles;
    * 
    */
    Label t[3]={};
    
    int transition_id = -1;
    
    TriangleType type;
    
    friend class Triangulation;
    friend class Vertex;
    friend class Edge;
    
public:
    
    /**
     * Destructor
     */
    ~Triangle(){}
    
    /**
    * @brief method interface
    * 
    * @return v[3]
    */
    Label* vertices();
    
    /**
    * @brief method interface
    * 
    * @return e[3]
    */
    Label* edges();
    
    /**
    * @brief method interface
    * 
    * @return t[3]
    */
    Label* adjacent_triangles();
    
    bool is12();
    
    bool is21();
    
    bool is_transition();
    
    int find_element(Label lab_Element, SimplexType type, bool debug_flag = false);
    
    int opposite(int i);
    
    // ##### GAUGE #####
    
    void gauge_transform(GaugeElement G);
    
    // ##### FILE I/O #####
    
    void write(ostream& output);
    
    void read(istream& input, const vector<Label>& List0, const vector<Label>& List1, const vector<Label>& List2);
    
    // ##### DEBUG FACILITIES #####
    
    void print_elements(ostream& os=cout);
    void print_elements(bool trans, ostream& os=cout);
};

#endif // TRIANGLE_H
