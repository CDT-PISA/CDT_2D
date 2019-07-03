/** @file */
#ifndef VERTEX_H
#define VERTEX_H

#include "simplex.h"
#include "label.h"
#include <iostream>
#include <memory>
#include <vector>
#include <fstream>
using namespace std;

class GaugeElement;
class Edge;

/**
 * @todo check docs
 * @todo how to link in Doxygen class data members? e.g. how to link t_slice in time() description?
 */
class Vertex : public Simplex
{
public:    
    
    /**
     * Auxiliary Vertex
     * 
     */ 
    Vertex();
    
    /**
     * 
     */ 
    Vertex(int list_position);
    
    /**
     * @brief Constructor
     * 
     * @param list_position the Simplex::id, that is the position in Triangulation::list0
     * @param Time the time slice to which the Vertex belongs
     * @param coordination_number the number of adjacent triangles
     * @param triangle the label of an adjacent triangle
     */
    Vertex(int list_position, int Time, int coordination_number, Label triangle);

    
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
    int coord_num;
    
    /**
    * @var label of a neighbouring Triangle
    * 
    */
    Label near_t;
    
    friend class Triangulation;
    friend class Edge;
    friend class shared_ptr<Vertex>;
    
public:

     /**
     * Destructor
     */
    ~Vertex(){}

    
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
    
    // ##### GAUGE #####
    
    bool orientation_convention(const Triangle& pointed, int from);
    
    /**
     * @param current current triangle in the loop
     * @param previous_idx the index of previous triangle in the loop in the internal array of current
     * 
     * ATTENTION: is not a pure function, it modifies the previous_idx for future uses
     */
    Triangle* next(Triangle* current, int& previous_idx, bool debug_flag = false);
    
    /**
     * @brief return a Plaquette
     */
    GaugeElement looparound(bool debug_flag = false);
    GaugeElement looparound(vector<int>& triangle_list, bool debug_flag = false);
    
    /**
     * @brief return a Staple
     */
    GaugeElement looparound(Triangle* edge_t[2], bool debug_flag = false);
    
    /**
     * @brief correspond to \tilde{\Pi} in the original document
     */
    double Pi_tilde(bool debug_flag = false);
    
    /**
     * @brief its the gauge action contribute of the Plaquette around the Vertex
     */
    double gauge_action_contrib(bool debug_flag = false);
    
    double topological_charge_density(bool debug_flag = false);
    
    vector<double> gauge_action_top_charge_densities(bool debug_flag = false);
    vector<double> gauge_action_top_charge_densities(vector<int>& triangle_list, bool debug_flag = false);
    
    // ##### FILE I/O #####
    
    void write(ostream& output);
    
    void read(istream& input, const vector<Label>& List2);
    
    // ##### DEBUG FACILITIES #####
    
    void print_elements(ostream& os=cout);
};

#endif // VERTEX_H
