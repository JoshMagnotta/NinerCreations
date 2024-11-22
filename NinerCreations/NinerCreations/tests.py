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
        # Set up a user and login
        self.user = User.objects.create_user(username="testuser", password="password")
        self.other_user = User.objects.create_user(username="otheruser", password="password")
        self.client.login(username="testuser", password="password")

        # Create posts, comments, and projects for each user
        self.post = Post.objects.create(author=self.user, title="Test Post", content="Test Content")
        self.comment = Comment.objects.create(post=self.post, author=self.user, content="Test Comment")
        self.project = Project.objects.create(user=self.user, name="Test Project", description="Test Description", github_link="https://github.com/test/project")

        # Other user's content
        self.other_post = Post.objects.create(author=self.other_user, title="Other User Post", content="Other Content")
        self.other_comment = Comment.objects.create(post=self.other_post, author=self.other_user, content="Other Comment")
        self.other_project = Project.objects.create(user=self.other_user, name="Other User Project", description="Other Description", github_link="https://github.com/otheruser/project")

    def test_profile_view_access(self):
        # Test that the profile page loads successfully for the logged-in user
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/profile.html')
        self.assertContains(response, self.user.username)

    def test_user_profile_view_access(self):
        # Test viewing the logged-in user's profile page
        response = self.client.get(reverse('user_profile', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/user_profile.html')
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.comment.content)
        self.assertContains(response, self.project.name)

    def test_view_another_users_profile(self):
        # Test viewing another user's profile page
        response = self.client.get(reverse('user_profile', args=[self.other_user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/user_profile.html')
        self.assertContains(response, self.other_user.username)
        self.assertContains(response, self.other_post.title)
        self.assertContains(response, self.other_comment.content)
        self.assertContains(response, self.other_project.name)
        
    def test_create_project(self):
        # Test creating a new project
        response = self.client.post(reverse('add_project'), {
            'project_name': 'New Test Project',
            'project_description': 'This is a test project description.',
            'project_link': 'https://github.com/test/new-test-project'
        })

        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.assertTrue(Project.objects.filter(name='New Test Project').exists())
        project = Project.objects.get(name='New Test Project')
        self.assertEqual(project.description, 'This is a test project description.')
        self.assertEqual(project.github_link, 'https://github.com/test/new-test-project')
        self.assertEqual(project.user, self.user)

    def test_edit_project(self):
        # Create a project to edit
        project = Project.objects.create(
            user=self.user, 
            name="Test Project", 
            description="Original Description", 
            github_link="https://github.com/test/original"
        )
        
        # Test editing the project
        response = self.client.post(reverse('edit_project', args=[project.id]), {
            'project_name': 'Updated Project Name',
            'project_description': 'Updated Description',
            'project_link': 'https://github.com/test/updated'
        })

        self.assertEqual(response.status_code, 302)  # Should redirect after success
        project.refresh_from_db()
        self.assertEqual(project.name, 'Updated Project Name')
        self.assertEqual(project.description, 'Updated Description')
        self.assertEqual(project.github_link, 'https://github.com/test/updated')

    def test_delete_project(self):
        # Create a project to delete
        project = Project.objects.create(
            user=self.user, 
            name="Test Project to Delete", 
            description="Delete Me", 
            github_link="https://github.com/test/delete-me"
        )
        
        # Test deleting the project
        response = self.client.post(reverse('delete_project', args=[project.id]))
        
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.assertFalse(Project.objects.filter(id=project.id).exists())