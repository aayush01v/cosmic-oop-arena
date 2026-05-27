#include "Enemy.h"
#include "Player.h"
#include <iostream>

int Enemy::totalEnemiesCreated = 0;

Enemy::Enemy(const std::string& type, int health, int damage, int rewardScrap, const Vec2& pos)
    : GameObject(pos), type(type), health(health), damage(damage), rewardScrap(rewardScrap) {
    ++totalEnemiesCreated;
}

Enemy::~Enemy() {
    std::cout << "[Destructor] Enemy '" << type << "' destroyed.\n";
}

void Enemy::display() const {
    std::cout << type << " at " << position << " | HP: " << health << " | DMG: " << damage << "\n";
}

void Enemy::takeDamage(int amount) { health -= amount; }
bool Enemy::isDead() const { return health <= 0; }
int Enemy::getRewardScrap() const { return rewardScrap; }

NormalEnemy::NormalEnemy() : Enemy("NormalEnemy", 40, 10, 20, Vec2(1, 1)) {}
void NormalEnemy::update() { position = position + Vec2(1, 0); }
void NormalEnemy::attack(Player& player) { player.takeDamage(damage); std::cout << type << " attacks!\n"; }

FastEnemy::FastEnemy() : Enemy("FastEnemy", 30, 12, 25, Vec2(2, 2)) {}
void FastEnemy::update() { position = position + Vec2(2, 0); }
void FastEnemy::attack(Player& player) { player.takeDamage(damage + 3); std::cout << type << " quick-strikes!\n"; }

TankEnemy::TankEnemy() : Enemy("TankEnemy", 80, 8, 35, Vec2(0, 3)) {}
void TankEnemy::update() { position = position + Vec2(0, 1); }
void TankEnemy::attack(Player& player) { player.takeDamage(damage); std::cout << type << " heavy-hits!\n"; }

BossEnemy::BossEnemy() : Enemy("BossEnemy", 150, 20, 100, Vec2(5, 5)) {}
void BossEnemy::update() { position = position + Vec2(1, 1); }
void BossEnemy::attack(Player& player) { player.takeDamage(damage + 10); std::cout << type << " unleashes cosmic cannon!\n"; }
int BossEnemy::bonusReward() const { return 75; }
