#ifndef PLAYER_H
#define PLAYER_H

#include <string>
#include "Weapon.h"

class Enemy;

class Player {
private:
    std::string name;
    int health;
    int fuel;
    int scrap;
    Weapon inventory[3]; // array of objects

public:
    static int totalPlayersCreated; // static data member

    Player();
    Player(const std::string& name, int health, int fuel, int scrap);
    Player(const Player& other);
    ~Player();

    Player& operator=(const Player& rhs);

    void setName(const std::string& name); // uses this pointer
    void heal();
    void heal(int amount); // function overloading
    void attack(Enemy& enemy);
    void takeDamage(int amount);
    void addScrap(int amount);
    bool spendScrap(int amount);

    void setWeaponInSlot(int idx, const Weapon& weapon);
    Weapon getWeaponFromSlot(int idx) const;
    int getBestDamage() const;

    const std::string& getName() const;
    int getHealth() const;
    int getFuel() const;
    int getScrap() const;
    void setFuel(int newFuel);

    void display() const;

    friend void showSecretPlayerData(const Player& p); // friend function
};

void showSecretPlayerData(const Player& p);

#endif
