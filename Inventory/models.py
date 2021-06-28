from django.db import models
from django.db.models import Sum, F

# Create your models here.
class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('KG', "kilograms"),
        ('L', "liters"),
        ('PSC', "pieces")
    ]
    name = models.CharField(max_length=50, unique=True)
    quantity = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    unit = models.CharField(max_length=3, choices=UNIT_CHOICES)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    total_price = models.DecimalField(editable=False, max_digits=6, decimal_places=2, blank=True, null=True)
    amount_to_add = models.DecimalField(max_digits=6, decimal_places=3, default=0, blank=True, null=True)
    update_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    last_update = models.DateTimeField(auto_now=True, editable=False)

    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"Name: {self.name}, Quantity: {self.quantity}"


class MenuItem(models.Model):
    title = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.title}, {self.price} €"

    def available(self):
        return all(X.enough() for X in self.reciperequirement_set.all())

    def food_cost(self):
        food_cost = 0
        for x in self.reciperequirement_set.all():
            food_cost += x.cost()
        return food_cost / self.price * 100

    def absolute_cost(self):
        absolute_cost = 0
        for x in self.reciperequirement_set.all():
            absolute_cost += x.cost()
        return absolute_cost


class RecipeRequirement(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=3)

    def __str__(self):
        return f"Recipe for {self.menu_item.title}: {self.ingredient.name} {self.quantity}"

    def enough(self):
        return self.quantity <= self.ingredient.quantity

    def cost(self):
        return self.quantity * self.ingredient.unit_price



class Purchase(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.menu_item.title}, {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


    def total_sum(self):
        return self.quantity * self.menu_item.price


