/** @file */
#include <iostream>
// #include <vector>
// #include <memory>
// #include "label.h"
// #include "edge.h"
// #include "vertex.h"
// #include "triangle.h"
#include "triangulation.h"
#include "randomgenerator.h"
// #include <cmath>
// #include <complex>
#include <random>

using namespace std;

int main(){
    Triangulation uni(10, 1., 0.01);
    
    RandomGen r1, r2;
    mt19937_64 gen;
    gen.seed(1145);
    
    for(int i=0; i<10; i++)
        cout << r1.next() << ", " << r2.next() << ", ";
//         cout << generate_canonical<double, 10>(gen) << ", ";
    
    cout << endl;
//     stringstream s;
//     
//     cout << s.str() << "ciao\n";
}
