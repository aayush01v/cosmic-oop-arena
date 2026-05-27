#ifndef ENEMY_H
#define ENEMY_H

#include <string>
#include "GameObject.h"

class Player;

class Enemy : public GameObject {
protected:
    std::string type;
    int health;
    int damage;
    int rewardScrap;

public:
    static int totalEnemiesCreated;

    Enemy(const std::string& type, int health, int damage, int rewardScrap, const Vec2& pos);
    virtual ~Enemy();

    virtual void attack(Player& player) = 0;
    virtual void display() const override;
    void takeDamage(int amount);
    bool isDead() const;

    int getRewardScrap() const;
};

class NormalEnemy : public Enemy {
public:
    NormalEnemy();
    void update() override;
    void attack(Player& player) override;
};

class FastEnemy : public Enemy {
public:
    FastEnemy();
    void update() override;
    void attack(Player& player) override;
};

class TankEnemy : public Enemy {
public:
    TankEnemy();
    void update() override;
    void attack(Player& player) override;
};

class RewardGiver {
public:
    virtual int bonusReward() const = 0; // abstract interface
    virtual ~RewardGiver() = default;
};

class BossEnemy : public Enemy, public RewardGiver { // multiple inheritance
public:
    BossEnemy();
    void update() override;
    void attack(Player& player) override;
    int bonusReward() const override;
};

#endif
