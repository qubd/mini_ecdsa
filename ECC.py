#mini_ecdsa.py must to be in the same folder with this file.
from mini_ecdsa import *;			#this script have dependency from mini_ecdsa.py, and can working with functions, which contains there.

'''
										Elliptic-Curve Cryptography (ECC) implementation - draft version.

To make encryption and decryption messages, on the elliptic curve in finite field,
need to encode and decode this data, as a points, which are contains on this elliptic-curve.

If EC, like secp256k1, have the "n" unique points, and if "n" - this is a "prime number",
then in the "semigroup" of "abel-group on this EC", there is "(n-1)/2" unique points with "unique coodinates".
In the "second semigroup" of this EC, there is a points, which are "inverted" of the points in the first semigroup.
This "inverted points" have the "same X-coodinates", but "parity of Y-coorinate" is inverted.


"""
#	See the following example code:
# Generate all points for small curve
C = CurveOverFp(0, 0, 7, 211);		#(y^2) mod p = (x^3 + 7) mod p
P = Point(150, 22);					#generator point, which "contains" on the curve.
n = C.order(P)						#points on the curve.
print("\n\nSmall curve: "+str(C), "\nP: Point"+str(P), "\npoints: n = "+str(n));

for i in range(0, n):
	point = C.mult(P, i);
	print(str(i)+" * P = "+str(point)+"\t\tis on curve: "+str(C.contains(point)),"; y_parity:", (point.y%2));
"""

quote:
  ...
	95 * P = (180,38)               is on curve: True ; y_parity: 0
	96 * P = (187,113)              is on curve: True ; y_parity: 1
	97 * P = (22,59)                is on curve: True ; y_parity: 1
	98 * P = (126,37)               is on curve: True ; y_parity: 1
	99 * P = (31,141)               is on curve: True ; y_parity: 1
	100 * P = (31,70)               is on curve: True ; y_parity: 0
	101 * P = (126,174)             is on curve: True ; y_parity: 0
	102 * P = (22,152)              is on curve: True ; y_parity: 0
	103 * P = (187,98)              is on curve: True ; y_parity: 0
	104 * P = (180,173)             is on curve: True ; y_parity: 1
  ...

As you can see, points (99*P and 100*P, 98*P and 101*P, ..., etc...)
have the same "X-coordinates", but different "Y-coordinates", and the "parity of Y" for this points are inverted.
That means, in one semigroup, there is maximum (n-1)/2 unique "X-coordinates", with values from 0 up to p (211).
Also, that means, each point from (0 up to n) "can be encoded" as "one number": (x*2 + y_parity_bit).

But, not all nubmers from [0-p] can be encoded as one point, which contains on elliptic curve.
And... Each number from 0-p can be writted as: x = k*c + r,
where c - qotient, k - divisor (2 by default), r - remainder (from 0 to k-1. Minumum is two variants if k = 2: 0 and 1);
That means, each number from 0 to p, can be divided to 2,
and c (which is lesser than p/2) can be encoded as point with x-coordinate from 0 to n, if this point contains on curve.
Else, possible to continue divide the number, with add sequence of remainders (one from excluded points - 0 or 1).

In this case, each number can be encoded as sequence of the points on elliptic cutve in finite field.
Decoding is the reversive operation, because all points are contains on the curve, and have specified X and Y coordinates.

After encoding the message on elliptic curve, result array with points can be encrypted,
by multiply all points to secret scalar contant.
	k*P = Q;
Reversive operation for decripting the points, is division the result-points for this scalar constant:
	Q/k = Q * k^(-1) mod p = Q * mult_inv(k, n);

Meaning this all, each message can be splitted by blocks with values from 0 up to p,
because the coordinates for each point have values from 0 to p.

The following code is implementation of ECC encryption and decryption (text and numbers), using small curve and secp256k1 (bitcoin elliptic-curve).

Summarry:
____________________________________________________________________________
pre-defined:	elliptic curve parameters; array with excluded points; key;
ciphertext:		array with numbers or ciphertext string
message:		number or text_string
encryption:		message -> array with points * key -> array with numbers -> ciphertext string = ciphertext;
decryption:		ciphertext -> array with numbers -> array with points / key -> decode array with points = message.
____________________________________________________________________________
To exchange the key, can be used Elliptic-Curve Diffie-Hellman (ECDH): https://github.com/username1565/ecdh
See working demo - here: https://username1565.github.io/ECDH/
'''

"""
#example code to encode text to hex and decode hex to text.

import binascii;
m_hex = binascii.hexlify(m.encode("utf-8"));
print("m_hex: ", m_hex);	#hex

decrypted_message = binascii.unhexlify(m_hex).decode('utf8')
print("decrypted_message: ", decrypted_message);			#text
"""

import random;	#need to generate points and numbers, using random.randrange()

#Generate array with unique excluded points.
#This points need to encode all numbers from 0 up to p, as points, which contains on elliptic-curve.
def generate_excluded_points(C, N='random'):
	N = random.randrange(3, C.char) if (N=='random' or (not(isinstance(N, int)))) else N;
	
	if(N<3):
		print("Mimumum 3 points needed.");
		N = 3;

	array = [];

	in_array = 0;
	while(len(array)<N):
		
		if(in_array>10 and len(array)>3):	#not lesser than 3 points must be generated 2 minimum + 1 as marker.
			print("Too many points already exists in array. Return array.");
			break;
		random_x = random.randrange(0, C.char);
		random_y_parity = random.randrange(0, 2);
		point = C.get_point_by_X(random_x, random_y_parity);
		is_on_curve = C.contains(point);
		if(is_on_curve and (not(point in array)) and (point.inf==False)):				#points on curve, whithout duplicates, and O
			array.append(point);
		elif(point.inf==True):															#if O - remove it.
			array.pop(0);
		elif(not(point in array)):														#if already exists
			in_array+=1;
#			print("point", point, " already exists in array. Skip.");
			continue;
		elif(is_on_curve==False):														#if not contains.
#			print("point", point, " not contains on curve. Skip.");
			continue;

	#show array in console.
	print("\nexcluded_points_array contains", len(array), "points.");

	print("\nexcluded_points_array = [\n", end = '');
	for i in range(0, len(array)):
		is_on_curve = C.contains(array[i]);
		print("\tPoint"+str(array[i])+(", " if i!=len(array)-1 else "")+"\n", end = '');
	print("];\n\n");
	
	#input("Array with points was been generated. Press Enter to continue...")			#pause and continue after press any key...
	return array;

#	By default key = 1, and points just will be encoded.
#	Else, if key!==0 and 0<key<=(p-1), then kP = Q, where P - encoded points, Q - encrypted points.
def encode_or_and_encrypt(C, x, excluded_points_array, key=1):	#x - number up to p, encoded - array with arrays with numbers of encoded points.
	encoded = [];
	if(int(x%C.char) != x):
		print("Encoding error, x =", x, ">=", C.char, "break;");
		return [];
	else:
		temp_point = C.get_point_by_X(x//2, x%2);
		encrypted_temp_point = C.mult(temp_point, key);
		is_on_curve = C.contains(encrypted_temp_point);
		temp_point_was_found_in_excluded_points = False;
		for item in range(0, len(excluded_points_array)):
			if( ( temp_point.x == excluded_points_array[item].x ) and ( temp_point.y == excluded_points_array[item].y )):
				temp_point_was_found_in_excluded_points = True;
				break;
			else:
				continue;
		if((is_on_curve) and (temp_point_was_found_in_excluded_points == False) and (encrypted_temp_point.inf==False)):
			encoded.append( int(int(encrypted_temp_point.x*2)+int(encrypted_temp_point.y%2)) );
		else: 
			remainder_index = int(x % (len(excluded_points_array)-1));
			excluded_point = excluded_points_array[remainder_index];
			excluded_point = C.mult(excluded_point, key);
			excluded_point_as_int = int(int(excluded_point.x*2)+int(excluded_point.y%2));
			encoded.append(excluded_point_as_int);
			new_x_coordinate = int((x-remainder_index)//(len(excluded_points_array)-1));
			if(new_x_coordinate == 0):
				encoded.append(0);
			else:
				new_sequence = encode_or_and_encrypt(C, new_x_coordinate, excluded_points_array, key);
				for i in range(0, len(new_sequence)):
					encoded.append(new_sequence[i]);
	return encoded;


import math;		#need for math.pow()
#	By default key = 1, and points just will be encoded.
#	Else, if key!==0 and 0<key<=(p-1), then kP = Q, where P - encoded points, Q - encrypted points.
def decode_or_and_decrypt(C, encoded, excluded_points_array, n, key=1): #encoded - array with arrays with numbers of encoded points, decoded - number, up to p
	decoded = int(0);
	for i in range(0, len(encoded)):
		x = encoded[i]//2;
		parity_bit = encoded[i]%2;
		current_point = C.get_point_by_X(x, parity_bit);
		current_point = C.divide_point(current_point, key, n);
		x_was_found_in_excluded_points = False;
		for item in range(0, len(excluded_points_array[:-1])):
			if( ( current_point.x == excluded_points_array[item].x ) and ( current_point.y == excluded_points_array[item].y ) ):
				x_was_found_in_excluded_points = True;
				break;
			else:
				continue;
		if( x_was_found_in_excluded_points == True ):
			decoded += int( int(excluded_points_array.index(current_point)) * int(math.pow((len(excluded_points_array)-1), i)) );
		elif(current_point.inf):
			decoded += int(0);
		elif(C.contains(current_point)):
			decoded += int( (int(current_point.x) * 2 + int(current_point.y%2) ) * int(math.pow((len(excluded_points_array)-1), i)) );
	return decoded;

import binascii		#need to encode to hex, and decode from hex.
def text_encode(m, C, excluded_points_array, key=1):
	hex = binascii.hexlify(m.encode());
	integer = int(hex, 16);
	points = [];
	encrypted_marker = C.mult(excluded_points_array[len(excluded_points_array)-1], key);

	while(True):
		points.append(int(int(encrypted_marker.x*2)+int(encrypted_marker.y%2)));
		new_integer = integer%C.char;
		current_points = encode_or_and_encrypt(C, new_integer, excluded_points_array, key);
		for i in range(0, len(current_points)):
			points.append(current_points[i]);
		if(integer%C.char == integer): break;
		integer = integer//C.char;
	return points;

def text_decode(c, C, excluded_points_array, n, key=1):
	result = 0;
	decoded = 0;
	current_array = [];
	encrypted_marker = C.mult(excluded_points_array[len(excluded_points_array)-1], key);
	encrypted_marker = int(int(encrypted_marker.x*2)+int(encrypted_marker.y%2));
	for i in range(len(c)-1, -1, -1):
		if(c[i]==encrypted_marker):
			decoded = decode_or_and_decrypt(C, current_array, excluded_points_array, n, key);
			result = int( int( int( int(result) * int(C.char) ) ) + int(decoded) );
			
			current_array = [];
			continue;
		else:
			current_array.insert(0,c[i]);
	return bytearray.fromhex(hex(result)[2::]).decode();
	
def int_encode(m, C, excluded_points_array, key=1):
	integer = m;
	points = [];
	encrypted_marker = C.mult(excluded_points_array[len(excluded_points_array)-1], key);

	while(True):
		points.append(int(int(encrypted_marker.x*2)+int(encrypted_marker.y%2)));
		new_integer = integer%C.char;
		current_points = encode_or_and_encrypt(C, new_integer, excluded_points_array, key);
		for i in range(0, len(current_points)):
			points.append(current_points[i]);
		if(integer%C.char == integer): break;
		integer = integer//C.char;
	return points;

def int_decode(c, C, excluded_points_array, n, key=1):
	result = 0;
	decoded = 0;
	current_array = [];
	encrypted_marker = C.mult(excluded_points_array[len(excluded_points_array)-1], key);
	encrypted_marker = int(int(encrypted_marker.x*2)+int(encrypted_marker.y%2));
	for i in range(len(c)-1, -1, -1):
		if(c[i]==encrypted_marker):
			decoded = decode_or_and_decrypt(C, current_array, excluded_points_array, n, key);
			result = int( int( int( int(result) * int(C.char) ) ) + int(decoded) );
			current_array = [];
			continue;
		else:
			current_array.insert(0,c[i]);
	return result;

#____	____	____	____	____	____	____	____	____	____	____	____


#encode array with numbers, of encoded points, contains on elliptic curve - encode this as string.
def array_to_string(array, C, excluded_points_array, key=1, hex_marker="h", point_marker="p"): #optional parameters to encode are default, if not specified.

	encrypted_marker = C.mult(excluded_points_array[len(excluded_points_array)-1], key);
	marker_num = int(int(encrypted_marker.x*2)+int(encrypted_marker.y%2));
	marker_hex = hex(marker_num)[2::];
	#print("marker_hex", marker_hex);		#"0x"
	string = "";
	for i in range(0, len(array)):
		string += hex_marker.join(hex(array[i]).split("0x"));
	string = point_marker.join(string.split(hex_marker+marker_hex))
	return string;
	
#decode string to array with numbers, with encoded points, contains on elliptic curve.
def array_from_string(string, C, excluded_points_array, key=1, hex_marker="h", point_marker="p"): #optional parameters to encode are default, if not specified.
	encrypted_marker = C.mult(excluded_points_array[len(excluded_points_array)-1], key);
	marker_num = int(int(encrypted_marker.x*2)+int(encrypted_marker.y%2));
	marker_hex = hex(marker_num)[2::];
	#print("marker_hex", marker_hex);		#"0x"
	string = (hex_marker+marker_hex).join(string.split(point_marker));
	return [int(x, 16) for x in (string.split(hex_marker))[1:]];

"""
#usage:
from random import randrange;
maximum = 100000000000000000000000000000000000000000000000000000000000000;
array = [randrange(0, maximum), randrange(0, maximum), randrange(0, maximum), randrange(0, maximum), randrange(0, maximum)];
print ("array", array);

# "array -> to string";
string = array_to_string(array);
print("string: ", string);

#back "string -> to array" ???
array2 = array_from_string(string);
print("array2", array2);
print("array==array2", array==array2);
"""
#____	____	____	____	____	____	____	____	____	____	____	____


#import random		#already imported.
import string

def randomString(stringLength=10):						#generate random string with specified length
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

"""
#usage:
print ("Random String is ", randomString() )
print ("Random String is ", randomString(10) )
print ("Random String is ", randomString(10) )
"""

# Run tests_mini_ecdsa.py to test the functions in included mini_ecdsa.py
# Run tests_ECC.py to test Elliptic-Curve Encryption functions from this ECC.py
