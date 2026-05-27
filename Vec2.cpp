#include "Vec2.h"

Vec2::Vec2() : x(0), y(0) {}

Vec2::Vec2(int x, int y) : x(x), y(y) {}

Vec2::Vec2(const Vec2& other) : x(other.x), y(other.y) {}

Vec2 Vec2::operator+(const Vec2& rhs) const {
    return Vec2(x + rhs.x, y + rhs.y);
}

Vec2& Vec2::operator=(const Vec2& rhs) {
    if (this != &rhs) {
        x = rhs.x;
        y = rhs.y;
    }
    return *this;
}

std::ostream& operator<<(std::ostream& os, const Vec2& v) {
    os << "(" << v.x << ", " << v.y << ")";
    return os;
}
