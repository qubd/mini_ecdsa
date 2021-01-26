mini_ecdsa
===============

Arithmetic on elliptic curves and introduction to ECDSA in Python.

*Disclaimer*: This module is a tool for learning about elliptic curves and elliptic curve cryptography. It provides a fully functional implementation of ECDSA, but don't use it as anything other than a sandbox. There are many [subtle and important implementation details](http://safecurves.cr.yp.to/index.html) that I haven't thought about.

You can find a really nice introduction to elliptic curve cryptography on [Andrea Corbellini's blog](http://andrea.corbellini.name/2015/05/17/elliptic-curve-cryptography-a-gentle-introduction/).

To use this module as is, instead of importing it for use in another project, let's open a Python console in the directory where it's stored and run the command below.

```
>>> exec(open("./mini_ecdsa.py").read())
```

To begin, we need to define a nonsingular elliptic curve over a field of prime characteristic, or over the rationals. `CurveOverFp(a,b,c,p)` will define an elliptic curve from the equation y^2 = x^3 + ax^2 + bx + c over F_p. `CurveOverQ(a,b,c)` will define a curve using the same equation over the rationals. This module assumes the coefficients a, b, and c are integers.

```
>>> C = CurveOverFp(2, 0, 1, 7)
y^2 = x^3 + 2x^2 + 1 over F_7
```

To see a list of all finite order rational points on the curve, use `C.show_points()`. This will produce a nicely printed set of points. To return a list of point objects, use `C.get_points()`. *Warning:* These functions are very computationally intensive. Use them only on curves with small discriminant, or when working over a small finite field.

```
>>> C.show_points()
['Inf', '(0,1)', '(0,6)', '(1,2)', '(1,5)', '(3,2)', '(3,5)', '(5,1)', '(5,6)', '(6,3)', '(6,4)']
```

Calling `C.torsion_group()` will classify the group of finite order rational points on a curve defined over Q, with the help of [Mazur's theorem](https://en.wikipedia.org/wiki/Torsion_conjecture#Elliptic_curves). Let's say we want to see the group of torsion points on the curve y^2 = x^3 + x + 2.

```
>>> C = CurveOverQ(0, 1, 2)
y^2 = x^3 + x + 2 over Q
>>> C.torsion_group()
Z/4Z
['Inf', '(-1,0)', '(1,2)', '(1,-2)']
```

In this case, the torsion points form a cyclic group of order four. You can also mess around with arithmetic on the curve by adding points, multiplying them by integers (remember multiplication in this context means repeated addition), and looking at the subgroup generated by a given point.

```
>>> C = CurveOverQ(0, 1, 2)
y^2 = x^3 + x + 2 over Q
>>> P = Point(-1,0)
>>> Q = Point(1,2)
>>> C.contains(P)
True
>>> C.contains(Q)
True
>>> print(C.add(P,Q))
(1,-2)
>>> print(C.mult(Q,4))
Inf
>>> C.generate(Q)
['Inf', '(-1,0)', '(1,2)', '(1,-2)']
```

ECDSA is a digital signature scheme that uses elliptic curves. It's part of SSL/TLS and so you use it every day (click the green lock next to the url in your browser). Another of its best known uses is in Bitcoin, where spending money amounts to generating a valid ECDSA signature.

To use ECDSA, we need to publicly agree on a curve over a finite field (this module works exclusively with prime characteristic fields) along with a distinguished point that generates a subgroup of prime order. Why the prime order requirement on the subgroup? As part of the signing process, we'll need to find a multiplicative inverse, and the prime order requirement guarantees this will work.

*Tiny Example*: Consider P = (1341,854) on the curve y^2 = x^3 + x + 1 over the field with 2833 elements.

```
>>> C = CurveOverFp(0, 1, 1, 2833)
y^2 = x^3 + x + 1 over F_2833
>>> P = Point(1341,854)
>>> C.contains(P)
True
>>> C.order(P)
131
```

Thus, P is on the curve, and it generates a subgroup of order 131, which is prime. The curve C, the point P, and the order of P are all public information.

To sign a message, create a private-public keypair by calling `generate_keypair`. This keypair will consist of a randomly generated positive integer d smaller than the order of P, and a point Q = dP. The pair is returned as a tuple and printed. Computing Q given d and P can be done very quickly (this module uses the [double and add method](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Double-and-add)), but at the moment, no one knows any effective and generally applicable method of computing d given P and Q. This is the [one-way function](https://en.wikipedia.org/wiki/One-way_function) that provides the theoretical security in all elliptic curve based cryptography.

```
>>> key = generate_keypair(C, P, 131)
Priv key: d = 71
Publ key: Q = (1449,1186)
```

Digital signatures generated by ECDSA consist of a public key Q as well as two positive integers, r and s, which are smaller than the order of P. These values are computed using the private key d and a hash of the message. In this implementation sha256 is the hash function being used. The signature is returned as a tuple by `sign` and also printed.

```
>>> msg = 'this is an important message'
>>> sig = sign(msg, C, P, 131, key)
ECDSA sig: (Q, r, s) = ((1449,1186), 105, 8)
```

Another randomly selected positive integer smaller than the order of P is chosen as part of the signature generation process. This value, k, is a [nonce](https://en.wikipedia.org/wiki/Cryptographic_nonce). It is crucially important to generate a new one each time a message is signed. As a consequence, if a fixed message is signed multiple times, a different signature will be produced each time. Well-known attacks on ECDSA have exploited implementations which have problems generating k.

The recipient can verify the authenticity of the message by calling `verify`, which takes a message and signature, as well as the public curve parameters, and checks that the signature is valid. Any modification of the message will, with very high probability, result in verify returning `False`.

```
>>> verify('this is an important message', C, P, 131, sig)
True
>>> verify('thiz is an important mossage', C, P, 131, sig)
False
```

*Big Example*: The curve (over a given finite field with a distinguished point) used to verify Bitcoin transactions is called secp256k1. I've been working with this curve a lot, so the classmethods `CurveOverFp.secp256k1()`, `Point.secp256k1()`, and the constant `secp256k1_order` are provided to save time, but you can also do it the hard way.

```
>>> C = CurveOverFp(0, 0, 7, 2**256-2**32-2**9-2**8-2**7-2**6-2**4-1)
y^2 = x^3 + 7 over F_115792089237316195423570985008687907853269984665640564039457584007908834671663
>>> P = Point(55066263022277343669578718895168534326250603453777594175500187360389116729240,
... 32670510020758816978083085130507043184471273380659243275938904335757337482424)
>>> n = 115792089237316195423570985008687907852837564279074904382605163141518161494337
```

There are few noteworthy things about the order of P for secp256k1. Note that it's given here, not calculated. That makes sense, since in order to find the order of a point (naively) we need to calculate iP for increasing i until we get the point at infinity. If that was actually feasible, we could crack public keys and recover d from Q in the same way, by calculating iP for increasing i until the result is Q. Calling `C.order(P)` will indeed calculate the order of P in this naive way, so don't do it unless you're prepared to wait a long time, and by long I mean universe ending long.

The order of P is also about the same as the size of the field the curve is defined over. If you've studied elliptic curves before and know about the [Hasse bound](https://en.wikipedia.org/wiki/Hasse's_theorem_on_elliptic_curves) along with a little bit of group theory, you should be able to convince yourself that the subgroup generated by P is actually the entire set of points on the curve. This is good, it means the set of private keys (possible values for d) is as large as it can be on this curve.

Generating keypairs, signing, and authenticating are all done exactly as in the tiny example.

```
>>> key = generate_keypair(C, P, n)
Priv key: 50815196737043990229212712040447958865064188767262580693117504952509239687366
Publ key: (60178516215593300273458789571475750050105656844208932820175446762050535381256,92933466624192676140900093650081093228918214155456856436706041935976250501492)
>>> msg = 'this is an important message'
>>> sig = sign(msg, C, P, n, key)
ECDSA sig: (Q, r, s) = ((60178516215593300273458789571475750050105656844208932820175446762050535381256,92933466624192676140900093650081093228918214155456856436706041935976250501492), 67756844576696401107541526159652184771668032529513958275679795576766605561987, 18515072816757752760109761447693938223957409424050002694174985246358775622034)
>>> verify('this is an important message', C, P, n, sig)
True
>>> verify('this is a faked important message', C, P, n, sig)
False
```

When you see these numbers in the wild, they are typically given as a sequence of hex bytes. In the case of Bitcoin, the private key d is stored in a Bitcoin wallet, while the public key Q goes through a [hashing procedure](https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses) and gets converted to base 58. That's what a Bitcoin address is, a point on the curve y^2 = x^3 + 7 over a really big finite field after being eaten by hash functions a few times and converted to base 58. Cool.

Also included in this module are a few methods of solving Q = dP for d, i.e. cracking a public key and recovering the private key. The group defined by the curve and point given below is small enough for brute forcing to succeed, but large enough that the process takes a few minutes on a desktop computer, so it's a nice context for comparing these key cracking methods.

```
>>> C = CurveOverFp(0, 1, 7, 729787)
y^2 = x^3 + x + 7 over F_729787
>>> P = Point(1,3)
>>> n = C.order(P)
>>> (d, Q) = generate_keypair(C, P, n)
Priv key: d = 692847
Publ key: Q = (257099,102580)
```

The `crack_brute_force` function will simply try all possible values of d in increasing order until Q = dP.

```
>>> crack_brute_force(C, P, n, Q)
Priv key: d = 692847
Time: 177.963 secs
```

The baby-step giant-step method works by using a hash table to trade space for time. It's particularly easy to implement since python has hash tables nicely built in as dictionaries.

```
>>> crack_baby_giant(C, P, n, Q)
Priv key: d = 692847
Time: 0.356 secs
```

In this example, the baby-step giant-step method performs well, but in larger examples the memory requirements become problematic, and simply constructing the hash table can take an enourmous amount of time. At some point the time-space tradeoff becomes unfeasible however you slice it.

Pollard's rho method manages to acheive the same aymptotic time complexity while eschewing the memory issues completely. It incorporates a clever idea called the [tortoise and hare algorithm](https://en.wikipedia.org/wiki/Cycle_detection#Tortoise_and_hare) to find two distinct linear combinations of P and Q that produce the same point, so aP + bQ = cP + dQ. Isolating Q yields the private key. The last argument to the function, `bits`, is used to create a small list of randomly generated linear combinations of P and Q, of length 2^bits. This list is then used to define an iterating function on the curve (for details, see section 4.1.2 of Menezes, Hankerson, and Vanstone's Guide to Elliptic Curve Cryptography).

```
>>> crack_rho(C, P, n, Q, 4)
Priv key: d = 692847
Time: 0.077 secs
```

Finally, there is a method to recover the private key from a pair of messages signed using the same value of k, called `crack_from_ECDSA_repeat_k`. This is a very quick calculation, using only a few lines of modular arithmetic and no iteration or arithmetic on the curve at all.
