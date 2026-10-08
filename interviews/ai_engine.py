import re
import math
import string
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AIScoringEngine:
    """
    Zero-Cost, 100% Free & Offline AI Interview Scoring Engine.
    Uses multi-factor NLP evaluation:
      1. TF-IDF Cosine Semantic Similarity (Sklearn)
      2. Domain Key Concept & Technical Keyword Spotting
      3. Depth, Completeness & Vocabulary Density
      4. Domain-Specific Structural Heuristics (STAR for HR, Big-O for DSA, etc.)
    Provides recruiter-grade feedback, actionable suggestions, and model answer comparison.
    """

    # Domain-specific structural markers
    STAR_PATTERNS = {
        'Situation': [r'\b(when i was|during my|at my|in our team|in a project|in college|while working)\b', r'\b(situation|context|scenario|background)\b'],
        'Task': [r'\b(my role|my task|responsible for|needed to|had to|objective was|the goal was|challenge was)\b', r'\b(assigned|expected to|deadline)\b'],
        'Action': [r'\b(i decided|i implemented|i built|i initiated|i took|i resolved|i communicated|i designed|i stepped in)\b', r'\b(action|strategy|approach|solution)\b'],
        'Result': [r'\b(as a result|ultimately|the outcome|we achieved|improved by|successfully|learned that|delivered|increased|reduced)\b', r'\b(impact|benefit|feedback)\b'],
    }

    COMPLEXITY_PATTERNS = [
        r'o\s*\(\s*(1|n|log\s*n|n\s*log\s*n|n\^2|2\^n|v\s*\+\s*e)\s*\)',
        r'time\s+complexity',
        r'space\s+complexity',
        r'constant\s+time',
        r'linear\s+time',
        r'logarithmic',
        r'quadratic',
    ]

    EDGE_CASE_PATTERNS = [
        r'\b(edge case|corner case|null|empty|boundary|overflow|duplicate|negative|base case|empty array|single element)\b'
    ]

    WEB_ARCH_PATTERNS = [
        r'\b(client|server|stateless|rest|http|request|response|database|cache|latency|async|render|dom|state|token|auth|security|middleware)\b'
    ]

    DS_METRIC_PATTERNS = [
        r'\b(accuracy|precision|recall|f1|roc|auc|loss|overfitting|underfitting|regularization|cross\s*validation|hyperparameter|bias|variance)\b'
    ]

    @classmethod
    def evaluate(cls, user_answer: str, question_obj) -> dict:
        """
        Evaluates a candidate's answer against a Question instance.
        Returns a rich scoring dictionary.
        """
        user_text = (user_answer or '').strip()
        model_text = question_obj.model_answer.strip()
        key_concepts = question_obj.get_key_concepts_list()
        domain = question_obj.domain
        difficulty = question_obj.difficulty

        # Handle blank or extremely short evasive responses
        words = re.findall(r'\b[a-zA-Z0-9_\-\+\#]+\b', user_text.lower())
        word_count = len(words)

        if word_count < 4:
            return cls._generate_minimal_response(question_obj, word_count)

        # 1. Semantic Similarity via TF-IDF + Cosine Distance
        sim_score = cls._compute_semantic_similarity(user_text, model_text, key_concepts)

        # 2. Concept Coverage (Keyword Spotting)
        concept_coverage_data = cls._evaluate_concept_coverage(user_text, key_concepts)
        coverage_ratio = concept_coverage_data['coverage_ratio']
        covered_concepts = concept_coverage_data['covered']
        missed_concepts = concept_coverage_data['missed']

        # 3. Depth & Vocabulary Richness
        depth_score = cls._compute_depth_score(word_count, difficulty, words)

        # 4. Domain Structure & Heuristics
        structure_data = cls._evaluate_domain_structure(user_text, domain)
        structure_score = structure_data['score']

        # 5. Composite Final Score (0 - 100)
        # Weights: Similarity (35%), Coverage (35%), Depth (15%), Structure (15%)
        raw_final = (
            (sim_score * 35.0) +
            (coverage_ratio * 35.0) +
            ((depth_score / 100.0) * 15.0) +
            ((structure_score / 100.0) * 15.0)
        )

        # Penalty for evasive or extremely terse responses
        if word_count < 15:
            raw_final = min(raw_final, 40.0)
        elif word_count < 30 and difficulty in ['medium', 'hard']:
            raw_final = min(raw_final, 60.0)

        final_score = max(5.0, min(100.0, round(raw_final, 1)))

        # Assign Grade
        grade, verdict = cls._calculate_grade_and_verdict(final_score)

        # Generate Strengths & Improvement Tips
        strengths, improvement_tips = cls._generate_qualitative_feedback(
            final_score, covered_concepts, missed_concepts, depth_score, structure_data, domain, difficulty
        )

        # Curated follow-up question
        follow_up = cls._get_follow_up_question(domain, difficulty, question_obj.title)

        return {
            'score': final_score,
            'grade': grade,
            'verdict': verdict,
            'metrics': {
                'semantic_similarity': round(sim_score * 100, 1),
                'concept_coverage': round(coverage_ratio * 100, 1),
                'depth_score': round(depth_score, 1),
                'structure_score': round(structure_score, 1),
                'word_count': word_count,
            },
            'covered_concepts': covered_concepts,
            'missed_concepts': missed_concepts,
            'strengths': strengths,
            'improvement_tips': improvement_tips,
            'domain_analysis': structure_data,
            'model_answer': model_text,
            'follow_up_question': follow_up,
        }

    @classmethod
    def _compute_semantic_similarity(cls, user_text: str, model_text: str, key_concepts: list) -> float:
        """Computes TF-IDF Cosine Similarity between user answer and reference."""
        try:
            # Augment reference document with key concepts to enhance signal
            augmented_ref = model_text + " " + " ".join(key_concepts)
            documents = [user_text, augmented_ref]

            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words='english',
                sublinear_tf=True
            )
            tfidf_matrix = vectorizer.fit_transform(documents)
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Map cosine range [0, 1] with slight curve so good human answers reach 0.85-0.95
            adjusted_sim = math.sqrt(max(0.0, float(cosine_sim)))
            return min(1.0, adjusted_sim)
        except Exception:
            return 0.35

    @classmethod
    def _evaluate_concept_coverage(cls, user_text: str, key_concepts: list) -> dict:
        """Spots which required concepts were present or omitted."""
        user_lower = user_text.lower()
        # Clean punctuation for matching
        cleaned_user = re.sub(r'[^\w\s]', ' ', user_lower)

        covered = []
        missed = []

        if not key_concepts:
            return {'coverage_ratio': 0.7, 'covered': [], 'missed': []}

        for concept in key_concepts:
            concept_clean = concept.strip().lower()
            if not concept_clean:
                continue

            # Tokenize concept
            concept_tokens = re.findall(r'\b\w+\b', concept_clean)
            
            # Direct substring check or all key tokens present
            if concept_clean in user_lower or concept_clean in cleaned_user:
                covered.append(concept)
            elif all(re.search(rf'\b{re.escape(token)}\b', cleaned_user) for token in concept_tokens if len(token) > 2):
                covered.append(concept)
            else:
                missed.append(concept)

        total = len(covered) + len(missed)
        ratio = (len(covered) / total) if total > 0 else 0.5

        return {
            'coverage_ratio': ratio,
            'covered': covered,
            'missed': missed,
        }

    @classmethod
    def _compute_depth_score(cls, word_count: int, difficulty: str, words: list) -> float:
        """Computes depth based on word count targets and technical term density."""
        target_words = {
            'easy': 35,
            'medium': 75,
            'hard': 110,
        }.get(difficulty, 60)

        length_ratio = min(1.2, word_count / target_words)
        base_depth = min(100.0, length_ratio * 80.0)

        # Unique word diversity bonus
        unique_words = len(set(words))
        diversity_ratio = unique_words / max(1, word_count)
        diversity_bonus = min(20.0, diversity_ratio * 20.0)

        return min(100.0, base_depth + diversity_bonus)

    @classmethod
    def _evaluate_domain_structure(cls, user_text: str, domain: str) -> dict:
        """Evaluates domain-specific answering structure (e.g., STAR, Big-O, Architecture)."""
        user_lower = user_text.lower()
        analysis = {'score': 70.0, 'domain': domain, 'highlights': []}

        if domain == 'hr':
            star_found = {}
            for component, patterns in cls.STAR_PATTERNS.items():
                found = any(re.search(pat, user_lower) for pat in patterns)
                star_found[component] = found

            star_count = sum(1 for v in star_found.values() if v)
            analysis['star_breakdown'] = star_found
            analysis['star_count'] = star_count
            analysis['score'] = min(100.0, 40.0 + (star_count * 15.0))
            if star_count >= 3:
                analysis['highlights'].append("Good use of the STAR (Situation-Task-Action-Result) framework!")
            else:
                analysis['highlights'].append("Structure using STAR: State the Situation, your Task, Actions taken, and measurable Results.")

        elif domain == 'dsa':
            has_complexity = any(re.search(pat, user_lower) for pat in cls.COMPLEXITY_PATTERNS)
            has_edge_cases = any(re.search(pat, user_lower) for pat in cls.EDGE_CASE_PATTERNS)
            
            score = 50.0
            if has_complexity:
                score += 30.0
                analysis['highlights'].append("Mentioned Time / Space Complexity ($O(N)$ notation).")
            else:
                analysis['highlights'].append("Did not explicitly specify Time and Space Complexity.")

            if has_edge_cases:
                score += 20.0
                analysis['highlights'].append("Identified boundary or edge cases.")
            analysis['score'] = min(100.0, score)

        elif domain == 'web_dev':
            matches = [term for term in ['stateless', 'async', 'promise', 'render', 'dom', 'component', 'api', 'http', 'cache', 'security', 'database'] if term in user_lower]
            arch_score = min(100.0, 50.0 + (len(matches) * 7.0))
            analysis['score'] = arch_score
            if len(matches) >= 3:
                analysis['highlights'].append(f"Strong web architecture vocabulary: {', '.join(matches[:4])}.")

        elif domain == 'ds':
            matches = [term for term in ['overfitting', 'accuracy', 'precision', 'recall', 'variance', 'bias', 'feature', 'gradient', 'loss', 'validation'] if term in user_lower]
            ds_score = min(100.0, 50.0 + (len(matches) * 8.0))
            analysis['score'] = ds_score
            if len(matches) >= 3:
                analysis['highlights'].append(f"Demonstrated ML evaluation fundamentals: {', '.join(matches[:4])}.")

        elif domain == 'project_defense':
            matches = [term for term in ['django', 'sqlite', 'nlp', 'tfidf', 'speech', 'webrtc', 'architecture', 'api', 'heuristic', 'scoring', 'scikit-learn'] if term in user_lower]
            analysis['score'] = min(100.0, 55.0 + (len(matches) * 9.0))
            if len(matches) >= 3:
                analysis['highlights'].append(f"Clear project defense details: {', '.join(matches[:4])}.")

        return analysis

    @classmethod
    def _calculate_grade_and_verdict(cls, score: float) -> tuple:
        """Maps numerical score to grade and placement verdict."""
        if score >= 90:
            return ('A+', 'Exceptional Candidate (Strong Hire)')
        elif score >= 80:
            return ('A', 'High Technical Competence (Hire)')
        elif score >= 70:
            return ('B', 'Solid Foundation (Shortlisted / Hire)')
        elif score >= 55:
            return ('C', 'Borderline (Needs More Preparation)')
        else:
            return ('Needs Work', 'Below Placement Cutoff (Revise Core Concepts)')

    @classmethod
    def _generate_qualitative_feedback(cls, score: float, covered: list, missed: list, depth: float, structure: dict, domain: str, difficulty: str) -> tuple:
        """Generates bulleted strengths and actionable improvement tips."""
        strengths = []
        tips = []

        # Strengths
        if covered:
            sample_covered = ", ".join(covered[:4])
            strengths.append(f"Accurately articulated key technical concepts: {sample_covered}.")
        if depth >= 70:
            strengths.append("Provided a thorough, well-elaborated response with sufficient technical substance.")
        if structure.get('highlights'):
            strengths.extend(structure['highlights'])

        if not strengths:
            strengths.append("Recognized the question context and made an attempt to explain the solution.")

        # Improvement Tips
        if missed:
            sample_missed = ", ".join(missed[:3])
            tips.append(f"Include essential terms that interviewers look for: {sample_missed}.")

        if depth < 55:
            tips.append(f"Expand on your explanation. Placement interviewers look for structured multi-sentence explanations for {difficulty.title()} level questions.")

        if domain == 'hr' and structure.get('star_count', 0) < 3:
            tips.append("Apply the STAR method: explicitly state the Task, your concrete Action, and the measurable Result or outcome.")

        if domain == 'dsa' and "Mentioned Time / Space Complexity" not in str(structure.get('highlights', [])):
            tips.append("Always state the Big-O Time Complexity and Auxiliary Space Complexity without being prompted.")

        if domain == 'web_dev':
            tips.append("Mention real-world trade-offs (e.g. caching, performance bottlenecks, or security best practices).")

        if not tips:
            tips.append("Great answer! For senior product company interviews, proactively discuss edge cases and scaling trade-offs.")

        return (strengths, tips)

    @classmethod
    def _get_follow_up_question(cls, domain: str, difficulty: str, title: str) -> str:
        """Generates an interviewer follow-up question."""
        follow_ups = {
            'web_dev': "How would you optimize this under heavy traffic with millions of concurrent requests?",
            'dsa': "Can you optimize the auxiliary space complexity down to O(1), or handle extreme edge cases like overflow?",
            'ds': "What trade-offs would you face in production, and how would you monitor model drift over time?",
            'hr': "Looking back, is there anything you would have handled differently with the benefit of hindsight?",
            'project_defense': "If an interviewer asks why you didn't use an external cloud LLM API, how do you justify the local NLP engine in terms of privacy, cost, and latency?",
        }
        return follow_ups.get(domain, "Could you elaborate on how this approach scales in a production setting?")

    @classmethod
    def _generate_minimal_response(cls, question_obj, word_count: int) -> dict:
        """Fallback for empty or single-word answers."""
        return {
            'score': 10.0,
            'grade': 'Needs Work',
            'verdict': 'Incomplete / Fluff Answer (Unsatisfactory)',
            'metrics': {
                'semantic_similarity': 5.0,
                'concept_coverage': 0.0,
                'depth_score': 10.0,
                'structure_score': 10.0,
                'word_count': word_count,
            },
            'covered_concepts': [],
            'missed_concepts': question_obj.get_key_concepts_list()[:5],
            'strengths': ['Acknowledged the question.'],
            'improvement_tips': [
                "Your answer was too brief. In a placement interview, elaborate on the definitions, working principles, and practical examples.",
                "Review the model answer below and practice explaining it in 3-5 complete sentences."
            ],
            'domain_analysis': {'score': 10.0, 'highlights': ['Insufficient length.']},
            'model_answer': question_obj.model_answer,
            'follow_up_question': "Can you try formulating a complete explanation covering the core mechanism?",
        }


class ConversationalInterviewerEngine:
    """
    Simulates a Real Human Placement Technical Interviewer.
    Key Capabilities:
      - Active listening and real-time interruption detection.
      - Classifies answers: CORRECT, PARTIALLY_CORRECT, INCORRECT, VAGUE, OFF_TOPIC, STRONG, IDONTKNOW, RAMBLING.
      - Never says 'Incorrect. Score: 2/10' — instead provides candid, professional verbal corrections.
      - Avoids sycophantic praise ('Great!', 'Excellent!') — speaks like a senior technical recruiter:
        'Okay.', 'I see.', 'Let's go one level deeper.', 'Hold on — that's not quite right.', 'Be more specific.'
      - Asks contextual follow-ups directly referencing the candidate's actual spoken words.
      - Supports multi-turn dialogue per topic before smoothly advancing.
    """

    IDONTKNOW_REGEX = re.compile(
        r"\b(i don'?t know|i do not know|no idea|not sure|have no clue|cannot recall|can'?t remember|can you skip|skip this|pass this|i am blank|not familiar)\b",
        re.IGNORECASE
    )

    VAGUE_PHRASES = [
        r"\b(makes (it|websites|things) (faster|better|good|easy))\b",
        r"\b(it is (very )?(good|useful|important|popular|nice))\b",
        r"\b(it helps (developers|programmers|people))\b",
        r"\b(for (writing|making) code)\b",
        r"\b(everyone uses it)\b",
    ]

    # Specific common placement blunders to detect and correct conversationally
    COMMON_BLUNDERS = {
        'binary search': {
            'patterns': [r'\bo\s*\(\s*n\s*\)', r'\blinear\b', r'\bsearch through (all|the entire) array\b'],
            'correction': "Binary search is O(log n), because the search space is divided approximately in half at every step.",
            'followup': "Can you explain why dividing the search space in half each step makes the time complexity logarithmic?"
        },
        'let and var': {
            'patterns': [r'\bvar is block scoped\b', r'\bvar stays inside the block\b', r'\bvar cannot be accessed outside the block\b'],
            'correction': "var is actually function-scoped, not block-scoped. So a var declared inside an if-statement or loop leaks into the surrounding function.",
            'followup': "Can you explain what the Temporal Dead Zone is in relation to let and const?"
        },
        'virtual dom': {
            'patterns': [r'\bmodifies the browser dom directly\b', r'\breal dom is faster\b', r'\bvdom is in the browser\b'],
            'correction': "The Virtual DOM is an in-memory JavaScript representation of the UI, not the browser's real DOM.",
            'followup': "What specifically does React do during the reconciliation phase that makes UI updates efficient?"
        },
        'event bubbling': {
            'patterns': [r'\bparent to child\b', r'\bfrom window down to target\b'],
            'correction': "Event bubbling travels upwards from the target child element to its ancestors in the DOM tree.",
            'followup': "Can you explain why event bubbling is useful when we need to handle clicks on many dynamic child elements?"
        },
        'overfitting': {
            'patterns': [r'\bhigh bias\b', r'\bmodel is too simple\b'],
            'correction': "Overfitting corresponds to High Variance, where the model memorizes training noise rather than generalizing.",
            'followup': "What regularization or sampling technique would you use to prevent a decision tree ensemble from overfitting?"
        },
    }

    @classmethod
    def detect_realtime_interruption(cls, partial_transcript: str, question_obj, word_count: int, turn_index: int) -> dict:
        """
        Analyzes streaming transcript in real time while candidate is talking.
        Decides whether a realistic interviewer would politely intervene.
        """
        text = (partial_transcript or '').strip().lower()
        if word_count < 6:
            return {'should_interrupt': False}

        # 1. Candidate says "I don't know"
        if cls.IDONTKNOW_REGEX.search(text):
            return {
                'should_interrupt': True,
                'category': 'IDONTKNOW',
                'spoken_interruption': "That's okay. Let's approach it differently. What would you expect to happen?",
                'reason': 'candidate_unsure'
            }

        # 2. Candidate going into prolonged rambling preamble
        if word_count >= 25:
            rambling_signals = [
                r'\b(was created in 1995|created by brendan eich|long time ago|in history|when computers were)\b',
                r'\b(as we all know|everyone knows that|first of all let me tell you about everything)\b',
            ]
            if any(re.search(pat, text) for pat in rambling_signals):
                return {
                    'should_interrupt': True,
                    'category': 'RAMBLING',
                    'spoken_interruption': f"Sorry to interrupt you there. Let's stay focused on the question. {question_obj.question_text}",
                    'reason': 'rambling_preamble'
                }

        # 3. Early factual blunder detection
        q_title_lower = question_obj.title.lower()
        for topic_key, blunder_data in cls.COMMON_BLUNDERS.items():
            if topic_key in q_title_lower or topic_key in question_obj.question_text.lower():
                for pat in blunder_data['patterns']:
                    if re.search(pat, text):
                        return {
                            'should_interrupt': True,
                            'category': 'INCORRECT',
                            'spoken_interruption': f"Hold on — that's not quite right. {blunder_data['correction']} {blunder_data['followup']}",
                            'reason': 'critical_factual_blunder'
                        }

        # 4. Off-topic check on longer monologue (word_count > 40)
        if word_count >= 40:
            key_terms = [t.lower() for t in question_obj.get_key_concepts_list()]
            terms_present = sum(1 for t in key_terms if t in text)
            if terms_present == 0 and question_obj.domain in ['web_dev', 'dsa', 'ds']:
                # Candidate spoke 40+ words with zero relevant keywords
                return {
                    'should_interrupt': True,
                    'category': 'OFF_TOPIC',
                    'spoken_interruption': f"Let's bring it back to the question. What is {question_obj.title} specifically?",
                    'reason': 'off_topic_ramble'
                }

        return {'should_interrupt': False}

    @classmethod
    def evaluate_conversational_turn(cls, candidate_answer: str, question_obj, turn_index: int = 1, conversation_history: list = None) -> dict:
        """
        Evaluates a complete candidate conversational turn.
        Returns:
          - category: CORRECT, PARTIALLY_CORRECT, INCORRECT, VAGUE, OFF_TOPIC, STRONG, IDONTKNOW, RAMBLING
          - interviewer_speech: Natural verbal response to speak aloud
          - action: 'continue_dialogue' (ask follow-up on current question) or 'advance_question'
          - score_data: numerical evaluation and concept breakdown
        """
        user_text = (candidate_answer or '').strip()
        user_lower = user_text.lower()
        words = re.findall(r'\b[a-zA-Z0-9_\-\+\#]+\b', user_lower)
        word_count = len(words)
        history = conversation_history or []

        # Run base scoring metrics
        eval_base = AIScoringEngine.evaluate(user_text, question_obj)
        score = eval_base['score']
        covered = eval_base['covered_concepts']
        missed = eval_base['missed_concepts']
        coverage_ratio = eval_base['metrics']['concept_coverage'] / 100.0

        q_title = question_obj.title
        q_text = question_obj.question_text
        q_topic = question_obj.category

        # =====================================================================
        # CATEGORY 1: I DON'T KNOW
        # =====================================================================
        if cls.IDONTKNOW_REGEX.search(user_lower) or word_count < 4:
            if turn_index == 1:
                return {
                    'category': 'IDONTKNOW',
                    'interviewer_speech': "That's okay. Let's approach it differently. What would you expect to happen?",
                    'action': 'continue_dialogue',
                    'score_data': eval_base,
                    'verdict_label': 'Needs Clarification'
                }
            else:
                return {
                    'category': 'IDONTKNOW',
                    'interviewer_speech': "No problem. We'll move on to the next topic.",
                    'action': 'advance_question',
                    'score_data': eval_base,
                    'verdict_label': 'Skipped / Unfamiliar'
                }

        # =====================================================================
        # CATEGORY 2: SPECIFIC FACTUAL BLUNDERS / INCORRECT
        # =====================================================================
        for topic_key, blunder_data in cls.COMMON_BLUNDERS.items():
            if topic_key in q_title.lower() or topic_key in q_text.lower():
                for pat in blunder_data['patterns']:
                    if re.search(pat, user_lower):
                        speech = (
                            f"Hold on — that's not quite right. "
                            f"{blunder_data['correction']} "
                            f"{blunder_data['followup']}"
                        )
                        return {
                            'category': 'INCORRECT',
                            'interviewer_speech': speech,
                            'action': 'continue_dialogue' if turn_index == 1 else 'advance_question',
                            'score_data': eval_base,
                            'verdict_label': 'Incorrect (Prompted Correction)'
                        }

        # =====================================================================
        # CATEGORY 3: VAGUE ANSWERS
        # =====================================================================
        is_vague = any(re.search(p, user_lower) for p in cls.VAGUE_PHRASES) and word_count < 18
        if is_vague or (word_count < 12 and coverage_ratio < 0.25):
            subject = question_obj.category or question_obj.title
            speech = f"That's a little too broad. What specifically does {subject} do to handle this?"
            return {
                'category': 'VAGUE',
                'interviewer_speech': speech,
                'action': 'continue_dialogue',
                'score_data': eval_base,
                'verdict_label': 'Too Vague (Asked for Precision)'
            }

        # =====================================================================
        # CATEGORY 4: OFF-TOPIC / EXCESSIVE RAMBLING
        # =====================================================================
        if word_count >= 50 and coverage_ratio < 0.15:
            speech = f"Okay, I'll stop you there for a moment. Can you give me the direct answer to the question?"
            return {
                'category': 'RAMBLING',
                'interviewer_speech': speech,
                'action': 'continue_dialogue',
                'score_data': eval_base,
                'verdict_label': 'Rambling / Off-Topic'
            }

        # =====================================================================
        # CATEGORY 5: PARTIALLY CORRECT ANSWERS
        # =====================================================================
        if coverage_ratio >= 0.20 and coverage_ratio < 0.65:
            # Candidate has a piece of the answer but missed the rest
            missing_hint = missed[0] if missed else "the practical trade-off"
            if turn_index == 1:
                speech = (
                    f"You're on the right track, but you're missing an important part. "
                    f"Can you explain how {missing_hint} fits into this?"
                )
                action = 'continue_dialogue'
            else:
                speech = f"Okay, that's partially correct. Let's move on to the next question."
                action = 'advance_question'

            return {
                'category': 'PARTIALLY_CORRECT',
                'interviewer_speech': speech,
                'action': action,
                'score_data': eval_base,
                'verdict_label': 'Partially Correct (Prompted to Expand)'
            }

        # =====================================================================
        # CATEGORY 6: STRONG / CORRECT ANSWERS
        # =====================================================================
        if coverage_ratio >= 0.65 or score >= 75.0:
            if turn_index == 1:
                # Ask a contextual harder follow-up using their actual vocabulary!
                deeper_probe = cls._generate_contextual_probe(user_lower, question_obj)
                speech = f"Good. Let's go one level deeper. {deeper_probe}"
                return {
                    'category': 'STRONG',
                    'interviewer_speech': speech,
                    'action': 'continue_dialogue',
                    'score_data': eval_base,
                    'verdict_label': 'Strong Answer (Probed Deeper)'
                }
            else:
                speech = "Correct. That demonstrates solid technical understanding. Let's proceed to the next question."
                return {
                    'category': 'CORRECT',
                    'interviewer_speech': speech,
                    'action': 'advance_question',
                    'score_data': eval_base,
                    'verdict_label': 'Competent Technical Explanation'
                }

        # Default fallback for modest attempt
        if turn_index == 1:
            speech = f"Not quite. Can you reconsider that in terms of {question_obj.category}?"
            action = 'continue_dialogue'
        else:
            speech = "Okay, let's keep that in mind and move on."
            action = 'advance_question'

        return {
            'category': 'NEEDS_CLARIFICATION',
            'interviewer_speech': speech,
            'action': action,
            'score_data': eval_base,
            'verdict_label': 'Needs Clarification'
        }

    @classmethod
    def _generate_contextual_probe(cls, user_text: str, question_obj) -> str:
        """
        Crafts an interviewer probe that explicitly builds upon what the candidate just said.
        """
        domain = question_obj.domain

        if 'event' in user_text:
            return "Since you've explained event propagation, what happens if the dynamically created element is removed from the DOM?"
        if 'dom' in user_text:
            return "Now, what happens to that DOM tree when JavaScript modifies an element at runtime?"
        if 'var' in user_text or 'scope' in user_text:
            return "What happens when you declare a var inside a nested block versus a let in the same block?"
        if 'complexity' in user_text or 'o(' in user_text:
            return "Can this algorithm be optimized further if the input is already sorted, or can space be reduced to O(1)?"
        if 'cache' in user_text or 'redis' in user_text:
            return "How would you handle cache invalidation when multiple writes happen simultaneously?"
        if 'overfitting' in user_text or 'regularization' in user_text:
            return "If you apply strong L2 regularization, what happens to the weights and how does it affect test set variance?"

        # Domain fallbacks
        probes = {
            'web_dev': "What potential performance bottleneck or security risk would you watch out for in production?",
            'dsa': "What is the worst-case space complexity, and how do you handle boundary edge cases?",
            'ds': "What trade-offs would you encounter when deploying this model into a real-time streaming pipeline?",
            'hr': "Looking back, is there anything you would have handled differently with hindsight?",
            'project_defense': "How does your system guarantee sub-50ms latency when multiple users dictate answers concurrently?"
        }
        return probes.get(domain, "What edge cases would you anticipate with this approach?")

    @classmethod
    def generate_behavioral_summary(cls, presence_events: list) -> str:
        """
        Generates candid, professional interviewer notes combining technical answers
        with camera presence observations.
        """
        if not presence_events:
            return "Candidate maintained strong eye contact and professional focus throughout the interview."

        away_count = sum(1 for e in presence_events if e.get('type') == 'looking_away')
        missing_count = sum(1 for e in presence_events if e.get('type') == 'not_detected')
        multi_count = sum(1 for e in presence_events if e.get('type') == 'multiple_faces')

        notes = []
        if away_count > 0:
            notes.append(f"occasionally looked away from the screen ({away_count} attention warnings recorded)")
        if missing_count > 0:
            notes.append("left camera frame briefly")
        if multi_count > 0:
            notes.append("secondary person appeared in frame")

        if not notes:
            return "Consistent camera presence and professional interview demeanor maintained."

        return f"Candidate demonstrated technical competence, but {' and '.join(notes)}. Ensure consistent eye level focus during formal placement drives."

