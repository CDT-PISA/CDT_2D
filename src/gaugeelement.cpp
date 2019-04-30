/*
 * <one line to give the program's name and a brief idea of what it does.>
 * Copyright (C) 2019  Alessandro Candido <email>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "gaugeelement.h"
#include <iostream>

GaugeElement::GaugeElement(){
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            if(i == j)
                mat[i][j] = 1; 
            else
                mat[i][j] = 0;
        }
    }
}

GaugeElement::GaugeElement(const complex<double> (&matrix)[N][N])
{
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            mat[i][j] = matrix[i][j];
    }
}

Label GaugeElement::base(){ return base_edge; }

int GaugeElement::dimension(){ return N; }

complex<double>** GaugeElement::matrix()
{
    complex<double>** aux = 0;
    aux = new complex<double>*[N];
    
    for(int i=0; i<N; i++){
        aux[i] = new complex<double>[N];
        
        for(int j=0; j<N; j++)
            aux[i][j] = mat[i][j];
    }
    
    return aux;
}

// ##### ALGEBRA #####

GaugeElement GaugeElement::operator+(const GaugeElement& V)
{
    GaugeElement U;
    complex<double> U_mat[N][N];
    
    U.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            U_mat[i][j] = this->mat[i][j] + V.mat[i][j];
    }

    return U;
}

GaugeElement GaugeElement::operator-(const GaugeElement& V)
{
    GaugeElement U;
    complex<double> U_mat[N][N];
    
    U.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            U_mat[i][j] = this->mat[i][j] - V.mat[i][j];
    }

    return U;
}

GaugeElement GaugeElement::operator*(const GaugeElement& V)
{
    GaugeElement U;
    complex<double> U_mat[N][N];
    
    U.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            U_mat[i][j] = 0;
            for(int k=0; k<N; k++)
                U_mat[i][j] += this->mat[i][k]*V.mat[k][j];
        }
    }

    return U;
}

GaugeElement GaugeElement::operator+=(const GaugeElement& V)
{
    return *this + V;
}

GaugeElement GaugeElement::operator-=(const GaugeElement& V)
{
    return *this - V;
}

GaugeElement GaugeElement::operator*=(const GaugeElement& V)
{
    return *this * V;
}

GaugeElement GaugeElement::dagger()
{
    GaugeElement U;
    complex<double> U_mat[N][N];
    
    U.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            U_mat[i][j] = conj(this->mat[j][i]);
    }

    return U;    
}

// scalars

GaugeElement GaugeElement::alpha_id(const double& alpha)
{
    GaugeElement alpha_id;
    
    alpha_id.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            if(i == j)
                alpha_id.mat[i][j] = alpha; 
            else
                alpha_id.mat[i][j] = 0;
        }
    }
    
    return alpha_id;
}

GaugeElement GaugeElement::operator=(const double& alpha)
{
    return alpha_id(alpha);
}

GaugeElement GaugeElement::operator+(const double& alpha)
{
    return *this + alpha_id(alpha);
}

GaugeElement GaugeElement::operator-(const double& alpha)
{
    return *this + alpha_id(alpha);
}

GaugeElement GaugeElement::operator*(const double& alpha)
{
    return *this * alpha_id(alpha);
}

GaugeElement GaugeElement::operator/(const double& alpha)
{
    GaugeElement quotient;
    
    quotient.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            quotient.mat[i][j] /= alpha;
        }
    }
    
    return quotient;
}

GaugeElement GaugeElement::operator+=(const double& alpha)
{
    return *this + alpha;
}

GaugeElement GaugeElement::operator-=(const double& alpha)
{
    return *this - alpha;
}

GaugeElement GaugeElement::operator*=(const double& alpha)
{
    return *this * alpha;
}

GaugeElement GaugeElement::operator/=(const double& alpha)
{
    return *this / alpha;
}

// auxiliary

void GaugeElement::unitarize()
{
    /// @todo
}

// ##### FILE I/O #####

void GaugeElement::write(std::ostream& output)
{
    int pos = base_edge->position();
    output.write((char*)&pos, sizeof(pos));
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            output.write((char*)&mat[i][j], sizeof(mat[i][j]));
    }
}

void GaugeElement::read(std::istream& input, const vector<Label>& List1)
{
    int pos = 0;
    input.read((char*)&pos, sizeof(pos));
    base_edge = List1[pos];
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            input.read((char*)&mat[i][j], sizeof(mat[i][j]));
    }
}
