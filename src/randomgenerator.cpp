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

#define SEED 1145

RandomGen::RandomGen()
{
    gen.seed(SEED);
}

stringstream RandomGen::state;

double RandomGen::next(){
    
    if(state.str() != "")
        state >> gen;
    state.clear();
    double rand = generate_canonical<double, 10>(gen);
    state << gen;
    
    return rand;
}

void RandomGen::really_rand()
{
    random_device rd;
    gen.seed(rd());
    state << gen;
}
