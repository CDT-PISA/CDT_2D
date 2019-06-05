/** @file */
#include <iostream>
// #include <vector>
// #include <memory>
// #include "label.h"
// #include "edge.h"
// #include "vertex.h"
// #include "triangle.h"
// #include "gaugeelement.h"
// #include "triangulation.h"
#include "randomgenerator.h"
// #include <cmath>
// #include <complex>
// #include <random>
// #include <limits>

using namespace std;

int main(){
//     Triangulation uni(10, -10., 1.);
    
    
//     cout << "Gauge Action: " << uni.total_gauge_action() << endl;
//     cout << "Carica Topologica: " << uni.topological_charge() << endl;
    
//     for( int i=0; i< 1; i++){
//         uni.move_24();
//         if((i % 100) == 0)
//             cout << "move[" << i << "] gauge action: " << uni.total_gauge_action() << endl;
//     }
//
//    double pi = 2*asin(1);
//    r.really_rand();
//    int i =  r.next() * uni.list2.size();
//    Triangle* tri_lab = uni.list2[i].dync_triangle();
//    tri_lab->edges()[0].dync_edge()->U = 1;
//    tri_lab->edges()[1].dync_edge()->U = exp(2i*pi/3.);
//    tri_lab->edges()[2].dync_edge()->U = exp(-2i*pi/3.);
//    string type;
//    if(tri_lab->is12())
//        type = "12";
//    else
//        type = "21";
//    cout << "tri: " << i  << "  (type" << type << ")"<< endl;
    
    for( int i=0; i< 2000; i++){
        RandomGen r;
        cout << r.next() << endl; 
    }
    
    return 0;
    
//      for( int i=0; i< 20000; i++){
//          uni.is_consistent();
//          
//          if(i%100 == 0){
//             cout << i << endl;
//             cout << "Gauge Action: " <<  uni.total_gauge_action() << endl;
//             cout << "Carica Topologica: " << uni.topological_charge() << endl;
//          }
//          for(int j=0; j<20; ++j){
//             //cout<<"gauge move"<<endl;
//             uni.move_gauge();
//          }
//          cout<<"hello"<<endl;
//          if(r.next()>0.4){
//              if(r.next()>0.5){
//                  cout<<"hello24"<<endl;
//                 uni.move_24();
//              }else{
//                  cout<<"hello42"<<endl;
//                 uni.move_42();
//              }
//          }else{
//              if(r.next()>0.5){
//                  cout<<"hello22_1"<<endl;
//                 uni.move_22_1();
//              }else{
//                  cout<<"hello22_2"<<endl;
//                 uni.move_22_2(true);
//              }
//          }
//     }
//     
//     cout << "Gauge Action: " <<  uni.total_gauge_action() << endl;
//     cout << "Carica Topologica: " << uni.topological_charge() << endl;
}
