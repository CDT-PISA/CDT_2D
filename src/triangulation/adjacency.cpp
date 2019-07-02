// ##### ADJACENCY LIST #####

void Triangulation::binary_adjacency_list(string filename)
{
    ofstream of(filename, ios::binary | ios::out);
    
    binary_adjacency_list(of);
    of.close();
}

void Triangulation::binary_adjacency_list(std::ofstream& output)
{
    int len=list2.size();
    output.write((char*)&len, sizeof(len));
    
    for(auto x: list2){
        for(int i=0; i<3; i++){
            int pos = x.dync_triangle()->t[i]->id;
            output.write((char*)&pos, sizeof(pos));
        }
    }
}


void Triangulation::text_adjacency_and_observables(string filename)
{
    ofstream of(filename, ios::binary | ios::out);
    
    text_adjacency_and_observables(of);
    of.close();
}

/// @todo stampare un json
void Triangulation::text_adjacency_and_observables(std::ofstream& output)
{
    string indent = "    ";
    
    
    output << "{" << endl;
    output << indent << "\"volume\": " << list2.size() << "," << endl;
    
    vector<double> gauge_action_contributions(list2.size(), 0.);
    vector<double> pi_tilde_list(list2.size(), 0.);
    vector<double> topological_charge_densities(list2.size(), 0.);
    
    for(auto x: list0){
        vector<int> adjacent_triangles;
        vector<double> v = x.dync_vertex()->gauge_action_top_charge_densities(adjacent_triangles);
        int coord = x.dync_vertex()->coordination();
        
        for(int i: adjacent_triangles){
            gauge_action_contributions[i] += - (beta * N) * (v[0] / coord);
            pi_tilde_list[i] += v[0];   // it would be Pi_tilde / coord, but v[0] = Pi_tilde / coord
            topological_charge_densities[i] += v[1] / coord;
        }
    }
    
    output << indent << "\"nodes\": [" << endl;
    for(auto x: list2){
        int i = x->id;
        
        output << indent << indent << "{" << endl;
        output << indent << indent << indent << "\"slab_time\": " << x.dync_triangle()->slab_index() << "," << endl;
        output << indent << indent << indent << "\"adjacents\": [ ";
        for(int i=0; i<3; i++){
            int pos = x.dync_triangle()->t[i]->id;
            output << pos;
            if(i != 2)
                output << ",";
            output << " ";
        }
        output << "]," << endl;
        output << indent << indent << indent << "\"gauge_action\": " << gauge_action_contributions[i] << "," << endl;
        output << indent << indent << indent << "\"pi_tilde\": " << pi_tilde_list[i] << "," << endl;
        output << indent << indent << indent << "\"topological_charge\": " << topological_charge_densities[i] << "," << endl;
        output << indent << indent << "}," << endl;
    }
    output << indent << "]," << endl;
    
    output << "}" << endl;
}
