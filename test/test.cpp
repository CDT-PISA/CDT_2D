/** @file */
#include <iostream>
// #include <vector>
// #include <memory>
// #include "label.h"
// #include "edge.h"
#include "vertex.h"
#include "triangle.h"
// #include "gaugeelement.h"
#include "triangulation.h"
#include "randomgenerator.h"
// #include <cmath>
// #include <complex>
// #include <random>
// #include <limits>

using namespace std;

int main(){
    Triangulation uni("./run1_check3.chkpt");
    
    cout << uni << endl;
    
    uni.is_consistent();
}
