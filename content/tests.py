from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser
from .models import Lesson, Test, Question

class ContentTests(TestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(username='teacher', password='password', is_teacher=True)
        self.student = CustomUser.objects.create_user(username='student', password='password', is_student=True)
        self.client = Client()

    def test_lesson_creation(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('lesson_create'), {
            'title': 'New Lesson',
            'content': 'Lesson Content'
        })
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertEqual(Lesson.objects.first().title, 'New Lesson')

    def test_test_creation(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('test_create'), {
            'title': 'New Test',
            'description': 'Test Description'
        })
        self.assertEqual(Test.objects.count(), 1)
        self.assertEqual(Test.objects.first().title, 'New Test')

    def test_student_access(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('lesson_list'))
        self.assertEqual(response.status_code, 200)

        # Student cannot create lesson
        response = self.client.get(reverse('lesson_create'))
        self.assertNotEqual(response.status_code, 200) # Should verify redirect or permission denied

    def test_take_test(self):
        # Create test with questions
        test = Test.objects.create(title="Math Test", author=self.teacher)
        q1 = Question.objects.create(
            test=test, text="2+2=?",
            option_a="3", option_b="4", option_c="5", option_d="6",
            correct_option="B"
        )
        
        self.client.login(username='student', password='password')
        
        # Test GET
        response = self.client.get(reverse('take_test', args=[test.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Test POST (Taking the test)
        response = self.client.post(reverse('take_test', args=[test.pk]), {
            f'question_{q1.id}': 'B'
        })
        
        # Check result
        from .models import Result
        result = Result.objects.first()
        self.assertEqual(result.score, 1)
        self.assertEqual(result.total_questions, 1)
        self.assertRedirects(response, reverse('result_detail', args=[result.pk]))

    def test_test_list(self):
        Test.objects.create(title="T1", author=self.teacher, description="D1")
        Test.objects.create(title="T2", author=self.teacher, description="D2")
        
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('test_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['tests']), 2)

    def test_dashboards(self):
        # Setup: Student takes a test
        test = Test.objects.create(title="T1", author=self.teacher)
        q = Question.objects.create(test=test, text="Q", option_a="A", option_b="B", option_c="C", option_d="D", correct_option="A")
        
        from .models import Result
        Result.objects.create(student=self.student, test=test, score=1, total_questions=1)
        
        # Test Student Dashboard
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 1)
        
        # Test Teacher Dashboard
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 1)

    def test_navigation(self):
        # Visitor
        response = self.client.get(reverse('home'))
        self.assertContains(response, f'href="{reverse("lesson_list")}"')
        self.assertContains(response, f'href="{reverse("test_list")}"')
        self.assertNotContains(response, 'Dashboard')
        
        # Student
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('home'))
        self.assertContains(response, f'href="{reverse("student_dashboard")}"')
        self.assertContains(response, 'Student') # Checking for badge text
        
        # Teacher
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('home'))
        self.assertContains(response, f'href="{reverse("teacher_dashboard")}"')
        self.assertContains(response, 'Teacher') # Checking for badge text
