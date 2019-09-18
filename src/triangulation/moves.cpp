// ##### MOVES #####


/**
 * Questa sarà la mossa se is22_1 == true, altrimenti la figura e' flippata verticalmente
 * \code
 *     v0         v1            v0         v1 
 *      * * * * * *             * * * * * *  
 *      **        *             *        **  
 *      *  *   0  *             *  0   *  *  
 *    2 *    *    * 3   -->   2 *    *    * 3
 *      *  1   *  *             *  *   1  *  
 *      *        **             **        *  
 *      * * * * * *             * * * * * *  
 *     v3         v2            v3         v2 
 * \endcode
 */ 
vector<double> Triangulation::move_22(int cell, bool debug_flag)
{

    RandomGen r;
    bool is22_1 = r.next()<0.5;
    vector<Label> *transitionlist = (is22_1)? &transition1221 : &transition2112;
    vector<Label> *Atransitionlist = (!is22_1)? &transition1221 : &transition2112;

    long num_t = transitionlist->size(); 
    
    // if I don't consider this case separately transition would have an Undefined Behaviour
    if(num_t == 0){
        vector<double> v;
        v.push_back(0.123456789);
        return v; // if not rejected goes on, otherwise it returns with nothing done
    }
    
    
    // ___ cell recognition ___
    
    int tr;
    
    // to make testing easier it is possible to specify the "cell" on which operate
    // if it is not specified (cell = -1), as in real runs, the cell is extracted
    if(cell == -1){
        tr  = r.next() * num_t;
        assert(tr < num_t); // this shouldn't happen never
    }
    else{
        tr = cell;
    }
    
//     uniform_int_distribution<int> transition(0, num_t - 1);
//     uniform_real_distribution<double> reject_trial(0.0,1.0);
//     int tr = transition(mt);
//     static int tr = 3;
//     tr++;
    if(debug_flag){
        cout << "move_22:" << endl;
        cout << (*transitionlist)[tr]->position() << " " << (*transitionlist)[tr].dync_triangle()->vertices()[1]->position() << " ";
    }
    
    /**
     * @todo lab_t e lab_v sono un po' ridondanti, quindi per ora credo siano solo temporanei
     * - o sostituisco i tri_lab e uso sempre dync_triangle (stessa cosa per i vertex)
     * - o non uso i lab_t e al loro posto metto sempre list2[tri_lab->position()]
     */ 
    // ___ find triangles (they are needed to compute the reject ratio) ___
    Label lab_t0 = (*transitionlist)[tr];
    Label lab_t1 = lab_t0.dync_triangle()->adjacent_triangles()[1];
    Label lab_t2 = lab_t1.dync_triangle()->adjacent_triangles()[1];
    Label lab_t3 = lab_t0.dync_triangle()->adjacent_triangles()[0];
    Triangle* tri_lab0 = lab_t0.dync_triangle();
    Triangle* tri_lab1 = lab_t1.dync_triangle();
    Triangle* tri_lab2 = lab_t2.dync_triangle();
    Triangle* tri_lab3 = lab_t3.dync_triangle();
    
    if(debug_flag){
        cout << tri_lab1->vertices()[0]->position() << endl;
    }
    
    // ----- REJECT RATIO -----
    
    // ___ find vertices ___
    /* it's anticipated, because vertices are needed in order to compute the gauge action variation
     */ 
    Label lab_v0 = tri_lab0->vertices()[0];
    Label lab_v1 = tri_lab0->vertices()[1];
    Label lab_v2 = tri_lab1->vertices()[1];
    Label lab_v3 = tri_lab1->vertices()[0];
    Vertex* v_lab0 = lab_v0.dync_vertex();
    Vertex* v_lab1 = lab_v1.dync_vertex();
    Vertex* v_lab2 = lab_v2.dync_vertex();
    Vertex* v_lab3 = lab_v3.dync_vertex();
    
    if(debug_flag){
        cout << endl;
        cout << "╔═══════════════════════╗" << endl;
        cout << "║BEGINNING OF move_22:  ║" << endl;
        cout << "╚═══════════════════════╝" << endl;
        cout << " (time " << v_lab0->time() << ")" << endl;
        cout << " [cell] (vertices) \t\t\tv0: " << lab_v0->id << ", v1: " << lab_v1->id << ", v2: " << lab_v2->id << ", v3: " << lab_v3->id  << endl;
        cout << "        (coordinations) \tv0: " << v_lab0->coord_num << ", v1: " << v_lab1->coord_num << ", v2: " << v_lab2->coord_num << ", v3: " << v_lab3->coord_num  << endl;
        cout << " (list0.size = "+to_string(list0.size())+", num40 = "+to_string(num40)+", num40p = "+to_string(num40p)+")" << endl;
    }
    
    int x = 1;
    if(is22_1 == tri_lab2->is21())
        x--;
    if(is22_1 == tri_lab3->is12())
        x--;
    
    double beta_N = beta * N;
    double delta_Sg = 0;
    delta_Sg -= ( v_lab0->Pi_tilde(debug_flag) / ((v_lab0->coordination() - 1)*v_lab0->coordination()) ) * beta_N;
    delta_Sg -= ( v_lab2->Pi_tilde(debug_flag) / ((v_lab2->coordination() - 1)*v_lab2->coordination()) ) * beta_N;
    delta_Sg += ( v_lab1->Pi_tilde(debug_flag) / ((v_lab1->coordination() + 1)*v_lab1->coordination()) ) * beta_N;
    delta_Sg += ( v_lab3->Pi_tilde(debug_flag) / ((v_lab3->coordination() + 1)*v_lab3->coordination()) ) * beta_N;
    
    double reject_trial = r.next();
    double acceptance = exp(-delta_Sg) * static_cast<double>(num_t)/(num_t + x);
    double reject_ratio = min(1.0, acceptance);
    
    // 1/num_t : prob selection direct move
    // 1/(num_t + x) : prob selection inverse move
    
    if(reject_trial > reject_ratio){
        vector<double> v;
        v.push_back(acceptance);
        v.push_back(delta_Sg);
        
        return v; // if not rejected goes on, otherwise it returns with nothing done
    }
    
    // ----- CELL "EVOLUTION" -----
    
    // ___ find edges ___
    Label lab_e0 = tri_lab1->edges()[0]; //           3    
    Label lab_e1 = tri_lab1->edges()[1]; //      * * * * * *  
    Label lab_e2 = tri_lab0->edges()[0]; //      *        **  
    Label lab_e3 = tri_lab1->edges()[2]; //      *  0   *  *  
    Label lab_e4 = tri_lab0->edges()[2]; //    1 *    *    * 2
    Edge* e_lab0 = lab_e0.dync_edge();   //      *  *      *  
    Edge* e_lab1 = lab_e1.dync_edge();   //      **        *  
    Edge* e_lab2 = lab_e2.dync_edge();   //      * * * * * *  
    Edge* e_lab3 = lab_e3.dync_edge();   //           4    
    Edge* e_lab4 = lab_e4.dync_edge();   
    
    // ___ gauge transform on t0 in order to put e0 = 1 ___
    // I'm gauge transforming on the right triangle, so e0 is its left edge
    // and left edges (e[1]) are multiplied by G.dagger() in gauge_transform
    
    if(r.next() < 0.5){
        tri_lab0->gauge_transform(e_lab0->gauge_element(), debug_flag);
    }
    else{
        tri_lab1->gauge_transform(e_lab0->gauge_element().dagger(), debug_flag);
    }
    
    if(debug_flag){
        GaugeElement Id(1.);
        GaugeElement Zero = e_lab0->gauge_element() - Id;
        
        if(Zero.norm() > 1e-10)
            throw runtime_error("move 22: e_lab0 element is not Id after gauge_transform.");
        else
            cout << endl << "move 22: gauge_transform check passed!" << endl << endl;
    }
        
    // ___ modify triangles' adjacencies ___
    tri_lab0->adjacent_triangles()[0] = lab_t1;
    tri_lab0->adjacent_triangles()[1] = lab_t2;
    tri_lab1->adjacent_triangles()[0] = lab_t3;
    tri_lab1->adjacent_triangles()[1] = lab_t0;
    tri_lab2->adjacent_triangles()[0] = lab_t0;
    tri_lab3->adjacent_triangles()[1] = lab_t1;
    
    // ___ modify triangles' vertices ___
    tri_lab0->vertices()[2] = lab_v3;
    tri_lab1->vertices()[2] = lab_v1;
    
    // ___ modify triangles' edges ___
    tri_lab1->edges()[0] = lab_e2;
    tri_lab1->edges()[1] = lab_e0;
    tri_lab0->edges()[0] = lab_e0;
    tri_lab0->edges()[1] = lab_e1;
    
    // ___ modify edges' near_t ___
    e_lab1->near_t = lab_t0;
    e_lab2->near_t = lab_t1;
    
    // ___ modify edges' vertices ___
    e_lab0->vertices()[0] = lab_v1;
    e_lab0->vertices()[1] = lab_v3;
    
    // ___ modify vertices' near_t ___
    /** @todo pensare se c'è un modo più furbo di fare le assegnazioni */
    v_lab0->near_t = lab_t0;
    v_lab2->near_t = lab_t1;
    
    // ___ modify vertices' coord_num ___
    v_lab0->coord_num--;
    v_lab2->coord_num--;
    v_lab1->coord_num++;
    v_lab3->coord_num++;
    
    // ----- AUXILIARY STRUCTURES -----
    
    // ___ modify transitions list ___
    
    if(is22_1 == tri_lab2->is21()){
        /** @todo uno potrrebbe anche pensare di impacchettare queste modifiche delle transition list in dei metodi separati in modo da avere più garanzie sul fatto che gli invarianti siano rispettati */
        if(tri_lab0->transition_id != (int)transitionlist->size() - 1){
            Label lab_end = (*transitionlist)[transitionlist->size() - 1];
            
            lab_end.dync_triangle()->transition_id = tri_lab0->transition_id;
            (*transitionlist)[tri_lab0->transition_id] = lab_end;
        }
        transitionlist->pop_back();
        tri_lab0->transition_id = -1;
    }
    else{
        /* we have to do this only in the case in which t2 is of the type such that a transition between t2 and t1 was not allowed before, indeed otherwise t1 was already a transition-cell right-member, but the transition  doesn't store the value of the left-member, so is not relevant that is changed: t1 was a transition right-member and still is */
        tri_lab1->transition_id = Atransitionlist->size();
        Atransitionlist->push_back(lab_t1);
    }
    if(is22_1 == tri_lab3->is12()){
        if(tri_lab3->transition_id != (int)Atransitionlist->size() - 1){
            Label lab_end = (*Atransitionlist)[Atransitionlist->size() - 1];
            
            lab_end.dync_triangle()->transition_id = tri_lab3->transition_id;
            (*Atransitionlist)[tri_lab3->transition_id] = lab_end;
        }
        Atransitionlist->pop_back();
        tri_lab3->transition_id = -1;
    }
    else{
        tri_lab3->transition_id = transitionlist->size();
        transitionlist->push_back(lab_t3);
    }
    
    /** @todo ripensare a questo errore */
    if(debug_flag){
        if(transitionlist->size() != Atransitionlist->size()){
            cout << "transitionlist: " << transitionlist->size() << " Atransition: " << Atransitionlist->size();
            cout.flush();
            throw runtime_error("Not the same number of transitions of the two types");
        }
    }
    
    // ___ find vert. coord. 4 and patologies ___
    
    /* vertex 0,2 were not of coord. 4, and they could have become
     * vertex 1,3 could be of coord. 4, and now they are not
     */ 
    
    vector<Vertex*> vec;
    vec.push_back(v_lab0);
    vec.push_back(v_lab2);
    
    for(auto x : vec){
        if(x->coordination() == 4){
            Label lab = list0[x->position()];
            
            list0[x->position()] = list0[num40 + num40p];
            list0[x->position()]->id = x->position();
            list0[num40 + num40p] = lab;
            list0[num40 + num40p]->id = num40 + num40p;
            
            if(spatial_profile[x->time()] == 3){
                num40p++;
            }
            else{                
                list0[x->position()] = list0[num40];
                list0[x->position()]->id = x->position();
                list0[num40] = lab;
                list0[num40]->id = num40;
                
                num40++;
            }
        }        
    }
    
    vec.clear();
    vec.push_back(v_lab1);
    vec.push_back(v_lab3);
    
    for(auto x : vec){
        if(x->coordination() == 5){
            Label lab = list0[x->position()];

            if(spatial_profile[x->time()] == 3){
                num40p--;
            }
            else{
                num40--;
                
                list0[x->position()] = list0[num40];
                list0[x->position()]->id = x->position();
                list0[num40] = lab;
                list0[num40]->id = num40;
            }
            list0[x->position()] = list0[num40 + num40p];
            list0[x->position()]->id = x->position();
            list0[num40 + num40p] = lab;
            list0[num40 + num40p]->id = num40 + num40p;
        }        
    }
    
    GaugeElement U;
    if(r.next() < 0.5){
        tri_lab0->gauge_transform(U.rand(), debug_flag);
    }
    else{
        tri_lab1->gauge_transform(U.rand(), debug_flag);
    }
    
    if(debug_flag){
        cout << endl;
        cout << "┌────────────────────────┐" << endl;
        cout << "│AT THE END OF move_22:  │ " << endl;
        cout << "└────────────────────────┘" << endl;
        cout << " [cell] (vertices) \t\t\tv0: " << lab_v0->id << ", v1: " << lab_v1->id << ", v2: " << lab_v2->id << ", v3: " << lab_v3->id  << endl;
        cout << "        (coordinations) \tv0: " << v_lab0->coord_num << ", v1: " << v_lab1->coord_num << ", v2: " << v_lab2->coord_num << ", v3: " << v_lab3->coord_num  << endl;
        cout << " (list0.size = "+to_string(list0.size())+", num40 = "+to_string(num40)+", num40p = "+to_string(num40p)+")" << endl;
    }
    
    vector<double> v;
    v.push_back(acceptance);
    v.push_back(delta_Sg);
    
    return v;
    // ----- END MOVE -----
}



/**
 * Questa sarà la mossa
 * \code
 *            v2                            v2
 *             *                             *       
 *            * *                          * * *      
 *        5  *   *  4                5   *   *   *   4
 *          *  0  *                    *  0  *  3  *  
 *         *       *                 *       *       *
 *     v0 * * * * * * v1   -->   v0 * * * * v4* * * * * * v1
 *         *       *                 *       *       *
 *          *  1  *                    *  1  *  2  *    
 *        6  *   *  7                6   *   *   *   7   
 *            * *                          * * *      
 *             *                             *       
 *            v3                            v3
 * \endcode
 * 
 * @todo check if there is something more to be done by the move_24
 * @test check if it works
 */
void Triangulation::move_24(int cell, bool debug_flag)
{
    if(debug_flag){
        cout << "move_24: " << endl;
    }
    
    // the number of points is equal to the number of space-links (space volume) that is equal to the number of triangles (spacetime volume)
    long volume = list2.size(); 
    
    // I don't have to consider separately the case of volume = 0, because the minimal volume is > 0
    
//     random_device rd;
//     mt19937_64 mt(rd());
//     uniform_int_distribution<int> extracted_triangle(0, volume - 1);
//     uniform_real_distribution<double> reject_trial(0.0,1.0);
    
    RandomGen r;
    
    // ___ cell recognition ___
    
    int extr;
    
    // to make testing easier it is possible to specify the "cell" on which operate
    // if it is not specified (cell = -1), as in real runs, the cell is extracted
    if(cell == -1){
        extr  = r.next() * volume;
        if(extr == volume) // this shouldn't happen never
            extr = volume - 1;
        //     int extr = extracted_triangle(mt);
        //     int extr = ;
    }
    else{
        extr = cell;
    }
    
    // ----- REJECT RATIO -----
    
    // ___ cell recognition ___
    
    Label lab_t0 = move_24_find_t0(list2[extr]);
    Label lab_t1 = lab_t0.dync_triangle()->adjacent_triangles()[2];
    Triangle* tri_lab0 = lab_t0.dync_triangle();
    Triangle* tri_lab1 = lab_t1.dync_triangle();
    
    Label lab_v0 = tri_lab0->vertices()[0];
    Label lab_v1 = tri_lab0->vertices()[1];
    Label lab_v2 = tri_lab0->vertices()[2];
    Label lab_v3 = tri_lab1->vertices()[2];
    Vertex* v_lab0 = lab_v0.dync_vertex();
    Vertex* v_lab1 = lab_v1.dync_vertex();
    Vertex* v_lab2 = lab_v2.dync_vertex();
    Vertex* v_lab3 = lab_v3.dync_vertex();
    
    Label lab_e0 = tri_lab0->edges()[2]; //         *        
    Label lab_e1 = tri_lab0->edges()[1]; //        * *       
    Label lab_e2 = tri_lab0->edges()[0]; //    1  *   *  2
    Label lab_e3 = tri_lab1->edges()[1]; //      *     *     
    Label lab_e4 = tri_lab1->edges()[0]; //     *       *    
    Edge* e_lab0 = lab_e0.dync_edge();   //    * * * * * * 
    Edge* e_lab1 = lab_e1.dync_edge();   //     *   0   *    
    Edge* e_lab2 = lab_e2.dync_edge();   //      *     *     
    Edge* e_lab3 = lab_e3.dync_edge();   //    3  *   *  4
    Edge* e_lab4 = lab_e4.dync_edge();   //        * *       
                                         //         *        
    
    
    // Gauge transforming on the upper triangle with G the gauge element on e0 will be transform with G.dagger()
    GaugeElement gt0(e_lab0->gauge_element());
    tri_lab0->gauge_transform(gt0, debug_flag);
    
    if(debug_flag){
        GaugeElement Id(1.);
        GaugeElement Zero = e_lab0->gauge_element() - Id;
        
        if(Zero.norm() > 1e-10)
            throw runtime_error("move 24: e_lab0 element is not Id after gauge_transform.");
        else
            cout << endl << "move 24: gauge_transform check passed!" << endl << endl;
    }


    double beta_N = beta * N;
    double delta_Sg_hat = 0;
    delta_Sg_hat += (v_lab1->Pi_tilde(debug_flag) / v_lab1->coordination()) * beta_N;
    delta_Sg_hat += (v_lab2->Pi_tilde(debug_flag) / ((v_lab2->coordination() + 1) * v_lab2->coordination()) ) * beta_N;
    delta_Sg_hat += (v_lab3->Pi_tilde(debug_flag) / ((v_lab3->coordination() + 1) * v_lab3->coordination()) ) * beta_N;
    delta_Sg_hat += beta_N * (1./4+1./v_lab1->coordination());
    
    // the conventional direction for GaugeElement on Edges is from down to up (and from left to right)
    Triangle *edge0_t[2] = {tri_lab1, tri_lab0};
    GaugeElement Staple = v_lab1->looparound(edge0_t, debug_flag);
    GaugeElement Force = (Staple/v_lab1->coordination() + 1./4.);
    
    double reject_trial = r.next();
    double reject_ratio = min(1.0, exp(-2*lambda - delta_Sg_hat) * Force.partition_function() * (static_cast<double>(volume) / (2*(num40+1)) ));
    
    
    if(reject_trial > reject_ratio){
        tri_lab0->gauge_transform(gt0.dagger());
        if(debug_flag){
            cout << endl;
        }
        return; // if not rejected goes on, otherwise it returns with nothing done
    }
    
    // ----- CELL "EVOLUTION" -----
    
    if(debug_flag){                                     
        cout << " (time " << v_lab0->time() << ")" << endl;
    }
    
    // ___ create new Triangles and vertex, and put already in them the right values ___
    Label lab_v4 = create_vertex(v_lab0->time(),4,lab_t0);
    Vertex* v_lab4 = lab_v4.dync_vertex();
    
    Label t2_adjancencies[3];
    Label t3_adjancencies[3];
    Label t2_edges[3];
    Label t3_edges[3];
    Label t2_vertices[3];
    Label t3_vertices[3];
    t2_adjancencies[0] = tri_lab1->adjacent_triangles()[0];
    t2_adjancencies[1] = lab_t1;
    t2_adjancencies[2] = lab_t0;    // actually wrong, is lab_t3, but is still to be created
    for(int i=0; i<3; i++)
        t2_edges[i] = lab_e0;       // actually wrong, but some edges are still to be created
    t2_vertices[0] = lab_v4;
    t2_vertices[1] = lab_v1;
    t2_vertices[2] = lab_v3;
    t3_adjancencies[0] = tri_lab0->adjacent_triangles()[0];
    t3_adjancencies[1] = lab_t0;
    t3_adjancencies[2] = lab_t1;    // actually wrong, is lab_t3, but is still to be created
    for(int i=0; i<3; i++)
        t3_edges[i] = lab_e0;       // actually wrong, but some edges are still to be created
    t3_vertices[0] = lab_v4;
    t3_vertices[1] = lab_v1;
    t3_vertices[2] = lab_v2;
    
    Label lab_t2 = create_triangle(t2_vertices, t2_edges, t2_adjancencies,TriangleType::_12);
    Label lab_t3 = create_triangle(t3_vertices, t3_edges, t3_adjancencies,TriangleType::_21);
    Triangle* tri_lab2 = lab_t2.dync_triangle();
    Triangle* tri_lab3 = lab_t3.dync_triangle();
    tri_lab2->adjacent_triangles()[2] = lab_t3;
    tri_lab3->adjacent_triangles()[2] = lab_t2;
    
    // ___ create new edges ___
    
    Label e5_vertices[2];                                              //           *          
    Label e6_vertices[2];                                              //         * * *        
    Label e7_vertices[2];                                              //   1   *   *   *   2  
    e5_vertices[0] = lab_v3;                                           //     *     *7    *    
    e5_vertices[1] = lab_v4;                                           //   *   0   *       *  
    e6_vertices[0] = lab_v4;                                           //  * * * * * * * * * * 
    e6_vertices[1] = lab_v1;                                           //   *       *   6   *  
    e7_vertices[0] = lab_v4;                                           //     *    5*     *    
    e7_vertices[1] = lab_v2;                                           //   3   *   *   *   4  
    Label lab_e5 = create_edge(e5_vertices, lab_t1, EdgeType::_time);  //         * * *        
    Label lab_e6 = create_edge(e6_vertices, lab_t2, EdgeType::_space); //           *          
    Label lab_e7 = create_edge(e7_vertices, lab_t3, EdgeType::_time);              
    Edge* e_lab5 = lab_e5.dync_edge();                        
    Edge* e_lab6 = lab_e6.dync_edge();                        
    Edge* e_lab7 = lab_e7.dync_edge();
    
    if(debug_flag){
        cout << endl;
        cout << "╔═════════════════════╗" << endl;
        cout << "║BEGINNING OF move_24:║" << endl;
        cout << "╚═════════════════════╝" << endl;
        cout << " [cell] (triangles) t0: " << lab_t0->id << ", t1: " << lab_t1->id << ", t2: " << lab_t2->id << ", t3: " << lab_t3->id <<  "\t(vertices) v0: " << lab_v0->id << ", v1: " << lab_v1->id << ", v2: " << lab_v2->id << ", v3: " << lab_v3->id << ", v4: " << lab_v4->id << endl;
        cout << " \t[adjacent triangles] v0: " << v_lab0->adjacent_triangle()->id << ", v1: " << v_lab1->adjacent_triangle()->id << ", v2: " << v_lab2->adjacent_triangle()->id << ", v3: " << v_lab3->adjacent_triangle()->id << ", v4: " << v_lab4->adjacent_triangle()->id << endl;
        cout << "        (coordinations) \tv0: " << v_lab0->coord_num << ", v1: " << v_lab1->coord_num << ", v2: " << v_lab2->coord_num << ", v3: " << v_lab3->coord_num << ", v4: " << v_lab4->coord_num << endl;
    }
    
    // ___ update adjancencies and vertices of the initial triangles ___
    tri_lab0->adjacent_triangles()[0] = lab_t3;
    tri_lab1->adjacent_triangles()[0] = lab_t2;
    tri_lab3->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] = lab_t3;
    tri_lab2->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] = lab_t2;
    
    tri_lab0->vertices()[1] = lab_v4;
    tri_lab1->vertices()[1] = lab_v4;
    
    // ___ modify triangles' edges ___
    tri_lab0->edges()[0] = lab_e7;
    tri_lab1->edges()[0] = lab_e5;
    tri_lab2->edges()[0] = lab_e4;
    tri_lab2->edges()[1] = lab_e5;
    tri_lab2->edges()[2] = lab_e6;
    tri_lab3->edges()[0] = lab_e2;
    tri_lab3->edges()[1] = lab_e7;
    tri_lab3->edges()[2] = lab_e6;
    
    // ___ modify edges' near_t ___
    e_lab2->near_t = lab_t3;
    e_lab4->near_t = lab_t2;
    
    // ___ modify edges' vertices ___
    e_lab0->vertices()[1] = lab_v4;
    
    // ___ update already existing vertex properties ___
    // coordination number
    v_lab2->coord_num++;
    v_lab3->coord_num++;

    // the adjacency of vertex 1
    /* (the other ones have still the same adjacencies of before, plus the new triangles, but not less) */
    v_lab1->near_t = lab_t3;
    
    // ___ update list0 (pathologies) ___
    
    if(spatial_profile[v_lab4->time()] == 4){ // 4 because the update of spatial_profile is directly in create_vertex
        /* vert. coord. 4 in the time slice of v4 previously pathological no longer are */
        if(v_lab0->coordination() == 4){
            list0[v_lab0->position()] = list0[num40];
            list0[v_lab0->position()]->id = v_lab0->position();
            list0[num40] = lab_v0;
            list0[num40]->id = num40;
            num40++;
            num40p--;
        }
        if(v_lab1->coordination() == 4){
            list0[v_lab1->position()] = list0[num40];
            list0[v_lab1->position()]->id = v_lab1->position();
            list0[num40] = lab_v1;
            list0[num40]->id = num40;
            num40++;
            num40p--;
        }
        
        // then find the third vertex
        /* the third, respect to vertex 1 and  0, already in the time slice of vertex 4 */
        Label current_triangle = tri_lab3->adjacent_triangles()[0];
        while(current_triangle.dync_triangle()->is12()){
            current_triangle = current_triangle.dync_triangle()->adjacent_triangles()[0];
        }
        Label third_vertex = current_triangle.dync_triangle()->vertices()[1]; 
        if(third_vertex.dync_vertex()->coordination() == 4){
            list0[third_vertex->position()] = list0[num40];
            list0[third_vertex->position()]->id = third_vertex->position();
            list0[num40] = third_vertex;
            list0[num40]->id = num40;
            num40++;
            num40p--;
        }    
    }
    // vertex 2 and 3 couldn't be of coord. 4 before, because they have more than one time link toward the same time slice
    
    if(debug_flag){
        cout << endl;
        cout << "┌──────────────────────┐" << endl;
        cout << "│AT THE END OF move_24:│ " << endl;
        cout << "└──────────────────────┘" << endl;;
        cout << " [cell] (triangles) t0: " << lab_t0->id << ", t1: " << lab_t1->id << ", t2: " << lab_t2->id << ", t3: " << lab_t3->id <<  "\t(vertices) v0: " << lab_v0->id << ", v1: " << lab_v1->id << ", v2: " << lab_v2->id << ", v3: " << lab_v3->id << ", v4: " << lab_v4->id << endl;
        cout << " \t[adjacent triangles] v0: " << v_lab0->adjacent_triangle()->id << ", v1: " << v_lab1->adjacent_triangle()->id << ", v2: " << v_lab2->adjacent_triangle()->id << ", v3: " << v_lab3->adjacent_triangle()->id << ", v4: " << v_lab4->adjacent_triangle()->id << endl;
        cout << "        (coordinations) \tv0: " << v_lab0->coord_num << ", v1: " << v_lab1->coord_num << ", v2: " << v_lab2->coord_num << ", v3: " << v_lab3->coord_num << ", v4: " << v_lab4->coord_num << endl;
        cout << " (list0.size = "+to_string(list0.size())+", num40 = "+to_string(num40)+", num40p = "+to_string(num40p)+")" << endl;
    }
    // ___ extraction of GaugeElement on link 6 ___
    e_lab6->U.heatbath(Force, debug_flag);
    /* the other links don't need to be extracted:
     *  - the old one (0-4) have already the correct values
     *  - the new one (5,7) are set to id by default (by create_edge function), and is correct 
     * 
     * Moreover is needed to do this at the end of the cell manipulation because
     * in order to calculate the heatbath is necessary to ensure that
     * the triangulation is in a consistent state
     */
    
    // ----- END MOVE -----
    
    /* notice that transition list has not to be updated (no need because of the choices made in move construction, in particular because of triangles are inserted on the right, and transitions are represented by right members of the cell) */
}

/**
 * Questa sarà la mossa
 * \code
 *              v2                              v2        
 *               *                               *        
 *             * * *                            * *       
 *       5   *   *   *   4                  5  *   *  4   
 *         *  0  *  3  *                      *  0  *     
 *       *       *       *                   *       *    
 *   v0 * * * * v4* * * * * v1    -->    v0 * * * * * * v1
 *       *       *       *                   *       *    
 *         *  1  *  2  *                      *  1  *     
 *       6   *   *   *   7                  6  *   *  7   
 *             * * *                            * *       
 *               *                               *        
 *              v3                              v3        
 * \endcode
 */
void Triangulation::move_42(int cell, bool debug_flag)
{
    // the number of points is equal to the number of space-links (space volume) that is equal to the number of triangles (spacetime volume)
    
    // also toward states with num40 = num40p = 0 there are non-null probabilities to go in, so if I exclude the trial of this move(_42) for these states the other moves will have probabilities of 1/3 instead of 1/4, and detailed balance would be ruined
    
    if(debug_flag){
        cout << "move_42: " << endl;
    }
    
    if((num40 == 0) && (num40p == 0)){
        if(debug_flag){
            cout << "no legal move_42 available" << endl;
        }
        return;
    }
    
    RandomGen r;
    
    // ___ cell extraction ___
    int extr;
    
    // to make testing easier it is possible to specify the "cell" on which operate
    // if it is not specified (cell = -1), as in real runs, the cell is extracted
    if(cell == -1){
        extr = r.next() * (num40 + num40p);
        if(extr == (num40 + num40p)) // this shouldn't happen never
            extr = (num40 + num40p) - 1;
    }
    else{
        extr = cell;
    }
    
    if(extr > num40 - 1)
        return;
    
    if(debug_flag){
        cout << extr;
    }
    
    // ___ cell recognition ___
    
    Label lab_t0 = move_42_find_t0(list0[extr]);
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
    Label lab_v4 = list0[extr];
    Vertex* v_lab0 = lab_v0.dync_vertex();
    Vertex* v_lab1 = lab_v1.dync_vertex();
    Vertex* v_lab2 = lab_v2.dync_vertex();
    Vertex* v_lab3 = lab_v3.dync_vertex();
    Vertex* v_lab4 = lab_v4.dync_vertex();
    
        
    Label lab_e0 = tri_lab0->edges()[2];  //            *             
    Label lab_e1 = tri_lab1->edges()[0];  //          * * *           
    Label lab_e2 = tri_lab2->edges()[2];  //    5   *   *   *   4  
    Label lab_e3 = tri_lab0->edges()[0];  //      *     *3    *       
    Label lab_e4 = tri_lab3->edges()[0];  //    *   0   *       *     
    Label lab_e5 = tri_lab0->edges()[1];  //   * * * * * * * * * *  
    Label lab_e6 = tri_lab1->edges()[1];  //    *       *   2   *     
    Label lab_e7 = tri_lab2->edges()[0];  //      *    1*     *       
    Edge* e_lab0 = lab_e0.dync_edge();    //    6   *   *   *   7  
    Edge* e_lab1 = lab_e1.dync_edge();    //          * * *           
    Edge* e_lab2 = lab_e2.dync_edge();    //            *             
    Edge* e_lab3 = lab_e3.dync_edge();
    Edge* e_lab4 = lab_e4.dync_edge();
    Edge* e_lab5 = lab_e5.dync_edge();
    Edge* e_lab6 = lab_e6.dync_edge();
    Edge* e_lab7 = lab_e7.dync_edge();
    
    /// @todo
    if(debug_flag){
        cout << endl;
        cout << "╔═════════════════════╗" << endl;
        cout << "║BEGINNING OF move_42:║" << endl;
        cout << "╚═════════════════════╝" << endl;
        cout << " (time " << v_lab0->time() << ")" << endl;
        cout << " [cell] (triangles) t0: " << lab_t0->id << ", t1: " << lab_t1->id << ", t2: " << lab_t2->id << ", t3: " << lab_t3->id <<  "\t(vertices) \tv0: " << lab_v0->id << ", v1: " << lab_v1->id << ", v2: " << lab_v2->id << ", v3: " << lab_v3->id << ", v4: " << lab_v4->id << endl;
        cout << " \t\t\t\t\t\t\t\t\t\t\t   (coordinations)  v0: " << v_lab0->coord_num << ", v1: " << v_lab1->coord_num << ", v2: " << v_lab2->coord_num << ", v3: " << v_lab3->coord_num << ", v4: " << v_lab4->coord_num << endl;
        cout << " [vertices' times] v0: " << v_lab0->time() << ", v1: " << v_lab1->time() << ", v4: " << v_lab4->time() << " \t\t[pretending v4] t0:" << tri_lab0->vertices()[1]->position() << " t1:" << tri_lab1->vertices()[1]->position() << " t2:" << tri_lab2->vertices()[0]->position() << " t3:" << tri_lab3->vertices()[0]->position() << endl;
        cout << " \t\t\t[adjacent triangles] v0: " << v_lab0->adjacent_triangle()->id << ", v1: " << v_lab1->adjacent_triangle()->id << ", v2: " << v_lab2->adjacent_triangle()->id << ", v3: " << v_lab3->adjacent_triangle()->id << ", v4: " << v_lab4->adjacent_triangle()->id << endl;
        cout << " [space volumes] " << spatial_profile[v_lab3->t_slice] << ", " << spatial_profile[v_lab0->t_slice] << ", " << spatial_profile[v_lab2->t_slice] << endl;
    }    
    
    // Gauge transforming on: 
    //  - the left triangle with G.dagger(), G the gauge element on e1
    //  - the upper triangle with G, the gauge element on e0
    //  - the right triangle with G, the gauge element on e3
    // this element (G) will be transform with G.dagger()
    GaugeElement gt1(e_lab1->gauge_element().dagger());
    tri_lab1->gauge_transform(gt1, debug_flag);
    GaugeElement gt0(e_lab0->gauge_element());
    tri_lab0->gauge_transform(gt0, debug_flag);
    GaugeElement gt3(e_lab3->gauge_element());
    tri_lab3->gauge_transform(gt3, debug_flag);
    
    
    if(debug_flag){
        GaugeElement Id(1.);
        GaugeElement Zero1 = e_lab1->gauge_element() - Id;
        GaugeElement Zero0 = e_lab0->gauge_element() - Id;
        GaugeElement Zero3 = e_lab3->gauge_element() - Id;
        
        if(Zero1.norm() > 1e-10)
            throw runtime_error("move 42: e_lab1 element is not Id after gauge_transform.");
        else if(Zero0.norm() > 1e-10)
            throw runtime_error("move 42: e_lab0 element is not Id after gauge_transform.");
        else if(Zero3.norm() > 1e-10)
            throw runtime_error("move 42: e_lab3 element is not Id after gauge_transform.");
        else
            cout << endl << "move 42: gauge_transform check passed!" << endl << endl;
    }
    
    // the conventional direction for GaugeElement on Edges is from down to up (and from left to right)
    Triangle *edge2_t[2] = {tri_lab2, tri_lab3};
//    Triangle *edge0_t[2] = {tri_lab1, tri_lab0};
    // the staple here it's searching for is the one of the cell with 2 triangles
    // to reconstruct it is needed to sum together the two contributes from the external staple of e0 and e2
    // FALSE --> substracting the contributes of the inner loop (the square)
    GaugeElement Staple = v_lab1->looparound(edge2_t,debug_flag);
    GaugeElement Force = (Staple/v_lab1->coordination() + 1./4.); // the coordination of v1 is unchanged
    
    double beta_N = beta * N;
    double delta_Sg_hat = 0;
    delta_Sg_hat -= (v_lab2->Pi_tilde(debug_flag) / ((v_lab2->coordination() - 1) * v_lab2->coordination()) ) * beta_N;
    delta_Sg_hat -= (v_lab3->Pi_tilde(debug_flag) / ((v_lab3->coordination() - 1) * v_lab3->coordination()) ) * beta_N;
    delta_Sg_hat -= (real(Staple.tr())/(Staple.N * v_lab1->coord_num)) * beta_N;
    delta_Sg_hat -= beta_N * (1./4);
    // the coordinations have to be adjusted to match the move_24, while the plaquettes remain the same
    // (because the "new" edges have id as gauge_element)
    
    //double reject_ratio = min(1.0, exp(-2*lambda - delta_Sg_hat) * Force.partition_function() * (volume / (2*(num40+1)) ));
        
//     random_device rd;
//     mt19937_64 mt(rd());
//     uniform_int_distribution<int> extracted_vertex(0, num40 + num40p - 1);
//     uniform_real_distribution<double> reject_trial(0.0,1.0);
    
    // ----- REJECT RATIO -----
    int volume = list2.size();
    double reject_trial = r.next();
    double reject_ratio = min(1.0, exp(2*lambda - delta_Sg_hat) * (num40 / (static_cast<double>(volume)/2 - 1)) / Force.partition_function());
    
    if(reject_trial > reject_ratio){
        tri_lab3->gauge_transform(gt3);
        tri_lab0->gauge_transform(gt0.dagger());
        tri_lab1->gauge_transform(gt1);
        if(debug_flag){
            cout << endl;
        }
        return; // if not rejected goes on, otherwise it returns with nothing done
    }
    
    // ----- CELL "EVOLUTION" -----    
    
    // ___ update adjacencies of persisting simplexes ___
    
    //triangles
    tri_lab0->adjacent_triangles()[0] = tri_lab3->adjacent_triangles()[0];
    tri_lab1->adjacent_triangles()[0] = tri_lab2->adjacent_triangles()[0];
    tri_lab0->vertices()[1] = tri_lab3->vertices()[1];
    tri_lab1->vertices()[1] = tri_lab2->vertices()[1];
    
    tri_lab3->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] = tri_lab3->adjacent_triangles()[1];
    tri_lab2->adjacent_triangles()[0].dync_triangle()->adjacent_triangles()[1] = tri_lab2->adjacent_triangles()[1];
    /* there is no need to update also the vertices for these two because they are already connected to the right one, because it will be vertex 4 that will be removed, and vertex 1 (the one they are already connected to) will remain */
    
    // ___ modify triangles' edges ___       //         *        
    tri_lab0->edges()[0] = lab_e4;           //        * *       
    tri_lab1->edges()[0] = lab_e7;           //    5  *   *  4  
                                             //      *     *     
    // ___ modify edges' near_t ___          //     *       *    
    e_lab4->near_t = lab_t0;                 //    * * * * * *  
    e_lab7->near_t = lab_t1;                 //     *   0   *    
                                             //      *     *     
    // ___ modify edges' vertices ___        //    6  *   *  7
    e_lab0->vertices()[1] = lab_v1;          //        * *       
                                             //         *        
    //vertices
    v_lab1->near_t = lab_t0;
    v_lab2->near_t = lab_t0;
    v_lab3->near_t = lab_t1;
    v_lab2->coord_num--;
    v_lab3->coord_num--;
    
    // ___ remove triangles 2 and 3, and vertex 4 ___
    remove_triangle(lab_t2);
    remove_triangle(lab_t3);
    remove_vertex(lab_v4);
    remove_edge(lab_e1);
    remove_edge(lab_e2);
    remove_edge(lab_e3);
    
    // ___ update list0 (pathologies) ___
    
    if(spatial_profile[v_lab4->time()] == 3){// 3 because the update of spatial_profile is directly in remove_vertex
        /* vert. coord. 4 in the time slice of v4 previously were not pathological, now they are */
        if(v_lab0->coordination() == 4){
            list0[v_lab0->position()] = list0[num40-1];
            list0[v_lab0->position()]->id = v_lab0->position();
            list0[num40-1] = lab_v0;
            list0[num40-1]->id = num40-1;
            num40--;
            num40p++;
        }
        if(v_lab1->coordination() == 4){
            list0[v_lab1->position()] = list0[num40-1];
            list0[v_lab1->position()]->id = v_lab1->position();
            list0[num40-1] = lab_v1;
            list0[num40-1]->id = num40-1;
            num40--;
            num40p++;
        }
        
        // then find the third vertex
        /* the third, respect to vertex 1 and  0, already in the time slice of vertex 4 */
        Label current_triangle = tri_lab0->adjacent_triangles()[0];
        while(current_triangle.dync_triangle()->is12()){
            current_triangle = current_triangle.dync_triangle()->adjacent_triangles()[0];
        }
        Label third_vertex = current_triangle.dync_triangle()->vertices()[1]; 
        if(third_vertex.dync_vertex()->coordination() == 4){
            list0[third_vertex->position()] = list0[num40-1];
            list0[third_vertex->position()]->id = third_vertex->position();
            list0[num40-1] = third_vertex;
            list0[num40-1]->id = num40-1;
            num40--;
            num40p++;
        }
    }
    
    if(debug_flag){
        cout << endl;
        cout << "┌──────────────────────┐" << endl;
        cout << "│AT THE END OF move_42:│ " << endl;
        cout << "└──────────────────────┘" << endl;;
        cout << " [cell] (triangles) t0: " << lab_t0->id << ", t1: " << lab_t1->id << ", t2: " << lab_t2->id << ", t3: " << lab_t3->id <<  "\t(vertices) \tv0: " << lab_v0->id << ", v1: " << lab_v1->id << ", v2: " << lab_v2->id << ", v3: " << lab_v3->id << ", v4: " << lab_v4->id << endl;
        cout << " \t\t\t\t\t\t\t\t\t\t\t   (coordinations)  v0: " << v_lab0->coord_num << ", v1: " << v_lab1->coord_num << ", v2: " << v_lab2->coord_num << ", v3: " << v_lab3->coord_num << ", v4: " << v_lab4->coord_num << endl;
        cout << " \t\t\t[adjacent triangles] v0: " << v_lab0->adjacent_triangle()->id << ", v1: " << v_lab1->adjacent_triangle()->id << ", v2: " << v_lab2->adjacent_triangle()->id << ", v3: " << v_lab3->adjacent_triangle()->id << endl;
        cout << " [space volumes] " << spatial_profile[v_lab3->t_slice] << ", " << spatial_profile[v_lab0->t_slice] << ", " << spatial_profile[v_lab2->t_slice] << endl;
        cout << " (list0.size = "+to_string(list0.size())+", num40 = "+to_string(num40)+", num40p = "+to_string(num40p)+")" << endl;
    }
    /* vertex 2 and 3 cannot become of coord. 4, because they have more than one time link toward the same time slice */ 

    // ----- END MOVE -----
    
    /* notice that transition list has not to be updated (no need because of the choices made in move construction, in particular because of triangles are removed on the right, and transitions are represented by right members of the cell) */
}


vector<complex<double>> Triangulation::move_gauge(int cell, bool debug_flag)
{
    RandomGen r;
    int e_num;
    
    if(debug_flag){
        cout << "gauge move: " << endl;
        cout << endl;
        cout << "╔════════════════════════╗" << endl;
        cout << "║BEGINNING OF move_gauge:║" << endl;
        cout << "╚════════════════════════╝" << endl;
    }
    
    // to make testing easier it is possible to specify the "cell" on which operate
    // if it is not specified (cell = -1), as in real runs, the cell is extracted
    if(cell == -1){
        e_num = r.next()*list1.size();
        if(e_num == list1.size()) // this shouldn't never happen
            e_num = list1.size() - 1;
    }
    else
        e_num = cell;
    
    vector<complex<double>> v;
        
    Label lab_e = list1[e_num];
    Edge* e_lab = lab_e.dync_edge();
    
    // GE_bef
    v.push_back(e_lab->U.tr());
    
    GaugeElement Force = e_lab->force(debug_flag);
    Force.set_base(lab_e);
    
    e_lab->U.heatbath(Force, debug_flag);

    //     // overrelaxation step
    //     GaugeElement U_new = Force * e_lab->U * Force;
    //     U_new.set_base(lab_e);
    //     e_lab->U = U_new.dagger(); 
    e_lab->U.unitarize();
    
    // GE_aft
    v.push_back(e_lab->U.tr());
    
    // Force
    v.push_back(Force.tr());

    
    if(debug_flag){
        cout << endl;
        cout << "┌─────────────────────────┐" << endl;
        cout << "│AT THE END OF move_gauge:│ " << endl;
        cout << "└─────────────────────────┘" << endl;;
    }
    
    return v;
    // ----- END MOVE -----
}

// +++++ auxiliary functions (for moves) +++++

Label Triangulation::move_24_find_t0(Label extr_lab)
{
    Triangle* tri_lab = extr_lab.dync_triangle();
    
    if(tri_lab->is21())
        return extr_lab;
    else
        return tri_lab->adjacent_triangles()[2];
}

/**
* @test da verificare
*/
Label Triangulation::move_42_find_t0(Label extr_lab)
{
    Vertex* v_lab = extr_lab.dync_vertex();
    Label  lab_t = v_lab->adjacent_triangle();
    Triangle* tri_lab = lab_t.dync_triangle();
    
    if(tri_lab->is21()){
        if(tri_lab->vertices()[1] == extr_lab)
            return lab_t;
        else if(tri_lab->vertices()[0] == extr_lab)
            return tri_lab->adjacent_triangles()[1];
        else
            throw runtime_error("Triangulation inconsistency: in cell (4,2) triangle 21 adjacent to the central vertex doesn't own it neither as v[0] nor as v[1]");
    }
    else{
        if(tri_lab->vertices()[1] == extr_lab)
            return tri_lab->adjacent_triangles()[2];
        else if(tri_lab->vertices()[0] == extr_lab)
            return tri_lab->adjacent_triangles()[2].dync_triangle()->adjacent_triangles()[1];
        else
            throw runtime_error("Triangulation inconsistency: in cell (4,2) triangle 12 adjacent to the central vertex doesn't own it neither as v[0] nor as v[1]");
    }
}
 
