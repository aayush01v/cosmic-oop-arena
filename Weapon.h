#ifndef WEAPON_H
#define WEAPON_H

#include <iostream>
#include <string>

class Weapon {
private:
    std::string name;
    int damage;
    int price;

public:
    Weapon();
    Weapon(const std::string& name, int damage, int price);
    Weapon(const Weapon& other); // copy constructor

    bool operator==(const Weapon& rhs) const;
    Weapon operator+(const Weapon& rhs) const; // combines weapon stats

    const std::string& getName() const;
    int getDamage() const;
    int getPrice() const;

    friend std::ostream& operator<<(std::ostream& os, const Weapon& w);
};

#endif
