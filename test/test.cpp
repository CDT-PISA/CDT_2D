/** @file */
#include <iostream>
#include <vector>
#include <memory>
#include "label.h"
#include "edge.h"
#include "vertex.h"
#include "triangle.h"
#include "triangulation.h"

using namespace std;

int main(){
    Triangulation uni(10,1);
    EdgeType e_t = EdgeType::_time;
    Label lab_v[2];
    Label lab_t = uni.list2[2];
    
    for(int i=0; i<2; i++){
        lab_v[i] = uni.list0[i];
    }
    
    Edge e(17, lab_v, lab_t, e_t);
    
    cout << e.position() << endl;
    cout << e.adjacent_triangle().dync_triangle()->position() << endl;
    cout << boolalpha << e.is_space() << " " << e.is_time() << endl;
    cout << e.gauge_element().dimension() << endl;
    
    int N = e.gauge_element().dimension();
    for(int i=0; i<N; i++){ 
        for(int j=0; j<N; j++){
            cout << e.gauge_element().matrix()[i][j] << " ";
        }
        cout << endl;
    }
    
    for(int i=0; i<30; i++){
        uni.move_24(false);
        cout << uni.list2.size() << " ";
    }
    cout << endl;
}
