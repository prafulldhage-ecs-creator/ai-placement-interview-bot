from django.core.management.base import BaseCommand
from interviews.models import Question
from interviews.question_bank import SEED_QUESTIONS


class Command(BaseCommand):
    help = 'Populates the database with curated placement interview questions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding placement interview question bank..."))
        created_count = 0
        updated_count = 0

        for q_data in SEED_QUESTIONS:
            obj, created = Question.objects.update_or_create(
                title=q_data['title'],
                defaults={
                    'domain': q_data['domain'],
                    'difficulty': q_data['difficulty'],
                    'category': q_data['category'],
                    'question_text': q_data['question_text'],
                    'key_concepts': q_data['key_concepts'],
                    'model_answer': q_data['model_answer'],
                    'hints': q_data.get('hints', ''),
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded question bank! Created: {created_count}, Updated: {updated_count}. Total in DB: {Question.objects.count()}"
        ))
