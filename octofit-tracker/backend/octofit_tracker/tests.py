from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User, Team, Activity, Leaderboard, Workout


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            fitness_level='beginner'
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.fitness_level, 'beginner')
        self.assertEqual(self.user.total_points, 0)
    
    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')


class TeamModelTest(TestCase):
    """Test cases for Team model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.team = Team.objects.create(
            name='Test Team',
            description='A test team',
            created_by=self.user
        )
    
    def test_team_creation(self):
        """Test team is created correctly"""
        self.assertEqual(self.team.name, 'Test Team')
        self.assertEqual(self.team.created_by, self.user)
        self.assertEqual(self.team.total_points, 0)
    
    def test_team_str(self):
        """Test team string representation"""
        self.assertEqual(str(self.team), 'Test Team')
    
    def test_add_member(self):
        """Test adding a member to a team"""
        member = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='testpass123'
        )
        self.team.members.add(member)
        self.assertEqual(self.team.members.count(), 1)
        self.assertIn(member, self.team.members.all())


class ActivityModelTest(TestCase):
    """Test cases for Activity model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.activity = Activity.objects.create(
            user=self.user,
            activity_type='running',
            duration=30,
            distance=5.0,
            calories_burned=300,
            date=timezone.now()
        )
    
    def test_activity_creation(self):
        """Test activity is created correctly"""
        self.assertEqual(self.activity.user, self.user)
        self.assertEqual(self.activity.activity_type, 'running')
        self.assertEqual(self.activity.duration, 30)
    
    def test_points_calculation(self):
        """Test activity points are calculated correctly"""
        # Points should be calculated based on duration and type
        # 30 minutes / 10 * 1.5 (running multiplier) = 4.5 -> 4 points
        self.assertEqual(self.activity.points_earned, 4)
    
    def test_user_points_update(self):
        """Test user total points are updated after activity creation"""
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 4)


class WorkoutModelTest(TestCase):
    """Test cases for Workout model"""
    
    def setUp(self):
        self.workout = Workout.objects.create(
            name='Beginner HIIT',
            description='High intensity interval training for beginners',
            difficulty_level='beginner',
            category='hiit',
            duration=20,
            exercises=['jumping jacks', 'burpees', 'mountain climbers'],
            equipment_needed=['mat'],
            target_muscles=['legs', 'core', 'cardio']
        )
    
    def test_workout_creation(self):
        """Test workout is created correctly"""
        self.assertEqual(self.workout.name, 'Beginner HIIT')
        self.assertEqual(self.workout.difficulty_level, 'beginner')
        self.assertEqual(len(self.workout.exercises), 3)
    
    def test_workout_str(self):
        """Test workout string representation"""
        self.assertEqual(str(self.workout), 'Beginner HIIT (beginner)')


class UserAPITest(APITestCase):
    """Test cases for User API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            fitness_level='beginner'
        )
    
    def test_get_users_list(self):
        """Test retrieving users list"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_user_detail(self):
        """Test retrieving a single user"""
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_create_user(self):
        """Test creating a new user"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'fitness_level': 'intermediate'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)


class TeamAPITest(APITestCase):
    """Test cases for Team API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.team = Team.objects.create(
            name='Test Team',
            description='A test team',
            created_by=self.user
        )
    
    def test_get_teams_list(self):
        """Test retrieving teams list"""
        response = self.client.get('/api/teams/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_team(self):
        """Test creating a new team"""
        data = {
            'name': 'New Team',
            'description': 'A new test team',
            'created_by_id': self.user.id
        }
        response = self.client.post('/api/teams/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 2)


class ActivityAPITest(APITestCase):
    """Test cases for Activity API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.activity = Activity.objects.create(
            user=self.user,
            activity_type='running',
            duration=30,
            distance=5.0,
            calories_burned=300,
            date=timezone.now()
        )
    
    def test_get_activities_list(self):
        """Test retrieving activities list"""
        response = self.client.get('/api/activities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_activity(self):
        """Test creating a new activity"""
        data = {
            'user_id': self.user.id,
            'activity_type': 'cycling',
            'duration': 45,
            'distance': 15.0,
            'calories_burned': 400,
            'date': timezone.now().isoformat()
        }
        response = self.client.post('/api/activities/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Activity.objects.count(), 2)


class WorkoutAPITest(APITestCase):
    """Test cases for Workout API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.workout = Workout.objects.create(
            name='Beginner HIIT',
            description='High intensity interval training',
            difficulty_level='beginner',
            category='hiit',
            duration=20,
            exercises=['jumping jacks', 'burpees'],
            equipment_needed=['mat'],
            target_muscles=['legs', 'core']
        )
    
    def test_get_workouts_list(self):
        """Test retrieving workouts list"""
        response = self.client.get('/api/workouts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_filter_workouts_by_difficulty(self):
        """Test filtering workouts by difficulty"""
        response = self.client.get('/api/workouts/?difficulty=beginner')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_workout_suggestions(self):
        """Test getting workout suggestions"""
        response = self.client.get('/api/workouts/suggestions/?fitness_level=beginner')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
