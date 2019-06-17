 /** @file */
#include <iostream>
#include <string>
#include <stdexcept>
#include "triangulation.h"

using namespace std;

/**
 * The following program is intended to be given a path to a file that is a
 * Triangulation checkpoint and produce the corresponding adjacency list
 * 
 * The only check that is done explicitly is that exactly one argument is given.
 * 
 * The duty to find the last checkpoint, if it is what is wanted, it's 
 * demanded to the caller.
 */

int find_nth_from_last(string str, const string& substr, const int& n){
    int pos;
    
    for(int i=0; i<n; i++){
        pos = str.find_last_of(substr);
        str = str.substr(0, pos);
    }
    
    return pos;
}

int main(int argc, char* argv[]){
    int len = argc;
    
    if(len < 2)
        throw runtime_error("missing triangulation from which extracting adj_list");
    else if(len > 2)
        throw runtime_error("too many arguments, the program accepts only one valid path");
        
    string triang_chkpt = argv[1];
    Triangulation triang(triang_chkpt);
    
    int pos = find_nth_from_last(triang_chkpt, "/", 2);
    string triang_path = triang_chkpt.substr(0, pos);
    int pos1 = triang_chkpt.find_last_of("/") + 1;
    int pos2 = triang_chkpt.find_last_of(".");
    string chkpt_name = triang_chkpt.substr(pos1, pos2 - pos1);
    
    string adj_list = triang_path + "/adjacency_lists/" + chkpt_name + ".adj";
    
    triang.produce_adjacency_list(adj_list);
}
