#Elliptic curve basics, tools for finding rational points, and ECDSA implementation.
#Brendan Cordy, 2015

from fractions import Fraction
from random import randrange
from hashlib import sha256

class Point(object):
    #Construct a point with two given coordindates.
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.inf = False

    #Construct the point at infinity.
    @classmethod
    def atInfinity(cls):
        P = cls(0, 0)
        P.inf = True
        return P

    def __str__(self):
        if self.inf:
            return 'Inf'
        else:
            return '(' + str(self.x) + ',' + str(self.y) + ')'

    def __eq__(self,other):
        if self.inf:
            return self.inf == other.inf
        elif other.inf:
            return self.inf == other.inf
        else:
            return self.x == other.x and self.y == other.y

class Curve(object):
    #Construct a Weierstrass cubic y^2 = x^3 + ax^2 + bx + c over a field of prime
    #characteristic, or over the rationals (characteristic zero). Print to confirm.
    def __init__(self, a, b, c, char):
        self.a, self.b, self.c = a, b, c
        self.char = char
        print(self)

    def __str__(self):
        #Lots of cases for pretty printing.
        if self.a == 0:
            aTerm = ''
        elif self.a == 1:
            aTerm = ' + x^2'
        elif self.a == -1:
            aTerm = ' - x^2'
        elif self.a < 1:
            aTerm = " - " + str(-self.a) + 'x^2'
        else:
            aTerm = " + " + str(self.a) + 'x^2'

        if self.b == 0:
            bTerm = ''
        elif self.b == 1:
            bTerm = ' + x'
        elif self.b == -1:
            bTerm = ' - x'
        elif self.b < 1:
            bTerm = " - " + str(-self.b) + 'x'
        else:
            bTerm = " + " + str(self.b) + 'x'

        if self.c == 0:
            cTerm = ''
        elif self.c < 1:
            cTerm = " - " + str(-self.c)
        else:
            cTerm = " + " + str(self.c)

        self.eq = 'y^2 = x^3' + aTerm + bTerm + cTerm

        #Print prettily.
        if self.char == 0:
            return self.eq + ' over Q'
        else:
            return self.eq + ' over ' + 'F_' + str(self.char)

    #Compute the discriminant.
    def discriminant(self):
        a = self.a, b = self.b, c = self.c
        return -4*a*a*a*c + a*a*b*b + 18*a*b*c - 4*b*b*b - 27*c*c

    #Is the point P on the curve?
    def contains(self, P):
        if P.inf:
            return True
        elif self.char == 0:
            return P.y*P.y == P.x*P.x*P.x + self.a*P.x*P.x + self.b*P.x + self.c
        else:
            return (P.y*P.y) % self.char == (P.x*P.x*P.x + self.a*P.x*P.x + self.b*P.x + self.c) % self.char

    #Returns a list of all rational points on the curve.
    def get_points(self):
        #Start with the point at infinity.
        points = [Point.atInfinity()]

        if self.char == 0:
            #The only possible y values are divisors of the discriminant (Nagell-Lutz).
            for y in divisors(self.discriminant()):
                #Each possible y value yields a monic cubic polynomial in x, whose roots
                #must divide the constant term.
                const_term = self.c - y*y
                if const_term != 0:
                    for x in divisors(const_term):
                        P = Point(x,y)
                        if 0 == x*x*x + self.a*x*x + self.b*x + const_term and self.has_finite_order(P):
                            points.append(P)
                #If the constant term is zero, factor out x and look for rational roots
                #of the resulting quadratic polynomial. Any such roots must divide b.
                elif self.b != 0:
                    for x in divisors(self.b):
                        P = Point(x,y)
                        if 0 == x*x*x+self.a*x*x+self.b*x+const_term and self.has_finite_order(P):
                            points.append(P)
                #If the constant term and b are both zero, factor out x^2 and look for rational
                #roots of the resulting linear polynomial. Any such roots must divide a.
                elif self.a != 0:
                     for x in divisors(self.a):
                        P = Point(x,y)
                        if 0 == x*x*x+self.a*x*x+self.b*x+const_term and self.has_finite_order(P):
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
                    if P == Q:
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
                    if (y*y) % self.char == (x*x*x + self.a*x*x + self.b*x + self.c) % self.char:
                        points.append(P)

            return points

    #Returns a pretty printed list of points.
    def show_points(self):
        return [str(P) for P in self.get_points()]

    #Add two points on the curve.
    def add(self, P_1, P_2):
        #Adding over Q.
        if self.char == 0:
            y_diff = P_2.y - P_1.y
            x_diff = P_2.x - P_1.x

            if P_1.inf:
                return P_2
            if P_2.inf:
                return P_1
            elif x_diff == 0 and y_diff != 0:
                return Point.atInfinity()
            elif x_diff == 0 and y_diff == 0:
                if P_1.y == 0:
                    return Point.atInfinity()
                else:
                    ld = Fraction(3*P_1.x*P_1.x + 2*self.a*P_1.x + self.b, 2*P_1.y)
            else:
                ld = Fraction(y_diff, x_diff)

            nu = P_1.y - ld*P_1.x
            x = ld*ld - self.a  -P_1.x - P_2.x
            y = -ld*x - nu

            return Point(x,y)

        #Adding over a prime characteristic field. The procedure is exactly the same
        #but the arithmetic happens in a finite field.
        else:
            y_diff = (P_2.y - P_1.y) % self.char
            x_diff = (P_2.x - P_1.x) % self.char

            if P_1.inf:
                return P_2
            if P_2.inf:
                return P_1
            elif x_diff == 0 and y_diff != 0:
                return Point.atInfinity()
            elif x_diff == 0 and y_diff == 0:
                if P_1.y == 0:
                    return Point.atInfinity()
                else:
                    ld = ((3*P_1.x*P_1.x + 2*self.a*P_1.x + self.b) * mult_inv(2*P_1.y, self.char)) % self.char
            else:
                ld = (y_diff * mult_inv(x_diff, self.char)) % self.char

            nu = (P_1.y - ld*P_1.x) % self.char
            x = (ld*ld - self.a - P_1.x - P_2.x) % self.char
            y = (-ld*x - nu) % self.char

            return Point(x,y)

    #Double a point on the curve (add it to itself).
    def double(self, P):
        return self.add(P,P)

    #Add P to itself k times, using the powermod idea, which amounts to repeated additions with doubling.
    def mult(self, P, k):
        #Convert k to binary and use repeated additions.
        b = bin(k)[2:]
        return self.repeat_additions(P, b, 1)

    def repeat_additions(self, P, b, n):
        if b == '0':
            return Point.atInfinity()
        elif b == '1':
            return P
        elif b[-1] == '0':
            return self.repeat_additions(self.double(P), b[:-1], n+1)
        elif b[-1] == '1':
            return self.add(P, self.repeat_additions(self.double(P), b[:-1], n+1))

    #Find the order of a point on the curve by brute force.
    def order(self, P):
        Q = P
        orderP = 1

        #Add P to Q repeatedly until obtaining the identity (point at infinity).
        while not Q.inf:
            Q = self.add(P,Q)
            orderP += 1

            #Over the rationals...
            if self.char == 0:
                #If we ever obtain non integer coordinates, the point must have infinite order
                #by Nagell-Lutz.
                if Q.x != int(Q.x) or Q.y != int(Q.y):
                    return -1
                #Moreover, all finite order points have order at most 12 by Mazur's theorem.
                if orderP > 12:
                    return -1

        return orderP

    #Check if a point known to be on the curve has finite order.
    def has_finite_order(self, P):
        if self.char == 0:
            return not self.order(P) == -1
        else:
            return True

    #List all multiples of a point on the curve.
    def generate(self, P):
        Q = P
        orbit = [str(Point.atInfinity())]

        #Repeatedly add P to Q, appending each (pretty printed) result.
        while not Q == Point.atInfinity():
            orbit.append(str(Q))
            Q = self.add(P,Q)

        return orbit

    #Classify the torsion group of an elliptic curve, appealing to Mazur's Theorem.
    def torsion_group(self):
        #This classification only applies to curves defined over Q.
        if self.char != 0:
            print 'Use this method for curves over Q only.'
        else:
            highest_order = 1
            #Find the rational point with the highest order.
            for P in self.get_points():
                if self.order(P) > highest_order:
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
    for i in range(1, abs(n) + 1):
        if n % i == 0:
            divs.append(i)
            divs.append(-i)
    return divs

#Extended Euclidean algorithm.
def euclid(a, b):
    #When the remainder is zero, it's done. The gcd is b.
    if a == 0:
        #In this case, gcd(a,b) = 0*a + 1*b.
        return (b, 0, 1)
    else:
        #Repeat with a and the remainder, b%a.
        g, y, x = euclid(b % a, a)
        #Backtrack through the calculation, keeping the gcd and rewriting the smallest value
        #in terms of larger ones.
        return (g, x - (b//a)*y, y)

#Compute multiplicative inverses mod n.
def mult_inv(a, n):
    g, x, y = euclid(a, n)
    #If gcd(a,n) is not one, then a has no multiplicative inverse.
    if g != 1:
        raise ValueError('multiplicative inverse does not exist')
    #If gcd(a,n) = 1, and gcd(a,n) = x*a + y*n, x is the multiplicative inverse of a.
    else:
        return x % n

#Use sha256 to hash a message, and return the hash value as an interger.
def hash(message):
    return int(sha256(message).hexdigest(), 16)

#Generate a keypair using the point P of order n on the given curve. The priveate key is a
#positive integer d smaller than n, and the public key is Q = dP.
def generate_keypair(curve, P, n):
    d = randrange(1, n)
    Q = curve.mult(P, d)
    print "Priv key: " + str(d)
    print "Publ key: " + str(Q)
    return (d, Q)

#Create a digital signature for the string message using a given curve with a distinguished
#point P which generates a prime order subgroup of size n.
def sign(message, curve, P, n, keypair):
    #Extract the private and public keys from the keypair.
    (d, Q) = keypair

    #Hash the message, convert the hash value to a bitstring, take only the L leftmost bits,
    #where L is the bit length of n, and convert that bitstring to an integer.
    h = hash(message)
    b = bin(h)[2:len(bin(n))]
    z = int(b, 2)

    #Choose a random multiple of P and sign the message with Q, r, and s.
    r, s = 0, 0
    while r == 0 or s == 0:
        k = randrange(1, n)
        R = curve.mult(P, k)
        r = R.x % n
        s = (mult_inv(k, n) * (z + r*d)) % n

    print 'Sig: (' + str(Q) + ', ' + str(r) + ', ' + str(s) + ')'
    return (Q, r, s)

#Verify the string message is authentic, given an ECDSA signature generated using a curve with
#a distinguished point P that generates a prime order subgroup of size n.
def verify(message, curve, P, n, sig):
    Q, r, s = sig

    #Confirm that Q is on the curve.
    if Q.inf or not curve.contains(Q):
        return False

    #Confirm that Q has order that divides n.
    if not curve.mult(Q,n) == Point.atInfinity():
        return False

    #Confirm that r and s are at least in the acceptable range.
    if r > n or s > n:
        return False

    #Hash the message, convert to a bitstring, select the leftmost bits to create an positive
    #integer z which is smaller than n.
    h = hash(message)
    b = bin(h)[2:len(bin(n))]
    z = int(b, 2)

    w = mult_inv(s, n) % n
    u_1 = z * w % n
    u_2 = r * w % n

    C_1 = curve.mult(P, u_1)
    C_2 = curve.mult(Q, u_2)

    C = curve.add(C_1, C_2)
    return r % n == C.x % n
