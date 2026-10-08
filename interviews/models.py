import uuid
from django.db import models


class Question(models.Model):
    DOMAIN_CHOICES = [
        ('web_dev', 'Web Development'),
        ('ds', 'Data Science & ML'),
        ('dsa', 'Data Structures & Algorithms'),
        ('hr', 'HR & Behavioral'),
        ('project_defense', 'Live Demo: Project Defense'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    domain = models.CharField(max_length=50, choices=DOMAIN_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    title = models.CharField(max_length=255)
    question_text = models.TextField()
    category = models.CharField(max_length=100, default='Core Concepts')
    key_concepts = models.TextField(help_text="Comma or newline-separated expected concepts/terms")
    model_answer = models.TextField(help_text="Gold-standard interviewer model answer")
    hints = models.TextField(blank=True, default='')
    rubric_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['domain', 'difficulty', 'id']

    def __str__(self):
        return f"[{self.get_domain_display()} - {self.get_difficulty_display()}] {self.title}"

    def get_key_concepts_list(self):
        """Returns clean list of key concepts for evaluation."""
        if not self.key_concepts:
            return []
        raw_items = [item.strip() for item in self.key_concepts.replace('\n', ',').split(',')]
        return [item for item in raw_items if item]


class InterviewSession(models.Model):
    MODE_CHOICES = [
        ('drill', 'Quick Drill'),
        ('mock', 'Full Mock Interview'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate_name = models.CharField(max_length=100, default='Candidate')
    domain = models.CharField(max_length=50, default='web_dev')
    difficulty = models.CharField(max_length=20, default='medium')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='drill')
    target_questions = models.IntegerField(default=5)
    
    # Aggregated performance metrics (0-100)
    overall_score = models.FloatField(default=0.0)
    technical_score = models.FloatField(default=0.0)
    concept_score = models.FloatField(default=0.0)
    depth_score = models.FloatField(default=0.0)
    communication_score = models.FloatField(default=0.0)
    
    verdict = models.CharField(max_length=50, blank=True, default='Pending')
    summary_feedback = models.TextField(blank=True, default='')
    behavioral_notes = models.TextField(blank=True, default='')
    presence_log = models.JSONField(default=list, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate_name} - {self.domain} ({self.mode}) - Score: {self.overall_score:.1f}"

    def calculate_results(self):
        """Re-computes session aggregate scores based on all submissions."""
        subs = self.submissions.all()
        if not subs.exists():
            return

        count = subs.count()
        self.overall_score = round(sum(s.score for s in subs) / count, 1)
        self.technical_score = round(sum(s.semantic_similarity * 100 for s in subs) / count, 1)
        self.concept_score = round(sum(s.concept_coverage * 100 for s in subs) / count, 1)
        self.depth_score = round(sum(s.depth_score for s in subs) / count, 1)
        self.communication_score = round(sum(s.structure_score for s in subs) / count, 1)

        if self.overall_score >= 85:
            self.verdict = 'Strong Hire (Exceptional)'
        elif self.overall_score >= 70:
            self.verdict = 'Hire (Placement Ready)'
        elif self.overall_score >= 55:
            self.verdict = 'Borderline (Needs Minor Polish)'
        else:
            self.verdict = 'Needs Preparation'

        self.save()


class AnswerSubmission(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='submissions')
    user_answer = models.TextField()
    answer_method = models.CharField(max_length=20, default='typed')  # 'voice' or 'typed'
    duration_seconds = models.IntegerField(default=0)
    
    # AI Evaluator scores
    score = models.FloatField(default=0.0)  # 0 to 100
    grade = models.CharField(max_length=20, default='C')  # A+, A, B, C, Needs Improvement
    semantic_similarity = models.FloatField(default=0.0)  # 0.0 to 1.0
    concept_coverage = models.FloatField(default=0.0)     # 0.0 to 1.0
    depth_score = models.FloatField(default=0.0)          # 0 to 100
    structure_score = models.FloatField(default=0.0)      # 0 to 100
    
    feedback_data = models.JSONField(default=dict)
    turn_history = models.JSONField(default=list, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['submitted_at']

    def __str__(self):
        return f"Sub for Q{self.question_id}: {self.score:.1f}/100 ({self.grade})"
