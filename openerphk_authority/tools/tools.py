# -*- coding: utf-8 -*-

import random


class RandomNumberGenerator:
    def __init__(self, generated_numbers: list[str]):
        self.generated_numbers = set(generated_numbers)
        self.item = []

    def generate_item(self, generate_qty: int = 1) -> list[str]:
        while len(self.item) < generate_qty:
            random_number = f"{random.randint(0, 999999):06d}"
            if random_number not in self.generated_numbers:
                self.item.append(random_number)
                self.generated_numbers.add(random_number)
        return self.item
