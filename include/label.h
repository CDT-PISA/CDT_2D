/** @file */
#ifndef LABEL_H
#define LABEL_H

#include <memory>

#include "simplex.h"
using namespace std;

class Vertex;
class Triangle;

/*
 * Non so davvero perché sto usando questi Label anziché gli shared_ptr<Simplex>, i motivi sono i seguenti:
 *      - il principale è che nella tesi di Giuseppe usava i Label
 *      - posso implementare come se fossero unique_ptr, se in futuro mi venisse comodo posso aggiungere struttura e metodi a Label
 *      - ultimo, ma quasi primo: è molto più corto scrivere Label che shared_ptr<Simplex>
 */

/**
* @test devo testare che il costruttore con Simplex* costruisca un oggetto Label che si comporti a tutti gli effetti come uno shared_ptr<Simplex>
* 
*/
class Label{
private:
    shared_ptr<Simplex> sh_ptr_simplex;
public:
    Label(){}
    Label(Simplex*);
//     Label(const Label&);
//     Label(Label&&);
//     
//     Label& operator=(const Label&);
//     Label& operator=(Label&&);
    
    ~Label(){}
    
    Simplex& operator*();
    Simplex* operator->();
    
    bool operator==(Label);
    bool operator!=(Label);
    
    Vertex* dync_vertex();
    Triangle* dync_triangle();
    
};

#endif // LABEL_H
