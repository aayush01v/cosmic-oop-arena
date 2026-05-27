# Cosmic OOP Arena

A console-based, turn-based C++17 space battle game built to demonstrate core university-level OOP concepts.

## Build

```bash
g++ -std=c++17 *.cpp -o CosmicOOPArena
```

## Run

```bash
./CosmicOOPArena
```

## Concept Mapping Table

| # | C++ Concept | Where it is used |
|---|---|---|
| 1 | class and object | All classes; object instances in `Game`, `Shop`, `main` |
| 2 | constructors | `Vec2`, `Weapon`, `Player`, `Enemy`, `Game`, `Shop` |
| 3 | parameterized constructors | `Vec2(int,int)`, `Weapon(name,damage,price)`, `Player(name,...)`, `Enemy(...)` |
| 4 | destructors | `Player::~Player`, `Enemy::~Enemy`, virtual destructors in base classes |
| 5 | copy constructor | `Vec2(const Vec2&)`, `Weapon(const Weapon&)`, `Player(const Player&)` |
| 6 | object assignment | `Vec2::operator=`, `Player::operator=`, `player = loaded` in `SaveSystem::loadPlayer` |
| 7 | friend function | `showSecretPlayerData(const Player&)`, `operator<<` in `Vec2` and `Weapon` |
| 8 | static data member | `Player::totalPlayersCreated`, `Enemy::totalEnemiesCreated` |
| 9 | array of objects | `Weapon inventory[3]` in `Player`, `Weapon availableWeapons[3]` in `Shop` |
| 10 | pointer to object | `Enemy* enemy` in `Game::startBattle` |
| 11 | this pointer | `Player::setName` |
| 12 | reference parameter | `Player::attack(Enemy& enemy)`, `Enemy::attack(Player& player)` |
| 13 | dynamic allocation new/delete | `new NormalEnemy/FastEnemy/...` and `delete enemy` in `Game::startBattle` |
| 14 | operator overloading | `Vec2::operator+`, `Vec2::operator=`, `Weapon::operator==`, `Weapon::operator+`, `operator<<` |
| 15 | function overloading | `Player::heal()` and `Player::heal(int)` |
| 16 | inline function | `Vec2::getX`, `Vec2::getY` in header |
| 17 | inheritance | `Enemy : public GameObject`; enemy subclasses from `Enemy` |
| 18 | protected members | `GameObject::position`, `Enemy` protected stats |
| 19 | multiple inheritance | `BossEnemy : public Enemy, public RewardGiver` |
| 20 | virtual functions | `Enemy::display`, virtual destructors, `GameObject` virtual methods |
| 21 | pure virtual functions | `GameObject::update/display`, `Enemy::attack`, `RewardGiver::bonusReward` |
| 22 | abstract class | `GameObject`, `Enemy`, `RewardGiver` |
| 23 | early binding | non-virtual call `player.heal()` in `Game::demonstrateOperatorOverloading` |
| 24 | late binding | `enemy->attack(player)` in battle loop |
| 25 | exception handling | `try/catch` in `Game::run`; throws `GameException` in `SaveSystem` |
| 26 | fstream file handling | `std::ofstream`/`std::ifstream` in `SaveSystem` |
| 27 | opening and closing files | `is_open()` checks and explicit `close()` in `SaveSystem` |
| 28 | reading and writing text files | Save and load player data from `savegame.txt` |

