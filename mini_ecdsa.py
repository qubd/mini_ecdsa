#Elliptic curve basics, tools for finding rational points, and ECDSA implementation.

#Brendan Cordy, 2015

from fractions import Fraction
from random import randrange

class Point(object):

    #Construct a point with two coordindates.
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.inf = False

    #Construct the point at infinity.
    @classmethod
    def atInfinity(cls):
        P = cls(0,0)
        P.inf = True
        return P

    def __str__(self):
        if(self.inf):
            return 'Inf'
        else:
            return '(' + str(self.x) + ',' + str(self.y) + ')'

    def __eq__(self,other):
        if(self.inf):
            return self.inf == other.inf
        elif(other.inf):
            return self.inf == other.inf
        else:
            return self.x == other.x and self.y == other.y

class Curve(object):

    #Construct a Weierstrass cubic y^2 = x^3 + ax^2 + bx + c over a field of prime
    #characteristic, or over the rationals (characteristic zero). Print to confirm.
    def __init__(self,a,b,c,char):
        self.a = a
        self.b = b
        self.c = c
        self.char = char
        print(self)

    def __str__(self):
        #Setting things up for pretty printing.
        if(self.a == 0):
            aTerm = ''
        elif(self.a == 1):
            aTerm = '+x^2'
        elif(self.a == -1):
            aTerm = '-x^2'
        else:
            aTerm = "%+d" % self.a + 'x^2'

        if(self.b == 0):
            bTerm = ''
        elif(self.b == 1):
            bTerm = '+x'
        elif(self.b == -1):
            bTerm = '-x'
        else:
            bTerm = "%+d" % self.b + 'x'

        if(self.c == 0):
            cTerm = ''
        else:
            cTerm = "%+d" % self.c

        self.eq = 'y^2 = x^3' + aTerm + bTerm + cTerm

        #Print prettily.
        if self.char == 0:
            return self.eq + ' over Q'
        else:
            return self.eq + ' over ' + 'F_' + str(self.char)

    #Compute the discriminant.
    def discriminant(self):
        a = self.a
        b = self.b
        c = self.c
        return -4*a*a*a*c+a*a*b*b+18*a*b*c-4*b*b*b-27*c*c

    #Is the point P on the curve?
    def contains(self,P):
        if(P.inf):
            return True
        elif self.char == 0:
            return P.y*P.y == P.x*P.x*P.x+self.a*P.x*P.x+self.b*P.x+self.c
        else:
            return (P.y*P.y) % self.char == (P.x*P.x*P.x+self.a*P.x*P.x+self.b*P.x+self.c) % self.char

    #Returns a list of all rational points on the curve.
    def get_points(self):
        #Start with the point at infinity.
        points = [Point.atInfinity()]

        if self.char == 0:
            #The only possible y values are divisors of the discriminant (Nagell-Lutz).
            for y in divisors(self.discriminant()):
                #Each possible y value yields a monic cubic polynomial in x, whose roots
                #must divide the constant term.
                const_term = self.c-y*y
                if const_term != 0:
                    for x in divisors(const_term):
                        P = Point(x,y)
                        if 0 == x*x*x+self.a*x*x+self.b*x+const_term and self.order(P) != -1:
                            points.append(P)
                #If the constant term is zero, factor out x and look for rational roots
                #of the resulting quadratic polynomial. Any such roots must divide b.
                elif self.b != 0:
                    for x in divisors(self.b):
                        P = Point(x,y)
                        if 0 == x*x*x+self.a*x*x+self.b*x+const_term and self.order(P) != -1:
                            points.append(P)
                #If the constant term and b are both zero, factor out x^2 and look for rational
                #roots of the resulting linear polynomial. Any such roots must divide a.
                elif self.a != 0:
                     for x in divisors(self.a):
                        P = Point(x,y)
                        if 0 == x*x*x+self.a*x*x+self.b*x+const_term and self.order(P) != -1:
                            points.append(P)
                #If the constant term, b, and a are all zero, we have 0 = x^3 + c - y^2 with
                #const_term = c - y^2 = 0, so (0,y) is a point on the curve.
                else:
                    points.append(Point(0,y))

            #Ensure that there are no duplicates in our list of points.
            unique_points = []

            for P in points:
                addP = True
                for Q in unique_points:
                    if(P == Q):
                        addP = False
                if addP:
                    unique_points.append(P)

            return unique_points

        #If we're working over a prime characteristic field, just brute force it, trying
        #every possible point.
        else:
            for x in range(self.char):
                for y in range(self.char):
                    P = Point(x,y)
                    if (y*y) % self.char == (x*x*x+self.a*x*x+self.b*x+self.c) % self.char:
                        points.append(P)

            return points

    #Returns a human readable list of points.
    def show_points(self):
        return [str(P) for P in self.get_points()]

    #Add two points on the curve.
    def add(self,P_1,P_2):

        #Adding over Q.
        if self.char == 0:
            y_diff = P_2.y - P_1.y
            x_diff = P_2.x - P_1.x

            if(P_1.inf):
                return P_2
            if(P_2.inf):
                return P_1
            elif x_diff == 0 and y_diff != 0:
                return Point.atInfinity()
            elif x_diff == 0 and y_diff == 0:
                if P_1.y == 0:
                    return Point.atInfinity()
                else:
                    ld = Fraction(3*P_1.x*P_1.x+2*self.a*P_1.x+self.b,2*P_1.y)
            else:
                ld = Fraction(y_diff,x_diff)

            nu = P_1.y-ld*P_1.x
            x = ld*ld-self.a-P_1.x-P_2.x
            y = -ld*x - nu

            return Point(x,y)

        #Adding over a prime characteristic field. The procedure is exactly the same
        #but the arithmetic happens in a finite field.
        else:
            y_diff = (P_2.y - P_1.y) % self.char
            x_diff = (P_2.x - P_1.x) % self.char

            if(P_1.inf):
                return P_2
            if(P_2.inf):
                return P_1
            elif x_diff == 0 and y_diff != 0:
                return Point.atInfinity()
            elif x_diff == 0 and y_diff == 0:
                if P_1.y == 0:
                    return Point.atInfinity()
                else:
                    ld = ((3*P_1.x*P_1.x+2*self.a*P_1.x+self.b)*mult_inv(2*P_1.y,self.char)) % self.char
            else:
                ld = (y_diff*mult_inv(x_diff,self.char)) % self.char

            nu = (P_1.y-ld*P_1.x) % self.char
            x = (ld*ld-self.a-P_1.x-P_2.x) % self.char
            y = (-ld*x - nu) % self.char

            return Point(x,y)

    #Add P to itself k times, i.e., multiply P by k.
    def mult(self,P,k):
        if k == 1:
            return P
        else:
            return self.add(P,self.mult(P,k-1))

    #Find the order of a point on the curve.
    def order(self,P):
        Q = P
        orderP = 1

        #Add P to Q repeatedly until obtaining the identity.
        while not Q.inf:
            Q = self.add(P,Q)
            orderP += 1

            #Over the rationals...
            if(self.char == 0):

                #If we obtain non integer coordinates, the point must have infinite order
                #by Nagell-Lutz.
                if Q.x != int(Q.x) or Q.y != int(Q.y):
                    return -1
                #All finite order points have order at most 12 by Mazur's theorem.
                if orderP > 12:
                    return -1

        return orderP

    #List all multiples of a point on the curve.
    def generate(self,P):

        Q = P
        orbit = [str(Point.atInfinity())]

        #Repeatedly add P to Q, appending each (pretty printed) result.
        while not Q == Point.atInfinity():
            orbit.append(str(Q))
            Q = self.add(P,Q)

        return orbit

    #Classify the torsion group of an elliptic curve over Q, appealing to Mazur's Theorem.
    def torsion_group(self):

        if self.char != 0:
            print 'Use this method for curves over Q only.'

        else:
            highest_order = 1

            #Find the rational point with the highest order.
            for P in self.get_points():
                if(self.order(P) > highest_order):
                    highest_order = self.order(P)

            #If this point generates the entire torsion group, the torsion group is cyclic.
            if highest_order == len(self.get_points()):
                print 'Z/' + str(highest_order) + 'Z'
            #If not, by Mazur's Theorem the torsion group must be a direct product of Z/2Z
            #with the cyclic group generated by the highest order point.
            else:
                print 'Z/2Z x ' + 'Z/' + str(highest_order) + 'Z'

            print C.show_points()

#List all integer divisors of a number.
def divisors(n):

    divs = [0]

    for i in range(1,abs(n)+1):
        if n%i == 0:
            divs.append(i)
            divs.append(-i)

    return divs

#Extended Euclidean algorithm.
def euclid(a, b):

    #When the remainder is zero, it's done. The gcd is b.
    if a == 0:
        #In this case, gcd(a,b) = 0*a + 1*b.
        return (b,0,1)
    else:
        #Repeat with a and the remainder, b%a.
        g,y,x = euclid(b%a,a)
        #Backtrack through the calculation, keeping the gcd and rewriting the smallest value
        #in terms of larger ones.
        return (g,x-(b//a)*y,y)

#Compute multiplicative inverses modulo n.
def mult_inv(a, n):

    g,x,y = euclid(a,n)

    #If gcd(a,n) is not one, then a has no multiplicative inverse.
    if g != 1:
        raise ValueError('multiplicative inverse does not exist')
    #If gcd(a,n) = 1, and gcd(a,n) = x*a + y*n, x is the multiplicative inverse of a.
    else:
        return x%n

#Silly hash function. Warning: not suitable for... anything.
def hash(message,n):

    h = 1

    for letter in message:
        h = h*ord(letter) % n

    return h

#Create a digital signature for the string message using the curve C with a point P which
#generates a prime order subgroup of size n. C, P, and n are all public knowledge.
def sign(message, curve, P, n):

    #Create the private-public key pair (d,Q) where Q = dP.
    d = randrange(1,n)
    Q = curve.mult(P,d)

    #Hash the message.
    z = hash(message,n)

    #Choose a random multiple of P and sign the message with r and s.
    r = 0
    s = 0
    while r == 0 or s == 0:

        k = randrange(1,n)
        R = curve.mult(P,k)

        r = R.x % n
        s = (mult_inv(k,n)*(z+r*d)) % n

    print 'Sig: (' + str(Q) + ', ' + str(r) + ', ' + str(s) + ')'
    return (Q,r,s)

#Verify the the digital signature S for the string message. As above, C, P, and n are all
#public knowledge.
def verify(message, curve, P, n, S):

    Q,r,s = S

    #Confirm that Q is on the curve.
    if Q.inf or not curve.contains(Q):
        return False

    #Confirm that Q has order less than or equal to the order of P.
    T = curve.mult(Q,n)

    if not T.inf:
        return False

    #Confirm that r and s are at least in the acceptable range.
    if r not in range(1,n) or s not in range(1,n):
        return False

    #Verify the signature is valid.
    z = hash(message,n)
    w = mult_inv(s,n) % n
    u_1 = z*w % n
    u_2 = r*w % n

    C_1 = curve.mult(P,u_1)
    C_2 = curve.mult(Q,u_2)

    C = curve.add(C_1,C_2)
    return r % n == C.x % n
