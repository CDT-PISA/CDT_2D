/** @file */
#ifndef RANDOMGEN_H
#define RANDOMGEN_H

#include <random>
#include <sstream>

using namespace std;

class RandomGen
{
private:
    
    // DATA
    
    mt19937_64 gen;
    
public:
    
    static stringstream state;
    
    // CLASS STANDARD
    
    RandomGen();
    
    ~RandomGen(){}
    
    // METHODS
    
    double next();
};

#endif // RANDOMGEN_H
