var x1 >=0 ;
var x2 >=0 ;
var x3 >=0 ;
var x4 >=0 ;
var x5 >=0 ;
var x6 >=0 ;
var x7 >=0 ;
var x8 >=0 ;
var x9 >=0 ;
var x10 >=0 ;
var x11 >=0 ;
var x12 >=0 ;
var x13 >=0 ;
maximize obj: 0.0  + 3.0 * x1   -3.0 * x2   + 2.0 * x3   -4.0 * x4   + 3.0 * x5   + 1.0 * x6   + 4.0 * x7 ;
c1: x8 = -1.0  -3.0 * x1  + 7.0 * x2  + 6.0 * x3  + 6.0 * x4  -7.0 * x5  + 2.0 * x6  + 4.0 * x7 ;
c2: x9 = 24.0  + 0.0 * x1  -9.0 * x2  + 1.0 * x3  + 5.0 * x4  -9.0 * x5  -7.0 * x6  -10.0 * x7 ;
c3: x10 = 19.0  + 5.0 * x1  -5.0 * x2  + 0.0 * x3  -4.0 * x4  -5.0 * x5  + 4.0 * x6  -10.0 * x7 ;
c4: x11 = 19.0  -5.0 * x1  + 9.0 * x2  + 4.0 * x3  -6.0 * x4  -3.0 * x5  + 4.0 * x6  -9.0 * x7 ;
c5: x12 = -25.0  + 8.0 * x1  -6.0 * x2  + 0.0 * x3  -1.0 * x4  + 6.0 * x5  + 3.0 * x6  + 10.0 * x7 ;
c6: x13 = 8.0  + 3.0 * x1  -10.0 * x2  -8.0 * x3  + 2.0 * x4  -2.0 * x5  -1.0 * x6  + 10.0 * x7 ;
solve; 
display 0.0  + 3.0 * x1   -3.0 * x2   + 2.0 * x3   -4.0 * x4   + 3.0 * x5   + 1.0 * x6   + 4.0 * x7 ;
 
 end; 
