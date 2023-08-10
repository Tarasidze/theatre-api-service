from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from performance.models import Play, Genre, Actor
from performance.serializers import PlayListSerializer, PlayDetailSerializer


PLAY_URL = reverse("performance:play-list")


def detail_url(play_id: int):
    return reverse("performance:play-detail", args=[play_id])


def sample_play(**params) -> Play:
    defaults = {
        "title": "Interstellar",
        "description": "Best play ever",
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_genre(**param) -> Genre:
    defaults = {
        "name": "Drama"
    }
    defaults.update(param)

    return Genre.objects.create(**defaults)


def sample_actor(**param) -> Actor:
    defaults = {
        "first_name": "Charlie",
        "last_name": "Chaplin",
    }
    defaults.update(param)

    return Actor.objects.create(**defaults)


class UnAuthenticatedPlayViesSet(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedplayViewSet(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "hans@zimmer.com",
            "inception",
        )

        self.play1 = sample_play(title="play1")
        self.play2 = sample_play(title="play2")
        self.play3 = sample_play()

        self.genre1 = sample_genre(name="genre1")
        self.genre2 = sample_genre(name="genre2")

        self.actor1 = sample_actor(first_name="first_one", last_name="last_one")
        self.actor2 = sample_actor(first_name="first_two", last_name="last_two")

        self.client.force_authenticate(self.user)

    def test_list_plays(self):
        sample_play()

        play_with_genre = sample_play()
        play_with_genre.genres.add(self.genre1, self.genre2)

        play_with_actor = sample_play()
        play_with_actor.actors.add(self.actor1, self.actor2)

        result = self.client.get(PLAY_URL)

        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_play_filter_by_title(self):
        result = self.client.get(PLAY_URL, {"title": "play"})

        serializer1 = PlayListSerializer(self.play1)
        serializer2 = PlayListSerializer(self.play2)
        serializer3 = PlayListSerializer(self.play3)

        self.assertIn(serializer1.data, result.data)
        self.assertIn(serializer2.data, result.data)
        self.assertNotIn(serializer3.data, result.data)

    def play_filter_by_genre(self):
        play_with_genre1 = self.play1.genres.add(self.genre1)
        play_with_genre2 = self.play2.genres.add(self.genre2)
        play_without_genre = self.play3

        result = self.client.get(PLAY_URL,
                                 {"genres": f"{self.genre1.id},{self.genre2.id}"})

        serializer1 = PlayListSerializer(play_with_genre1)
        serializer2 = PlayListSerializer(play_with_genre2)
        serializer3 = PlayListSerializer(play_without_genre)

        self.assertIn(serializer1.data, result.data)
        self.assertIn(serializer2.data, result.data)
        self.assertNotIn(serializer3.data, result.data)

    def movi_filter_by_actor(self):
        play_with_actor1 = self.play1.actors.add(self.actor1)
        play_with_actor2 = self.play1.actors.add(self.actor2)
        play_without_actor = self.play3

        result = self.client.get(PLAY_URL,
                                 {"actors": f"{self.actor1.id},{self.actor2.id}"})

        serializer1 = PlayListSerializer(play_with_actor1)
        serializer2 = PlayListSerializer(play_with_actor2)
        serializer3 = PlayListSerializer(play_without_actor)

        self.assertIn(serializer1.data, result.data)
        self.assertIn(serializer2.data, result.data)
        self.assertNotIn(serializer3.data, result.data)

    def test_retrieve_play_detail(self):
        play = sample_play()
        play.genres.add(sample_genre())

        url = detail_url(play.id)
        result = self.client.get(url)

        serializer = PlayDetailSerializer(play)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self. assertEqual(result.data, serializer.data)

    def test_create_play_forbidden(self):
        payload = {
            "title": "title",
            "description": "description",
        }

        result = self.client.post(PLAY_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminplayApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "password",
            is_staff=True,
        )

        self.play1 = sample_play(title="play1")
        self.genre1 = sample_genre(name="genre1")
        self.actor1 = sample_actor(first_name="first_one", last_name="last_one")

        self.client.force_authenticate(self.user)

    def test_create_play(self):
        payload = {
            "title": "title",
            "description": "description",
            "genres": self.genre1.id,
            "actors": self.actor1.id,
        }

        result = self.client.post(PLAY_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_delete_play_not_allowed(self):
        play = self.play1

        url = detail_url(play.id)

        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)