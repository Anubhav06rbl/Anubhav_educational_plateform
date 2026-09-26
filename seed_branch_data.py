import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "uploads", "documents")
os.makedirs(DOCS_DIR, exist_ok=True)

# 1. Generate text files for new sub-categories

# Python Guide
python_guide = """===================================================================
PYTHON 3 COMPREHENSIVE PROGRAMMING GUIDE
Department of Computer Science | Unit 1: Core to Advanced Python
===================================================================

1. CORE DATA STRUCTURES & COMPLEXITIES
--------------------------------------
- Lists (Dynamic Arrays): Append O(1), Insert/Delete O(n), Indexing O(1)
- Tuples (Immutable Sequences): Memory-efficient, hashable for dict keys
- Dictionaries (Hash Maps): Average O(1) lookup, insertion, deletion
- Sets: Unique unordered elements, O(1) membership checking (x in s)

2. LIST COMPREHENSIONS & GENERATORS
-----------------------------------
# List comprehension (creates list in memory):
squares = [x**2 for x in range(10) if x % 2 == 0]

# Generator expression (lazy evaluation for large streams):
gen_squares = (x**2 for x in range(10**6))
# Memory usage is constant O(1)!

3. DECORATORS & HIGHER-ORDER FUNCTIONS
--------------------------------------
A decorator wraps a function to modify or log its behavior:

def timer_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} executed in {time.time() - start:.4f}s")
        return result
    return wrapper

@timer_decorator
def compute_heavy_task():
    return sum(i * i for i in range(100000))

4. OBJECT-ORIENTED PROGRAMMING (OOP)
------------------------------------
Class inheritance, polymorphism, and encapsulated dunder methods:
- __init__(self): Constructor
- __str__(self): User-friendly string representation
- __repr__(self): Unambiguous developer representation
- @classmethod and @staticmethod decorators
"""
with open(os.path.join(DOCS_DIR, "python_complete_guide.txt"), "w", encoding="utf-8") as f:
    f.write(python_guide)

# GenAI Guide
genai_guide = """===================================================================
GENERATIVE AI, LLMS & TRANSFORMER ARCHITECTURES
Department of Computer Science | Advanced AI Specialization
===================================================================

1. THE TRANSFORMER REVOLUTION ("Attention Is All You Need", 2017)
-----------------------------------------------------------------
Traditional RNNs and LSTMs suffered from sequential bottleneck and
vanishing gradients over long contexts. Transformers introduced:

Self-Attention Equation:
    Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V

Where:
- Q (Query): What the current token is seeking
- K (Key): What each other token contains
- V (Value): The informational payload of each token
- d_k: Dimension of the keys (prevents exploding dot products)

2. CORE LLM PARADIGMS
---------------------
- Autoregressive Models (GPT series): Causal decoder-only, predicts next token
- Autoencoding Models (BERT series): Masked encoder-only, bidirectional context
- Sequence-to-Sequence (T5, BART): Encoder-decoder for translation/summarization

3. MODERN GENAI TECHNIQUES
--------------------------
- RAG (Retrieval-Augmented Generation): Grounds model generation in external
  knowledge bases using vector similarity search (cosine distance on embeddings).
- Fine-Tuning with LoRA (Low-Rank Adaptation): Freezes base model weights and
  injects trainable rank decomposition matrices, drastically reducing GPU memory.
- RLHF (Reinforcement Learning from Human Feedback): Uses PPO/DPO to align
  models with human preferences for safety, helpfulness, and tone.
"""
with open(os.path.join(DOCS_DIR, "generative_ai_llm_handbook.txt"), "w", encoding="utf-8") as f:
    f.write(genai_guide)

# Chemistry Guide
chem_guide = """===================================================================
ORGANIC CHEMISTRY: REACTION MECHANISMS & PERIODICITY
Department of Chemical Sciences | Unit 2 Revision Notes
===================================================================

1. NUCLEOPHILIC SUBSTITUTION: SN1 VS SN2
-----------------------------------------
Property         | SN1 (Substitution Nucleophilic Unimolecular) | SN2 (Bimolecular)
-----------------|---------------------------------------------|------------------
Mechanism Steps  | 2 steps (Carbocation intermediate formed)   | 1 concerted step
Kinetics         | Rate = k[Substrate]                         | Rate = k[Substrate][Nu]
Substrate Pref.  | Tertiary (3°) > Secondary (2°)             | Methyl > Primary (1°) > Secondary
Stereochemistry  | Racemization (mixture of enantiomers)       | Complete inversion (Walden)
Solvent          | Polar protic (e.g. H2O, EtOH)               | Polar aprotic (e.g. Acetone, DMSO)

2. ELECTROPHILIC AROMATIC SUBSTITUTION (EAS)
--------------------------------------------
Benzene rings react with electrophiles (E+) through arenium ion intermediates:
- Activating Groups (ortho/para directors): -OH, -NH2, -OCH3, -CH3
- Deactivating Groups (meta directors): -NO2, -CN, -COOH, -CHO
- Halogens (-Cl, -Br): Deactivating yet ortho/para directing due to resonance.

3. CHEMICAL EQUILIBRIUM & LE CHATELIER'S PRINCIPLE
--------------------------------------------------
If a system at dynamic equilibrium is subjected to stress (concentration,
temperature, pressure), the equilibrium shifts in the direction that minimizes
the imposed perturbation.
"""
with open(os.path.join(DOCS_DIR, "organic_chemistry_mechanisms.txt"), "w", encoding="utf-8") as f:
    f.write(chem_guide)

# History Guide
history_guide = """===================================================================
MODERN WORLD HISTORY: INDUSTRIAL REVOLUTION TO CONTEMPORARY ERA
Department of Humanities | Unit 1 Study Guide
===================================================================

1. THE INDUSTRIAL REVOLUTION (1760 - 1840)
------------------------------------------
- Origin: Great Britain due to abundant coal deposits, capital, and colonial trade.
- Technological breakthroughs: James Watt's improved steam engine, Hargreaves'
  Spinning Jenny, and Henry Cort's puddling process for wrought iron.
- Socio-economic impact: Rapid urbanization, emergence of the industrial working
  class (proletariat) and capitalist class (bourgeoisie), and factory labor laws.

2. THE AGE OF REVOLUTIONS
-------------------------
- American Revolution (1776): Declaration of Independence based on Enlightenment
  principles of Locke and Montesquieu (popular sovereignty and natural rights).
- French Revolution (1789): "Liberté, Égalité, Fraternité", storming of the Bastille,
  overthrow of the Ancien Régime, and the rise of Napoleon Bonaparte.

3. GLOBAL CONFLICTS & DECOLONIZATION
------------------------------------
- World War I (1914-1918) & Treaty of Versailles (1919)
- World War II (1939-1945) & Establishment of the United Nations
- The Cold War (1947-1991): Bipolar ideological conflict between NATO and the Warsaw Pact
- Decolonization across Asia and Africa leading to the Non-Aligned Movement (NAM).
"""
with open(os.path.join(DOCS_DIR, "modern_world_history.txt"), "w", encoding="utf-8") as f:
    f.write(history_guide)

# Geography Guide
geography_guide = """===================================================================
PHYSICAL GEOGRAPHY: PLATE TECTONICS & CLIMATIC SYSTEMS
Department of Humanities | Earth Systems Science
===================================================================

1. PLATE TECTONICS THEORY
-------------------------
The Earth's lithosphere is divided into rigid tectonic plates floating on the
semi-fluid asthenosphere.
- Convergent Boundaries: Plates collide. Oceanic-continental subduction forms
  volcanic arcs (e.g. Andes); continental-continental collision builds fold
  mountains (e.g. Himalayas).
- Divergent Boundaries: Plates pull apart, creating mid-ocean ridges (e.g. Mid-Atlantic
  Ridge) and rift valleys (East African Rift).
- Transform Boundaries: Plates slide horizontally past each other, generating
  shallow earthquakes (e.g. San Andreas Fault).

2. ATMOSPHERIC CIRCULATION & PRESSURE BELTS
-------------------------------------------
- Hadley Cells: Warm air rises at the Intertropical Convergence Zone (ITCZ), creating
  the Equatorial Low-Pressure trough, and sinks at 30° N/S (Subtropical Highs).
- Ferrel Cells & Polar Cells: Drive Mid-Latitude Westerlies and Polar Easterlies.
- Coriolis Effect: Deflects winds to the right in the Northern Hemisphere and to
  the left in the Southern Hemisphere.
"""
with open(os.path.join(DOCS_DIR, "physical_geography_notes.txt"), "w", encoding="utf-8") as f:
    f.write(geography_guide)

# Political Science Guide
polsci_guide = """===================================================================
POLITICAL SCIENCE: CONSTITUTIONAL FRAMEWORKS & DEMOCRACY
Department of Humanities | Foundations of Governance
===================================================================

1. FOUNDATIONAL POLITICAL THEORIES
----------------------------------
- Social Contract Theory: Thomas Hobbes (Leviathan), John Locke (Two Treatises of
  Government), and Jean-Jacques Rousseau (The Social Contract).
- Separation of Powers (Montesquieu): Division among Legislative (law-making),
  Executive (law-enforcing), and Judicial (law-interpreting) branches.
- Checks and Balances: Prevents despotic concentration of authority.

2. FORMS OF GOVERNMENT
-----------------------
- Parliamentary Democracy: Executive is drawn directly from and accountable to
  the legislature (e.g. United Kingdom, India). Prime Minister is head of government.
- Presidential System: Executive is independent of the legislature with a fixed
  term and separate popular mandate (e.g. United States).
- Federalism vs Unitary States: Division of sovereignty between central government
  and federated states/provinces.

3. FUNDAMENTAL RIGHTS & RULE OF LAW
-----------------------------------
- Rule of Law (A.V. Dicey): Supremacy of law, equality before the law, and
  protection of individual liberties against arbitrary power.
"""
with open(os.path.join(DOCS_DIR, "comparative_political_science.txt"), "w", encoding="utf-8") as f:
    f.write(polsci_guide)

# Hindi Notes
hindi_guide = """===================================================================
हिंदी साहित्य एवं व्याकरण (HINDI SAHITYA & GRAMMAR)
शाखा: Other | विषय: हिंदी
===================================================================

१. हिंदी व्याकरण के मूल तत्व (HINDI GRAMMAR)
---------------------------------------------
- संज्ञा (Noun): किसी व्यक्ति, वस्तु, स्थान या भाव के नाम को संज्ञा कहते हैं (व्यक्तिवाचक, जातिवाचक, भाववाचक)।
- सर्वनाम (Pronoun): संज्ञा के स्थान पर प्रयुक्त होने वाले शब्द (पुरुषवाचक, निश्चयवाचक, अनिश्चयवाचक, संबंधवाचक, प्रश्नवाचक, निजवाचक)।
- विशेषण (Adjective): संज्ञा या सर्वनाम की विशेषता बताने वाले शब्द (गुणवाचक, संख्यावाचक, परिमाणवाचक, सार्वनामिक)।
- क्रिया और काल (Verbs & Tenses): सकर्मक क्रिया, अकर्मक क्रिया। भूतकाल, वर्तमान काल, भविष्यत काल।

२. रस, छंद और अलंकार (LITERARY AESTHETICS)
------------------------------------------
- रस (Rasa): काव्य को पढ़ने या सुनने से उत्पन्न आनंद। मुख्य ९ रस (शृंगार, हास्य, करुण, रौद्र, वीर, भयानक, बीभत्स, अद्भुत, शांत)।
- अलंकार (Alankara): काव्य की शोभा बढ़ाने वाले तत्व:
  * शब्दालंकार: अनुप्रास (वर्णों की आवृत्ति), यमक (शब्द की पुनरावृत्ति भिन्न अर्थ में), श्लेष।
  * अर्थालंकार: उपमा, रूपक, उत्प्रेक्षा, अतिशयोक्ति।

३. हिंदी साहित्य का इतिहास कालखंड
----------------------------------
१. आदिकाल (वीरगाथा काल): संवत १०५० - १३७५
२. भक्तिकाल (स्वर्ण युग): संवत १३७५ - १७०० (कबीर, सूरदास, तुलसीदास, जायसी)
३. रीतिकाल: संवत १७०० - १९०० (बिहारी, केशवदास, घनानंद)
४. आधुनिक काल (गद्य काल): संवत १९०० से अब तक (भारतेंदु हरिश्चंद्र, प्रेमचंद, महादेवी वर्मा, दिनकर)
"""
with open(os.path.join(DOCS_DIR, "hindi_sahitya_grammar_notes.txt"), "w", encoding="utf-8") as f:
    f.write(hindi_guide)

# English Guide
english_guide = """===================================================================
ADVANCED ENGLISH GRAMMAR, RHETORIC & COMPOSITION
Branch: Other | Subject: English
===================================================================

1. ADVANCED SYNTAX & SENTENCE ARCHITECTURE
------------------------------------------
- Clauses: Independent vs Dependent (Subordinate: Noun, Adjective, Adverbial clauses).
- Parallelism: Balancing paired grammatical structures for rhetorical clarity.
  Example: "She likes reading, writing, and swimming" (not "to read, writing, and swim").
- Conditional Sentences:
  * Zero: General truths (If it rains, grass gets wet).
  * First: Realistic future possibilities (If you study, you will succeed).
  * Second: Hypothetical present/future (If I had more time, I would travel).
  * Third: Counterfactual past events (If she had known, she would have called).

2. COMMON GRAMMATICAL PITFALLS
------------------------------
- Dangling Modifiers: A modifier that lacks a clear subject to modify.
  Incorrect: "Walking into the room, the smoke was seen."
  Correct: "Walking into the room, the inspector saw smoke."
- Subject-Verb Agreement with collective nouns and indefinite pronouns (neither/nor, either/or).

3. VOCABULARY & RHETORICAL DEVICES
----------------------------------
- Metaphor, Simile, Personification, Hyperbole, Irony, Oxymoron.
- Academic & Professional Register: Cohesion, logical transitions (furthermore, nevertheless, consequently).
"""
with open(os.path.join(DOCS_DIR, "english_advanced_grammar_composition.txt"), "w", encoding="utf-8") as f:
    f.write(english_guide)

print("Educational text notes created successfully!")

# 2. Build Updated materials.json with complete taxonomy
materials_data = [
    # Computer Science
    {
        "id": "mat_cs_1",
        "title": "Python 3 Modern Programming: Fundamentals to Advanced OOP",
        "branch": "Computer Science",
        "sub_category": "Python",
        "category": "Computer Science",
        "chapter": "Unit 1: Python Core & Idiomatic Code",
        "resource_type": "documents",
        "description": "Comprehensive reference handbook covering Python data structures, list comprehensions, decorators, generators, and object-oriented class hierarchies.",
        "tags": ["Python", "Programming", "OOP", "Decorators", "CS"],
        "filename": "python_complete_guide.txt",
        "file_url": "/uploads/documents/python_complete_guide.txt",
        "is_external_link": False,
        "filesize": os.path.getsize(os.path.join(DOCS_DIR, "python_complete_guide.txt")),
        "filesize_formatted": "2.2 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-26T16:00:00Z"
    },
    {
        "id": "mat_cs_2",
        "title": "Generative AI, LLMs & Transformer Architectures Handbook",
        "branch": "Computer Science",
        "sub_category": "GenAI",
        "category": "Computer Science",
        "chapter": "CS 502: Advanced Generative Modeling",
        "resource_type": "documents",
        "description": "Deep dive into self-attention mathematics, Transformer encoder-decoder mechanics, RAG architecture, LoRA fine-tuning, and RLHF alignment.",
        "tags": ["GenAI", "LLMs", "Transformers", "RAG", "Attention"],
        "filename": "generative_ai_llm_handbook.txt",
        "file_url": "/uploads/documents/generative_ai_llm_handbook.txt",
        "is_external_link": False,
        "filesize": os.path.getsize(os.path.join(DOCS_DIR, "generative_ai_llm_handbook.txt")),
        "filesize_formatted": "2.4 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-26T16:05:00Z"
    },
    {
        "id": "mat_cs_3",
        "title": "Machine Learning & Deep Learning 101 Lecture Slide Deck",
        "branch": "Computer Science",
        "sub_category": "ML",
        "category": "Computer Science",
        "chapter": "CS 401: Foundations of Artificial Intelligence",
        "resource_type": "slides",
        "description": "Multi-page landscape presentation covering supervised vs unsupervised learning, backpropagation gradients, loss functions, and optimization algorithms.",
        "tags": ["MachineLearning", "DeepLearning", "AI", "Slides", "NeuralNetworks"],
        "filename": "machine_learning_101_slides.pdf",
        "file_url": "/uploads/slides/machine_learning_101_slides.pdf",
        "is_external_link": False,
        "filesize": 3835,
        "filesize_formatted": "4.2 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-24T16:00:00Z"
    },

    # Science
    {
        "id": "mat_sci_1",
        "title": "Quantum Physics Fundamentals & Wave-Particle Duality",
        "branch": "Science",
        "sub_category": "Physics",
        "category": "Science",
        "chapter": "Unit 3: Modern Physics & Quantum Mechanics",
        "resource_type": "documents",
        "description": "Comprehensive study notes covering Planck's quantum hypothesis, Einstein's photoelectric effect, de Broglie matter waves, and the Heisenberg uncertainty principle.",
        "tags": ["Physics", "Quantum", "Planck", "Photons", "Science"],
        "filename": "quantum_physics_fundamentals.txt",
        "file_url": "/uploads/documents/quantum_physics_fundamentals.txt",
        "is_external_link": False,
        "filesize": 2540,
        "filesize_formatted": "2.5 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-20T10:30:00Z"
    },
    {
        "id": "mat_sci_2",
        "title": "Organic Chemistry: Reaction Mechanisms & Periodic Equilibrium",
        "branch": "Science",
        "sub_category": "Chemistry",
        "category": "Science",
        "chapter": "Unit 2: Organic Reaction Pathways",
        "resource_type": "documents",
        "description": "Master SN1 vs SN2 substitution kinetics, electrophilic aromatic substitution directing effects, and Le Chatelier's equilibrium principles.",
        "tags": ["Chemistry", "Organic", "SN1", "SN2", "Reactions"],
        "filename": "organic_chemistry_mechanisms.txt",
        "file_url": "/uploads/documents/organic_chemistry_mechanisms.txt",
        "is_external_link": False,
        "filesize": os.path.getsize(os.path.join(DOCS_DIR, "organic_chemistry_mechanisms.txt")),
        "filesize_formatted": "2.0 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-26T16:02:00Z"
    },
    {
        "id": "mat_sci_3",
        "title": "DNA Replication Fork & Molecular Architecture Diagram",
        "branch": "Science",
        "sub_category": "Biology",
        "category": "Science",
        "chapter": "Chapter 7: Genetics & Molecular Biology",
        "resource_type": "images",
        "description": "High-resolution schematic diagram illustrating leading strand continuous synthesis, lagging strand Okazaki fragments, helicase, and DNA polymerase.",
        "tags": ["Genetics", "DNA", "Biology", "Helicase", "Diagram"],
        "filename": "dna_replication_diagram.png",
        "file_url": "/uploads/images/dna_replication_diagram.png",
        "is_external_link": False,
        "filesize": 22050,
        "filesize_formatted": "32.4 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-22T09:40:00Z"
    },

    # Humanities
    {
        "id": "mat_hum_1",
        "title": "Modern World History: Industrial Revolution to Contemporary Era",
        "branch": "Humanities",
        "sub_category": "History",
        "category": "Humanities",
        "chapter": "Unit 1: The Modern Transformation",
        "resource_type": "documents",
        "description": "Historical synthesis covering the British Industrial Revolution, Age of Democratic Revolutions, World Wars, Cold War geopolitics, and global decolonization.",
        "tags": ["History", "IndustrialRevolution", "ColdWar", "Humanities"],
        "filename": "modern_world_history.txt",
        "file_url": "/uploads/documents/modern_world_history.txt",
        "is_external_link": False,
        "filesize": os.path.getsize(os.path.join(DOCS_DIR, "modern_world_history.txt")),
        "filesize_formatted": "2.1 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-26T16:03:00Z"
    },
    {
        "id": "mat_hum_2",
        "title": "Physical Geography: Plate Tectonics & Atmospheric Dynamics",
        "branch": "Humanities",
        "sub_category": "Geography",
        "category": "Humanities",
        "chapter": "Earth Systems & Geomorphology",
        "resource_type": "documents",
        "description": "Exploration of convergent and divergent plate boundaries, seismic fault zones, global atmospheric pressure belts, Hadley cells, and the Coriolis force.",
        "tags": ["Geography", "PlateTectonics", "Climate", "EarthScience"],
        "filename": "physical_geography_notes.txt",
        "file_url": "/uploads/documents/physical_geography_notes.txt",
        "is_external_link": False,
        "filesize": os.path.getsize(os.path.join(DOCS_DIR, "physical_geography_notes.txt")),
        "filesize_formatted": "1.9 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-26T16:04:00Z"
    },
    {
        "id": "mat_hum_3",
        "title": "Comparative Political Science: Constitutional Governance & Rights",
        "branch": "Humanities",
        "sub_category": "Political Science",
        "category": "Humanities",
        "chapter": "Foundations of Democratic Governance",
        "resource_type": "documents",
        "description": "Study of social contract philosophy, Montesquieu's separation of powers, parliamentary vs presidential frameworks, and constitutional rule of law.",
        "tags": ["PoliticalScience", "Constitution", "Democracy", "Governance"],
        "filename": "comparative_political_science.txt",
        "file_url": "/uploads/documents/comparative_political_science.txt",
        "is_external_link": False,
        "filesize": os.path.getsize(os.path.join(DOCS_DIR, "comparative_political_science.txt")),
        "filesize_formatted": "1.8 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-26T16:05:00Z"
    },

    # Other (Hindi & English)
    {
        "id": "mat_oth_1",
        "title": "हिंदी साहित्य परिचय एवं संपूर्ण व्याकरण नोट्स (Hindi Vyakaran)",
        "branch": "Other",
        "sub_category": "Hindi",
        "category": "Other",
        "chapter": "हिंदी व्याकरण, रस, छंद व कालखंड",
        "resource_type": "documents",
        "description": "हिंदी संज्ञा, सर्वनाम, विशेषण, क्रिया, काल, रस, छंद, अलंकार तथा भक्तिकाल-आधुनिक काल के प्रमुख साहित्यकारों का विस्तृत संकलन।",
        "tags": ["Hindi", "हिंदी", "व्याकरण", "साहित्य", "Other"],
        "filename": "hindi_sahitya_grammar_notes.txt",
        "file_url": "/uploads/documents/hindi_sahitya_grammar_notes.txt",
        "is_external_link": False,
        "filesize": os.path.getsize(os.path.join(DOCS_DIR, "hindi_sahitya_grammar_notes.txt")),
        "filesize_formatted": "2.2 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-26T16:06:00Z"
    },
    {
        "id": "mat_oth_2",
        "title": "Advanced English Grammar, Rhetoric & Composition Handbook",
        "branch": "Other",
        "sub_category": "English",
        "category": "Other",
        "chapter": "Unit 1: Syntax, Conditionals & Rhetoric",
        "resource_type": "documents",
        "description": "Master advanced sentence structures, conditional clauses, dangling modifier corrections, parallelism, and academic rhetorical composition.",
        "tags": ["English", "Grammar", "Syntax", "Writing", "Composition"],
        "filename": "english_advanced_grammar_composition.txt",
        "file_url": "/uploads/documents/english_advanced_grammar_composition.txt",
        "is_external_link": False,
        "filesize": os.path.getsize(os.path.join(DOCS_DIR, "english_advanced_grammar_composition.txt")),
        "filesize_formatted": "2.0 KB",
        "uploaded_by": "Anubhav (Super Admin)",
        "uploaded_at": "2026-09-26T16:07:00Z"
    }
]

with open(os.path.join(DATA_DIR, "materials.json"), "w", encoding="utf-8") as f:
    json.dump(materials_data, f, indent=2, ensure_ascii=False)

# 3. Update quizzes.json with branch and sub_category
quizzes_data = [
    {
        "id": "quiz_cs_py",
        "title": "Python Core & Advanced Programming Mastery Test",
        "branch": "Computer Science",
        "sub_category": "Python",
        "category": "Computer Science",
        "chapter": "Unit 1: Python Core",
        "description": "Test your mastery of Python data structures, decorators, generator expressions, and complexity.",
        "time_limit_minutes": 10,
        "total_points": 20,
        "created_at": "2026-09-26T16:00:00Z",
        "questions": [
            {
                "id": "q_py_1",
                "question": "What is the average time complexity of looking up a key in a Python dictionary?",
                "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
                "correct_option_index": 2,
                "points": 10,
                "explanation": "Python dictionaries are implemented as hash tables, providing average O(1) time complexity for lookups."
            },
            {
                "id": "q_py_2",
                "question": "What is the primary memory advantage of a generator expression over a list comprehension?",
                "options": [
                    "Generators store elements in binary format",
                    "Generators evaluate items lazily on-the-fly, consuming constant O(1) memory",
                    "Generators allow multithreaded evaluation",
                    "Generators automatically cache results on disk"
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "Generators yield items one at a time using iterator protocol, avoiding memory allocation for the entire collection."
            }
        ]
    },
    {
        "id": "quiz_cs_genai",
        "title": "Generative AI & Transformer Architectures Assessment",
        "branch": "Computer Science",
        "sub_category": "GenAI",
        "category": "Computer Science",
        "chapter": "CS 502: Advanced GenAI",
        "description": "Assess your knowledge of self-attention mechanisms, LLM architectures, and RAG systems.",
        "time_limit_minutes": 10,
        "total_points": 20,
        "created_at": "2026-09-26T16:05:00Z",
        "questions": [
            {
                "id": "q_genai_1",
                "question": "In the self-attention equation Attention(Q, K, V) = softmax((Q*K^T)/sqrt(d_k))*V, why is the dot product scaled by sqrt(d_k)?",
                "options": [
                    "To convert the matrix into square form",
                    "To prevent large values from pushing softmax into regions with extremely small gradients",
                    "To enforce symmetric attention matrices",
                    "To eliminate negative embedding weights"
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "Scaling by sqrt(d_k) prevents large dot products from causing vanishing gradients in the softmax function."
            },
            {
                "id": "q_genai_2",
                "question": "Which component is central to Retrieval-Augmented Generation (RAG) to ground LLMs in private documents?",
                "options": [
                    "Vector embeddings and similarity search index",
                    "Convolutional feature extraction layers",
                    "Hidden Markov models",
                    "Recurrent cell hidden states"
                ],
                "correct_option_index": 0,
                "points": 10,
                "explanation": "RAG indexes documents as dense vector embeddings and retrieves semantically relevant passages via vector similarity."
            }
        ]
    },
    {
        "id": "quiz_sci_phy",
        "title": "Modern Physics & Quantum Concepts Test",
        "branch": "Science",
        "sub_category": "Physics",
        "category": "Science",
        "chapter": "Unit 3: Modern Physics",
        "description": "Test your grasp on wave-particle duality, uncertainty principle, and photoelectric equations.",
        "time_limit_minutes": 10,
        "total_points": 20,
        "created_at": "2026-09-21T10:00:00Z",
        "questions": [
            {
                "id": "q_phy_1",
                "question": "Who formulated the hypothesis that light is emitted or absorbed in discrete packets called quanta?",
                "options": ["Albert Einstein", "Max Planck", "Niels Bohr", "Erwin Schrödinger"],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "Max Planck introduced the quantum hypothesis in 1900 to resolve the ultraviolet catastrophe."
            },
            {
                "id": "q_phy_2",
                "question": "According to de Broglie relationship (λ = h / p), what happens to wavelength when momentum doubles?",
                "options": ["It doubles", "It is halved", "It quadruples", "It remains unchanged"],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "Wavelength is inversely proportional to momentum: if momentum doubles, wavelength is halved."
            }
        ]
    },
    {
        "id": "quiz_oth_hi",
        "title": "हिंदी व्याकरण एवं साहित्य ज्ञान परीक्षा (Hindi Test)",
        "branch": "Other",
        "sub_category": "Hindi",
        "category": "Other",
        "chapter": "हिंदी व्याकरण व साहित्य",
        "description": "रस, अलंकार तथा हिंदी साहित्य के प्रमुख कालखंडों पर आधारित ज्ञान परखें।",
        "time_limit_minutes": 10,
        "total_points": 20,
        "created_at": "2026-09-26T16:06:00Z",
        "questions": [
            {
                "id": "q_hi_1",
                "question": "हिंदी साहित्य के किस कालखंड को 'स्वर्ण युग' (Golden Age) कहा जाता है?",
                "options": ["आदिकाल", "भक्तिकाल", "रीतिकाल", "आधुनिक काल"],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "कबीर, तुलसीदास, सूरदास और जायसी जैसे महान संतों की रचनाओं के कारण भक्तिकाल को हिंदी साहित्य का स्वर्ण युग कहा जाता है।"
            },
            {
                "id": "q_hi_2",
                "question": "'कनक कनक ते सौ गुनी, मादकता अधिकाय' में कौन-सा अलंकार है?",
                "options": ["अनुप्रास अलंकार", "यमक अलंकार", "श्लेष अलंकार", "उपमा अलंकार"],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "यहाँ 'कनक' शब्द दो बार आया है और दोनों बार अर्थ अलग है (एक कनक = सोना, दूसरा कनक = धतूरा), इसलिए यह यमक अलंकार है।"
            }
        ]
    },
    {
        "id": "quiz_oth_en",
        "title": "Advanced English Grammar & Syntax Assessment",
        "branch": "Other",
        "sub_category": "English",
        "category": "Other",
        "chapter": "Unit 1: Advanced Syntax",
        "description": "Evaluate proficiency in conditionals, parallelism, and grammatical agreement.",
        "time_limit_minutes": 10,
        "total_points": 20,
        "created_at": "2026-09-26T16:07:00Z",
        "questions": [
            {
                "id": "q_en_1",
                "question": "Identify the sentence that correctly exemplifies Third Conditional syntax:",
                "options": [
                    "If she studies hard, she will pass the exam.",
                    "If she had studied harder, she would have passed the exam.",
                    "If she studied harder, she would pass the exam.",
                    "If she studies hard, she passes the exam."
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "Third conditional structures follow: If + Past Perfect, would have + Past Participle."
            },
            {
                "id": "q_en_2",
                "question": "Which of the following contains a dangling modifier?",
                "options": [
                    "Having finished the experiment, the scientist recorded the observations.",
                    "Having finished the experiment, the results were recorded.",
                    "After finishing the experiment, she left the laboratory.",
                    "Upon concluding the study, they published the findings."
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "In 'Having finished the experiment, the results were recorded', the results cannot finish an experiment, leaving the participle dangling."
            }
        ]
    }
]

with open(os.path.join(DATA_DIR, "quizzes.json"), "w", encoding="utf-8") as f:
    json.dump(quizzes_data, f, indent=2, ensure_ascii=False)

print("Seed generation complete for all 4 branches!")
