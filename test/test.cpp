/** @file */
// #include <iostream>
// // #include <vector>
// // #include <memory>
// #include "label.h"
// #include "edge.h"
// #include "vertex.h"
#include "triangle.h"
// #include "gaugeelement.h"
// #include "triangulation.h"
// #include "randomgenerator.h"
// #include <cmath>
// #include <complex>
// // #include <random>
// // #include <limits>
#include <iostream>
#include <cstdio>
#include <chrono>
#include <string>
#include <complex>
#include <sys/stat.h>
#include "triangulation.h"
#include "randomgenerator.h"
#include "edge.h"

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
    Triangulation uni(80, 0.4, 6.);
    RandomGen r;
    
    r.really_rand();
    
    for(int i=0; i<1000; i++){
        vector<double> x;
        uni.move_24();
        x = uni.move_22();
        x = uni.move_22();
        for(int i=0; i<10; i++)
            uni.move_gauge();
    }
   
    uni.move_22(true);
    uni.move_22(true);
    uni.move_24(true);
    uni.move_42(true);
    
//     GaugeElement U;
//     for(int i=0; i < 1000; i++)
//         cout << arg(U.rand()[0][0]) << endl;
//     
//     vector<complex<double>> current = uni.toleron();
//     vector<complex<double>> initial = current;
//     for(int i=0; i<1000; i++){
//         vector<complex<double>> previous = current;
//         
//         int a = uni.list2.size()*r.next();
//         GaugeElement U;
//         U = U.rand();
//         
//         uni.list2[a].dync_triangle()->gauge_transform(U);
//         current = uni.toleron();
//         
//         for(int j=0; j<current.size(); j++){
//             if(abs(current[j] - previous[j]) > 1e-10){
//                 cout << abs(current[j] - previous[j]) << endl;
//                 throw runtime_error("not gauge invariant");
//             }
//         }
//     }
//     
//     for(int j=0; j<current.size(); j++){
//         if(abs(current[j] - initial[j]) > 1e-10){
//             cout << abs(current[j] - initial[j]) << endl;
//             throw runtime_error("not gauge invariant");
//         }
//     }
//     complex<double> prev = exp(1i*4.6);
//     cout << (imag(prev) > 0) * 2 - 1 << endl;
//     
//     U[0][0] = 3i;
//     V[0][0] = 1. + 7i;
//     
//     cout << U << endl << V << endl << 2 * V << endl;
    

//     for(int i=0; i<1000; ++i){
// 
//         switch(dice()){
//             case 1:
//             {
// //                cout<<"mv22"<<endl;
//                 uni.move_22();
//                 break;
//             }
//             case 2:
//             {
// //                cout<<"mv22"<<endl;
//                 uni.move_22();
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
    
    cout << endl << endl;
    cout << "╔═══════════════════════╗" << endl;
    cout << "║     Happy Ending!     ║" << endl;
    cout << "╚═══════════════════════╝" << endl;
}
