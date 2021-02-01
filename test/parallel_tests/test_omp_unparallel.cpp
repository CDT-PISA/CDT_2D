#include <iostream>
#include <list>
#include <vector>
#include <algorithm>
#include "../../include/pcg32.h"
#include <omp.h>

#define N 20

#define STEPS 100

using namespace std;

pcg32** rng_arr;

vector<int> field(N);

/* rules:
 *      direct : select one of the up spins and flip it and its nearest neighbours
 *      inverse: select one of the down spins and flip it and its nearest neighbours
 */

vector<int> list_up, list_down;

int main(){

    // setup
    rng_arr = new pcg32*[64*omp_get_max_threads()];

    omp_lock_t up_lock, down_lock;
    omp_init_lock(&up_lock);
    omp_init_lock(&down_lock);


    // cache-friendly access
#pragma omp parallel for shared(rng_arr)
    for(int tid=0; tid<omp_get_max_threads(); ++tid){
        rng_arr[64*tid] = new pcg32(tid*12356428174ULL+10485729375ULL);
    }

    // initialization
#pragma omp parallel for shared(rng_arr,field,list_up,list_down)
    for(int i=0; i<N; ++i){
        if(rng_arr[64*omp_get_thread_num()]->nextDouble()>0.5){
            field[i] = 1;
            omp_set_lock(&up_lock);
            list_up.push_back(i);
            omp_unset_lock(&up_lock);
        }else{
            field[i] = -1;
            omp_set_lock(&down_lock);
            list_down.push_back(i);
            omp_unset_lock(&down_lock);
        }
    }


    // run

//#pragma omp parallel for 
    for(int i=0; i<STEPS; ++i){
        
//#pragma omp critical
        {
        int tid = omp_get_thread_num();
        int site;
        if(rng_arr[0]->nextDouble()>0.5){ // do direct
            site = list_up[rng_arr[64*tid]->nextUInt(list_up.size())];
        }else{ // do inverse
            site = list_down[rng_arr[64*tid]->nextUInt(list_down.size())];
        }
        for(int s=-1; s<=1; ++s){
            int nn=(site+s+N)%N;
            if(field[nn]==1){
                omp_set_lock(&up_lock);
                auto it = std::find(list_up.begin(), list_up.end(),nn);
                list_up.erase(it);
                omp_unset_lock(&up_lock);
                omp_set_lock(&down_lock);
                list_down.push_back(nn);
                omp_unset_lock(&down_lock);
            }else{
                omp_set_lock(&down_lock);
                auto it = std::find(list_down.begin(), list_down.end(),nn);
               list_down.erase(it);
                omp_unset_lock(&down_lock);
                omp_set_lock(&up_lock);
                list_up.push_back(nn);
                omp_unset_lock(&up_lock);
            }
            field[nn]*=-1;
        }

        cout<<std::showpos<<i<<": ";
        for(int pos=0; pos<N; ++pos){
            cout<<field[pos]<<" "; 
        }
        cout<<endl;
        }
    }


    // clear
    //
    omp_destroy_lock(&up_lock);
    omp_destroy_lock(&down_lock);

#pragma omp parallel for shared(rng_arr)
    for(int tid=0; tid<omp_get_max_threads(); ++tid){
        delete rng_arr[64*tid];
    }

    delete [] rng_arr;

    return 0;
}
