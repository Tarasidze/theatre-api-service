from django.db import models

from django.db import models


class Actor(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    class Meta:
        ordering = ["first_name"]

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return f"{self.first_name}  {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TheatreHall(models.Model):
    name = models.CharField(max_length=63)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Hall: {self.name}"


class Play(models.Model):
    title = models.CharField(max_length=63)
    description = models.TextField()
    genre = models.ManyToManyField(
        to=Genre,
        on_delete=models.DO_NOTHING,
        related_name="plays"
    )
    actor = models.ManyToManyField(
        to=Actor,
        on_delete=models.DO_NOTHING,
        related_name="plays"
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Performance(models.Model):
    show_time = models.DateTimeField(auto_now_add=True)
    play = models.ForeignKey(to=Play, on_delete=models.CASCADE, related_name="performances")
    theatre_hall = models.ForeignKey(to=TheatreHall, related_name="performances")

    class Meta:
        ordering = ["-show_time"]
