#mini_ecdsa.py and ECC.py must to be in the same folder with this file.
from ECC import *;	#import function from ECC.py. All functions importing there too from mini_ecdsa.py.

#______________________________________________________________________________________________________________________________
#			tests Elliptic-curve encryption-decryption	
#	initialization tests.

print("_________________________________");
#		initialization of elliptic curve

'''
#smaller elliptic curve
C = CurveOverFp(0, 0, 7, 211);
P = Point(150, 22);
print("\n\n"+"smaller curve:", C, ", generator point: ", P);
n = C.order(P)
print("n", n);
#(d, Q) = generate_keypair(C, P, n); #limited value of d (max = n)
#print("d", d, "Q", Q);
'''

"""
larger elliptic curve
C = CurveOverFp(0, 1, 7, 729787)
P = Point(1,3)
n = 730819;
"""


#secp256k1 - this is a big elliptic curve, which is using bitcoin.
C = CurveOverFp.secp256k1();
P = Point.secp256k1();
n = 115792089237316195423570985008687907852837564279074904382605163141518161494337;
print("P = Point", P)
print("n =", n);
print("_________________________________");

#______________________________________________________________________________________________________________________________

#		initialization of encryption-decryption key

#import random		#already imported.

#	set key for encryption. This is scalar value - k. cyphertext: Q = kP; text: P = Q/k = Q * k^(-1) mod p = Q * mult_inv(k, n);
#key = 1;		#no key, just encode and decode. This can be not specifiec and key=1 by default.
#key = 2;		#test with some key.
key = random.randrange(1, C.char-1); 	# generate this key, not 0, because all points will be nulled then. Also not C.char (because C.char%C.char == 0)
print("\nGenerated key for encryption-decryption: ", key);					# show key.
	
'''
print("_________________________________");
#	change limit for recursion, if you see an error.
import sys;
print(sys.getrecursionlimit())		#default 1000, and this limit can be is reached.
sys.setrecursionlimit(5000)			#set this limit higher
print(sys.getrecursionlimit())		#default 1000, and this limit can be is reached.
'''

print("_________________________________");


#		generate array with excluded points

#Minumum 3 points must to be excluded.
#Two for encoding-decoding numbers, that is not a coordinates of the points, which are contains on elliptic curve,
#and one more point, as block-marker, to do descrimination the beginning of new encoded point.
#if array contains k+1 points, then:
#x = c*k + r, where x - encoded number, c - quotient, k - divisor, r - remainder point, contains in this array by index from 0 to k-1.

excluded_points_array = generate_excluded_points(C, 3);				#3 points		x = c*2 + r
#excluded_points_array = generate_excluded_points(C, 4);			#4 points		x = c*3 + r
#excluded_points_array = generate_excluded_points(C, 8);			#8 points		x = c*7 + r
#excluded_points_array = generate_excluded_points(C, 'random');		#from 3 up to p-1 (C.char)


print("_________________________________");

#______________________________________________________________________________________________________________________________

#	test encryption-decryption text

print("\n\ntest string encryption-decryption:\n");
#open_message = "test_text";										#utf-8 encoded string
open_message = randomString(50);									#random string
#open_message = randomString(5);									#shorter random string

#print("open_message =", open_message);								#show message
c = text_encode(open_message, C, excluded_points_array, key);		#encoded message - array with numbers of encoded points on curve.
#print("c =", c);													#show cypher-array

# "array -> to string";
c_string = array_to_string(c, C, excluded_points_array, key, "point_", "hex_");				#show encoded string
print("cyphertext: c_string =", c_string);							#show cyphertext

#back "string -> to array" ???
c_array = array_from_string(c_string, C, excluded_points_array, key, "point_", "hex_");		#decode array from cyphertext
print("c == c_array", (c == c_array));								#show result of comparison arrays.

decrypted_message = text_decode(c_array, C, excluded_points_array, n, key);		#decoded message from array 			- 	text of message
#decrypted_message = text_decode(c, C, excluded_points_array, n, key);			#decoded message from encoded c_array	- 	text of message
print("open_message  =", open_message, "\ndecrypted_message =", decrypted_message, "\ndecrypted_message == open_message??", decrypted_message==open_message);	#compare open_message and decrypted_message



print("_________________________________");

#______________________________________________________________________________________________________________________________

print("\n\ntest number encryption-decryption:\n");
#import random;		#already imported.

#open_message = random.randrange(0, C.char);				#up to p-parameter of elliptic curve.
open_message = random.randrange(0, math.pow(2,24));			#shorter number.
#open_message = random.randrange(0, int(math.pow(2,512)));	#message - number. Working.

#print("open_message =", open_message);							#show number
c = int_encode(open_message, C, excluded_points_array, key);	#get encrypted array - nubmers of encoded points on the elliptic curve.
#print("c =", c);												#show

# "array -> to string";
c_string = array_to_string(c, C, excluded_points_array, key);							#encode this array to string	(optional parameters are default)
print("cyphertext: c_string =", c_string);					#show cyphertext string

#back "string -> to array" ???
c_array = array_from_string(c_string, C, excluded_points_array, key, "h", "p");		#restore array from cyphertext string.
print("c == c_array", (c == c_array));						#show result of comparison arrays.

decrypted_message = int_decode(c_array, C, excluded_points_array, n, key);		#decoded message from c_array	- 	number
#decrypted_message = int_decode(c, C, excluded_points_array, n,  key);			#decoded message from c			- 	number
print(
	"open_message  =", open_message,
	"\ndecrypted_message =", decrypted_message,
	"\ndecrypted_message == open_message??", decrypted_message==open_message	#compare m and decrypted_message
);

print("_________________________________");



input("Press Enter to continue, and start 100 tests...")			#pause and continue after press any key...
#run test in cycle
import time	#to using interval
print ("Start : %s" % time.ctime())
interval = 0.1;	#seconds
for m in range(0, 100):
	print ("continue : %s" % time.ctime())
	time.sleep( interval )	# wait...
	#print("\n\n next test. Key:", key);
	#open_message = random.randrange(0, C.char);
	open_message = m;									#use i as message.
	c = int_encode(open_message, C, excluded_points_array, key);		#encoded and encrypted message 	- 	array with numbers of encoded points on curve
	decrypted_message = int_decode(c, C, excluded_points_array, n, key);		#decoded and decrypted message 	- 	i
	if(decrypted_message!=open_message):
		print("\nError found! break;")
		print("open_message", open_message, "!=", "decrypted_message", decrypted_message, "open_message =", open_message, "decrypted_message =", decrypted_message, "key", key);

		print("len(excluded_points_array)", len(excluded_points_array));
		for i in range(0, len(excluded_points_array)):
			is_on_curve = C.contains(excluded_points_array[i]);
			print("i = ", i, "excluded_points_array[i] =", excluded_points_array[i], "is_on_curve: ", is_on_curve);
		break;
	else:
		print("m", m, "(decrypted_message==open_message)", (decrypted_message==open_message));
		
	if(m%C.char==0):
		excluded_points_array = generate_excluded_points(C);		#regenerate array with excluded points.
print ("End : %s" % time.ctime())
