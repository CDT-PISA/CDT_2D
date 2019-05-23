/** @file */
#include <iostream>
// #include <vector>
// #include <memory>
// #include "label.h"
#include "edge.h"
#include "vertex.h"
#include "triangle.h"
#include "gaugeelement.h"
#include "triangulation.h"
#include "randomgenerator.h"
#include <cmath>
#include <complex>
// #include <random>
// #include <limits>

using namespace std;

int main(){
    RandomGen r;
    Triangulation uni(10, 1., 1.);
    
//     GaugeElement A, B;
//     
//     A = 6.;
//     B = 5. + 7i;
//     
//     A *= 3;
//     
//     cout << A.matrix()[0][0] << endl;
    
    cout << uni.total_gauge_action() << endl;
    
    for( int i=0; i< 20; i++)
        uni.move_gauge();
    cout << uni.total_gauge_action() << endl;
}
