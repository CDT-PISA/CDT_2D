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
public:
    
    // DATA
    
   static pcg32 rng;

   bool check_first();

    
    // CLASS STANDARD
    
    RandomGen();

    RandomGen(long long seed);
    
    ~RandomGen(){}
    
    // METHODS
    
    double next();
    
    void really_rand();

    void set_seed(long long seed);

    uint64_t get_state();
    
    void set_state(uint64_t state);
};

#endif // RANDOMGEN_H
