#ifndef GAMEOBJECT_H
#define GAMEOBJECT_H

#include "Vec2.h"

// Abstract class: contains pure virtual functions and cannot be instantiated directly.
class GameObject {
protected:
    Vec2 position; // protected member accessible by child classes

public:
    GameObject() : position() {}
    explicit GameObject(const Vec2& pos) : position(pos) {}

    // Pure virtual functions
    virtual void update() = 0;
    virtual void display() const = 0;

    virtual ~GameObject() = default;
};

#endif
