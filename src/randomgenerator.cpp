/*
 * <one line to give the program's name and a brief idea of what it does.>
 * Copyright (C) 2019  Alessandro Candido <email>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "randomgenerator.h"
#include <random>
#include <iostream>

using namespace std;

//#define SEED 1145

pcg32 RandomGen::rng;

RandomGen::RandomGen()
{
//    struct timeval tval;
//    gettimeofday(&tval,NULL);
//    j=tval.tv_sec*1000000ULL+tval.tv_usec;
    if(RandomGen::check_first()){
//        rng.seed(SEED);
      rng.seed(time(NULL));
    }
}

RandomGen::RandomGen(long long seed)
{
//    struct timeval tval;
//    gettimeofday(&tval,NULL);
//    j=tval.tv_sec*1000000ULL+tval.tv_usec;
    if(RandomGen::check_first()){
//        rng.seed(SEED);
      rng.seed( (seed>0) ? seed : time(NULL) );
    }
}

bool RandomGen::check_first(){
    static bool first = true;
    if(first){
        first=false;
        return true;
    }
    return false;
}

double RandomGen::next(){
//    
//    if(state.str() != "")
//        state >> gen;
//    state.clear();
//    double rand = generate_canonical<double, 10>(gen);
//    state << gen;
//    
//    return rand;
//    return generate_canonical<double, 10>(gen);
    return rng.nextDouble();
}

void RandomGen::really_rand()
{
    struct timeval tval;
    gettimeofday(&tval,NULL);
    int j=tval.tv_sec*1000000ULL+tval.tv_usec;
    rng.seed(j);
}

void RandomGen::set_seed(long long seed){
    rng.seed((seed>0)? seed : time(NULL));
}

uint64_t RandomGen::get_state()
{
    return rng.state;
}


void RandomGen::set_state(uint64_t state)
{
//    rng.state = gs.state;
    rng.state=state;
    RandomGen::check_first();
}
