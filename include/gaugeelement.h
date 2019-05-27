/** @file */
#ifndef GAUGE_H
#define GAUGE_H

#include "label.h"
#include <memory>
#include <vector>
#include <fstream>
#include <complex>
#include <cmath>
using namespace std;

class Vertex;

class GaugeElement
{
public:
    static const int N=1;
    
private:
    
    // DATA
    
    /**
    * @var representation of the gauge group element as an NxN matrix
    * 
    */
    complex<double> mat[N][N];
    
    /**
    * @var label of the base edge 
    * 
    */
    Label base_edge;
    
    friend class Triangulation;
    friend class Vertex;
    
public:
    
    /**
     * 
     */ 
    GaugeElement();
    
    /**
     * 
     */ 
    GaugeElement(const Label& edge);
    
    /**
     * 
     */
    GaugeElement(const complex<double> (&matrix)[N][N]);

     /**
     * Destructor
     */
    ~GaugeElement(){}
    
    // ##### METHODS #####

    /**
    * @brief interface method
    * 
    * @return gauge element representation
    */
    complex<double>** matrix();
    
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
    
    void set_base(Label base);
    
    complex<double>* operator[](int i);
    
    // ##### OPERATIONS #####
    
    double partition_function();
    
    void random_element(double a = nan(""));
    
    void heatbath(GaugeElement Force);
    
    // ##### ALGEBRA #####
    
    GaugeElement operator+(const GaugeElement& V);
    
    GaugeElement operator-(const GaugeElement& V);
    
    GaugeElement operator*(const GaugeElement& V);
    
    GaugeElement operator+=(const GaugeElement& V);
    
    GaugeElement operator-=(const GaugeElement& V);
    
    GaugeElement operator*=(const GaugeElement& V);
    
    GaugeElement dagger();
    
    complex<double> trace();
    complex<double> tr();
    
    // scalars
    
    GaugeElement alpha_id(const complex<double>& alpha);
    
    GaugeElement operator=(const complex<double>& alpha);
    
    GaugeElement operator+(const complex<double>& alpha);
    
    GaugeElement operator-(const complex<double>& alpha);
    
    GaugeElement operator*(const complex<double>& alpha);
    
    GaugeElement operator/(const complex<double>& alpha);
    
    GaugeElement operator+=(const complex<double>& alpha);
    
    GaugeElement operator-=(const complex<double>& alpha);
    
    GaugeElement operator*=(const complex<double>& alpha);
    
    GaugeElement operator/=(const complex<double>& alpha);
        
    // auxiliary
    
    void unitarize();
    
    // ##### FILE I/O #####
    
    void write(ostream& output);
    
    void read(istream& input, const vector<Label>& List1);

};

#endif // GAUGE_H
