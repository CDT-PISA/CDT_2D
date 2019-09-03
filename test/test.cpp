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
// #include <cmath>
// #include <complex>
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
    Triangulation uni(3, 0.4, 6.);
    
//     cout << boolalpha << uni.list0[0].dync_vertex()->orientation_convention(*uni.list2[0].dync_triangle(), 2);
//     uni.explore();
    
    GaugeElement U(1.);
    GaugeElement V(1.);
    
    cout << (U - V).norm() << endl;
    
    for(int i=0; i<10000; i++)
        uni.move_gauge();
    
    uni.move_22_2(true);
        
    
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
