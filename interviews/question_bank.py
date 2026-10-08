"""
Comprehensive Placement Interview Question Bank.
Covers:
  - Web Development (Frontend, Backend, APIs, Performance, Security)
  - Data Structures & Algorithms (Arrays, Linked Lists, Trees, DP, Graphs)
  - Data Science & Machine Learning (Regression, Classification, Overfitting, Metrics)
  - HR & Behavioral (STAR method, Leadership, Conflict, Strengths/Weaknesses)
  - Project Defense (Live Demo: Interviewing this very AI placement bot project!)
"""

SEED_QUESTIONS = [
    # =========================================================================
    # WEB DEVELOPMENT - EASY
    # =========================================================================
    {
        'domain': 'web_dev',
        'difficulty': 'easy',
        'category': 'Frontend & JS Fundamentals',
        'title': 'Difference between var, let, and const in JavaScript',
        'question_text': 'Explain the key differences between var, let, and const in modern JavaScript, focusing on scoping, hoisting, and re-assignment.',
        'key_concepts': 'scope, function scope, block scope, hoisting, temporal dead zone, reassignment, mutation, let, const, var',
        'model_answer': (
            "In JavaScript, 'var' is function-scoped and hoisted with an initial value of undefined, allowing re-declaration. "
            "In contrast, 'let' and 'const' were introduced in ES6 and are block-scoped (enclosed within curly braces). "
            "They are also hoisted but placed in the Temporal Dead Zone (TDZ) until evaluation, preventing access before declaration. "
            "'let' allows variable re-assignment, whereas 'const' cannot be re-assigned after initialization, although objects and arrays declared with const can still have their contents mutated."
        ),
        'hints': 'Focus on block scope vs function scope, hoisting behavior, and re-assignment rules.',
    },
    {
        'domain': 'web_dev',
        'difficulty': 'easy',
        'category': 'Web Architecture',
        'title': 'How does the HTTP Request-Response lifecycle work?',
        'question_text': 'What happens when a user types a URL in a browser and presses Enter? Describe the steps from DNS resolution to DOM rendering.',
        'key_concepts': 'DNS resolution, IP address, TCP handshake, SYN-ACK, TLS handshake, HTTP GET request, server response, status code, HTML parsing, DOM, CSSOM, render tree',
        'model_answer': (
            "When a user enters a URL, the browser first resolves the domain name into an IP address using DNS lookup (checking browser cache, OS cache, router, and ISP resolvers). "
            "Next, a TCP 3-way handshake (SYN, SYN-ACK, ACK) establishes a connection, followed by a TLS handshake for HTTPS. "
            "The browser sends an HTTP GET request to the web server. The server processes it and returns an HTTP response containing headers and HTML payload (e.g. 200 OK). "
            "Finally, the browser parses HTML to construct the DOM tree, CSS to construct CSSOM, builds the render tree, computes layout, and paints pixels onto the screen."
        ),
        'hints': 'Start with DNS lookup, mention TCP/TLS, server HTTP response, and client-side DOM/CSSOM rendering.',
    },
    {
        'domain': 'web_dev',
        'difficulty': 'easy',
        'category': 'CSS & Responsive Design',
        'title': 'CSS Box Model and Box-Sizing Property',
        'question_text': 'What is the CSS Box Model? How does box-sizing: border-box change element width calculation compared to content-box?',
        'key_concepts': 'content, padding, border, margin, box-sizing, border-box, content-box, total width, layout calculation',
        'model_answer': (
            "The CSS Box Model is the container structure wrapping every HTML element, consisting of four layers from inside out: Content, Padding, Border, and Margin. "
            "With default 'content-box', the specified width and height apply only to the content; any padding and border are added on top, making total element width equal to width + padding + border. "
            "With 'box-sizing: border-box', the declared width includes content, padding, and border. This makes responsive UI layout calculation much more predictable."
        ),
        'hints': 'List the 4 components from inside out, and explain why border-box simplifies responsive layouts.',
    },

    # =========================================================================
    # WEB DEVELOPMENT - MEDIUM
    # =========================================================================
    {
        'domain': 'web_dev',
        'difficulty': 'medium',
        'category': 'React & Frontend Architecture',
        'title': 'Virtual DOM and React Reconciliation Algorithm',
        'question_text': 'What is the Virtual DOM in React, and how does the reconciliation (diffing) algorithm optimize rendering performance?',
        'key_concepts': 'virtual DOM, real DOM, reconciliation, diffing algorithm, fiber, keys, re-render, batching, performance, tree comparison',
        'model_answer': (
            "The Virtual DOM (VDOM) is a lightweight in-memory JavaScript representation of the real DOM. "
            "When state or props change, React creates a new Virtual DOM tree and runs a reconciliation (diffing) algorithm against the previous tree. "
            "Rather than computing expensive O(n^3) tree comparisons, React uses an O(n) heuristic: elements of different types generate different trees, and lists use stable 'key' attributes to track identity. "
            "React calculates the minimal set of changes (diffs) and batch-updates the real DOM in a single commit phase, dramatically reducing expensive browser reflows and repaints."
        ),
        'hints': 'Highlight why touching the real DOM is slow, explain tree diffing O(N) heuristics and the importance of keys.',
    },
    {
        'domain': 'web_dev',
        'difficulty': 'medium',
        'category': 'Backend & Security',
        'title': 'REST API Principles vs GraphQL & Web Security (CORS & CSRF)',
        'question_text': 'What are the core constraints of a RESTful API? Briefly contrast REST with GraphQL and explain how CORS protects web clients.',
        'key_concepts': 'stateless, client-server, uniform interface, cacheable, over-fetching, under-fetching, single endpoint, CORS, cross-origin resource sharing, preflight OPTIONS, same-origin policy',
        'model_answer': (
            "REST is an architectural style based on constraints: Statelessness, Client-Server separation, Cacheability, Layered System, and a Uniform Interface using standard HTTP verbs (GET, POST, PUT, DELETE). "
            "While REST uses multiple resource-oriented endpoints and can suffer from over-fetching or under-fetching data, GraphQL exposes a single endpoint where clients request exact query structures. "
            "CORS (Cross-Origin Resource Sharing) is a browser security mechanism based on the Same-Origin Policy. It uses HTTP headers (such as Access-Control-Allow-Origin) and preflight OPTIONS requests to allow or deny client web applications from making cross-origin requests."
        ),
        'hints': 'Mention statelessness, compare endpoint counts & payload flexibility, and explain CORS headers.',
    },

    # =========================================================================
    # WEB DEVELOPMENT - HARD
    # =========================================================================
    {
        'domain': 'web_dev',
        'difficulty': 'hard',
        'category': 'High Scalability & Web Performance',
        'title': 'Designing a High-Concurrency Web Architecture with Caching & Rate Limiting',
        'question_text': 'How would you design a scalable web backend to handle 100,000 requests per minute with low latency? Address caching layers, database scaling, and rate limiting.',
        'key_concepts': 'load balancer, reverse proxy, nginx, redis, caching, cdn, database indexing, read replicas, connection pooling, rate limiting, token bucket, horizontal scaling, asynchronous celery',
        'model_answer': (
            "To handle 100,000 RPM with low latency, I would design a multi-tiered distributed architecture: "
            "1. Edge Tier: Use a Global CDN (Cloudflare/CloudFront) for static assets and edge caching, backed by Nginx/HAProxy load balancers using round-robin or least-connections. "
            "2. Application Tier: Horizontally scaled stateless backend containers (Django/FastAPI) managed via Kubernetes, with connection pooling. "
            "3. Caching & Rate Limiting: Deploy Redis clusters for sub-millisecond in-memory caching (cache-aside pattern with TTL) and token-bucket / sliding-window rate limiting. "
            "4. Database Layer: Implement primary-replica replication (writes to primary, read queries offloaded to read replicas), proper composite indexing, and database connection pools (PgBouncer). "
            "5. Async Processing: Offload heavy tasks (emails, notifications, analytics) to asynchronous queues like Celery with RabbitMQ/Redis."
        ),
        'hints': 'Structure your answer by tiers: CDN/Load balancer, stateless application servers, Redis caching, DB read replicas, and async task queues.',
    },

    # =========================================================================
    # DATA STRUCTURES & ALGORITHMS (DSA) - EASY
    # =========================================================================
    {
        'domain': 'dsa',
        'difficulty': 'easy',
        'category': 'Arrays & Hash Maps',
        'title': 'Two Sum Problem - Brute Force vs Optimal Solution',
        'question_text': 'Given an array of integers and a target sum, explain how to find two numbers that add up to the target. Compare the brute-force and optimal approaches in terms of Time and Space complexity.',
        'key_concepts': 'hash map, complement, time complexity O(n), space complexity O(n), brute force O(n^2), nested loops, lookup O(1)',
        'model_answer': (
            "The brute force approach uses two nested loops to check all pairs (nums[i] + nums[j] == target). This takes O(n^2) time complexity and O(1) auxiliary space. "
            "The optimal approach uses a Hash Map (dictionary) to store visited values and their indices. In a single pass, for each element 'num', we calculate its complement (target - num). "
            "If the complement exists in the hash map, we immediately return the pair of indices. Otherwise, we store the current element and index. "
            "This achieves an optimal O(n) time complexity because hash map lookups take O(1) average time, with O(n) auxiliary space complexity."
        ),
        'hints': 'Explain target - current element, hash map O(1) average lookup, and contrast O(N^2) vs O(N).',
    },
    {
        'domain': 'dsa',
        'difficulty': 'easy',
        'category': 'Linked Lists',
        'title': 'Reversing a Singly Linked List',
        'question_text': 'How do you reverse a singly linked list in-place iteratively? Explain the pointer manipulation and complexities.',
        'key_concepts': 'prev, current, next, pointer, three pointers, in-place, time complexity O(n), space complexity O(1), null termination',
        'model_answer': (
            "To reverse a singly linked list iteratively in-place, we maintain three pointers: 'prev' initialized to null, 'curr' initialized to head, and 'next_node' initialized to null. "
            "While 'curr' is not null, we: "
            "1. Save the next node: next_node = curr.next. "
            "2. Reverse the current node's pointer: curr.next = prev. "
            "3. Advance prev: prev = curr. "
            "4. Advance curr: curr = next_node. "
            "When the loop terminates, 'prev' points to the new head of the reversed list. "
            "This runs in O(n) time complexity as each node is visited once, and uses O(1) auxiliary space since it operates purely in-place."
        ),
        'hints': 'Walk through the 3 pointers (prev, curr, next) and show step-by-step re-wiring.',
    },

    # =========================================================================
    # DATA STRUCTURES & ALGORITHMS (DSA) - MEDIUM
    # =========================================================================
    {
        'domain': 'dsa',
        'difficulty': 'medium',
        'category': 'Trees & Binary Search Trees',
        'title': 'Validate Binary Search Tree and Tree Traversals',
        'question_text': 'How do you validate whether a Binary Tree is a valid Binary Search Tree (BST)? What is the relationship between BST validation and Inorder Traversal?',
        'key_concepts': 'binary search tree, left subtree, right subtree, lower bound, upper bound, inorder traversal, strictly ascending, recursion, time complexity O(n), space complexity O(h)',
        'model_answer': (
            "A valid BST requires that every node's value must be strictly greater than all values in its left subtree and strictly less than all values in its right subtree—not just its direct children. "
            "Approach 1 (Recursive with Bounds): We pass min_bound and max_bound down the tree. For node val, we check (min_val < node.val < max_val). When recursing left, upper bound becomes node.val; when recursing right, lower bound becomes node.val. "
            "Approach 2 (Inorder Traversal): An inorder traversal (Left, Root, Right) of a valid BST must yield a strictly increasing sequence of values. By tracking the previously visited value, any violation (curr <= prev) indicates an invalid BST. "
            "Both algorithms operate in O(n) time complexity and O(h) auxiliary space complexity, where h is the tree height (O(log n) balanced, O(n) skewed)."
        ),
        'hints': 'Emphasize that checking only direct parent-child values is a common trap; global subtree bounds or inorder monotonic check are needed.',
    },
    {
        'domain': 'dsa',
        'difficulty': 'medium',
        'category': 'Dynamic Programming',
        'title': '0/1 Knapsack Problem - Overlapping Subproblems & Optimal Substructure',
        'question_text': 'Explain the 0/1 Knapsack problem and how Dynamic Programming improves upon the exponential recursive solution.',
        'key_concepts': 'dynamic programming, overlapping subproblems, optimal substructure, memoization, tabulation, 2D table, time complexity O(n*w), pseudo-polynomial, space optimization O(w)',
        'model_answer': (
            "In the 0/1 Knapsack problem, given items with weights and values and a maximum capacity W, we want to maximize total value without exceeding capacity, where each item can either be taken (1) or left (0). "
            "A naive recursive solution explores two choices per item (include or exclude), resulting in exponential O(2^n) time complexity with overlapping subproblems. "
            "Dynamic Programming solves this using optimal substructure: dp[i][w] = max(dp[i-1][w], val[i-1] + dp[i-1][w - wt[i-1]]). "
            "Using a 2D table (or space-optimized 1D array traversing backwards), we achieve O(n * W) time complexity and O(W) auxiliary space complexity, transforming an exponential brute-force problem into pseudo-polynomial time."
        ),
        'hints': 'Discuss state definition dp[i][w], recurrence relation (include vs exclude), and transition from O(2^N) to O(N*W).',
    },

    # =========================================================================
    # DATA STRUCTURES & ALGORITHMS (DSA) - HARD
    # =========================================================================
    {
        'domain': 'dsa',
        'difficulty': 'hard',
        'category': 'Graphs & Shortest Path',
        'title': 'Dijkstra vs Bellman-Ford vs Floyd-Warshall Algorithms',
        'question_text': 'Compare Dijkstra, Bellman-Ford, and Floyd-Warshall algorithms for shortest path calculations. When would you use each, and how do they handle negative weight cycles?',
        'key_concepts': 'dijkstra, bellman-ford, floyd-warshall, greedy, priority queue, min-heap, negative edge weights, negative cycles, time complexity O((V+E)log V), O(V*E), O(V^3), all-pairs shortest path',
        'model_answer': (
            "1. Dijkstra's Algorithm: A greedy single-source shortest path algorithm using a Min-Heap (priority queue). It operates in O((V + E) log V) time complexity. Constraint: Fails on graphs with negative edge weights because once a vertex is marked visited, its distance is assumed final. "
            "2. Bellman-Ford Algorithm: A dynamic programming single-source shortest path algorithm that relaxes all E edges (V - 1) times in O(V * E) time complexity. Crucially, it handles negative edge weights and can detect negative weight cycles (if a distance can still be relaxed on the V-th iteration). "
            "3. Floyd-Warshall Algorithm: An all-pairs shortest path dynamic programming algorithm that tests whether a path through intermediate vertex 'k' is shorter. It runs in O(V^3) time complexity and O(V^2) space, best suited for dense graphs or small networks."
        ),
        'hints': 'Categorize by single-source vs all-pairs, performance complexities, and behavior with negative weights/cycles.',
    },

    # =========================================================================
    # DATA SCIENCE & MACHINE LEARNING - EASY
    # =========================================================================
    {
        'domain': 'ds',
        'difficulty': 'easy',
        'category': 'Machine Learning Core',
        'title': 'Overfitting vs Underfitting and How to Prevent Them',
        'question_text': 'What are overfitting and underfitting in Machine Learning? How do you diagnose and mitigate them in a model?',
        'key_concepts': 'overfitting, underfitting, high variance, high bias, training error, validation error, regularization, L1 L2, dropout, cross-validation, feature selection',
        'model_answer': (
            "Underfitting occurs when a model is too simple to capture underlying data patterns (High Bias), resulting in poor performance on both training and validation sets. It is solved by increasing model complexity, engineering better features, or decreasing regularization. "
            "Overfitting occurs when a model memorizes training noise rather than generalizing (High Variance), resulting in near-zero training loss but high validation error. "
            "Overfitting is diagnosed via learning curves and train-test splits, and mitigated through: L1/L2 Regularization (Lasso/Ridge), Dropout, Early Stopping, Cross-Validation (K-Fold), Data Augmentation, and pruning/reducing model complexity."
        ),
        'hints': 'Link underfitting to High Bias and overfitting to High Variance. List at least 4 practical mitigation techniques.',
    },
    {
        'domain': 'ds',
        'difficulty': 'easy',
        'category': 'Model Evaluation',
        'title': 'Precision, Recall, F1-Score, and Confusion Matrix',
        'question_text': 'Explain Precision, Recall, and F1-Score. In what real-world scenarios is Recall preferred over Precision, and vice-versa?',
        'key_concepts': 'precision, recall, f1-score, true positive, false positive, false negative, confusion matrix, harmonic mean, medical diagnosis, spam detection, imbalanced data',
        'model_answer': (
            "In classification evaluation: "
            "Precision = TP / (TP + FP). It measures accuracy among positive predictions (minimizing False Positives). "
            "Recall (Sensitivity) = TP / (TP + FN). It measures the proportion of actual positives correctly identified (minimizing False Negatives). "
            "F1-Score is the harmonic mean of Precision and Recall: 2 * (Precision * Recall) / (Precision + Recall), ideal for imbalanced datasets. "
            "Scenario for High Recall: Cancer detection or fraud screening, where missing an actual positive (False Negative) is catastrophic. "
            "Scenario for High Precision: Email spam filtering or YouTube recommendation, where marking legitimate emails as spam (False Positive) disrupts user experience."
        ),
        'hints': 'Define formulas clearly using TP, FP, FN and provide concrete real-world examples (medical vs spam).',
    },

    # =========================================================================
    # DATA SCIENCE & MACHINE LEARNING - MEDIUM
    # =========================================================================
    {
        'domain': 'ds',
        'difficulty': 'medium',
        'category': 'Ensemble Learning',
        'title': 'Random Forest vs Gradient Boosting (Bagging vs Boosting)',
        'question_text': 'Explain the difference between Bagging and Boosting. Contrast Random Forest with Gradient Boosted Decision Trees (GBDT/XGBoost).',
        'key_concepts': 'bagging, boosting, bootstrap aggregating, variance reduction, bias reduction, parallel trees, sequential trees, residuals, gradient descent, xgboost, random forest',
        'model_answer': (
            "Bagging (Bootstrap Aggregating) builds multiple independent decision trees in parallel on random bootstrap samples and feature subsets, aggregating predictions by majority vote or average. Random Forest is the benchmark bagging method that primarily reduces model variance without increasing bias. "
            "Boosting builds decision trees sequentially, where each new tree is trained to correct the pseudo-residuals (errors) of the preceding ensemble via gradient descent on a loss function. XGBoost and LightGBM are prime boosting implementations that primarily reduce model bias. "
            "Random Forest is less prone to overfitting and easily parallelizable, while Gradient Boosting often achieves superior predictive accuracy on structured tabular data when tuned properly."
        ),
        'hints': 'Contrast parallel vs sequential training, variance reduction vs bias reduction, and how errors are handled.',
    },

    # =========================================================================
    # DATA SCIENCE & MACHINE LEARNING - HARD
    # =========================================================================
    {
        'domain': 'ds',
        'difficulty': 'hard',
        'category': 'Production ML & Drift',
        'title': 'Handling Severe Class Imbalance and Monitoring Concept Drift in Production',
        'question_text': 'How would you train a fraud detection model with 99.9% negative and 0.1% positive classes? How do you monitor and handle data and concept drift post-deployment?',
        'key_concepts': 'imbalance, SMOTE, undersampling, focal loss, class weights, precision-recall curve, PR-AUC, concept drift, data drift, KS-test, PSI, population stability index, shadow deployment, retraining pipeline',
        'model_answer': (
            "1. Handling Class Imbalance (0.1% fraud): "
            "Never use accuracy as an evaluation metric; use PR-AUC (Area Under Precision-Recall Curve) and Cost-sensitive matrices. "
            "At data level: Use SMOTE (Synthetic Minority Over-sampling) or Tomek-links under-sampling. "
            "At algorithmic level: Apply balanced class weighting or Focal Loss (which downweights easy negative examples). "
            "2. Production Drift Monitoring: "
            "Track Data Drift (P(X) changes) using statistical tests like Kolmogorov-Smirnov (KS-test) or Population Stability Index (PSI > 0.2 indicates significant shift). "
            "Track Concept Drift (P(Y|X) changes, where fraud patterns evolve) by monitoring rolling F1-score and calibration curve slope. "
            "Implement automated alerting and a scheduled continuous retraining pipeline with shadow/canary model deployments."
        ),
        'hints': 'Discuss evaluation metrics (PR-AUC), algorithmic sampling/loss techniques, and statistical tests (PSI, KS-test) for drift.',
    },

    # =========================================================================
    # HR & BEHAVIORAL - EASY
    # =========================================================================
    {
        'domain': 'hr',
        'difficulty': 'easy',
        'category': 'Introduction & Communication',
        'title': 'Tell Me About Yourself (Elevator Pitch)',
        'question_text': 'Walk me through your resume and introduce yourself. Focus on your background, technical passions, key projects, and career goal.',
        'key_concepts': 'education, computer science, technical skills, projects, problem solving, passion, campus placement, career aspirations, contribution',
        'model_answer': (
            "Hello, I am a final-year Computer Science student passionate about building scalable software solutions and intelligent systems. "
            "Throughout my academics, I have developed strong foundations in Data Structures, Algorithms, Full-Stack Web Development, and Machine Learning. "
            "Recently, I built an end-to-end AI Placement Interview Practice Bot that utilizes Django, web audio APIs, and NLP algorithms to evaluate candidate performance in real time. "
            "I enjoy solving challenging problems and collaborating in agile teams. I am excited about this role because your engineering team solves high-impact problems where I can contribute my development skills and grow as a software engineer."
        ),
        'hints': 'Follow the Present-Past-Future structure: who you are now, key accomplishments/projects, and why you are excited for this opportunity.',
    },
    {
        'domain': 'hr',
        'difficulty': 'easy',
        'category': 'Cultural Fit',
        'title': 'Why Do You Want to Join Our Company?',
        'question_text': 'Why are you specifically interested in joining our company rather than other placement opportunities?',
        'key_concepts': 'company mission, technology stack, culture, growth opportunities, innovation, mentorship, learning curve, alignment, impact',
        'model_answer': (
            "I have been following your company's work, particularly your innovation in engineering reliable, customer-centric products at scale. "
            "What stands out to me is your engineering culture of continuous learning, rigorous code reviews, and strong mentorship for entry-level developers. "
            "During my academic projects, I realized that I thrive in collaborative environments where ownership and practical problem-solving are valued. "
            "I want to start my career in an environment that pushes technical boundaries, where my work directly impacts thousands of users while allowing me to learn best engineering practices."
        ),
        'hints': 'Demonstrate research about the company, show genuine alignment with culture, and express eagerness to learn.',
    },

    # =========================================================================
    # HR & BEHAVIORAL - MEDIUM
    # =========================================================================
    {
        'domain': 'hr',
        'difficulty': 'medium',
        'category': 'Conflict Resolution (STAR)',
        'title': 'Handling Team Conflict & Disagreement (STAR Technique)',
        'question_text': 'Describe a situation where you had a disagreement with a team member or peer on a project. How did you handle it and what was the outcome?',
        'key_concepts': 'situation, task, action, result, disagreement, communication, listening, compromise, objective data, team collaboration, resolution',
        'model_answer': (
            "Situation: During our capstone engineering project, my teammate and I strongly disagreed on database selection—he favored MongoDB for fast schema-less iteration, while I advocated for PostgreSQL because our schema had strict relational constraints. "
            "Task: As lead developers, we needed to resolve this swiftly without creating friction or delaying our project milestone. "
            "Action: Instead of debating opinions, I proposed setting up an objective benchmarking test. We mapped out our entity relations, tested write-heavy transactions, and evaluated ACID requirements. I actively listened to his concerns regarding development velocity. We agreed that while Postgres handled relational queries best, we could use JSONB columns for flexible attributes. "
            "Result: The compromise preserved team trust, eliminated data integrity bugs during testing, and our project was delivered on schedule with high commendation from our professors."
        ),
        'hints': 'Use the STAR format: Situation, Task, Action (empathy + objective data), and measurable positive Result.',
    },
    {
        'domain': 'hr',
        'difficulty': 'medium',
        'category': 'Self-Awareness & Growth',
        'title': 'What Is Your Greatest Weakness and How Do You Manage It?',
        'question_text': 'Tell me about an area where you struggle or a weakness you possess, and what concrete steps you take to overcome it.',
        'key_concepts': 'weakness, self-awareness, concrete steps, improvement, time management, perfectionism, delegation, feedback, progress',
        'model_answer': (
            "Earlier in my college projects, my biggest weakness was perfectionism—I would spend excessive time refactoring code or obsessing over minor UI animations before completing the core minimum viable product (MVP). "
            "To overcome this, I started adopting agile sprint planning and the 80/20 rule. I now time-box tasks using calendar blocks, define strict 'Definition of Done' criteria upfront, and prioritize shipping working functionality before optimizing. "
            "This structured approach has significantly improved my project velocity and helped me deliver full-stack projects on time without burning out."
        ),
        'hints': 'Pick a real, genuine professional trait (not a fake humblebrag), explain the negative consequence, and detail the actionable habit you adopted to manage it.',
    },

    # =========================================================================
    # HR & BEHAVIORAL - HARD
    # =========================================================================
    {
        'domain': 'hr',
        'difficulty': 'hard',
        'category': 'Crisis & Failure Management (STAR)',
        'title': 'Tell Me About a Significant Project Failure or Missed Deadline',
        'question_text': 'Describe a time when a project did not go as planned, an unexpected bug broke production, or you missed an important milestone. What went wrong and what did you learn?',
        'key_concepts': 'situation, task, failure, root cause, accountability, post-mortem, mitigation, proactive communication, resilience, lessons learned',
        'model_answer': (
            "Situation: Two days before our inter-college hackathon deadline, our application crashed during a team demo due to unhandled asynchronous API rate-limiting errors under concurrent load. "
            "Task: As backend maintainer, I had to fix the critical failure, communicate transparently with my team, and salvage our submission. "
            "Action: I took full accountability rather than blaming team members. I conducted a rapid root-cause analysis, identifying synchronous external API calls as the bottleneck. I immediately refactored the pipeline with exponential backoff retries, client-side caching, and graceful fallback responses. I also added automated unit test assertions for error states. "
            "Result: Our system recovered with zero crash errors during the live judges' evaluation, and we finished in the top 5 teams. More importantly, it taught me the crucial importance of defensive coding, load testing early, and remaining calm under pressure."
        ),
        'hints': 'Take 100% accountability without blaming teammates, explain root cause analysis, corrective action taken, and permanent resilience lessons learned.',
    },

    # =========================================================================
    # 🔥 LIVE DEMO: PROJECT DEFENSE (INTERVIEW THIS VERY PROJECT!)
    # =========================================================================
    {
        'domain': 'project_defense',
        'difficulty': 'easy',
        'category': 'Architecture & Tech Stack Rationale',
        'title': 'Explain the Architecture of Your AI Placement Interview Practice Bot',
        'question_text': 'Walk us through the high-level architecture of this project. Why did you choose Python Django, and how do the frontend, audio, and NLP components integrate?',
        'key_concepts': 'django, mvt architecture, web speech api, speech synthesis, speech recognition, scikit-learn, tf-idf, cosine similarity, sqlite, restful api, decoupled architecture',
        'model_answer': (
            "Our AI Placement Interview Practice Bot follows a modern Model-View-Template (MVT) architecture with a decoupled client-server interaction: "
            "1. Frontend: Built with responsive HTML/CSS/JavaScript utilizing native Web Speech APIs—SpeechSynthesis for the virtual interviewer's voice and SpeechRecognition for real-time speech-to-text transcript generation. "
            "2. Backend: Powered by Python Django, which provides robust routing, session state management, SQLite ORM for persistence, and RESTful API endpoints for asynchronous evaluation. "
            "3. AI Scoring Engine: An offline, zero-cost NLP pipeline using Scikit-Learn that combines TF-IDF n-gram vectorization, cosine similarity, keyword concept spotting, depth heuristics, and domain rubrics (like STAR for HR and Big-O for DSA) to generate instant scores and recruiter feedback. "
            "This design ensures zero external API latency, 100% uptime without paid cloud bills, and a secure local environment."
        ),
        'hints': 'Cover the 3 key layers: Browser Web Speech API, Django backend controller/ORM, and Scikit-Learn local NLP scoring pipeline.',
    },
    {
        'domain': 'project_defense',
        'difficulty': 'medium',
        'category': 'Algorithm Defense',
        'title': 'How Does Your Scoring Algorithm Evaluate Answers Without Paid APIs?',
        'question_text': 'The panel wants to know: In a world of OpenAI and cloud LLMs, how does your system score candidate responses accurately and provide feedback completely free of charge?',
        'key_concepts': 'zero-cost, tf-idf, n-grams, cosine similarity, concept coverage, keyword spotting, depth score, STAR heuristic, big-o detection, rubric weighting, scikit-learn',
        'model_answer': (
            "Instead of relying on costly, rate-limited, third-party APIs that can fail during panel demos, we engineered a multi-factor NLP rubric engine using Scikit-Learn and Python: "
            "1. Semantic Similarity (35%): TF-IDF n-gram (1-2) vectorization computes the cosine angle between candidate response and our benchmark model answer. "
            "2. Concept Coverage (35%): A domain keyword and phrase-spotting algorithm checks for mandatory technical terminology, categorizing concepts as 'Covered' or 'Missed'. "
            "3. Answer Depth & Substance (15%): Evaluates word count targets adjusted for question difficulty, alongside unique vocabulary density to filter out terse or evasive responses. "
            "4. Domain Structure Heuristics (15%): Tailored rule-based analyzers detect STAR framework components for HR, Big-O complexity for DSA, and architectural terms for Web Dev. "
            "The composite score (0-100) is converted into letter grades, recruiter verdicts, strengths, and targeted improvement tips deterministically in sub-50 milliseconds."
        ),
        'hints': 'Detail the 4 scoring pillars (TF-IDF Cosine 35%, Concept Spotting 35%, Depth 15%, Structure 15%) and emphasize sub-50ms latency with zero API costs.',
    },
    {
        'domain': 'project_defense',
        'difficulty': 'hard',
        'category': 'Engineering Trade-offs & Limitations',
        'title': 'Speech Handling, Latency Trade-offs, and Future Scaling of This Project',
        'question_text': 'What were the hardest technical challenges you encountered building this bot (e.g., speech accents, latency, edge cases), and how would you scale it commercially?',
        'key_concepts': 'web speech api, browser compatibility, background noise, microphone accents, fallback keyboard typing, latency, scikit-learn vs transformers, docker, postgresql, redis, webrtc, commercial scaling',
        'model_answer': (
            "We tackled three primary technical challenges during development: "
            "1. Speech Recognition Reliability: The browser Web Speech API can struggle with strong regional accents, noisy microphones, or technical acronyms (e.g. 'SQL' vs 'sequel'). To ensure zero frustration, we built seamless real-time interim transcript streaming with an instant editable text-area fallback, allowing candidates to speak and type concurrently. "
            "2. Evaluation Latency vs Quality: Heavy deep-learning transformer models introduce multi-second latency and memory overhead on typical student laptops. By optimizing Scikit-Learn's TF-IDF vectorizer and token matching in Python, evaluation occurs in under 50ms with zero GPU requirement. "
            "3. Commercial Scaling: To scale this to an institutional campus placement SaaS, we would containerize the Django backend with Docker, migrate SQLite to PostgreSQL with Redis caching for question delivery, integrate WebRTC for video recording and facial expression confidence analysis, and offer fine-tuned domain LLMs on a hybrid private cloud."
        ),
        'hints': 'Discuss speech recognition challenges & editable fallback, TF-IDF speed vs heavy GPU transformers, and the SaaS scaling roadmap.',
    },
]
