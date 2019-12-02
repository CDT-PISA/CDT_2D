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
    
    double move22 = 0.2;
    double move24 = 0.3;
    
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
    RandomGen r;

    ofstream fout;
    fout.open("test.dat", ios::out);

 /*   
    for(int i=0; i<1000; i++){
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
    
    GaugeElement U;
    for(int i=0; i < 1000; i++)
        cout << arg(U.rand()[0][0]) << endl;
    
    double current = uni.total_gauge_action();
    for(int i=0; i<1000; i++){
        double previous = current;
        
        int a = uni.list2.size()*r.next();
        GaugeElement U;
        U = U.random_element(1.);
        
        uni.list2[a].dync_triangle()->gauge_transform(U);
        current = uni.total_gauge_action();
        
        cout << a << endl << U << endl;
        
        if(current - previous > 1e-10){
            cout << current - previous << endl;
            throw runtime_error("not gauge invariant");
        }
    }*/
//     complex<double> prev = exp(1i*4.6);
//     cout << (imag(prev) > 0) * 2 - 1 << endl;
//     
//     U[0][0] = 3i;
//     V[0][0] = 1. + 7i;
//     
//     cout << U << endl << V << endl << 2 * V << endl;
    
    double top;
    double avgtop = 0, avgtop2 = 0, vartop = 0;

    int i;
     for(i=0; i<1000; ++i){
 
         switch(dice()){
             case 1:
             {
 //                cout<<"mv22"<<endl;
                 uni.move_22();
                 break;
             }
             case 2:
             {
 //                cout<<"mv22"<<endl;
                 uni.move_22();
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

	top = uni.topological_charge();
	avgtop += top;
	avgtop2 += top*top;
        cout<<i<<" "<<top<<endl; 	
        for(int s = 0; s < 20; ++s){
 //        cout<<10*i+s<<" "<<uni.topological_charge()<<endl;     
            uni.move_gauge();
        }
	if(i%200==0){
		
	}
     }

     avgtop /= i;
     avgtop2 /= i;
     vartop = avgtop2 - (avgtop * avgtop);
    cout << "avg top = " << avgtop << endl;
    cout << "var top = " << vartop ;
    return 0;
}
