/*
 * <one line to give the program's name and a brief idea of what it does.>
 * Copyright (C) 2019  Alessandro Candido <email>
 * Copyright (C) 2019  Federico Rottoli
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
#include "randomgenerator.h"
#include "triangulation.h"
#include "edge.h"
#include <iostream>
#include <cmath>
#include <random>

//distributions used in the von Neumann algorithms in the heat bath

double lorentzRand(double c){
    //extract a random number in [0, pi[ distributed as a lorentzian
    RandomGen r;
    double pi = 2 * asin(1);
    double k, x, z;

    x = r.next();

    k = atan(c * pi);
    z = tan(k * x) / c;

    return z; 
}

double expRand(double gamma){
    //extract a random variable y in [-1, +1] distributed as exp(gamma * y)

    RandomGen r;
    double x, x2sinh, y;
    x = r.next();

    x2sinh = x * (exp(gamma) - exp(- gamma));
    y = ( log(x2sinh + exp(- gamma)) ) / gamma;

    return y;
}

/***********************************************************/

//GaugeElement class

GaugeElement::GaugeElement(){
    Label lab;
    base_edge = lab;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            if(i == j)
                mat[i][j] = 1; 
            else
                mat[i][j] = 0;
        }
    }
}

GaugeElement::GaugeElement(const Label& edge)
{
    base_edge = edge;
    *this = alpha_id(1.);
}

GaugeElement::GaugeElement(const complex<double> alpha)
{
    Label lab;
    base_edge = lab;
    *this = alpha_id(alpha);
}

GaugeElement::GaugeElement(const complex<double> (&matrix)[N][N])
{
    Label lab;
    base_edge = lab;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            mat[i][j] = matrix[i][j];
    }
}

Label GaugeElement::base(){ return base_edge; }

void GaugeElement::set_base(Label base){ base_edge = base; }

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

complex<double>* GaugeElement::operator[](int i)
{
    if( i >= N )
        throw out_of_range("Index out of bounds");
    
    return mat[i];
}

double GaugeElement::partition_function(bool debug_flag)
{
    /** @todo
     * deve dipendere da N
     */ 
    
    double beta = base_edge.dync_edge()->get_owner()->beta;
    
    // slightly transform the Force in order to put the integrand in the form
    // exp(tr(Source.dagger * U + U.dagger * Source))
    GaugeElement Force = *this;
    //TODO: check beta def
    GaugeElement Source;
    Source = (Force * (beta / 2.)).dagger();

    double Z = 1.;
    
//TODO
//cout<<Force<<"\n";

#if NC == 1
        // I_0(2|z|), bib: R.Brower, P.Rossi, C.Tan "The external field problem for QCD"
        Z = cyl_bessel_i(0, 2*abs(Source.mat[0][0]));

#elif NC == 2
        complex<double> trProd;
       	double K;
        
        trProd = (Source.dagger() * Source).tr();
	//check reality
	if(debug_flag){
	    if(abs(imag(trProd)) > 1e-8){
	        throw runtime_error("partition_function: N == 2: tr(J.dag * J) is not real: imag = " + to_string(abs(imag(trProd))));
	    }
	}

	//TODO check positivity

        K = abs(trProd + Source.det() + (Source.dagger()).det());

        Z = cyl_bessel_i(1, 2.0 * sqrt(K)) / sqrt(K);
//TODO test
//cout <<2. * beta * sqrt(abs(Force.det()))  << " "<<K << " "<< Z << "\n";

#endif 
    
    if(N != 1 && N != 2){
    	throw runtime_error("partition_function: Not implemented fir N != 1 or N != 2");
    }
    
    double pi = 2 * asin(1);
    
    return Z;
}

GaugeElement GaugeElement::rand(){
    RandomGen r;
    
    double pi = 2 * asin(1);

    if(N != 1 && N != 2){
        throw runtime_error("rand: not implemented for N != 1");
    }

#if NC == 1
    //the angle is uniform on the circle
    double alpha = pi * (2 * r.next() - 1);
    GaugeElement U(exp(1i * alpha));

    return U;

#elif NC == 2
    //the angles are uniform on the sphere S^3, with measure
    //d(phi) sinTheta d(theta) (sinAlpha)^2 d(alpha)
    
    double accept_ratio;
    double cosAlpha, sinAlpha, cosTheta, sinTheta, phi;

    //Pauli matrices
    GaugeElement sigma1(matSigma1);
    GaugeElement sigma2(matSigma2);
    GaugeElement sigma3(matSigma3);

    // Von Neumann algorithm to extract cos alpha in [-1, +1] 
    // distributed as sqrt(1 - cosAlpha^2)
    do{
        cosAlpha = (2 * r.next()) - 1;
        accept_ratio = sqrt(1 - (cosAlpha * cosAlpha));
    }while(r.next() > accept_ratio);
    sinAlpha = sqrt(1 - (cosAlpha * cosAlpha));


    //cos theta is uniform in [-1, +1]
    cosTheta = (2 * r.next()) - 1;
    sinTheta = sqrt(1 - (cosTheta * cosTheta));

    //phi is uniform in [0, 2*pi]
    phi = r.next() * 2 * pi;

    GaugeElement U;
    U = sigma3 * (1i * (sinAlpha * sinTheta * cos(phi)))
      + sigma2 * (1i * (sinAlpha * sinTheta * sin(phi)))
      + sigma1 * (1i * (sinAlpha * cosTheta))
      + cosAlpha;

    return U;
#endif

}

void GaugeElement::heatbath(bool overrelaxation, GaugeElement Force, bool debug_flag)
{
    RandomGen r;
    
    if(debug_flag){
        cout << "+----------+" << endl;
        cout << "| HEATBATH |" << endl;
        cout << "+----------+" << endl;
	cout << "Overrelaxation? "<< overrelaxation <<endl;
        cout << "Given force: " << Force.tr() << endl;
    }

    double pi = 2 * asin(1);
    double beta = Force.base()->get_owner()->beta;

//TODO:test
//cout << "heat " << Force << endl;

#if NC == 1 
       double a, c, alpha, eta, accept_ratio;
	
        a = beta * abs(Force.tr());
	c = sqrt(a / 2);

	//extract alpha in [0, pi[ distributed as a lorentzian
	//perform then a von Neumann algorithm to extract the correct distribution: exp(a (cos alpha - 1))
	//Campostrini et al.

	do{
	    alpha = lorentzRand(c);

	    if(a >= 0.8)
	        eta = 0.99;
	    else
	        eta = 0.73;
	    accept_ratio = eta * (1 + (c * c) * (alpha * alpha)) * exp(a * (cos(alpha) - 1));
	}while(r.next() > accept_ratio);

	//rotate the element in the direction of the force
        GaugeElement Force_phase = (Force.dagger() / abs(Force.tr()));
	if(overrelaxation) {
            complex<double> prev = this->mat[0][0] * conj(Force_phase[0][0]);
            double sgn = (imag(prev) > 0) * 2 - 1;
            *this =  Force_phase * exp(- 1i * alpha * sgn);
        } else {
	    //with probability 1/2 we take the angle with negative sign
            if(r.next() > 0.5)
	        alpha = - alpha;
    	    *this = Force_phase * exp(- 1i * alpha);
	}

#elif NC == 2
    GaugeElement U;

	//Pauli matrices
	GaugeElement sigma1(matSigma1);
	sigma1.set_base(this->base_edge);
	GaugeElement sigma2(matSigma2);
	sigma2.set_base(this->base_edge);
	GaugeElement sigma3(matSigma3);
	sigma3.set_base(this->base_edge);

    double Force_mod = sqrt(abs(Force.det()));
	// Check if the module of the force is too small
	// If the module is too small the division of the force by its module gives a nan
	// Indeed, if the force is zero, it does not have a defined direction
	// and the element gets extracted uniformly the SU(2) group
	
	if(Force_mod > 1e-10){
	    if(debug_flag){
	        cout << "heatbath: N == 2:\n\tForce module = " << Force_mod << "\nCreutz algorithm\n"; 
	    }

	    double gamma = 2 * beta * Force_mod;
//TODO
//cout << gamma <<" "<< Force.partition_function() << endl;

	    double cosAlpha, sinAlpha, cosTheta, sinTheta, phi;
	    double accept_ratio;
	    // Creutz algorithm:
            // Von Neumann algorithm to extract cos alpha in [-1, +1] 
	    // distributed as sqrt(1 - cosAlpha^2) * exp(gamma * cosAlpha)
            do{
                cosAlpha = expRand(gamma);
                accept_ratio = sqrt(max(0.0,1 - (cosAlpha * cosAlpha)));
            }while(r.next() > accept_ratio);
            sinAlpha = sqrt(max(0.0,1 - (cosAlpha * cosAlpha)));


	    //cos theta is uniform in [-1, +1]
	    cosTheta = (2 * r.next()) - 1;
	    sinTheta = sqrt(max(0.0,1 - (cosTheta * cosTheta)));

	    //phi is uniform in [0, 2*pi]
	    phi = r.next() * 2 * pi;
            
	    GaugeElement U_tilde;
	    U_tilde = sigma3 * (1i * (sinAlpha * sinTheta * cos(phi)))
	    	    + sigma2 * (1i * (sinAlpha * sinTheta * sin(phi)))
	    	    + sigma1 * (1i * (sinAlpha * cosTheta))
	    	    + cosAlpha;
	    U_tilde.set_base(this->base_edge);

	    //Unitarity check
	    if(debug_flag){
            cout<<"U_tilde = "<<U_tilde<<endl; 
	        if(abs(U_tilde.det() - 1.0) > 1e-8){
	            throw runtime_error("heatbath: N == 2: Extracted gauge element is not special unitary:\n\tdet U_tilde - 1 = (" + to_string(real(U_tilde.det()) - 1.0) + ", " + to_string(imag(U_tilde.det())) + "))\n\t|U_tilde| - 1 = " + to_string(abs(abs(U_tilde.det()) - 1.0)));
	        }
	    }

	    //rotate in the direction of the force
	    GaugeElement Force_phase = Force / Force_mod;
	    Force_phase.set_base(this->base_edge);
	    //Unitarity check
	    if(debug_flag){
	        if(abs(Force_phase.det() - 1.0) > 1e-8){
	            throw runtime_error("heatbath: N == 2: Force phase is not special unitary:\n\tdet f - 1 = (" + to_string(real(Force_phase.det()) - 1.0) + ", " + to_string(imag(Force_phase.det())) + ")\n\t|f| - 1 = " + to_string(abs(abs(Force_phase.det()) - 1.0)));
	        }
	        if(isnan( abs(Force_phase.det()) )){
	            throw runtime_error("heatbath: N == 2: Force phase is nan!");
	        }
	    }
	    
	    U = U_tilde * (Force_phase.dagger());
	    //Unitarity check
	    if(debug_flag){
	        if(abs(U.det() - 1.0) > 1e-8){
	            throw runtime_error("heatbath: N == 2: Rotated extracted gauge element is not unitary:\n\tdet U - 1 = (" + to_string(real(U.det()) - 1.0) + ", " + to_string(imag(U.det())) + ")\n\t|U| - 1 = " + to_string(abs(abs(U.det()) - 1.0)));
	        }
	    }

	}else{
	    if(debug_flag){
	        cout << "heatbath: N == 2:\n\tForce module = " << Force_mod << "\nExtract uniformly\n"; 
	    }

	    U = U.rand();
            U.set_base(this->base_edge);
	}

	*this = U;
#endif

    if(N != 1 && N != 2){
	throw runtime_error("heatbath: Not implemented for N!=1 or N!=2");
    }
}

// ##### ALGEBRA #####

GaugeElement GaugeElement::operator+(const GaugeElement& V)
{
    GaugeElement U;
    
    U.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            U.mat[i][j] = this->mat[i][j] + V.mat[i][j];
    }

    return U;
}

GaugeElement GaugeElement::operator-(const GaugeElement& V)
{
    GaugeElement U;
    
    U.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            U.mat[i][j] = (this->mat[i][j] - V.mat[i][j]);
    }

    return U;
}

GaugeElement GaugeElement::operator*(const GaugeElement& V)
{
    GaugeElement U;
    
    U.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            U.mat[i][j] = 0;
            for(int k=0; k<N; k++)
                U.mat[i][j] += this->mat[i][k]*V.mat[k][j];
        }
    }
    
    return U;
}

GaugeElement GaugeElement::operator+=(const GaugeElement& V)
{
    return *this = *this + V;
}

GaugeElement GaugeElement::operator-=(const GaugeElement& V)
{
    return *this = *this - V;
}

GaugeElement GaugeElement::operator*=(const GaugeElement& V)
{
    return *this = *this * V;
}

GaugeElement GaugeElement::dagger()
{
    GaugeElement U;
    
    U.base_edge = this->base_edge;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++)
            U.mat[i][j] = conj(this->mat[j][i]);
    }

    return U;    
}

complex<double> GaugeElement::trace()
{
    complex<double> trace = 0;
    
    for(int i=0; i<N; i++)
        trace += mat[i][i];
    
    return trace;
}

complex<double> GaugeElement::tr()
{
    return trace();
}

complex<double> GaugeElement::det()
{
    complex<double> det;
    if(N == 1){
        det = mat[0][0];
    } else if(N == 2){
        det = (mat[0][0] * mat[1][1]) - (mat[0][1] * mat[1][0]);
    } else {
        throw runtime_error("det: Not implemented for N != 1 or N != 2");
    }

    return det;
}

double GaugeElement::norm()
{
    double norm = 0;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            norm += pow(abs(mat[i][j]), 2);
        }
    }
    
    return norm;
}

// scalars

GaugeElement GaugeElement::alpha_id(const complex<double>& alpha)
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

GaugeElement GaugeElement::operator=(const complex<double>& alpha)
{
    *this = alpha_id(alpha);
    
    return *this;
}

GaugeElement GaugeElement::operator+(const complex<double>& alpha)
{
    return *this + alpha_id(alpha);
}

GaugeElement GaugeElement::operator-(const complex<double>& alpha)
{
    return *this - alpha_id(alpha);
}

GaugeElement GaugeElement::operator*(const complex<double>& alpha)
{
    return *this * alpha_id(alpha);
}

GaugeElement GaugeElement::operator/(const complex<double>& alpha)
{
    GaugeElement aux;
    aux = *this;
    
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            aux.mat[i][j] = this->mat[i][j] / alpha;
        }
    }
    
    return aux;
}

GaugeElement GaugeElement::operator-()
{
    return alpha_id(0) - *this;
}

GaugeElement operator+(const complex<double>& alpha, GaugeElement U)
{
    return U + alpha;
}

GaugeElement operator-(const complex<double>& alpha, GaugeElement U)
{
    return - ( U - alpha );
}

GaugeElement operator*(const complex<double>& alpha, GaugeElement U)
{
    return U * alpha;
}

GaugeElement GaugeElement::operator+=(const complex<double>& alpha)
{
    return *this = *this + alpha;
}

GaugeElement GaugeElement::operator-=(const complex<double>& alpha)
{
    return *this = *this - alpha;
}

GaugeElement GaugeElement::operator*=(const complex<double>& alpha)
{
    return *this = *this * alpha;
}

GaugeElement GaugeElement::operator/=(const complex<double>& alpha)
{
    return *this = *this / alpha;
}

// auxiliary

void GaugeElement::unitarize()
{
    if(N == 1){

        mat[0][0] /= abs(mat[0][0]);

    } else if(N == 2){

	*this /= sqrt(abs(det()));

    } else {
        throw runtime_error("unitarize: Not implemented");
    }
        
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

ostream& operator<<(ostream& os, const GaugeElement& U){
    os.precision(2);
    os << fixed;
    
    stringstream s;
    s.precision(2);
    s << fixed;
    int len=0;
    
    for(int i=0; i<U.N; i++){
                
        for(int j=0; j<U.N; j++){
            s << U.mat[i][j];
            if(j != U.N -1)
                s << "    ";
        }
        
        if(s.str().length() > len)
            len = s.str().length();
        
        s.str("");
    }
    
    if(U.N <= 5){
        os << " ┌";
        for(int j=0; j<len; j++){
            os << " ";
        }
        
        os << "  ┐" << endl;
    }
    
    for(int i=0; i<U.N; i++){
        if(U.N <= 5)
            os << " │ ";
                
        for(int j=0; j<U.N; j++){
            os << U.mat[i][j];
            if(j != U.N -1)
                os << "    ";
        }
        
        if(U.N <= 5)
            os << " │";
        os << endl;
    }
    
    if(U.N <= 5){
        os << " └";
        for(int j=0; j<len; j++){
            cout << " ";
        }
        os << "  ┘";
    }
    
    return os;
}
