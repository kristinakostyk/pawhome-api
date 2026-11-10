from django.db import models


class Shelter(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Animal(models.Model):
    SPECIES_CHOICES = [
        ("dog", "Собака"),
        ("cat", "Кіт"),
    ]

    SEX_CHOICES = [
        ("male", "Самець"),
        ("female", "Самка"),
    ]

    STATUS_CHOICES = [
        ("available", "Шукає дім"),
        ("adopted", "Знайшов дім"),
    ]

    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.PROTECT,
        related_name="animals",
    )
    name = models.CharField(max_length=100)
    species = models.CharField(
        max_length=10,
        choices=SPECIES_CHOICES,
    )
    breed = models.CharField(max_length=100)
    age_months = models.PositiveIntegerField()
    sex = models.CharField(
        max_length=10,
        choices=SEX_CHOICES,
    )
    description = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
