#include <iostream>
#include <fstream>
#include <iomanip>

using namespace std;

int main(int argc, char* argv[]){
    int len = argc;
    
    if(len < 2)
        throw runtime_error("missing triangulation from which extracting adj_list");
    else if(len > 2)
        throw runtime_error("too many arguments, the program accepts only one valid path");
    
    string adj_list = argv[1];
    ifstream input(adj_list, ios::binary | ios::in);
    
    int len_mat;
    input.read((char*)&len_mat, sizeof(len_mat));
    
    for(int i=0; i<len_mat; i++){
        for(int j=0; j<3; j++){
            int pos;
            input.read((char*)&pos, sizeof(pos));
            cout << setw(6) << pos << " ";
        }
        cout << endl;
    }
    
    cout << endl;
    
    input.close();
}
