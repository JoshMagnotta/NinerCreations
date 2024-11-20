from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Topic

class SearchFunctionalityTestCase(TestCase):
    def setUp(self):
        # Set up a user
        self.user = User.objects.create_user(username="testuser", password="password")
        
        # Set up topics
        topic1 = Topic.objects.create(name="Django")
        topic2 = Topic.objects.create(name="Python")

        # Set up posts
        self.post1 = Post.objects.create(
            author=self.user,
            title="Django Testing Guide",
            content="Learn how to test Django applications."
        )
        self.post2 = Post.objects.create(
            author=self.user,
            title="Python Basics",
            content="An introductory guide to Python."
        )
        self.post3 = Post.objects.create(
            author=self.user,
            title="Advanced Python",
            content="Deep dive into Python's advanced features."
        )

        # Add topics to posts
        self.post1.topics.add(topic1)
        self.post2.topics.add(topic2)
        self.post3.topics.add(topic2)

    def test_search_with_results(self):
        # Test a search that should return some results
        response = self.client.get(reverse('search'), {'q': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.post3.title)
        self.assertNotContains(response, self.post1.title)

    def test_search_with_no_results(self):
        # Test a search that should return no results
        response = self.client.get(reverse('search'), {'q': 'Ruby'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)
        self.assertNotContains(response, self.post3.title)

    def test_search_partial_match(self):
        # Test that partial matches return appropriate results
        response = self.client.get(reverse('search'), {'q': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)
        self.assertNotContains(response, self.post3.title)

    def test_empty_query(self):
        # Test that an empty search query returns no results
        response = self.client.get(reverse('search'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['posts'], [])
