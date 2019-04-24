/** @file */
#ifndef EDGE_H
#define EDGE_H

#include "simplex.h"
#include "label.h"
#include "gaugeelement.h"
#include <memory>
#include <vector>
#include <fstream>
using namespace std;

enum class EdgeType {_time, _space };

class Edge : public Simplex
{
private:    
    
    /**
     * 
     */ 
    Edge(const int& list_position);
    
    /**
     * @todo
     */
    Edge(const int& list_position, const Label (&vertices)[2], const Label& triangle, const EdgeType& e_type);

    
    // DATA
    
    /**
    * @var labels of owned Vertices
    * 
    */
    Label v[2]={};
    
    /**
    * @var number of adjacent Triangles
    * 
    */
    GaugeElement U;
    
    /**
    * @var label of a neighbouring Triangle
    * 
    * Space Edges: the near triangle is the one below
    * Time Edges: the near triangle is the one on the left
    * 
    */
    Label near_t;
    
    EdgeType type;
    
    friend class Triangulation;
    friend class shared_ptr<Edge>;
    
public:

     /**
     * Destructor
     */
    ~Edge(){}

    
    /**
    * @brief interface method
    * 
    * @return t_slice
    */
    GaugeElement gauge_element();

    /**
    * @brief interface method
    * 
    * @return coord_num
    */
    Label* vertices();

    /**
    * @brief interface method
    * 
    * @return near_t
    */
    Label adjacent_triangle();
        
    bool is_time();
    
    bool is_space();
    
    // ##### FILE I/O #####
    
    void write(ostream& output);
    
    void read(istream& input, const vector<Label>& List0, const vector<Label>& List1, const vector<Label>& List2);

};

#endif // EDGE_H
