from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Topic, Comment, Project

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
        
class ProfilePageViewTestCase(TestCase):
    def setUp(self):
        # Set up user and login
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

        # Create posts, comments, and projects for the user
        self.post = Post.objects.create(author=self.user, title="Test Post", content="Test Content")
        self.comment = Comment.objects.create(post=self.post, author=self.user, content="Test Comment")
        self.project = Project.objects.create(user=self.user, name="Test Project", description="Test Description", github_link="https://github.com/test/project")

    def test_profile_view_access(self):
        # Test that the profile page loads successfully
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/profile.html')
        self.assertContains(response, self.user.username)

    def test_user_profile_view_access(self):
        # Test viewing a specific user's profile page
        response = self.client.get(reverse('user_profile', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/user_profile.html')
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.comment.content)
        self.assertContains(response, self.project.name)