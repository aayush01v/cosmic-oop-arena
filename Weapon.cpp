#include "Weapon.h"

Weapon::Weapon() : name("Rusty Blaster"), damage(10), price(0) {}

Weapon::Weapon(const std::string& name, int damage, int price)
    : name(name), damage(damage), price(price) {}

Weapon::Weapon(const Weapon& other)
    : name(other.name), damage(other.damage), price(other.price) {}

bool Weapon::operator==(const Weapon& rhs) const {
    return name == rhs.name && damage == rhs.damage && price == rhs.price;
}

Weapon Weapon::operator+(const Weapon& rhs) const {
    return Weapon(name + "-" + rhs.name, damage + rhs.damage, price + rhs.price);
}

const std::string& Weapon::getName() const { return name; }
int Weapon::getDamage() const { return damage; }
int Weapon::getPrice() const { return price; }

std::ostream& operator<<(std::ostream& os, const Weapon& w) {
    os << w.name << " (DMG: " << w.damage << ", Price: " << w.price << ")";
    return os;
}
