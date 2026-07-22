import unittest
import json
from main import create_app
from models import db, User, TuitionPost
from auth import generate_password_hash, generate_token

class AdminAndRolesTestCase(unittest.TestCase):

    def setUp(self):
        """Set up in-memory database and test client before each test."""
        self.app = create_app(db_uri='sqlite:///:memory:')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create test users
        self.client_user = User(
            name="Test Client User",
            email="test_client@example.com",
            password_hash=generate_password_hash("password123"),
            role="client",
            is_blocked=False
        )
        self.tutor_user = User(
            name="Test Tutor User",
            email="test_tutor@example.com",
            password_hash=generate_password_hash("password123"),
            role="tutor",
            is_blocked=False
        )
        self.admin_user = User(
            name="Test Admin User",
            email="test_admin@example.com",
            password_hash=generate_password_hash("password123"),
            role="admin",
            is_blocked=False
        )

        db.session.add_all([self.client_user, self.tutor_user, self.admin_user])
        db.session.commit()

        # Generate JWT tokens
        self.client_token = generate_token(self.client_user.id)
        self.tutor_token = generate_token(self.tutor_user.id)
        self.admin_token = generate_token(self.admin_user.id)

    def tearDown(self):
        """Clean up database after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 1. Client registration succeeds
    def test_01_client_registration_succeeds(self):
        payload = {
            "name": "New Client",
            "email": "new_client@example.com",
            "password": "password123",
            "role": "client"
        }
        res = self.client.post('/api/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['role'], 'client')

    # 2. Tutor registration succeeds
    def test_02_tutor_registration_succeeds(self):
        payload = {
            "name": "New Tutor",
            "email": "new_tutor@example.com",
            "password": "password123",
            "role": "tutor"
        }
        res = self.client.post('/api/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['role'], 'tutor')

    # 3. Public admin registration is rejected
    def test_03_public_admin_registration_rejected(self):
        payload = {
            "name": "Hacker Admin",
            "email": "hacker@example.com",
            "password": "password123",
            "role": "admin"
        }
        res = self.client.post('/api/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], "Invalid account role")

    # 4. Client can create a tuition post
    def test_04_client_can_create_tuition_post(self):
        payload = {
            "title": "Need Class 10 Math Tutor",
            "student_class": "Class 10",
            "subjects": "Math",
            "location": "Dhanmondi, Dhaka",
            "monthly_salary": 8000,
            "teaching_mode": "Offline",
            "days_per_week": 4
        }
        res = self.client.post(
            '/api/tuition-posts',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.client_token}'}
        )
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['post']['title'], "Need Class 10 Math Tutor")

    # 5. Tutor cannot create a tuition post
    def test_05_tutor_cannot_create_tuition_post(self):
        payload = {
            "title": "Tutor Trying To Post",
            "student_class": "Class 8",
            "subjects": "English",
            "location": "Mirpur, Dhaka",
            "monthly_salary": 5000,
            "teaching_mode": "Online",
            "days_per_week": 3
        }
        res = self.client.post(
            '/api/tuition-posts',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.tutor_token}'}
        )
        self.assertEqual(res.status_code, 403)
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertIn("Only clients can create tuition posts", data['error'])

    # 6. Unauthenticated user cannot create a tuition post
    def test_06_unauthenticated_user_cannot_create_post(self):
        payload = {"title": "No Auth Post", "student_class": "Class 5", "subjects": "All", "location": "Gulshan", "monthly_salary": 4000, "teaching_mode": "Offline", "days_per_week": 3}
        res = self.client.post('/api/tuition-posts', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 401)

    # 7. Client can retrieve only their own tuition posts
    def test_07_client_retrieves_own_tuition_posts(self):
        post = TuitionPost(
            user_id=self.client_user.id,
            title="Client Post 1",
            student_class="Class 9",
            subjects="Physics",
            location="Uttara",
            monthly_salary=6000,
            teaching_mode="Offline",
            days_per_week=3,
            status="open"
        )
        db.session.add(post)
        db.session.commit()

        res = self.client.get('/api/tuition-posts/my-posts', headers={'Authorization': f'Bearer {self.client_token}'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['posts']), 1)

    # 8. Admin can open the admin dashboard API
    def test_08_admin_can_open_admin_dashboard(self):
        res = self.client.get('/api/admin/dashboard', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('total_users', data)

    # 9. Client cannot open admin APIs
    def test_09_client_cannot_open_admin_apis(self):
        res = self.client.get('/api/admin/dashboard', headers={'Authorization': f'Bearer {self.client_token}'})
        self.assertEqual(res.status_code, 403)

    # 10. Tutor cannot open admin APIs
    def test_10_tutor_cannot_open_admin_apis(self):
        res = self.client.get('/api/admin/dashboard', headers={'Authorization': f'Bearer {self.tutor_token}'})
        self.assertEqual(res.status_code, 403)

    # 11. Admin can view users
    def test_11_admin_can_view_users(self):
        res = self.client.get('/api/admin/users', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 3)

    # 12. Admin can block a normal user
    def test_12_admin_can_block_user(self):
        res = self.client.patch(
            f'/api/admin/users/{self.tutor_user.id}/status',
            data=json.dumps({"is_blocked": True}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['user']['is_blocked'])

    # 13. Admin cannot block their own account
    def test_13_admin_cannot_block_own_account(self):
        res = self.client.patch(
            f'/api/admin/users/{self.admin_user.id}/status',
            data=json.dumps({"is_blocked": True}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertIn("Cannot block your own admin account", data['error'])

    # 14. Blocked user cannot access protected APIs
    def test_14_blocked_user_cannot_access_apis(self):
        self.client_user.is_blocked = True
        db.session.commit()

        res = self.client.get('/api/tuition-posts/my-posts', headers={'Authorization': f'Bearer {self.client_token}'})
        self.assertEqual(res.status_code, 403)
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertIn("blocked", data['error'])

    # 15. Admin can view all tuition posts
    def test_15_admin_can_view_all_tuition_posts(self):
        post = TuitionPost(user_id=self.client_user.id, title="Post 1", student_class="9", subjects="Math", location="Dhanmondi", monthly_salary=5000, teaching_mode="Offline", days_per_week=3)
        db.session.add(post)
        db.session.commit()

        res = self.client.get('/api/admin/tuition-posts', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 1)

    # 16. Admin can close a tuition post
    def test_16_admin_can_close_tuition_post(self):
        post = TuitionPost(user_id=self.client_user.id, title="Post Open", student_class="9", subjects="Math", location="Banani", monthly_salary=5000, teaching_mode="Online", days_per_week=3, status="open")
        db.session.add(post)
        db.session.commit()

        res = self.client.patch(
            f'/api/admin/tuition-posts/{post.id}/status',
            data=json.dumps({"status": "closed"}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['post']['status'], 'closed')

    # 17. Admin can delete a tuition post
    def test_17_admin_can_delete_tuition_post(self):
        post = TuitionPost(user_id=self.client_user.id, title="Post Delete", student_class="9", subjects="Math", location="Banani", monthly_salary=5000, teaching_mode="Online", days_per_week=3)
        db.session.add(post)
        db.session.commit()

        res = self.client.delete(f'/api/admin/tuition-posts/{post.id}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIsNone(db.session.get(TuitionPost, post.id))

    # 18. Old guardian and student roles are migrated to client
    def test_18_old_roles_migrated_to_client(self):
        old_guardian = User(name="Old Guardian", email="old_guardian@example.com", password_hash="pw", role="guardian")
        old_student = User(name="Old Student", email="old_student@example.com", password_hash="pw", role="Student")
        db.session.add_all([old_guardian, old_student])
        db.session.commit()

        # Run migration check logic
        users = User.query.all()
        for u in users:
            r = (u.role or '').strip().lower()
            if r in ['guardian', 'student', 'student_guardian']:
                u.role = 'client'
        db.session.commit()

        self.assertEqual(db.session.get(User, old_guardian.id).role, 'client')
        self.assertEqual(db.session.get(User, old_student.id).role, 'client')


if __name__ == '__main__':
    unittest.main()
