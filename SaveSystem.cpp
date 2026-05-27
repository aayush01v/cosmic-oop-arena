#include "SaveSystem.h"
#include "GameException.h"
#include <fstream>

void SaveSystem::savePlayer(const Player& player) {
    std::ofstream out("savegame.txt");
    if (!out.is_open()) throw GameException("Could not open save file for writing.");

    out << player.getName() << "\n"
        << player.getHealth() << "\n"
        << player.getFuel() << "\n"
        << player.getScrap() << "\n";

    out.close(); // explicit close
}

void SaveSystem::loadPlayer(Player& player) {
    std::ifstream in("savegame.txt");
    if (!in.is_open()) throw GameException("Could not open save file for reading.");

    std::string name;
    int health = 0, fuel = 0, scrap = 0;

    if (!std::getline(in, name) || !(in >> health >> fuel >> scrap)) {
        in.close();
        throw GameException("Save file data is invalid.");
    }

    in.close();

    if (health < 0 || fuel < 0 || scrap < 0) throw GameException("Save data contains negative values.");

    Player loaded(name, health, fuel, scrap);
    player = loaded; // assignment operator demonstration
}
