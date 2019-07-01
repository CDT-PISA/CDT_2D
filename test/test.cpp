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

int main(){
    Triangulation uni("./run1_check3.chkpt");
    
//    cout << uni << endl;
    
    uni.is_consistent();


//    for(int s=0; s<100; ++s)
//        uni.move_gauge();

//    cout<<"Q_i = "<<uni.topological_charge()<<endl;     
//
//    for(auto& lb : uni.list1){
//        Edge * edg = lb.dync_edge();
//        GaugeElement gl(edg->U);
//        edg->U = gl.dagger();
//    }
//    cout<<"Q_f = "<<uni.topological_charge()<<endl;     
//
//
//    for(int s=0; s<100; ++s)
//        uni.move_gauge();
//
//    cout<<"Q_i = "<<uni.topological_charge()<<endl;     
//
//    for(auto& lb : uni.list1){
//        Edge * edg = lb.dync_edge();
//        GaugeElement gl(edg->U);
//        edg->U = gl.dagger();
//    }
//    cout<<"Q_f = "<<uni.topological_charge()<<endl;     

    for(int i=0; i<100; ++i){
        cout<<10*i<<" "<<uni.topological_charge()<<endl;     

        if(i==50){
        
            for(auto& lb : uni.list1){
                Edge * edg = lb.dync_edge();
            GaugeElement gl(edg->U);
            edg->U = gl.dagger();
            }
        }

        switch(dice()){
            case 1:
            {
//                cout<<"mv22_1"<<endl;
                uni.move_22_1();
                break;
            }
            case 2:
            {
//                cout<<"mv22_2"<<endl;
                uni.move_22_2();
                break;
            }
            case 3:
            {
//                cout<<"mv24"<<endl;
                uni.move_24();
                break;   
            }
            case 4:
            {
//                cout<<"mv42"<<endl;
                uni.move_42();
                break;
            }
            case 5:
            {
                uni.move_gauge();
                break;
            }
        }
//        cout<<i<<" "<<uni.topological_charge()<<endl;     
//        for(int s = 0; s < 10; ++s){
//        cout<<10*i+s<<" "<<uni.topological_charge()<<endl;     
//            uni.move_gauge();
//        }
    }
}
