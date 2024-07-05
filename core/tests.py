from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from .constants import PYTHON_QUESTION_LIST
from .views import record_current_answer, generate_bot_responses, get_next_question, generate_final_response

class QuizBotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.session = self.client.session
        self.session['quiz_answers'] = {}
        self.session.save()

    def test_record_current_answer_valid(self):
        success, message = record_current_answer("5", 0, self.session)
        self.assertTrue(success)
        self.assertEqual(message, "Answer recorded successfully.")
        self.assertEqual(self.session['quiz_answers'][0], "5")

    def test_record_current_answer_invalid_answer_format(self):
        success, message = record_current_answer(5, 0, self.session)
        self.assertFalse(success)
        self.assertEqual(message, "Invalid answer format. Answer must be a string.")

    def test_record_current_answer_invalid_question_id_format(self):
        success, message = record_current_answer("5", "0", self.session)
        self.assertFalse(success)
        self.assertEqual(message, "Invalid question ID format. Question ID must be an integer.")

    def test_generate_bot_responses_initial(self):
        responses = generate_bot_responses("", self.session)
        self.assertIn("Welcome to the Python quiz! Let's get started.", responses)
        self.assertIn(PYTHON_QUESTION_LIST[0]["question"], responses)
        self.assertEqual(self.session["current_question_id"], 0)

    def test_generate_bot_responses_next_question(self):
        self.session["current_question_id"] = 0
        self.session.save()
        responses = generate_bot_responses("5", self.session)
        self.assertIn(PYTHON_QUESTION_LIST[1]["question"], responses)
        self.assertEqual(self.session["current_question_id"], 1)

    def test_generate_bot_responses_final_response(self):
        for i, question in enumerate(PYTHON_QUESTION_LIST):
            self.session['quiz_answers'][i] = question['correct_answer']
        self.session["current_question_id"] = len(PYTHON_QUESTION_LIST) - 1
        self.session.save()
        responses = generate_bot_responses(PYTHON_QUESTION_LIST[-1]['correct_answer'], self.session)
        self.assertIn("You've completed the quiz!", responses[-1])
        self.assertEqual(self.session.get("current_question_id"), None)

    def test_get_next_question(self):
        next_question, next_question_id = get_next_question(None)
        self.assertEqual(next_question, PYTHON_QUESTION_LIST[0])
        self.assertEqual(next_question_id, 0)

        next_question, next_question_id = get_next_question(0)
        self.assertEqual(next_question, PYTHON_QUESTION_LIST[1])
        self.assertEqual(next_question_id, 1)

        next_question, next_question_id = get_next_question(len(PYTHON_QUESTION_LIST) - 1)
        self.assertIsNone(next_question)
        self.assertIsNone(next_question_id)

    def test_generate_final_response(self):
        for i, question in enumerate(PYTHON_QUESTION_LIST):
            self.session['quiz_answers'][i] = question['correct_answer']
        final_response = generate_final_response(self.session)
        expected_score = len(PYTHON_QUESTION_LIST)
        self.assertIn(f"Your score is {expected_score} out of {expected_score}.", final_response)

