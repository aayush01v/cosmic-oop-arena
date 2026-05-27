#include "Shop.h"
#include <iostream>

Shop::Shop() {
    availableWeapons[0] = Weapon("Pulse Rifle", 18, 30);
    availableWeapons[1] = Weapon("Ion Cannon", 25, 50);
    availableWeapons[2] = Weapon("Plasma Lance", 35, 80);
}

void Shop::showItems() const {
    std::cout << "--- Shop Items ---\n";
    for (int i = 0; i < 3; ++i) std::cout << i + 1 << ". " << availableWeapons[i] << "\n";
}

void Shop::buyWeapon(Player& player) {
    showItems();
    std::cout << "Choose weapon index (1-3): ";
    int choice;
    std::cin >> choice;
    if (choice < 1 || choice > 3) return;

    Weapon w = availableWeapons[choice - 1];
    if (!player.spendScrap(w.getPrice())) {
        std::cout << "Not enough scrap!\n";
        return;
    }

    std::cout << "Choose inventory slot (1-3): ";
    int slot; std::cin >> slot;
    player.setWeaponInSlot(slot - 1, w);
    std::cout << "Purchased " << w.getName() << "\n";
}

void Shop::upgradePlayerFuel(Player& player) {
    const int cost = 20;
    if (player.spendScrap(cost)) {
        player.setFuel(player.getFuel() + 20);
        std::cout << "Fuel upgraded by 20!\n";
    } else {
        std::cout << "Not enough scrap for fuel upgrade.\n";
    }
}
