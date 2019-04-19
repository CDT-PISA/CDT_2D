/** @file */
#ifndef EDGE_H
#define EDGE_H

#include "simplex.h"
#include "label.h"
#include <memory>
#include <vector>
#include <fstream>
using namespace std;

enum class TriangleType {_time, _space };

class Edge : public Simplex
{
private:    
    
    /**
     * 
     */ 
    Edge(int list_position);
    
    /**
     * @todo
     */
    Edge(int list_position, int Time, Label triangle);


    
    // DATA
    
    /**
    * @var time label of the slice
    * 
    */
    int t_slice;
    
    /**
    * @var number of adjacent Triangles
    * 
    */
    GaugeField U;
    
    /**
    * @var label of a neighbouring Triangle
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
    int time();

    /**
    * @brief interface method
    * 
    * @return coord_num
    */
    int coordination();

    /**
    * @brief interface method
    * 
    * @return near_t
    */
    Label adjacent_triangle();
    
    // ##### FILE I/O #####
    
    void write(ostream& output);
    
    void read(istream& input, const vector<Label>& List2);

};

#endif // EDGE_H
