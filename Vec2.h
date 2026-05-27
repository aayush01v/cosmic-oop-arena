#ifndef VEC2_H
#define VEC2_H

#include <iostream>

class Vec2 {
private:
    int x;
    int y;

public:
    Vec2();
    Vec2(int x, int y);
    Vec2(const Vec2& other); // copy constructor

    Vec2 operator+(const Vec2& rhs) const; // operator overloading
    Vec2& operator=(const Vec2& rhs);      // object assignment

    inline int getX() const { return x; } // inline function
    inline int getY() const { return y; }

    friend std::ostream& operator<<(std::ostream& os, const Vec2& v);
};

#endif
