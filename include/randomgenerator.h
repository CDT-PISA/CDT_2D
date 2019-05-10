/** @file */
#ifndef RANDOMGEN_H
#define RANDOMGEN_H

#include <random>

using namespace std;

class RandomGen
{
private:
    
    // DATA
    
    mt19937_64 gen;
    
public:
    
    static long n;
    long m;
    
    /**
     * Auxiliary Vertex
     * 
     */ 
    RandomGen();
    
    ~RandomGen(){}
    
    double next();
};

#endif // RANDOMGEN_H
