// #include <iostream>
// #include <fstream>
// #include <iomanip>
// #include <memory>
// #include <stdexcept>
// #include <random>
// #include <cmath>
// #include <complex>
// #include <string>
// #include "randomgenerator.h"
// #include "triangulation.h"
// #include "vertex.h"
// #include "edge.h"
// #include "triangle.h"
// #include "label.h"
// #include "gaugeelement.h"

void Triangulation::is_consistent(bool verbose)
{
        
    if(verbose)
        cout << "\n\ndebug..." << endl;
    
    // check list0: Vertices, num40, num40p
    
    for(int i=0; i < list0.size(); i++){
        Label lab = list0[i];
        Vertex* v_lab = lab.dync_vertex();
        
        // id
        
        if(i != lab->id)
            throw runtime_error("Vertex identifier wrong: Vertex in position "+to_string(i)+" in list0, while its identifier points to "+to_string(lab->id));
        
        // near_t
        
        if((v_lab->near_t->id > list2.size()) or (&*v_lab->near_t != &*list2[v_lab->near_t->id]))
            throw runtime_error("Error in Vertex ["+to_string(i)+"]: adjacent Triangle ["+to_string(v_lab->near_t->id)+"] is not in list2 (list2.size = "+to_string(list2.size())+")");
         
        if(not find_vertex_in_triangle(v_lab->near_t.dync_triangle(),lab->id))
            throw runtime_error("Error in Vertex ["+to_string(i)+"]: adjacent Triangle ["+to_string(v_lab->near_t->id)+"] does not include it");
        
        // coordination_number
        
        
//         if(v_lab->coordination() != count_adjacents(v_lab))
//             throw runtime_error("Error in Vertex ["+to_string(i)+"]: number of adjacents triangles is not equal to coordination number stored");
        
        if(v_lab->coord_num == 4){
            if(i > (num40 + num40p - 1))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: is of coord. 4 but is listed like it isn't");
            if((spatial_profile[v_lab->t_slice] == 3) && (i < num40))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: is of coord. 4 and pathological but is listed like it is only of coord. 4");
            else if((spatial_profile[v_lab->t_slice] > 3) && (i > (num40 - 1)))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: is of coord. 4 and not pathological but is listed like it is pathological");
        }
        
        // vert. coord. 4
        if(i < num40){
            if(list0[i].dync_vertex()->coord_num > 4)
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: is not of coord. 4 but is listed like it is (list0.size = "+to_string(list0.size())+", num40 = "+to_string(num40)+", num40p = "+to_string(num40p)+")");
            
            if(spatial_profile[v_lab->time()] == 3)
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: is pathological but is listed like it isn't  (list0.size = "+to_string(list0.size())+", num40 = "+to_string(num40)+", num40p = "+to_string(num40p)+")");
            
            Label lab_t0 = move_42_find_t0(list0[i]);
            Label lab_t1 = lab_t0.dync_triangle()->adjacent_triangles()[2];
            Label lab_t2 = lab_t1.dync_triangle()->adjacent_triangles()[0];
            Label lab_t3 = lab_t0.dync_triangle()->adjacent_triangles()[0];
            Triangle* tri_lab0 = lab_t0.dync_triangle();
            Triangle* tri_lab1 = lab_t1.dync_triangle();
            Triangle* tri_lab2 = lab_t2.dync_triangle();
            Triangle* tri_lab3 = lab_t3.dync_triangle();
            
            Label lab_v0 = tri_lab0->vertices()[0];
            Label lab_v1 = tri_lab3->vertices()[1];
            Label lab_v2 = tri_lab0->vertices()[2];
            Label lab_v3 = tri_lab1->vertices()[2];
            Label lab_v4 = list0[i];
            Vertex* v_lab0 = lab_v0.dync_vertex();
            Vertex* v_lab1 = lab_v1.dync_vertex();
            Vertex* v_lab2 = lab_v2.dync_vertex();
            Vertex* v_lab3 = lab_v3.dync_vertex();
            Vertex* v_lab4 = lab_v4.dync_vertex();
            
            // --- check cell members (triangles) type
            
            if(not (tri_lab0->type == TriangleType::_21))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 identify a cell whose t0 ["+to_string(lab_t0->position())+"] is not of type (2,1)");
            if(not (tri_lab1->type == TriangleType::_12))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 identify a cell whose t1 ["+to_string(lab_t1->position())+"] is not of type (1,2)");
            if(not (tri_lab2->type == TriangleType::_12))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 identify a cell whose t2 ["+to_string(lab_t2->position())+"] is not of type (1,2)");
            if(not (tri_lab3->type == TriangleType::_21))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 identify a cell whose t3 ["+to_string(lab_t3->position())+"] is not of type (2,1)");
            
            // --- check central vertex (v4) coherency
            
            if(lab_v4 != tri_lab0->vertices()[1])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 not coincident with the candidate from t0");
            if(lab_v4 != tri_lab1->vertices()[1])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 not coincident with the candidate from t1");
            if(lab_v4 != tri_lab2->vertices()[0])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 not coincident with the candidate from t2");
            if(lab_v4 != tri_lab3->vertices()[0])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 not coincident with the candidate from t3");
            
            // --- check other vertices coherence
            
            if(tri_lab0->vertices()[0] != tri_lab1->vertices()[0])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: in the cell of vert. coord. 4 v0 is not unique");
            if(tri_lab2->vertices()[1] != tri_lab3->vertices()[1])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: in the cell of vert. coord. 4 v1 is not unique");
            if(tri_lab0->vertices()[2] != tri_lab3->vertices()[2])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: in the cell of vert. coord. 4 v2 is not unique");
            if(tri_lab1->vertices()[2] != tri_lab2->vertices()[2])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: in the cell of vert. coord. 4 v3 is not unique");            
        }
        
        // vert. coord. 4 pat.
        else if(i < num40p){
            if(list0[i].dync_vertex()->coord_num > 4)
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: is not of coord. 4 but is listed like it is");
            
            if(spatial_profile[v_lab->time()] != 3)
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: is not pathological but is listed like it is");
            
            Label lab_t0 = move_42_find_t0(list0[i]);
            Label lab_t1 = lab_t0.dync_triangle()->adjacent_triangles()[2];
            Label lab_t2 = lab_t1.dync_triangle()->adjacent_triangles()[0];
            Label lab_t3 = lab_t0.dync_triangle()->adjacent_triangles()[0];
            Triangle* tri_lab0 = lab_t0.dync_triangle();
            Triangle* tri_lab1 = lab_t1.dync_triangle();
            Triangle* tri_lab2 = lab_t2.dync_triangle();
            Triangle* tri_lab3 = lab_t3.dync_triangle();
            
            Label lab_v0 = tri_lab0->vertices()[0];
            Label lab_v1 = tri_lab3->vertices()[1];
            Label lab_v2 = tri_lab0->vertices()[2];
            Label lab_v3 = tri_lab1->vertices()[2];
            Label lab_v4 = list0[i];
            Vertex* v_lab0 = lab_v0.dync_vertex();
            Vertex* v_lab1 = lab_v1.dync_vertex();
            Vertex* v_lab2 = lab_v2.dync_vertex();
            Vertex* v_lab3 = lab_v3.dync_vertex();
            Vertex* v_lab4 = lab_v4.dync_vertex();
            
            if(not (tri_lab0->type == TriangleType::_21))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 pat. identify a cell whose t0 ["+to_string(lab_t0->position())+"] is not of type (2,1)");
            if(not (tri_lab1->type == TriangleType::_12))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 pat. identify a cell whose t1 ["+to_string(lab_t1->position())+"] is not of type (1,2)");
            if(not (tri_lab2->type == TriangleType::_12))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 pat. identify a cell whose t2 ["+to_string(lab_t2->position())+"] is not of type (1,2)");
            if(not (tri_lab3->type == TriangleType::_21))
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 pat. identify a cell whose t3 ["+to_string(lab_t3->position())+"] is not of type (2,1)");
            
            // --- check central vertex (v4) coherency
            
            if(lab_v4 != tri_lab0->vertices()[1])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 pat. not coincident with the candidate from t0");
            if(lab_v4 != tri_lab1->vertices()[1])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 pat. not coincident with the candidate from t1");
            if(lab_v4 != tri_lab2->vertices()[0])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 pat. not coincident with the candidate from t2");
            if(lab_v4 != tri_lab3->vertices()[0])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: vert. coord. 4 pat. not coincident with the candidate from t3");
            
            // --- check other vertices coherence
            
            if(tri_lab0->vertices()[0] != tri_lab1->vertices()[0])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: in the cell of vert. coord. 4 pat. v0 is not unique");
            if(tri_lab2->vertices()[1] != tri_lab3->vertices()[1])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: in the cell of vert. coord. 4 pat. v1 is not unique");
            if(tri_lab0->vertices()[2] != tri_lab3->vertices()[2])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: in the cell of vert. coord. 4 pat. v2 is not unique");
            if(tri_lab1->vertices()[2] != tri_lab2->vertices()[2])
                throw runtime_error("Error in Vertex ["+to_string(i)+"]: in the cell of vert. coord. 4 pat. v3 is not unique");            
        }
        
        
    }
    
    // check list1: Edges
    for(int i=0; i < list1.size(); i++){
        Label lab = list1[i];
        Edge* e_lab = lab.dync_edge();
        GaugeElement U = e_lab->gauge_element();
        
        // id
        
        if(i != lab->id)
            throw runtime_error("Edge identifier wrong: Edge in position ["+to_string(i)+"] in list1, while its identifier points to ["+to_string(lab->id)+"]");
        
        // GaugeElement
        
        if(isnan(real(U.tr())) || isinf(real(U.tr())))
            throw runtime_error("Inf or Nan encountered in Edge ["+to_string(i)+"]");
        
        double threshold = 1e4;
        if(U.N == 1 && ( real(U.tr()) > threshold || imag(U.tr()) > threshold)){
            stringstream s;
            s << U.tr();
            throw runtime_error("Big Value encountered in Edge ["+to_string(i)+"], U = "+s.str());
        }
    }
    
    // check list2: Triangles
    
    for(int i=0; i < list2.size(); i++){
        Label lab = list2[i];
        Triangle* tri_lab = lab.dync_triangle();
        
        // id
        
        if(i != lab->id)
            throw runtime_error("Triangle identifier wrong: Triangle in position ["+to_string(i)+"] in list2, while its identifier points to ["+to_string(lab->id)+"]");
        
        // TriangleType
        
        if(not (tri_lab->type == TriangleType::_12 or tri_lab->type == TriangleType::_21))
            throw range_error("Error in Triangle ["+to_string(i)+"]: TriangleType not recognized");
        
        // vertices: check identities
        
        if((tri_lab->vertices()[0]->id > list0.size()) or (&*tri_lab->vertices()[0] != &*list0[tri_lab->vertices()[0]->id]))
            throw runtime_error("Error in Triangle ["+to_string(i)+"]: adjacent Vertex ["+to_string(tri_lab->vertices()[0]->id)+"], the right one [0], is not in list0 (list0.size = "+to_string(list0.size())+")");
        
        if((tri_lab->vertices()[1]->id > list0.size()) or (&*tri_lab->vertices()[1] != &*list0[tri_lab->vertices()[1]->id]))
            throw runtime_error("Error in Triangle ["+to_string(i)+"]: adjacent Vertex ["+to_string(tri_lab->vertices()[1]->id)+"], the left one [1], is not in list0 (list0.size = "+to_string(list0.size())+")");
        
        if((tri_lab->vertices()[2]->id > list0.size()) or (&*tri_lab->vertices()[2] != &*list0[tri_lab->vertices()[2]->id]))
            throw runtime_error("Error in Triangle ["+to_string(i)+"]: adjacent Vertex ["+to_string(tri_lab->vertices()[2]->id)+"], the \"lonely\" one [2], is not in list0 (list0.size = "+to_string(list0.size())+")");
        
        // edges: right vertices
        
        for(int j=0; j<3; j++){
            Edge e = *tri_lab->edges()[j].dync_edge();
            for(int k=0; k<2; k++){
                try{
                    tri_lab->find_element(e.v[k], SimplexType::_vertex);
                }
                catch(runtime_error){
                    throw runtime_error("Error in Triangle ["+to_string(i)+"]: Edge ["+to_string(e.position())+"] ("+to_string(j)+" in triangle) incosistent, missing its vertex "+to_string(k)+" (i.e. Vertex ["+to_string(e.v[k]->position())+"])");
                }
            }
        }
        
        // adjacent_triangles: check identities and "loops" (they share a couple of vertices)
        
        if((tri_lab->adjacent_triangles()[0]->id > list2.size()) or (&*tri_lab->adjacent_triangles()[0] != &*list2[tri_lab->adjacent_triangles()[0]->id]))
            throw runtime_error("Error in Triangle ["+to_string(i)+"]: adjacent Triangle ["+to_string(tri_lab->adjacent_triangles()[0]->id)+"], the right one [0], is not in list2 (list2.size = "+to_string(list2.size())+")");
        
        if((tri_lab->adjacent_triangles()[1]->id > list2.size()) or (&*tri_lab->adjacent_triangles()[1] != &*list2[tri_lab->adjacent_triangles()[1]->id]))
            throw runtime_error("Error in Triangle ["+to_string(i)+"]: adjacent Triangle ["+to_string(tri_lab->adjacent_triangles()[1]->id)+"], the left one [1], is not in list2 (list2.size = "+to_string(list2.size())+")");
        
        if((tri_lab->adjacent_triangles()[2]->id > list2.size()) or (&*tri_lab->adjacent_triangles()[2] != &*list2[tri_lab->adjacent_triangles()[2]->id]))
            throw runtime_error("Error in Triangle ["+to_string(i)+"]: adjacent Triangle ["+to_string(tri_lab->adjacent_triangles()[2]->id)+"], the \"time adjacent\" [2], is not in list2 (list2.size = "+to_string(list2.size())+")");
        
        if(tri_lab->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1]->position() != tri_lab->position())
            throw runtime_error("Error in Triangle: The _right_ adjacent of Triangle ["+to_string(i)+"] is Triangle ["+to_string(tri_lab->adjacent_triangles()[0].dync_triangle()->id)+"], but its _left_ adjacent is not ["+to_string(i)+"] itself");
        /**
         * @todo shared vertices
        bool find_shared_vertices(Triangle* tri_lab,Triangle* ->adjacent_triangles()[0].dync_triangle());
         *
        if(not find_shared_vertices(tri_lab,tri_lab->adjacent_triangles()[0].dync_triangle(),found))
            throw runtime_error("Error in Triangle ["+to_string(i)+"]: is adjacent with Triangle ["+to_string(i)+"] but they don't share two vertices");
        */
        
        if(tri_lab->adjacent_triangles()[1].dync_triangle()->adjacent_triangles()[0]->position() != tri_lab->position())
            throw runtime_error("Error in Triangle: The _left_ adjacent of Triangle ["+to_string(i)+"] is Triangle ["+to_string(tri_lab->adjacent_triangles()[1].dync_triangle()->id)+"], but its _right_ adjacent is not ["+to_string(i)+"] itself");
        
        if(tri_lab->adjacent_triangles()[2].dync_triangle()->adjacent_triangles()[2]->position() != tri_lab->position())
            throw runtime_error("Error in Triangle: The _time_ adjacent of Triangle ["+to_string(i)+"] is Triangle ["+to_string(tri_lab->adjacent_triangles()[2].dync_triangle()->id)+"], but its _time_ adjacent is not ["+to_string(i)+"] itself");
        
        for(int j=0; j<3; j++){
            Label lab_e0 = tri_lab->adjacent_triangles()[j].dync_triangle()->edges()[tri_lab->opposite(j)];
            Label lab_e1 = tri_lab->edges()[j];
            
            if(lab_e0 != lab_e1)
                throw runtime_error("Error in Triangle: The Edge ["+to_string(lab_e1->id)+"] ("+to_string(j)+") of Triangle ["+to_string(i)+"] is different from the corresponding one in Triangle ["+to_string(tri_lab->adjacent_triangles()[j]->id)+"], that is Edge ["+to_string(lab_e0->id)+"]");
        }
        
        // vertices 0 and 1 on the same t_slice, coherent with the TriangleType (vertex 2 on adjacent slice)
        
        
        if(tri_lab->vertices()[0].dync_vertex()->time() == tri_lab->vertices()[1].dync_vertex()->time()){
            int t_slice0 = tri_lab->vertices()[0].dync_vertex()->time();
            int t_slice2 = tri_lab->vertices()[2].dync_vertex()->time();
            if(tri_lab->is21()){
                if(t_slice2 != ((t_slice0 + 1) % spatial_profile.size()))
                    throw runtime_error("Error in Triangle ["+to_string(tri_lab->id)+"]: vertex 2 in wrong time slice");
            }
            else{
                if(t_slice0 == 0)
                    t_slice0 += spatial_profile.size();
                if(t_slice2 != (t_slice0-1))
                    throw runtime_error("Error in Triangle ["+to_string(tri_lab->id)+"]: vertex 2 in wrong time slice");
            }
        }
        else
            throw runtime_error("Error in Triangle["+to_string(i)+"]: vertices 0 and 1 of the triangle are not on the same time slice");
        
        // transition_id
        
        if(tri_lab->transition_id != -1){ // if is -1 and it's wrong it will be verified in transition lists checks
            if(tri_lab->is12()){
                if(transition2112[tri_lab->transition_id] != lab)
                    throw runtime_error("Error in Triangle ["+to_string(i)+"]: wrong transition_id");
            }
            else{
                if(transition1221[tri_lab->transition_id] != lab)
                    throw runtime_error("Error in Triangle ["+to_string(i)+"]: wrong transition_id");
            }
        }
    }
    
    // check space_profile
    
    /**
     * @todo devo trovare il modo di contare i vertici per fare il confronto
     */
    
    // check transitions
    
    /// @todo check transition cells
    
    for(int i=0; i < transition1221.size(); i++){
        Label lab = transition1221[i];
        Triangle* tri_lab = lab.dync_triangle();
        
        if(tri_lab->transition_id != i)
            throw runtime_error("Error in transition list: in transition1221 element ["+to_string(i)+"] has transition identifier"+to_string(tri_lab->transition_id));
        
        if(not tri_lab->is21())
            throw runtime_error("Error in transition list: in transition1221 right member Triangle ["+to_string(lab->id)+"] is not of type (2,1)");
        if(not tri_lab->adjacent_triangles()[1].dync_triangle()->is12())
            throw runtime_error("Error in transition list: in transition1221 left member Triangle ["+to_string(tri_lab->adjacent_triangles()[1]->id)+"] is not of type (1,2)");
    }
    for(int i=0; i < transition2112.size(); i++){
        Label lab = transition2112[i];
        Triangle* tri_lab = lab.dync_triangle();
        
        if(tri_lab->transition_id != i)
            throw runtime_error("Error in transition list: in transition2112 element ["+to_string(i)+"] has transition identifier"+to_string(tri_lab->transition_id));
        
        if(not tri_lab->is12())
            throw runtime_error("Error in transition list: in transition2112 right member Triangle ["+to_string(lab->id)+"] is not of type (1,2)");
        if(not tri_lab->adjacent_triangles()[1].dync_triangle()->is21())
            throw runtime_error("Error in transition list: in transition2112 left member Triangle ["+to_string(tri_lab->adjacent_triangles()[1]->id)+"] is not of type (1,2)");
    }
}

int Triangulation::count_adjacents(Vertex* v_lab){
    Triangle* initial_triangle = v_lab->near_t.dync_triangle();
    Triangle* current_triangle = initial_triangle;
    int adjacencies = 1;
    bool same_strip = true;
    
    while(same_strip){
        current_triangle = current_triangle->adjacent_triangles()[1].dync_triangle();
        if(not find_vertex_in_triangle(current_triangle,v_lab->id))
            same_strip = false;
        else
            adjacencies++;
    }
    same_strip = true;
    current_triangle = current_triangle->adjacent_triangles()[2].dync_triangle();
    adjacencies++;
    while(same_strip){
        current_triangle = current_triangle->adjacent_triangles()[0].dync_triangle();
        if(not find_vertex_in_triangle(current_triangle,v_lab->id))
            same_strip = false;
        else
            adjacencies++;
    }
    current_triangle = current_triangle->adjacent_triangles()[2].dync_triangle();
    adjacencies++;
    while(current_triangle->id != initial_triangle->id){
        current_triangle = current_triangle->adjacent_triangles()[1].dync_triangle();
        adjacencies++;
    }
    return adjacencies;
}

bool Triangulation::find_vertex_in_triangle(Triangle* adjacent_triangle, int v_id){
    if(v_id == adjacent_triangle->vertices()[0]->id){
        return true;
    }
    else if(v_id == adjacent_triangle->vertices()[1]->id){
        return true;
    }
    else if(v_id == adjacent_triangle->vertices()[2]->id){
        return true;
    }
    else{
        return false;
    }
}

ostream& operator<<(ostream& os, Triangulation& T){
    
    os << endl;
    os << "-------------" << endl;
    os << "TRIANGULATION" << endl;
    os << "-------------" << endl;
    
    os << "lambda: " << T.lambda << ", beta: " << T.beta << ", N: " << T.N << endl;
    os << "volume_step: " << T.volume_step << " steps_done: " << T.steps_done << " iterations_done: " << T.iterations_done << endl << endl;
    
    
    os << "num40: " << T.num40 << ", num40p: " << T.num40p << ", n_v: " << T.list0.size() << endl;
    os << "n_e: " << T.list1.size() << endl;
    os << "n_t: " << T.list2.size() << endl << endl;
    
    os << "timelength: " << T.spatial_profile.size() << endl;
    
    os << "space_profile: " << endl;
    T.print_space_profile(os);
    
//     os << endl << "  checking triangulation consistency... " << endl;
//     T.is_consistent(false);
//     os << "  triangulation is consistent!" << endl;
    
    return os;
}
