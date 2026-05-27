#include "Player.h"
#include "Enemy.h"
#include <iostream>

int Player::totalPlayersCreated = 0;

Player::Player() : name("Pilot"), health(100), fuel(100), scrap(50) {
    ++totalPlayersCreated;
}

Player::Player(const std::string& name, int health, int fuel, int scrap)
    : name(name), health(health), fuel(fuel), scrap(scrap) {
    ++totalPlayersCreated;
}

// Copy constructor demonstration.
Player::Player(const Player& other)
    : name(other.name), health(other.health), fuel(other.fuel), scrap(other.scrap) {
    for (int i = 0; i < 3; ++i) inventory[i] = other.inventory[i];
    ++totalPlayersCreated;
}

Player::~Player() {
    std::cout << "[Destructor] Player '" << name << "' destroyed.\n";
}

Player& Player::operator=(const Player& rhs) {
    if (this != &rhs) {
        name = rhs.name;
        health = rhs.health;
        fuel = rhs.fuel;
        scrap = rhs.scrap;
        for (int i = 0; i < 3; ++i) inventory[i] = rhs.inventory[i];
    }
    return *this;
}

void Player::setName(const std::string& name) {
    this->name = name; // this pointer usage
}

void Player::heal() { heal(10); }
void Player::heal(int amount) {
    health += amount;
    if (health > 100) health = 100;
}

void Player::attack(Enemy& enemy) {
    int dmg = getBestDamage();
    std::cout << name << " attacks for " << dmg << " damage!\n";
    enemy.takeDamage(dmg);
}

void Player::takeDamage(int amount) {
    health -= amount;
    if (health < 0) health = 0;
}

void Player::addScrap(int amount) { scrap += amount; }

bool Player::spendScrap(int amount) {
    if (scrap < amount) return false;
    scrap -= amount;
    return true;
}

void Player::setWeaponInSlot(int idx, const Weapon& weapon) {
    if (idx >= 0 && idx < 3) inventory[idx] = weapon;
}

Weapon Player::getWeaponFromSlot(int idx) const {
    if (idx >= 0 && idx < 3) return inventory[idx];
    return Weapon();
}

int Player::getBestDamage() const {
    int best = 0;
    for (int i = 0; i < 3; ++i) if (inventory[i].getDamage() > best) best = inventory[i].getDamage();
    return best == 0 ? 8 : best;
}

const std::string& Player::getName() const { return name; }
int Player::getHealth() const { return health; }
int Player::getFuel() const { return fuel; }
int Player::getScrap() const { return scrap; }
void Player::setFuel(int newFuel) { fuel = newFuel; }

void Player::display() const {
    std::cout << "Player: " << name << " | HP: " << health << " | Fuel: " << fuel << " | Scrap: " << scrap << "\n";
    std::cout << "Inventory:\n";
    for (int i = 0; i < 3; ++i) std::cout << "  Slot " << i + 1 << ": " << inventory[i] << "\n";
}

// Friend function can access private members directly.
void showSecretPlayerData(const Player& p) {
    std::cout << "[SECRET] Name=" << p.name << ", Health=" << p.health
              << ", Fuel=" << p.fuel << ", Scrap=" << p.scrap << "\n";
}
