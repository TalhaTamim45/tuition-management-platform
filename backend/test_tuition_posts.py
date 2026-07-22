import unittest
import json
from main import create_app
from models import db, User, TuitionPost
from auth import generate_password_hash, generate_token

class TuitionPostTestCase(unittest.TestCase):

    def setUp(self):
        """Set up in-memory database and test client before each test."""
        self.app = create_app(db_uri='sqlite:///:memory:')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create test users with unified 'client' and 'tutor' roles
        self.client_user = User(
            name="Client User",
            email="client_test@example.com",
            password_hash=generate_password_hash("password123"),
            role="client",
            is_blocked=False
        )
        self.tutor_user = User(
            name="Tutor User",
            email="tutor_test@example.com",
            password_hash=generate_password_hash("password123"),
            role="tutor",
            is_blocked=False
        )

        db.session.add_all([self.client_user, self.tutor_user])
        db.session.commit()

        # Generate tokens
        self.client_token = generate_token(self.client_user.id)
        self.tutor_token = generate_token(self.tutor_user.id)

    def tearDown(self):
        """Clean up database and pop app context after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_1_successful_tuition_post_creation(self):
        """Test successful tuition post creation by authenticated client."""
        payload = {
            "title": "Need Class 10 Physics & Chemistry Tutor",
            "student_class": "Class 10",
            "subjects": "Physics, Chemistry",
            "location": "Gulshan, Dhaka",
            "monthly_salary": 9000.00,
            "preferred_tutor_gender": "Female",
            "teaching_mode": "Offline",
            "days_per_week": 3,
            "additional_notes": "Needs experienced tutor."
        }
        response = self.client.post(
            '/api/tuition-posts',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.client_token}'}
        )
        self.assertEqual(response.status_code, 201)
        res_data = json.loads(response.data)
        self.assertTrue(res_data['success'])
        self.assertEqual(res_data['post']['title'], "Need Class 10 Physics & Chemistry Tutor")
        self.assertEqual(res_data['post']['status'], "open")
        self.assertEqual(res_data['post']['user_id'], self.client_user.id)

    def test_2_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        payload = {
            "title": "", # Missing title
            "student_class": "Class 8",
            "subjects": "", # Missing subjects
            "location": "Uttara, Dhaka",
            "monthly_salary": 5000,
            "teaching_mode": "Online",
            "days_per_week": 3
        }
        response = self.client.post(
            '/api/tuition-posts',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.client_token}'}
        )
        self.assertEqual(response.status_code, 400)
        res_data = json.loads(response.data)
        self.assertFalse(res_data['success'])
        self.assertIn('title', res_data['errors'])
        self.assertIn('subjects', res_data['errors'])

    def test_3_invalid_salary(self):
        """Test validation error when salary is <= 0 or invalid."""
        payload = {
            "title": "Class 7 All Subjects",
            "student_class": "Class 7",
            "subjects": "All Subjects",
            "location": "Mirpur, Dhaka",
            "monthly_salary": -500, # Invalid negative salary
            "teaching_mode": "Offline",
            "days_per_week": 4
        }
        response = self.client.post(
            '/api/tuition-posts',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.client_token}'}
        )
        self.assertEqual(response.status_code, 400)
        res_data = json.loads(response.data)
        self.assertFalse(res_data['success'])
        self.assertIn('monthly_salary', res_data['errors'])

    def test_4_invalid_days_per_week(self):
        """Test validation error when days per week is not between 1 and 7."""
        payload = {
            "title": "HSC English Tutor Needed",
            "student_class": "HSC 2nd Year",
            "subjects": "English",
            "location": "Banani, Dhaka",
            "monthly_salary": 7000,
            "teaching_mode": "Online",
            "days_per_week": 10 # Invalid days per week > 7
        }
        response = self.client.post(
            '/api/tuition-posts',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.client_token}'}
        )
        self.assertEqual(response.status_code, 400)
        res_data = json.loads(response.data)
        self.assertFalse(res_data['success'])
        self.assertIn('days_per_week', res_data['errors'])

    def test_5_unauthorized_access(self):
        """Test creating post without token or with tutor role."""
        payload = {
            "title": "Class 5 General Tutor",
            "student_class": "Class 5",
            "subjects": "General Subjects",
            "location": "Dhanmondi, Dhaka",
            "monthly_salary": 4000,
            "teaching_mode": "Offline",
            "days_per_week": 3
        }

        # Case A: Missing token
        res_no_token = self.client.post(
            '/api/tuition-posts',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res_no_token.status_code, 401)

        # Case B: Tutor user trying to post
        res_tutor = self.client.post(
            '/api/tuition-posts',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.tutor_token}'}
        )
        self.assertEqual(res_tutor.status_code, 403)

    def test_6_retrieving_my_tuition_posts(self):
        """Test fetching tuition posts created by the logged-in client."""
        post1 = TuitionPost(
            user_id=self.client_user.id,
            title="Post 1",
            student_class="Class 6",
            subjects="Math",
            location="Location 1",
            monthly_salary=5000,
            teaching_mode="Offline",
            days_per_week=3,
            status="open"
        )
        post2 = TuitionPost(
            user_id=self.client_user.id,
            title="Post 2",
            student_class="Class 7",
            subjects="Science",
            location="Location 2",
            monthly_salary=6000,
            teaching_mode="Online",
            days_per_week=4,
            status="open"
        )
        db.session.add_all([post1, post2])
        db.session.commit()

        # Retrieve my posts
        response = self.client.get(
            '/api/tuition-posts/my-posts',
            headers={'Authorization': f'Bearer {self.client_token}'}
        )
        self.assertEqual(response.status_code, 200)
        res_data = json.loads(response.data)
        self.assertTrue(res_data['success'])
        self.assertEqual(res_data['count'], 2)
        self.assertEqual(len(res_data['posts']), 2)


if __name__ == '__main__':
    unittest.main()
