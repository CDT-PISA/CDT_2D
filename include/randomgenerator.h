/** @file */
#ifndef RANDOMGEN_H
#define RANDOMGEN_H

#include <random>
#include <sstream>
#include "pcg32.h"
#include <sys/time.h>

using namespace std;

struct generator_state
{
    uint64_t state;
    
    generator_state(){}
    
    generator_state(uint64_t i) : state(i) {}
    
    ~generator_state(){}
    
    // ##### FILE I/O #####
    
    void write(ostream& output);
    void read(istream& input);
};

class RandomGen
{
private:
    
    // DATA
    
   static pcg32 rng;

   bool check_first();

public:
    
    // CLASS STANDARD
    
    RandomGen();

    RandomGen(long long seed);
    
    ~RandomGen(){}
    
    // METHODS
    
    double next();
    
    void really_rand();
    
    generator_state get_state();
    
    void set_state(generator_state gs);
};

#endif // RANDOMGEN_H
