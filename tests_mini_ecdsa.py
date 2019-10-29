#mini_ecdsa.py must to be in the same folder with this file.
from mini_ecdsa import *;

#tests the fucntions in mini_ecdsa.py
def run_test():
    print("_____________________")
	#smaller elliptic curve
    C = CurveOverFp(0, 0, 7, 211);
    P = Point(150, 22);
    print("\n\n", "smaller curve:", C, ", generator point: ", P);

    n = C.order(P)
    print("n", n);

    (d, Q) = generate_keypair(C, P, n); #limited value of d (max = n)
    print("d", d, "Q", Q);
	
    print("\ntest brute_force:");
    crack_brute_force(C, P, n, Q, 150, 100);

    print("\ntest BSGS:");
    crack_baby_giant(C, P, n, Q);

    print("\ntest pollard_rho:");
    crack_rho(C, P, n, Q, 1);

    (d1, Q1) = generate_keypair(C, P, n);
    print("d1", d1, "Q1", Q1);
	
    print("\ntest subtraction:", Q.__eq__(C.add(C.subtract(Q, Q1),Q1)));
    print("\ntest divide:", Q.__eq__(C.mult(C.divide_point(Q, d1, n), d1)));

    print("test get_Y (even Y):", C.getY(Q1.x, 0));
    print("test get_point_by_X (odd Y):", C.get_point_by_X(Q1.x, 1));
    print("test is on curve?:", C.contains(Point(Q1.x, C.getY(Q1.x,0))), C.contains(C.get_point_by_X(Q1.x,1)));
    print("test is on curve (pow_mod)?:", C.contains(Point(Q1.x, C.getY(Q1.x,0))), C.contains(C.get_point_by_X(Q1.x,1)));
    print("_____________________")
#end function

run_test();	#result of one test just as demo

"""
# test many random points with many iterations.
import time	#to using interval
interval = 0.5;	#seconds
# run tests
print ("Start : %s" % time.ctime())
for i in range(0, 100):
	print ("continue : %s" % time.ctime())
	time.sleep( interval )	# wait...
	run_test();				# repeat test again, after some time
print ("End : %s" % time.ctime())
"""