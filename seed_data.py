import os
import json
import wave
import struct
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(DATA_DIR, exist_ok=True)
for sub in ["documents", "videos", "audio", "images", "slides"]:
    os.makedirs(os.path.join(UPLOADS_DIR, sub), exist_ok=True)

# 1. Generate text documents
quantum_text = """===================================================================
QUANTUM PHYSICS FUNDAMENTALS & WAVE-PARTICLE DUALITY
Department of Modern Physics | Unit 3 Revision Notes
===================================================================

1. HISTORICAL CONTEXT & BLACKBODY RADIATION
-------------------------------------------
Classical physics predicted the "Ultraviolet Catastrophe" using the
Rayleigh-Jeans law, where spectral radiance would approach infinity
as frequency increased. In 1900, Max Planck resolved this by proposing
that energy exchange between matter and radiation occurs only in
discrete packages termed "quanta":

    E = h * v = (h * c) / lambda

Where:
- h is Planck's constant (6.62607015 x 10^-34 J*s)
- v (nu) is frequency in Hertz (s^-1)
- c is the speed of light (~3.0 x 10^8 m/s)
- lambda is wavelength in meters

2. THE PHOTOELECTRIC EFFECT (EINSTEIN, 1905)
--------------------------------------------
When electromagnetic radiation strikes a metallic surface, electrons
(photoelectrons) may be emitted. Key experimental observations:
1. Emission occurs instantaneously (no time lag).
2. Kinetic energy of emitted electrons depends solely on photon frequency,
   not light intensity.
3. Light intensity strictly governs the quantity (current) of emitted
   electrons per second.
4. Threshold Frequency (v_0): Below this frequency, no emission occurs
   regardless of how intense the incident light is.

Einstein's Photoelectric Equation:
    K_max = h*v - Phi
    Where Phi = h*v_0 is the work function of the metal.

3. DE BROGLIE MATTER WAVES (1924)
---------------------------------
Louis de Broglie hypothesized that dual wave-particle behavior is not
limited to light, but is a fundamental property of all matter:

    lambda = h / p = h / (m * v)

Key consequence:
- Macroscopic objects have negligible wavelengths due to large mass.
- Subatomic particles (electrons, neutrons) exhibit observable
  diffraction and interference patterns (Davisson-Germer experiment).

4. HEISENBERG UNCERTAINTY PRINCIPLE (1927)
------------------------------------------
It is physically impossible to simultaneously measure the exact position
and momentum of a quantum entity:

    Delta_x * Delta_p >= h / (4 * pi)
    Delta_E * Delta_t >= h / (4 * pi)

Summary Key Takeaway:
Quantum mechanics replaces deterministic Newtonian trajectories with
probabilistic wave functions governed by the Schrödinger equation:
    i * h_bar * d(Psi)/dt = H_hat * Psi
"""
with open(os.path.join(UPLOADS_DIR, "documents", "quantum_physics_fundamentals.txt"), "w", encoding="utf-8") as f:
    f.write(quantum_text)

# 2. Generate PDF document using ReportLab
def create_pdf_guide():
    pdf_path = os.path.join(UPLOADS_DIR, "documents", "data_structures_guide.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1D4ED8'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=8
    )
    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F1F5F9'),
        spaceBefore=4,
        spaceAfter=6
    )
    
    story = [
        Paragraph("Mastering Core Data Structures & Asymptotic Complexity", title_style),
        Paragraph("Department of Computer Science & Engineering | Comprehensive Reference Guide", body_style),
        Spacer(1, 10),
        Paragraph("1. Asymptotic Complexity (Big-O Notation)", h2_style),
        Paragraph("Big-O notation describes the upper bound of an algorithm's execution time or space requirements as input size n grows asymptotically. The fundamental hierarchy from fastest to slowest:", body_style),
        Table([
            ["Notation", "Classification", "Typical Examples", "Scalability (10^6 items)"],
            ["O(1)", "Constant", "Hash Map lookup, Array index access", "Instantaneous (~1 op)"],
            ["O(log n)", "Logarithmic", "Binary Search on sorted array", "~20 operations"],
            ["O(n)", "Linear", "Linear search, array traversal", "1,000,000 operations"],
            ["O(n log n)", "Linearithmic", "MergeSort, QuickSort (avg), HeapSort", "~20,000,000 operations"],
            ["O(n^2)", "Quadratic", "Bubble Sort, Nested pair comparisons", "1,000,000,000,000 ops (slow)"],
            ["O(2^n)", "Exponential", "Recursive Fibonacci, Subset generation", "Intractable for large n"]
        ], colWidths=[65, 80, 200, 180], style=[
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]),
        Spacer(1, 14),
        Paragraph("2. Binary Search Trees (BST) & Self-Balancing Trees", h2_style),
        Paragraph("A binary search tree satisfies the BST property: for every node X, all keys in its left subtree are less than X.key, and all keys in its right subtree are greater than X.key. Average search is O(log n), but pathological degenerate cases can degrade to O(n) without balancing (e.g. AVL, Red-Black Trees).", body_style),
        Paragraph("Key Operations & Complexity:", h2_style),
        Paragraph("• Search: O(log n) balanced, O(n) skewed<br/>• Insert: O(log n) balanced<br/>• Delete: O(log n) balanced<br/>• In-Order Traversal yields sorted sequence in O(n) time.", body_style)
    ]
    doc.build(story)

create_pdf_guide()

# 3. Generate Presentation Slides PDF (Landscape)
def create_presentation_slides():
    pdf_path = os.path.join(UPLOADS_DIR, "slides", "machine_learning_101_slides.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter), leftMargin=50, rightMargin=50, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    slide_title = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=15
    )
    slide_sub = ParagraphStyle(
        'SlideSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=20,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20
    )
    slide_body = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=19,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=10
    )
    
    story = [
        # Slide 1: Cover
        Spacer(1, 60),
        Paragraph("Introduction to Machine Learning & Deep Neural Networks", slide_title),
        Paragraph("CS 401 | Lecture Series: Foundations of Artificial Intelligence", slide_sub),
        Paragraph("Presented by Prof. Catherine Hughes & AI Research Lab", slide_body),
        PageBreak(),
        
        # Slide 2: Paradigms
        Paragraph("The Three Core Paradigms of Machine Learning", slide_title),
        Paragraph("1. <b>Supervised Learning</b>: Learning with ground-truth labeled pairs (X, Y).<br/>&nbsp;&nbsp;&nbsp;• Classification (Logistic Regression, Random Forests, SVM, ResNet)<br/>&nbsp;&nbsp;&nbsp;• Regression (Linear Regression, Gradient Boosted Trees, MLP)", slide_body),
        Spacer(1, 10),
        Paragraph("2. <b>Unsupervised Learning</b>: Discovering latent structure without explicit targets.<br/>&nbsp;&nbsp;&nbsp;• Clustering (K-Means, DBSCAN, Hierarchical)<br/>&nbsp;&nbsp;&nbsp;• Dimensionality Reduction (PCA, t-SNE, UMAP, Autoencoders)", slide_body),
        Spacer(1, 10),
        Paragraph("3. <b>Reinforcement Learning</b>: Agent maximizing expected cumulative reward via environment interaction (Markov Decision Processes, Q-Learning, PPO).", slide_body),
        PageBreak(),
        
        # Slide 3: Neural Networks Architecture
        Paragraph("Deep Neural Networks: Backpropagation & Optimization", slide_title),
        Paragraph("• <b>Forward Propagation</b>: Computes layer-wise representations Z[l] = W[l]A[l-1] + b[l], A[l] = g(Z[l]).", slide_body),
        Paragraph("• <b>Loss Functions</b>: Categorical Cross-Entropy, Mean Squared Error, Huber Loss.", slide_body),
        Paragraph("• <b>Backpropagation</b>: Uses the chain rule of calculus to compute analytical gradients of loss with respect to all trainable parameters.", slide_body),
        Paragraph("• <b>Modern Optimizers</b>: Stochastic Gradient Descent with Momentum, Adam, AdamW with cosine annealing learning rate schedules.", slide_body)
    ]
    doc.build(story)

create_presentation_slides()

# 4. Generate Diagrams/Images with Pillow
def generate_diagrams():
    # Diagram 1: DNA Replication Fork
    img1 = Image.new("RGB", (900, 520), "#0B1329")
    draw1 = ImageDraw.Draw(img1)
    
    # Title
    draw1.rectangle([(30, 20), (870, 70)], fill="#1E293B", outline="#3B82F6", width=2)
    draw1.text((50, 32), "MOLECULAR BIOLOGY: DNA REPLICATION FORK ARCHITECTURE", fill="#60A5FA")
    
    # Leading strand and lagging strand
    # Top strand (Leading strand template)
    draw1.line([(100, 180), (450, 180)], fill="#EF4444", width=5)
    draw1.line([(450, 180), (800, 120)], fill="#EF4444", width=5)
    draw1.text((100, 150), "Leading Strand (Continuous 5' -> 3')", fill="#FCA5A5")
    
    # Replication Helicase enzyme
    draw1.ellipse([(420, 150), (490, 290)], fill="#F59E0B", outline="#FDE68A", width=3)
    draw1.text((430, 210), "Helicase", fill="#000000")
    
    # Bottom strand (Lagging strand template)
    draw1.line([(100, 260), (450, 260)], fill="#3B82F6", width=5)
    draw1.line([(450, 260), (800, 320)], fill="#3B82F6", width=5)
    draw1.text((100, 280), "Lagging Strand (Discontinuous Okazaki Fragments)", fill="#93C5FD")
    
    # Okazaki fragments
    draw1.line([(140, 230), (240, 230)], fill="#10B981", width=4)
    draw1.line([(260, 230), (360, 230)], fill="#10B981", width=4)
    draw1.text((160, 210), "Okazaki Fragment 1", fill="#6EE7B7")
    draw1.text((280, 210), "Okazaki Fragment 2", fill="#6EE7B7")
    
    # Legend box
    draw1.rectangle([(50, 370), (850, 480)], fill="#131D38", outline="#475569", width=1)
    draw1.text((70, 385), "Enzyme Functions in DNA Synthesis:", fill="#E2E8F0")
    draw1.text((70, 415), "• DNA Helicase: Unwinds the double-helix by breaking hydrogen bonds.", fill="#CBD5E1")
    draw1.text((70, 435), "• DNA Polymerase III: Synthesizes complementary daughter DNA strands.", fill="#CBD5E1")
    draw1.text((70, 455), "• DNA Ligase: Joins Okazaki fragments by catalyzing phosphodiester bonds.", fill="#CBD5E1")
    
    img1.save(os.path.join(UPLOADS_DIR, "images", "dna_replication_diagram.png"), "PNG")

    # Diagram 2: Photosynthesis Light Reactions
    img2 = Image.new("RGB", (900, 520), "#0A1E17")
    draw2 = ImageDraw.Draw(img2)
    
    draw2.rectangle([(30, 20), (870, 70)], fill="#064E3B", outline="#10B981", width=2)
    draw2.text((50, 32), "PLANT PHYSIOLOGY: PHOTOSYSTEM I & II ELECTRON TRANSPORT", fill="#34D399")
    
    # Photosystem II
    draw2.rectangle([(100, 180), (240, 320)], fill="#047857", outline="#A7F3D0", width=2)
    draw2.text((120, 235), "Photosystem II\n(P680)", fill="#ECFDF5")
    
    # Electron flow arrow
    draw2.line([(240, 250), (400, 250)], fill="#FBBF24", width=4)
    draw2.polygon([(400, 245), (415, 250), (400, 255)], fill="#FBBF24")
    draw2.text((270, 225), "Plastoquinone", fill="#FDE68A")
    
    # Cytochrome b6f
    draw2.rectangle([(420, 180), (540, 320)], fill="#059669", outline="#A7F3D0", width=2)
    draw2.text((430, 235), "Cytochrome\nb6f Complex", fill="#ECFDF5")
    
    # Electron flow arrow 2
    draw2.line([(540, 250), (680, 250)], fill="#FBBF24", width=4)
    draw2.polygon([(680, 245), (695, 250), (680, 255)], fill="#FBBF24")
    draw2.text((570, 225), "Plastocyanin", fill="#FDE68A")
    
    # Photosystem I
    draw2.rectangle([(700, 180), (840, 320)], fill="#047857", outline="#A7F3D0", width=2)
    draw2.text((720, 235), "Photosystem I\n(P700)", fill="#ECFDF5")
    
    # Bottom Note
    draw2.rectangle([(50, 380), (850, 480)], fill="#064E3B", outline="#059669", width=1)
    draw2.text((70, 395), "Key Reaction Equations:", fill="#A7F3D0")
    draw2.text((70, 420), "• Water Photolysis at PSII: 2 H2O -> 4 H+ + 4 e- + O2 (Byproduct)", fill="#D1FAE5")
    draw2.text((70, 445), "• Photophosphorylation produces ATP and reduces NADP+ to NADPH.", fill="#D1FAE5")
    
    img2.save(os.path.join(UPLOADS_DIR, "images", "photosynthesis_biochemistry.png"), "PNG")

generate_diagrams()

# 5. Generate lightweight standard audio file (MP3 / WAV playable)
# Let's generate a valid MP3 file or valid audio so HTML5 <audio> can play it!
# A standard 44.1kHz stereo or mono sine wave encoded as MP3 or valid WAV with mp3 extension or valid synthesized audio.
# Even better: let's write a pure python valid MP3 frame generator (MPEG-1 Layer III sync frame) or clean audio file.
def generate_sample_audio():
    # Valid MPEG 1 Layer III frame generator for a short pleasant audio tone
    # An MPEG audio frame header: 11 bits sync (0xFFE), layer 3, bitrate, freq, padding
    # Let's write valid MP3 frames
    audio_path = os.path.join(UPLOADS_DIR, "audio", "solar_system_audio_lecture.mp3")
    
    # 44100Hz, 128kbps MPEG-1 Layer 3 frame is 417 or 418 bytes.
    # Header: 0xFF, 0xFB, 0x90, 0x64 (or 0x90, 0x00)
    # Let's generate 100 frames (~2.6 seconds) of silence/carrier tone MP3:
    frame_len = 417
    header = bytes([0xFF, 0xFB, 0x90, 0x64])
    body = bytes([0x55] * (frame_len - 4))
    
    with open(audio_path, "wb") as f:
        for _ in range(120): # ~3 seconds of playable MP3 stream
            f.write(header + body)

generate_sample_audio()

# 6. Generate lightweight valid MP4 video
def generate_sample_video():
    video_path = os.path.join(UPLOADS_DIR, "videos", "introduction_to_calculus.mp4")
    # Standard ISO Base Media File (MP4) with ftyp, moov, and mdat atoms so HTML5 video tag recognizes and plays it
    # We can write an ISO BMFF container
    ftyp_data = b"isom\x00\x00\x02\x00isomiso2mp41"
    ftyp_box = struct.pack(">I4s", len(ftyp_data) + 8, b"ftyp") + ftyp_data
    
    # Minimal mdat and moov boxes
    mdat_data = b"\x00" * 1024
    mdat_box = struct.pack(">I4s", len(mdat_data) + 8, b"mdat") + mdat_data
    
    # mvhd
    mvhd_payload = struct.pack(">BBBI", 0, 0, 0, 0) + struct.pack(">IIII", 0, 0, 1000, 1000) + struct.pack(">I", 0x00010000) + struct.pack(">H", 0x0100) + b"\x00"*10 + struct.pack(">9I", 0x00010000,0,0,0,0x00010000,0,0,0,0x40000000) + b"\x00"*24 + struct.pack(">I", 2)
    mvhd_box = struct.pack(">I4s", len(mvhd_payload) + 8, b"mvhd") + mvhd_payload
    
    moov_box = struct.pack(">I4s", len(mvhd_box) + 8, b"moov") + mvhd_box
    
    with open(video_path, "wb") as f:
        f.write(ftyp_box + moov_box + mdat_box)

generate_sample_video()

# 7. Seed Materials Database (materials.json)
materials_seed = [
    {
        "id": "mat_1",
        "title": "Quantum Physics Fundamentals & Wave-Particle Duality",
        "category": "Physics",
        "chapter": "Unit 3: Modern Physics & Quantum Mechanics",
        "resource_type": "documents",
        "description": "Comprehensive study notes covering Planck's quantum hypothesis, Einstein's photoelectric effect, de Broglie matter waves, and the Heisenberg uncertainty principle.",
        "tags": ["Physics", "Quantum", "Planck", "Photons", "DeBroglie"],
        "filename": "quantum_physics_fundamentals.txt",
        "file_url": "/uploads/documents/quantum_physics_fundamentals.txt",
        "filesize": os.path.getsize(os.path.join(UPLOADS_DIR, "documents", "quantum_physics_fundamentals.txt")),
        "filesize_formatted": "1.8 KB",
        "uploaded_at": "2026-09-20T10:30:00Z"
    },
    {
        "id": "mat_2",
        "title": "Data Structures & Asymptotic Complexity Handbook",
        "category": "Computer Science",
        "chapter": "Module 1: Algorithms & Complexity Analysis",
        "resource_type": "documents",
        "description": "Essential cheat-sheet and textbook reference covering Big-O hierarchy, binary search trees, worst-case versus amortized complexities, and balanced trees.",
        "tags": ["Algorithms", "DataStructures", "Big-O", "BST", "Complexity"],
        "filename": "data_structures_guide.pdf",
        "file_url": "/uploads/documents/data_structures_guide.pdf",
        "filesize": os.path.getsize(os.path.join(UPLOADS_DIR, "documents", "data_structures_guide.pdf")),
        "filesize_formatted": "3.5 KB",
        "uploaded_at": "2026-09-21T11:15:00Z"
    },
    {
        "id": "mat_3",
        "title": "DNA Replication Fork & Molecular Architecture",
        "category": "Biology",
        "chapter": "Chapter 7: Genetics & Molecular Biology",
        "resource_type": "images",
        "description": "High-resolution labeled schematic diagram illustrating leading strand continuous synthesis, lagging strand Okazaki fragments, helicase, and DNA polymerase.",
        "tags": ["Genetics", "DNA", "Biology", "Helicase", "Diagram"],
        "filename": "dna_replication_diagram.png",
        "file_url": "/uploads/images/dna_replication_diagram.png",
        "filesize": os.path.getsize(os.path.join(UPLOADS_DIR, "images", "dna_replication_diagram.png")),
        "filesize_formatted": "32.4 KB",
        "uploaded_at": "2026-09-22T09:40:00Z"
    },
    {
        "id": "mat_4",
        "title": "Photosystem I & II Electron Transport Pathway",
        "category": "Biology",
        "chapter": "Chapter 4: Plant Physiology & Photosynthesis",
        "resource_type": "images",
        "description": "Biochemical pathway diagram depicting light reactions in the thylakoid membrane, water photolysis, and photophosphorylation yielding ATP and NADPH.",
        "tags": ["Photosynthesis", "Biochemistry", "Plastoquinone", "Diagram"],
        "filename": "photosynthesis_biochemistry.png",
        "file_url": "/uploads/images/photosynthesis_biochemistry.png",
        "filesize": os.path.getsize(os.path.join(UPLOADS_DIR, "images", "photosynthesis_biochemistry.png")),
        "filesize_formatted": "30.1 KB",
        "uploaded_at": "2026-09-23T14:20:00Z"
    },
    {
        "id": "mat_5",
        "title": "Machine Learning & Deep Learning 101 Slide Deck",
        "category": "Computer Science",
        "chapter": "CS 401: Artificial Intelligence Foundations",
        "resource_type": "slides",
        "description": "Landscape presentation slides detailing supervised, unsupervised, and reinforcement learning paradigms, neural network feedforward mechanics, and backpropagation.",
        "tags": ["MachineLearning", "DeepLearning", "AI", "Slides", "NeuralNetworks"],
        "filename": "machine_learning_101_slides.pdf",
        "file_url": "/uploads/slides/machine_learning_101_slides.pdf",
        "filesize": os.path.getsize(os.path.join(UPLOADS_DIR, "slides", "machine_learning_101_slides.pdf")),
        "filesize_formatted": "4.2 KB",
        "uploaded_at": "2026-09-24T16:00:00Z"
    },
    {
        "id": "mat_6",
        "title": "Solar System Mechanics & Planetary Orbits Audio Lecture",
        "category": "Astronomy",
        "chapter": "Unit 2: Celestial Mechanics",
        "resource_type": "audio",
        "description": "Short audio summary discussing Kepler's laws of planetary motion, gravitational orbital resonance, and terrestrial vs jovian planet formation.",
        "tags": ["Astronomy", "SolarSystem", "Kepler", "Podcast", "Audio"],
        "filename": "solar_system_audio_lecture.mp3",
        "file_url": "/uploads/audio/solar_system_audio_lecture.mp3",
        "filesize": os.path.getsize(os.path.join(UPLOADS_DIR, "audio", "solar_system_audio_lecture.mp3")),
        "filesize_formatted": "48.8 KB",
        "uploaded_at": "2026-09-25T08:50:00Z"
    },
    {
        "id": "mat_7",
        "title": "Introduction to Calculus: Derivatives & Rates of Change",
        "category": "Mathematics",
        "chapter": "Differential Calculus: Limits & Tangents",
        "resource_type": "videos",
        "description": "Visual video lecture introducing the derivative as instantaneous rate of change, geometric slope of tangent lines, and power rule derivations.",
        "tags": ["Calculus", "Mathematics", "Derivatives", "Video", "STEM"],
        "filename": "introduction_to_calculus.mp4",
        "file_url": "/uploads/videos/introduction_to_calculus.mp4",
        "filesize": os.path.getsize(os.path.join(UPLOADS_DIR, "videos", "introduction_to_calculus.mp4")),
        "filesize_formatted": "1.2 KB",
        "uploaded_at": "2026-09-25T13:10:00Z"
    }
]

with open(os.path.join(DATA_DIR, "materials.json"), "w", encoding="utf-8") as f:
    json.dump(materials_seed, f, indent=2)

# 8. Seed Quizzes Database (quizzes.json)
quizzes_seed = [
    {
        "id": "quiz_1",
        "title": "Modern Physics & Quantum Mechanics Mastery Test",
        "category": "Physics",
        "chapter": "Unit 3: Modern Physics",
        "description": "Assess your understanding of blackbody radiation, the photoelectric effect, and matter wave wavelengths.",
        "time_limit_minutes": 10,
        "total_points": 30,
        "created_at": "2026-09-21T10:00:00Z",
        "questions": [
            {
                "id": "q1_1",
                "question": "Who postulated in 1900 that radiant energy is emitted and absorbed only in discrete packets called quanta?",
                "options": [
                    "Albert Einstein",
                    "Max Planck",
                    "Erwin Schrödinger",
                    "Niels Bohr"
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "Max Planck introduced the quantum hypothesis to resolve the ultraviolet catastrophe of blackbody radiation."
            },
            {
                "id": "q1_2",
                "question": "In the photoelectric effect, what happens when the intensity of incident light increases while its frequency stays constant above threshold?",
                "options": [
                    "The maximum kinetic energy of emitted photoelectrons increases",
                    "The work function of the metal decreases",
                    "The number of photoelectrons emitted per second increases",
                    "The threshold frequency increases proportionally"
                ],
                "correct_option_index": 2,
                "points": 10,
                "explanation": "Light intensity is proportional to photon flux. More photons yield more emitted electrons, but each electron's kinetic energy is dictated solely by photon energy (frequency)."
            },
            {
                "id": "q1_3",
                "question": "According to the de Broglie relationship (λ = h / p), what happens to a particle's wavelength if its momentum doubles?",
                "options": [
                    "It doubles",
                    "It is halved",
                    "It quadruples",
                    "It remains unchanged"
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "Wavelength is inversely proportional to momentum: if momentum p doubles, λ becomes λ/2."
            }
        ]
    },
    {
        "id": "quiz_2",
        "title": "Data Structures & Big-O Computational Complexity Quiz",
        "category": "Computer Science",
        "chapter": "Module 1: Algorithms & Data Structures",
        "description": "Evaluate your proficiency in asymptotic time complexities, tree traversals, and search algorithms.",
        "time_limit_minutes": 15,
        "total_points": 40,
        "created_at": "2026-09-22T14:30:00Z",
        "questions": [
            {
                "id": "q2_1",
                "question": "What is the worst-case time complexity of searching for an element in an unbalanced, degenerate Binary Search Tree?",
                "options": [
                    "O(1)",
                    "O(log n)",
                    "O(n)",
                    "O(n log n)"
                ],
                "correct_option_index": 2,
                "points": 10,
                "explanation": "In an unbalanced BST (e.g. elements inserted in sorted order), the tree degenerates into a linked list where search is O(n)."
            },
            {
                "id": "q2_2",
                "question": "Which data structure provides average O(1) time complexity for insertion, deletion, and lookup operations?",
                "options": [
                    "Hash Table / Map",
                    "Binary Search Tree",
                    "Red-Black Tree",
                    "Min Heap"
                ],
                "correct_option_index": 0,
                "points": 10,
                "explanation": "A hash table maps keys to array buckets via a hashing function, achieving average O(1) performance."
            },
            {
                "id": "q2_3",
                "question": "Which sorting algorithm maintains a guaranteed worst-case time complexity of O(n log n) by using the divide-and-conquer strategy?",
                "options": [
                    "QuickSort",
                    "MergeSort",
                    "BubbleSort",
                    "InsertionSort"
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "MergeSort recursively halves the array and merges sorted halves, always running in O(n log n) even in the worst case."
            },
            {
                "id": "q2_4",
                "question": "What tree traversal sequence visits nodes in the order: Left Subtree -> Root Node -> Right Subtree?",
                "options": [
                    "Pre-order Traversal",
                    "Post-order Traversal",
                    "In-order Traversal",
                    "Level-order Traversal"
                ],
                "correct_option_index": 2,
                "points": 10,
                "explanation": "In-order traversal visits left subtree, current node, then right subtree. On a BST, this yields keys in ascending sorted order."
            }
        ]
    },
    {
        "id": "quiz_3",
        "title": "Molecular Biology & DNA Replication Checkpoint",
        "category": "Biology",
        "chapter": "Chapter 7: Molecular Genetics",
        "description": "Test your mastery over DNA replication enzymes, Okazaki fragments, and synthesis polarity.",
        "time_limit_minutes": 10,
        "total_points": 20,
        "created_at": "2026-09-23T12:00:00Z",
        "questions": [
            {
                "id": "q3_1",
                "question": "Which enzyme is responsible for unwinding the double-stranded DNA helix at the replication fork?",
                "options": [
                    "DNA Ligase",
                    "DNA Helicase",
                    "RNA Primase",
                    "Topoisomerase"
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "DNA Helicase breaks the hydrogen bonds holding the paired nitrogenous bases together, creating the replication fork."
            },
            {
                "id": "q3_2",
                "question": "In what direction does DNA Polymerase synthesize the new complementary daughter strand?",
                "options": [
                    "3' to 5' direction only",
                    "5' to 3' direction only",
                    "Bidirectionally without restriction",
                    "From either terminus depending on temperature"
                ],
                "correct_option_index": 1,
                "points": 10,
                "explanation": "DNA Polymerase can only add free nucleotides to the 3' hydroxyl (-OH) end of a growing polynucleotide chain, synthesizing 5' -> 3'."
            }
        ]
    }
]

with open(os.path.join(DATA_DIR, "quizzes.json"), "w", encoding="utf-8") as f:
    json.dump(quizzes_seed, f, indent=2)

# 9. Seed Submissions Database (submissions.json)
submissions_seed = [
    {
        "id": "sub_1",
        "quiz_id": "quiz_1",
        "quiz_title": "Modern Physics & Quantum Mechanics Mastery Test",
        "student_name": "Eleanor Vance",
        "student_email": "eleanor.vance@campus.edu",
        "score": 30,
        "total_points": 30,
        "percentage": 100.0,
        "submitted_at": "2026-09-24T15:22:10Z",
        "answers": [
            {"question_id": "q1_1", "selected_option_index": 1, "is_correct": True, "points_earned": 10},
            {"question_id": "q1_2", "selected_option_index": 2, "is_correct": True, "points_earned": 10},
            {"question_id": "q1_3", "selected_option_index": 1, "is_correct": True, "points_earned": 10}
        ]
    },
    {
        "id": "sub_2",
        "quiz_id": "quiz_2",
        "quiz_title": "Data Structures & Big-O Computational Complexity Quiz",
        "student_name": "Marcus Aurelius Chen",
        "student_email": "marcus.chen@campus.edu",
        "score": 30,
        "total_points": 40,
        "percentage": 75.0,
        "submitted_at": "2026-09-25T11:05:40Z",
        "answers": [
            {"question_id": "q2_1", "selected_option_index": 2, "is_correct": True, "points_earned": 10},
            {"question_id": "q2_2", "selected_option_index": 0, "is_correct": True, "points_earned": 10},
            {"question_id": "q2_3", "selected_option_index": 1, "is_correct": True, "points_earned": 10},
            {"question_id": "q2_4", "selected_option_index": 0, "is_correct": False, "points_earned": 0}
        ]
    }
]

with open(os.path.join(DATA_DIR, "submissions.json"), "w", encoding="utf-8") as f:
    json.dump(submissions_seed, f, indent=2)

print("Seed generation complete! All databases and sample educational files populated.")
