import json
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Avg, Count

from .models import Question, InterviewSession, AnswerSubmission
from .ai_engine import AIScoringEngine, ConversationalInterviewerEngine


def landing_page(request):
    """Home landing page with domain picker, practice modes, and stats."""
    total_questions = Question.objects.count()
    total_sessions = InterviewSession.objects.filter(is_completed=True).count()
    avg_score = InterviewSession.objects.filter(is_completed=True).aggregate(Avg('overall_score'))['overall_score__avg'] or 0.0

    domain_counts = {
        'web_dev': Question.objects.filter(domain='web_dev').count(),
        'ds': Question.objects.filter(domain='ds').count(),
        'dsa': Question.objects.filter(domain='dsa').count(),
        'hr': Question.objects.filter(domain='hr').count(),
        'project_defense': Question.objects.filter(domain='project_defense').count(),
    }

    recent_sessions = InterviewSession.objects.filter(is_completed=True).order_by('-created_at')[:5]

    context = {
        'total_questions': total_questions,
        'total_sessions': total_sessions,
        'avg_score': round(avg_score, 1),
        'domain_counts': domain_counts,
        'recent_sessions': recent_sessions,
    }
    return render(request, 'interviews/landing.html', context)


def practice_room(request):
    """Quick Drill Practice Room with instant AI scoring."""
    domain = request.GET.get('domain', 'web_dev')
    difficulty = request.GET.get('difficulty', 'all')

    questions_qs = Question.objects.all()
    if domain != 'all':
        questions_qs = questions_qs.filter(domain=domain)
    if difficulty != 'all':
        questions_qs = questions_qs.filter(difficulty=difficulty)

    initial_question = questions_qs.order_by('?').first()

    context = {
        'initial_question': initial_question,
        'selected_domain': domain,
        'selected_difficulty': difficulty,
        'domains': Question.DOMAIN_CHOICES,
        'difficulties': Question.DIFFICULTY_CHOICES,
    }
    return render(request, 'interviews/practice_room.html', context)


def live_video_interview(request):
    """
    Immersive Live Video Call Interview:
    AI asks questions by voice, candidate answers via voice with live webcam stream.
    Zero typing required — hands-free conversational loop with real-time scoring.
    """
    domain = request.GET.get('domain', 'web_dev')
    difficulty = request.GET.get('difficulty', 'medium')
    candidate_name = request.GET.get('candidate_name', 'Placement Candidate').strip() or 'Placement Candidate'
    rounds = int(request.GET.get('rounds', 3) or 3)

    session = InterviewSession.objects.create(
        candidate_name=candidate_name,
        domain=domain,
        difficulty=difficulty,
        mode='mock',
        target_questions=rounds,
    )

    context = {
        'session': session,
        'domain': domain,
        'difficulty': difficulty,
        'candidate_name': candidate_name,
        'domain_display': dict(Question.DOMAIN_CHOICES).get(domain, domain.title()),
        'rounds': rounds,
        'domains': Question.DOMAIN_CHOICES,
        'difficulties': Question.DIFFICULTY_CHOICES,
    }
    return render(request, 'interviews/live_video_interview.html', context)


def mock_interview_room(request):
    """Full 5-Round Mock Interview with virtual panel and final scorecard."""
    domain = request.GET.get('domain', 'web_dev')
    difficulty = request.GET.get('difficulty', 'medium')
    candidate_name = request.GET.get('candidate_name', 'Placement Candidate').strip() or 'Placement Candidate'

    # Create new interview session
    session = InterviewSession.objects.create(
        candidate_name=candidate_name,
        domain=domain,
        difficulty=difficulty,
        mode='mock',
        target_questions=5,
    )

    context = {
        'session': session,
        'domain': domain,
        'difficulty': difficulty,
        'candidate_name': candidate_name,
        'domain_display': dict(Question.DOMAIN_CHOICES).get(domain, domain.title()),
    }
    return render(request, 'interviews/mock_interview.html', context)


def interview_report(request, session_id):
    """Placement Readiness Scorecard & Official Evaluation Report."""
    session = get_object_or_404(InterviewSession, id=session_id)
    submissions = session.submissions.select_related('question').all()

    # Recalculate results if needed
    if not session.is_completed and submissions.exists():
        session.calculate_results()
        session.is_completed = True
        session.save()

    # Compile domain display name
    domain_display = dict(Question.DOMAIN_CHOICES).get(session.domain, session.domain.title())

    # Build skill breakdown for radar/bar chart
    radar_data = {
        'labels': ['Technical Similarity', 'Key Concepts', 'Answer Depth', 'Communication & Structure'],
        'values': [
            session.technical_score,
            session.concept_score,
            session.depth_score,
            session.communication_score
        ]
    }

    context = {
        'session': session,
        'submissions': submissions,
        'domain_display': domain_display,
        'radar_data_json': json.dumps(radar_data),
    }
    return render(request, 'interviews/report.html', context)


def session_history(request):
    """List of all past practice and mock interview sessions."""
    sessions = InterviewSession.objects.prefetch_related('submissions').order_by('-created_at')
    
    total_completed = sessions.filter(is_completed=True).count()
    avg_score = sessions.filter(is_completed=True).aggregate(Avg('overall_score'))['overall_score__avg'] or 0.0

    context = {
        'sessions': sessions,
        'total_completed': total_completed,
        'avg_score': round(avg_score, 1),
    }
    return render(request, 'interviews/history.html', context)


def question_bank_view(request):
    """Searchable Placement Question Bank & Cheat Sheet."""
    domain = request.GET.get('domain', 'all')
    difficulty = request.GET.get('difficulty', 'all')
    search_query = request.GET.get('q', '').strip()

    questions = Question.objects.all()

    if domain != 'all':
        questions = questions.filter(domain=domain)
    if difficulty != 'all':
        questions = questions.filter(difficulty=difficulty)
    if search_query:
        questions = questions.filter(
            title__icontains=search_query
        ) | questions.filter(
            question_text__icontains=search_query
        ) | questions.filter(
            key_concepts__icontains=search_query
        )

    context = {
        'questions': questions.order_by('domain', 'difficulty'),
        'domains': Question.DOMAIN_CHOICES,
        'difficulties': Question.DIFFICULTY_CHOICES,
        'selected_domain': domain,
        'selected_difficulty': difficulty,
        'search_query': search_query,
        'total_results': questions.count(),
    }
    return render(request, 'interviews/question_bank.html', context)


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@require_GET
def api_get_question(request):
    """Returns a question by domain/difficulty or random, excluding already answered."""
    domain = request.GET.get('domain', 'all')
    difficulty = request.GET.get('difficulty', 'all')
    exclude_ids = request.GET.getlist('exclude_ids[]') or request.GET.get('exclude_ids', '').split(',')

    qs = Question.objects.all()
    if domain != 'all':
        qs = qs.filter(domain=domain)
    if difficulty != 'all':
        qs = qs.filter(difficulty=difficulty)

    clean_exclude_ids = [int(i) for i in exclude_ids if i and str(i).isdigit()]
    if clean_exclude_ids:
        qs = qs.exclude(id__in=clean_exclude_ids)

    question = qs.order_by('?').first()

    # If all questions in filter exhausted, fallback to any in domain
    if not question:
        question = Question.objects.filter(domain=domain).order_by('?').first() if domain != 'all' else Question.objects.order_by('?').first()

    if not question:
        return JsonResponse({'status': 'error', 'message': 'No questions found'}, status=404)

    return JsonResponse({
        'status': 'success',
        'question': {
            'id': question.id,
            'title': question.title,
            'domain': question.domain,
            'domain_display': question.get_domain_display(),
            'difficulty': question.difficulty,
            'difficulty_display': question.get_difficulty_display(),
            'category': question.category,
            'question_text': question.question_text,
            'hints': question.hints,
            'key_concepts_preview': question.get_key_concepts_list()[:3],
        }
    })


@csrf_exempt
@require_POST
def api_evaluate_answer(request):
    """
    Evaluates candidate's answer using Scikit-Learn NLP scoring engine.
    Saves submission and updates session if in mock mode.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    question_id = data.get('question_id')
    user_answer = data.get('user_answer', '').strip()
    answer_method = data.get('answer_method', 'typed')
    duration_seconds = int(data.get('duration_seconds', 0) or 0)
    session_id = data.get('session_id')

    if not question_id:
        return JsonResponse({'status': 'error', 'message': 'Missing question_id'}, status=400)

    question = get_object_or_404(Question, id=question_id)

    # Run Free Local NLP AI Evaluation Engine
    eval_result = AIScoringEngine.evaluate(user_answer, question)

    session = None
    if session_id:
        try:
            session = InterviewSession.objects.get(id=session_id)
        except InterviewSession.DoesNotExist:
            session = None

    # Persist submission
    sub = AnswerSubmission.objects.create(
        session=session,
        question=question,
        user_answer=user_answer,
        answer_method=answer_method,
        duration_seconds=duration_seconds,
        score=eval_result['score'],
        grade=eval_result['grade'],
        semantic_similarity=eval_result['metrics']['semantic_similarity'] / 100.0,
        concept_coverage=eval_result['metrics']['concept_coverage'] / 100.0,
        depth_score=eval_result['metrics']['depth_score'],
        structure_score=eval_result['metrics']['structure_score'],
        feedback_data=eval_result,
    )

    if session:
        session.calculate_results()

    return JsonResponse({
        'status': 'success',
        'submission_id': sub.id,
        'evaluation': eval_result,
        'session_completed': session.is_completed if session else False,
    })


@csrf_exempt
@require_POST
def api_finish_session(request):
    """Marks a mock interview session as completed and computes verdict."""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    session_id = data.get('session_id')
    session = get_object_or_404(InterviewSession, id=session_id)
    session.calculate_results()
    session.is_completed = True
    session.save()

    return JsonResponse({
        'status': 'success',
        'redirect_url': f'/interview/report/{session.id}/',
        'overall_score': session.overall_score,
        'verdict': session.verdict,
    })


@csrf_exempt
@require_POST
def api_realtime_check(request):
    """
    Analyzes candidate's streaming words in real time.
    Allows AI interviewer to politely interrupt if candidate goes off-topic,
    starts rambling, makes a critical factual blunder, or says 'I don't know'.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    question_id = data.get('question_id')
    partial_transcript = data.get('partial_transcript', '').strip()
    word_count = int(data.get('word_count', 0) or 0)
    turn_index = int(data.get('turn_index', 1) or 1)

    if not question_id:
        return JsonResponse({'status': 'error', 'message': 'Missing question_id'}, status=400)

    question = get_object_or_404(Question, id=question_id)
    result = ConversationalInterviewerEngine.detect_realtime_interruption(
        partial_transcript, question, word_count, turn_index
    )
    return JsonResponse({'status': 'success', **result})


@csrf_exempt
@require_POST
def api_turn_response(request):
    """
    Processes a completed candidate conversational turn.
    Classifies response (CORRECT, PARTIALLY_CORRECT, INCORRECT, VAGUE, OFF_TOPIC, STRONG, IDONTKNOW, RAMBLING).
    Returns conversational interviewer dialogue to speak aloud and indicates whether
    to probe deeper (turn 2) or advance to next question.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    question_id = data.get('question_id')
    candidate_answer = data.get('candidate_answer', '').strip()
    session_id = data.get('session_id')
    turn_index = int(data.get('turn_index', 1) or 1)
    conversation_history = data.get('conversation_history', [])

    if not question_id:
        return JsonResponse({'status': 'error', 'message': 'Missing question_id'}, status=400)

    question = get_object_or_404(Question, id=question_id)
    turn_eval = ConversationalInterviewerEngine.evaluate_conversational_turn(
        candidate_answer, question, turn_index, conversation_history
    )

    session = None
    if session_id:
        try:
            session = InterviewSession.objects.get(id=session_id)
        except InterviewSession.DoesNotExist:
            session = None

    # Save or update submission for this question
    sub = None
    if session:
        sub = session.submissions.filter(question=question).first()

    if not sub:
        sub = AnswerSubmission.objects.create(
            session=session,
            question=question,
            user_answer=candidate_answer,
            answer_method='voice_call',
            duration_seconds=int(data.get('duration_seconds', 0) or 0),
            score=turn_eval['score_data']['score'],
            grade=turn_eval['score_data']['grade'],
            semantic_similarity=turn_eval['score_data']['metrics']['semantic_similarity'] / 100.0,
            concept_coverage=turn_eval['score_data']['metrics']['concept_coverage'] / 100.0,
            depth_score=turn_eval['score_data']['metrics']['depth_score'],
            structure_score=turn_eval['score_data']['metrics']['structure_score'],
            feedback_data=turn_eval['score_data'],
            turn_history=[{
                'turn': turn_index,
                'candidate_answer': candidate_answer,
                'category': turn_eval['category'],
                'interviewer_speech': turn_eval['interviewer_speech'],
            }],
        )
    else:
        existing_history = sub.turn_history or []
        existing_history.append({
            'turn': turn_index,
            'candidate_answer': candidate_answer,
            'category': turn_eval['category'],
            'interviewer_speech': turn_eval['interviewer_speech'],
        })
        sub.turn_history = existing_history
        sub.user_answer = f"{sub.user_answer}\n[Follow-Up]: {candidate_answer}"
        if turn_eval['score_data']['score'] > sub.score:
            sub.score = turn_eval['score_data']['score']
            sub.grade = turn_eval['score_data']['grade']
            sub.feedback_data = turn_eval['score_data']
        sub.save()

    if session:
        session.calculate_results()

    return JsonResponse({
        'status': 'success',
        'category': turn_eval['category'],
        'interviewer_speech': turn_eval['interviewer_speech'],
        'action': turn_eval['action'],
        'verdict_label': turn_eval['verdict_label'],
        'score_data': turn_eval['score_data'],
        'submission_id': sub.id,
    })


@csrf_exempt
@require_POST
def api_log_presence(request):
    """
    Logs camera attention events (looking away, face not detected, multiple faces)
    and updates professional interviewer behavioral notes for the scorecard.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    session_id = data.get('session_id')
    event_type = data.get('event_type')
    timestamp = data.get('timestamp')
    details = data.get('details', '')

    if not session_id:
        return JsonResponse({'status': 'error', 'message': 'Missing session_id'}, status=400)

    try:
        session = InterviewSession.objects.get(id=session_id)
    except InterviewSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)

    log = session.presence_log or []
    log.append({
        'type': event_type,
        'timestamp': timestamp,
        'details': details,
    })
    session.presence_log = log
    session.behavioral_notes = ConversationalInterviewerEngine.generate_behavioral_summary(log)
    session.save()

    return JsonResponse({
        'status': 'success',
        'warnings_count': len(log),
        'behavioral_notes': session.behavioral_notes,
    })

