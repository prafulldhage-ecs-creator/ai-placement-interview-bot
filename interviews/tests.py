import json
from django.test import TestCase, Client
from django.urls import reverse
from interviews.models import Question, InterviewSession, AnswerSubmission
from interviews.ai_engine import AIScoringEngine, ConversationalInterviewerEngine


class AIScoringEngineTestCase(TestCase):
    def setUp(self):
        self.q_web = Question.objects.create(
            domain='web_dev',
            difficulty='easy',
            title='var let const in JS',
            question_text='Explain the differences between var, let, and const in JavaScript.',
            key_concepts='scope, function scope, block scope, hoisting, temporal dead zone, reassignment, let, const, var',
            model_answer=(
                "In JavaScript, 'var' is function-scoped and hoisted with undefined. "
                "'let' and 'const' are block-scoped and hoisted in the Temporal Dead Zone. "
                "'let' can be reassigned while 'const' cannot be reassigned after declaration."
            ),
            hints='Focus on scope, hoisting, and re-assignment.',
        )

        self.q_hr = Question.objects.create(
            domain='hr',
            difficulty='medium',
            title='Handling Conflict',
            question_text='Describe a situation where you had a disagreement with a peer.',
            key_concepts='situation, task, action, result, disagreement, communication, resolution',
            model_answer="In my college project (Situation), our task was to select a database...",
            hints='Use the STAR framework.',
        )

        self.q_dsa = Question.objects.create(
            domain='dsa',
            difficulty='easy',
            title='Two Sum',
            question_text='Find two numbers that add to target.',
            key_concepts='hash map, complement, time complexity O(n), space complexity O(n)',
            model_answer="Use a hash map to store visited complements in O(N) time and O(N) space.",
            hints='Use a hash map.',
        )

    def test_high_quality_answer_evaluation(self):
        answer = (
            "In JavaScript, var is function scoped and hoisted to the top with undefined. "
            "On the other hand, let and const are block scoped and live in the temporal dead zone before declaration. "
            "Variables declared with let can be reassigned, whereas const prevents reassignment."
        )
        result = AIScoringEngine.evaluate(answer, self.q_web)
        self.assertGreaterEqual(result['score'], 75.0)
        self.assertIn(result['grade'], ['A+', 'A', 'B'])
        self.assertIn('block scope', result['covered_concepts'])
        self.assertGreater(result['metrics']['concept_coverage'], 50.0)

    def test_minimal_fluff_answer_penalty(self):
        result = AIScoringEngine.evaluate("I don't know", self.q_web)
        self.assertLessEqual(result['score'], 25.0)
        self.assertEqual(result['grade'], 'Needs Work')

    def test_hr_star_heuristic_detection(self):
        star_answer = (
            "During my internship (Situation), our task was to resolve a database migration delay (Task). "
            "I decided to organize a technical benchmark and implemented connection pooling (Action). "
            "As a result, we improved query latency by 40% and delivered on time (Result)."
        )
        result = AIScoringEngine.evaluate(star_answer, self.q_hr)
        self.assertGreaterEqual(result['domain_analysis']['score'], 70.0)
        self.assertIn('star_breakdown', result['domain_analysis'])

    def test_dsa_complexity_detection(self):
        dsa_answer = (
            "I would use a hash map to store elements. For each number, we look up target - num in O(1) time. "
            "The overall time complexity is O(N) and space complexity is O(N)."
        )
        result = AIScoringEngine.evaluate(dsa_answer, self.q_dsa)
        self.assertGreaterEqual(result['domain_analysis']['score'], 70.0)


class ViewsAndAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.q = Question.objects.create(
            domain='web_dev',
            difficulty='easy',
            title='Test Question',
            question_text='What is CSS box model?',
            key_concepts='content, padding, border, margin',
            model_answer='Content, padding, border, and margin form the box model.',
        )

    def test_landing_page_renders(self):
        response = self.client.get(reverse('interviews:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Placement Interview Practice Bot')

    def test_practice_room_renders(self):
        response = self.client.get(reverse('interviews:practice_room'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quick Practice Drill')

    def test_question_bank_renders(self):
        response = self.client.get(reverse('interviews:question_bank'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Placement Interview Question Bank')

    def test_api_get_question(self):
        response = self.client.get(reverse('interviews:api_get_question'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('question', data)

    def test_api_evaluate_answer(self):
        payload = {
            'question_id': self.q.id,
            'user_answer': (
                "The CSS box model consists of four distinct layers: content in the center, "
                "surrounded by padding, then border, and finally outer margin which controls element spacing."
            ),
            'answer_method': 'typed',
            'duration_seconds': 25,
        }
        response = self.client.post(
            reverse('interviews:api_evaluate_answer'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('evaluation', data)
        self.assertGreater(data['evaluation']['score'], 60.0)

    def test_mock_interview_flow(self):
        # 1. Start mock interview
        response = self.client.get(reverse('interviews:mock_interview_room') + '?candidate_name=Alex&domain=web_dev')
        self.assertEqual(response.status_code, 200)
        session = InterviewSession.objects.first()
        self.assertIsNotNone(session)
        self.assertEqual(session.candidate_name, 'Alex')

        # 2. Submit answer to session
        payload = {
            'question_id': self.q.id,
            'user_answer': (
                "The CSS box model defines how HTML elements are structured with content, "
                "inner padding, enclosing border, and outer margin for spacing across layouts."
            ),
            'answer_method': 'voice',
            'duration_seconds': 40,
            'session_id': str(session.id),
        }
        res_sub = self.client.post(
            reverse('interviews:api_evaluate_answer'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res_sub.status_code, 200)

        # 3. Finish session
        res_finish = self.client.post(
            reverse('interviews:api_finish_session'),
            data=json.dumps({'session_id': str(session.id)}),
            content_type='application/json'
        )
        self.assertEqual(res_finish.status_code, 200)

        # 4. View report
        res_report = self.client.get(reverse('interviews:interview_report', args=[session.id]))
        self.assertEqual(res_report.status_code, 200)
        self.assertContains(res_report, 'Candidate: Alex')


class ConversationalInterviewerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.q_bs = Question.objects.create(
            domain='dsa',
            difficulty='easy',
            title='Binary Search Time Complexity',
            question_text='What is the time complexity of binary search?',
            key_concepts='binary search, time complexity, logarithmic, O(log n), divide and conquer',
            model_answer='Binary search operates in O(log n) time by dividing the search space in half each step.',
        )
        self.q_scope = Question.objects.create(
            domain='web_dev',
            difficulty='easy',
            title='Let and Var scope',
            question_text='What is the difference between let and var in JavaScript?',
            key_concepts='block scope, function scope, let, var, temporal dead zone',
            model_answer='let is block-scoped while var is function-scoped.',
        )

    def test_incorrect_binary_search_conversational_correction(self):
        candidate_speech = "O(n), because we have to search through the entire array."
        turn = ConversationalInterviewerEngine.evaluate_conversational_turn(candidate_speech, self.q_bs, turn_index=1)
        self.assertEqual(turn['category'], 'INCORRECT')
        self.assertIn("Hold on — that's not quite right", turn['interviewer_speech'])
        self.assertIn("O(log n)", turn['interviewer_speech'])
        self.assertEqual(turn['action'], 'continue_dialogue')

    def test_vague_answer_demands_precision(self):
        candidate_speech = "It makes things very good and faster."
        turn = ConversationalInterviewerEngine.evaluate_conversational_turn(candidate_speech, self.q_scope, turn_index=1)
        self.assertEqual(turn['category'], 'VAGUE')
        self.assertIn("That's a little too broad", turn['interviewer_speech'])
        self.assertEqual(turn['action'], 'continue_dialogue')

    def test_partially_correct_forces_thinking(self):
        candidate_speech = "Both are variables in javascript but one is newer than the other."
        turn = ConversationalInterviewerEngine.evaluate_conversational_turn(candidate_speech, self.q_scope, turn_index=1)
        # Partially correct or needs clarification
        self.assertIn(turn['category'], ['PARTIALLY_CORRECT', 'NEEDS_CLARIFICATION'])
        self.assertEqual(turn['action'], 'continue_dialogue')

    def test_strong_answer_probes_deeper(self):
        candidate_speech = (
            "The primary difference is scope: let is block-scoped and exists inside curly braces, "
            "whereas var is function-scoped and hoisted with undefined."
        )
        turn = ConversationalInterviewerEngine.evaluate_conversational_turn(candidate_speech, self.q_scope, turn_index=1)
        self.assertEqual(turn['category'], 'STRONG')
        self.assertIn("Good. Let's go one level deeper", turn['interviewer_speech'])
        self.assertEqual(turn['action'], 'continue_dialogue')

    def test_idontknow_supportive_then_moves_on(self):
        # Turn 1: "I don't know" -> encourages thinking
        turn1 = ConversationalInterviewerEngine.evaluate_conversational_turn("I don't know.", self.q_bs, turn_index=1)
        self.assertEqual(turn1['category'], 'IDONTKNOW')
        self.assertIn("That's okay. Let's approach it differently", turn1['interviewer_speech'])
        self.assertEqual(turn1['action'], 'continue_dialogue')

        # Turn 2: Still don't know -> moves on
        turn2 = ConversationalInterviewerEngine.evaluate_conversational_turn("I have no clue.", self.q_bs, turn_index=2)
        self.assertEqual(turn2['category'], 'IDONTKNOW')
        self.assertIn("No problem. We'll move on", turn2['interviewer_speech'])
        self.assertEqual(turn2['action'], 'advance_question')

    def test_realtime_rambling_interruption(self):
        rambling_text = (
            "javascript is a programming language and it was created in 1995 and websites use it "
            "and html is very popular and everyone learns computers long time ago..."
        )
        res = ConversationalInterviewerEngine.detect_realtime_interruption(rambling_text, self.q_scope, word_count=28, turn_index=1)
        self.assertTrue(res['should_interrupt'])
        self.assertEqual(res['category'], 'RAMBLING')
        self.assertIn("Sorry to interrupt you there", res['spoken_interruption'])

    def test_api_turn_response_endpoint(self):
        session = InterviewSession.objects.create(candidate_name="Priya", domain="dsa", mode="mock")
        payload = {
            'question_id': self.q_bs.id,
            'candidate_answer': "Binary search runs in O(log n) logarithmic time because the space halves.",
            'session_id': str(session.id),
            'turn_index': 1,
            'duration_seconds': 15,
        }
        res = self.client.post(reverse('interviews:api_turn_response'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('interviewer_speech', data)
        self.assertIn('category', data)

    def test_api_log_presence_endpoint(self):
        session = InterviewSession.objects.create(candidate_name="Priya", domain="dsa", mode="mock")
        payload = {
            'session_id': str(session.id),
            'event_type': 'looking_away',
            'timestamp': '2026-10-08T20:00:00Z',
            'details': 'Warning 1/3: Please maintain focus on the interview.',
        }
        res = self.client.post(reverse('interviews:api_log_presence'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['warnings_count'], 1)
        session.refresh_from_db()
        self.assertIn("looked away", session.behavioral_notes)

