/** @file */
#include <iostream>
// #include <vector>
// #include <memory>
#include "label.h"
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



int dice()
{
    static RandomGen r;
    int dice = 0;
    
    double move22 = 0.1;
    double move24 = 0.2;
    
    double extraction = r.next();
    if(extraction < move22)
        dice = 1;
    else if(extraction < 2*move22)
        dice = 2;
    else if(extraction < move24 + 2*move22)
        dice = 3;
    else if(extraction < 2*move24 + 2*move22)
        dice = 4;
    else
        dice = 5;
    
    return dice;
}

int main(int argc, char* argv[]){
//     Triangulation uni(3, 0.4, 6.);
//     RandomGen r;
    
//     for(int i=0; i<1000; i++)
//         uni.move_24();
//     
//     for(int i=0; i<10000; i++)
//         uni.move_gauge();
//    
//     uni.move_42(true);
    
//     double current = uni.total_gauge_action();
//     for(int i=0; i<10000; i++){
//         double previous = current;
//         
//         int a = uni.list2.size()*r.next();
//         GaugeElement U;
//         U = U.random_element(1.);
//         
//         uni.list2[a].dync_triangle()->gauge_transform(U);
//         current = uni.total_gauge_action();
//         
//         cout << a << endl << U << endl;
//         
//         if(current - previous > 1e-10){
//             cout << current - previous << endl;
//             throw runtime_error("not gauge invariant");
//         }
//     }
    complex<double> prev = exp(1i*4.6);
    cout << (imag(prev) > 0) * 2 - 1 << endl;
    
//     U[0][0] = 3i;
//     V[0][0] = 1. + 7i;
//     
//     cout << U << endl << V << endl << 2 * V << endl;
    

//     for(int i=0; i<1000; ++i){
// 
//         switch(dice()){
//             case 1:
//             {
// //                cout<<"mv22_1"<<endl;
//                 uni.move_22_1();
//                 break;
//             }
//             case 2:
//             {
// //                cout<<"mv22_2"<<endl;
//                 uni.move_22_2();
//                 break;
//             }
//             case 3:
//             {
// //                cout<<"mv24"<<endl;
//                 uni.move_24();
//                 break;   
//             }
//             case 4:
//             {
// //                cout<<"mv42"<<endl;
//                 uni.move_42();
//                 break;
//             }
//             case 5:
//             {
//                 uni.move_gauge();
//                 break;
//             }
//         }
//         cout<<i<<" "<<uni.topological_charge()<<endl;     
//        for(int s = 0; s < 10; ++s){
// //        cout<<10*i+s<<" "<<uni.topological_charge()<<endl;     
//            uni.move_gauge();
//        }
//     }
}
