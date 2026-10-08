from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('interview/live/', views.live_video_interview, name='live_video_interview'),
    path('interview/practice/', views.practice_room, name='practice_room'),
    path('interview/mock/', views.mock_interview_room, name='mock_interview_room'),
    path('interview/report/<uuid:session_id>/', views.interview_report, name='interview_report'),
    path('interview/history/', views.session_history, name='session_history'),
    path('questions/', views.question_bank_view, name='question_bank'),
    
    # API Endpoints
    path('api/get-question/', views.api_get_question, name='api_get_question'),
    path('api/evaluate-answer/', views.api_evaluate_answer, name='api_evaluate_answer'),
    path('api/finish-session/', views.api_finish_session, name='api_finish_session'),
    path('api/live/realtime-check/', views.api_realtime_check, name='api_realtime_check'),
    path('api/live/turn-response/', views.api_turn_response, name='api_turn_response'),
    path('api/live/log-presence/', views.api_log_presence, name='api_log_presence'),
]

