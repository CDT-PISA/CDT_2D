/** @file */
#ifndef RANDOMGEN_H
#define RANDOMGEN_H

#include <random>
#include <sstream>
#include "pcg32.h"
#include <sys/time.h>

using namespace std;

class RandomGen
{
private:
    
    // DATA
    
   pcg32 rng;

public:
    
    // CLASS STANDARD
    
    RandomGen();
    
    ~RandomGen(){}
    
    // METHODS
    
    double next();
    
    void really_rand();
};

#endif // RANDOMGEN_H
