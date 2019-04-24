/** @file */
#ifndef GAUGE_H
#define GAUGE_H

#include "label.h"
#include <memory>
#include <vector>
#include <fstream>
using namespace std;

class GaugeElement
{
    static const int N=1;
    
private:
    
    // DATA
    
    /**
    * @var representation of the gauge group element as an NxN matrix
    * 
    */
    double mat[N][N];
    
    /**
    * @var label of the base edge 
    * 
    */
    Label base_edge;
    
    friend class Triangulation;
    
public:
    
    /**
     * 
     */ 
    GaugeElement();
    
    /**
     * 
     */
    GaugeElement(const double (&matrix)[N][N]);

     /**
     * Destructor
     */
    ~GaugeElement(){}
    
    // METHODS

    /**
    * @brief interface method
    * 
    * @return gauge element representation
    */
    double** matrix();
    
    /**
    * @brief interface method
    * 
    * @return the dimension of the gauge group
    */
    int dimension();

    /**
    * @brief interface method
    * 
    * @return base_edge
    */
    Label base();
    
    // ##### FILE I/O #####
    
    void write(ostream& output);
    
    void read(istream& input, const vector<Label>& List1);

};

#endif // GAUGE_H
