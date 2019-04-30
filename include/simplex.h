/** @file */
#ifndef SIMPLEX_H
#define SIMPLEX_H

enum class SimplexType {_vertex, _edge, _triangle};

class Triangulation;
class Label;

/**
 * @todo check docs
 */
class Simplex
{
protected:
    
    // DATA
    
    /**
    * @var index in list of simplices
    * 
    * @todo come lo gestisco in modo sensato?\n
    * il suo senso credo sia risalire al Label che lo possiede, in modo da includerlo in altre strutture (qui solo i triangoli)
    */
    int id;
    
    Triangulation* owner;
    
    friend class Triangulation;
    
public:
    virtual ~Simplex() {}
    
    // METHODS

    /** 
     * @param other the triangle I'm comparing with
     * @return the equality truth value of the Simplex::id of the two
     */
    bool operator== ( const Simplex& other ) const;

    /** 
     * @param other the triangle I'm comparing with
     * @return the  truth value of the Simplex::id of the two
     */
    bool operator!= ( const Simplex& other ) const;
    
    /**
    * @brief interface method
    * 
    * @return id
    */
    int position();
};

#endif // SIMPLEX_H
