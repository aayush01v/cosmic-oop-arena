#include "Game.h"
#include "Enemy.h"
#include "SaveSystem.h"
#include "GameException.h"
#include <cstdlib>
#include <ctime>
#include <iostream>

Game::Game() : player("Ace", 100, 100, 100), running(true) {
    std::srand(static_cast<unsigned>(std::time(nullptr)));
}

void Game::startBattle() {
    // Dynamic allocation using new: pointer to object.
    Enemy* enemy = nullptr;
    int roll = std::rand() % 4;

    if (roll == 0) enemy = new NormalEnemy();
    else if (roll == 1) enemy = new FastEnemy();
    else if (roll == 2) enemy = new TankEnemy();
    else enemy = new BossEnemy();

    std::cout << "\nA battle begins!\n";
    enemy->display();

    while (!enemy->isDead() && player.getHealth() > 0) {
        player.attack(*enemy);
        if (!enemy->isDead()) {
            // Late binding (runtime polymorphism): resolves correct derived attack() at runtime.
            enemy->attack(player);
            enemy->update();
        }
        enemy->display();
        player.display();
        std::cout << "----------------------\n";
    }

    if (enemy->isDead()) {
        int reward = enemy->getRewardScrap();
        if (BossEnemy* boss = dynamic_cast<BossEnemy*>(enemy)) reward += boss->bonusReward();
        player.addScrap(reward);
        std::cout << "You won and earned " << reward << " scrap!\n";
    } else {
        std::cout << "You lost this battle.\n";
    }

    delete enemy; // dynamic deallocation + virtual destructor chain
}

void Game::visitShop() {
    int choice = 0;
    std::cout << "1. Buy Weapon\n2. Upgrade Fuel\nChoice: ";
    std::cin >> choice;
    if (choice == 1) shop.buyWeapon(player);
    else if (choice == 2) shop.upgradePlayerFuel(player);
}

void Game::showStats() const {
    player.display();
    std::cout << "Total Players Created (static): " << Player::totalPlayersCreated << "\n";
    std::cout << "Total Enemies Created (static): " << Enemy::totalEnemiesCreated << "\n";
}

void Game::demonstrateCopyConstructor() {
    Player clone(player); // copy constructor call
    std::cout << "Cloned player via copy constructor:\n";
    clone.display();
}

void Game::demonstrateOperatorOverloading() {
    Weapon a("Alpha", 10, 10), b("Beta", 20, 20);
    Weapon c = a + b; // operator+ overloading
    std::cout << "Combined weapon: " << c << "\n";
    std::cout << "Are A and B equal? " << (a == b ? "Yes" : "No") << "\n";

    Vec2 p1(1, 2), p2(3, 4);
    Vec2 p3 = p1 + p2;
    std::cout << "Vec2 sum: " << p1 << " + " << p2 << " = " << p3 << "\n";

    // Early binding: non-virtual direct function call resolved at compile time.
    player.heal();
}

void Game::demonstrateFriendFunction() const {
    showSecretPlayerData(player);
}

void Game::run() {
    while (running) {
        std::cout << "\n=== Cosmic OOP Arena ===\n"
                  << "1. Start Battle\n"
                  << "2. Visit Shop\n"
                  << "3. Show Player Stats\n"
                  << "4. Save Game\n"
                  << "5. Load Game\n"
                  << "6. Demonstrate Copy Constructor\n"
                  << "7. Demonstrate Operator Overloading\n"
                  << "8. Demonstrate Friend Function\n"
                  << "9. Exit\n"
                  << "Choice: ";

        int choice = 0;
        std::cin >> choice;

        try {
            switch (choice) {
                case 1: startBattle(); break;
                case 2: visitShop(); break;
                case 3: showStats(); break;
                case 4: SaveSystem::savePlayer(player); std::cout << "Saved.\n"; break;
                case 5: SaveSystem::loadPlayer(player); std::cout << "Loaded.\n"; break;
                case 6: demonstrateCopyConstructor(); break;
                case 7: demonstrateOperatorOverloading(); break;
                case 8: demonstrateFriendFunction(); break;
                case 9: running = false; break;
                default: std::cout << "Invalid choice.\n";
            }
        } catch (const GameException& ex) {
            std::cout << "GameException: " << ex.what() << "\n";
        }
    }
}
