/**
 * EduSphere Learning Platform - Student Hub Application Logic
 */

let state = {
  materials: [],
  quizzes: [],
  categories: [],
  currentTab: 'materials',
  activeTypeFilter: 'all',
  activeCategoryFilter: 'all',
  searchQuery: '',
  
  // Media Viewer states
  txtFontSize: 15,
  imageZoomLevel: 1.0,
  
  // Quiz taking state
  activeQuiz: null,
  activeQuestionIndex: 0,
  studentAnswers: {}, // { question_id: selected_index }
  studentName: '',
  studentEmail: ''
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  fetchPlatformStats();
  fetchCategories();
  loadMaterials();
  loadQuizzes();
  setupAudioListeners();
});

// ==========================================
// TABS & NAVIGATION
// ==========================================

function switchMainTab(tab) {
  state.currentTab = tab;
  const materialsTabBtn = document.getElementById('navTabMaterials');
  const quizzesTabBtn = document.getElementById('navTabQuizzes');
  const materialsSection = document.getElementById('materialsSection');
  const quizzesSection = document.getElementById('quizzesSection');

  if (tab === 'materials') {
    materialsTabBtn.className = "px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center space-x-2 bg-indigo-600 text-white shadow-sm shadow-indigo-200";
    quizzesTabBtn.className = "px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center space-x-2 text-slate-600 hover:text-indigo-600 hover:bg-slate-100";
    materialsSection.classList.remove('hidden');
    quizzesSection.classList.add('hidden');
  } else {
    quizzesTabBtn.className = "px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center space-x-2 bg-indigo-600 text-white shadow-sm shadow-indigo-200";
    materialsTabBtn.className = "px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center space-x-2 text-slate-600 hover:text-indigo-600 hover:bg-slate-100";
    quizzesSection.classList.remove('hidden');
    materialsSection.classList.add('hidden');
  }
}

// ==========================================
// DATA FETCHING & STATS
// ==========================================

async function fetchPlatformStats() {
  try {
    const res = await fetch('/api/stats');
    const json = await res.json();
    if (json.status === 'success') {
      const data = json.data;
      document.getElementById('statTotalMaterials').textContent = data.total_materials;
      document.getElementById('statTotalQuizzes').textContent = data.total_quizzes;
      document.getElementById('statTotalSubmissions').textContent = data.total_submissions;
      document.getElementById('statAverageScore').textContent = `${data.average_score}%`;
    }
  } catch (err) {
    console.error('Failed to fetch platform stats:', err);
  }
}

async function fetchCategories() {
  try {
    const res = await fetch('/api/categories');
    const json = await res.json();
    if (json.status === 'success') {
      state.categories = json.data;
      
      const catSelect = document.getElementById('categorySelect');
      const quizCatSelect = document.getElementById('quizCategorySelect');
      
      let optionsHtml = '<option value="all">All Subjects</option>';
      json.data.forEach(c => {
        optionsHtml += `<option value="${escapeHtml(c.name)}">${escapeHtml(c.name)} (${c.count})</option>`;
      });
      
      catSelect.innerHTML = optionsHtml;
      quizCatSelect.innerHTML = '<option value="all">All Subjects</option>' + json.data.map(c => `<option value="${escapeHtml(c.name)}">${escapeHtml(c.name)}</option>`).join('');
    }
  } catch (err) {
    console.error('Failed to load categories:', err);
  }
}

// ==========================================
// MATERIALS BROWSING & FILTERS
// ==========================================

async function loadMaterials() {
  const grid = document.getElementById('materialsGrid');
  const emptyState = document.getElementById('noMaterialsState');
  
  let url = `/api/materials?`;
  if (state.activeTypeFilter !== 'all') {
    url += `resource_type=${encodeURIComponent(state.activeTypeFilter)}&`;
  }
  if (state.activeCategoryFilter !== 'all') {
    url += `category=${encodeURIComponent(state.activeCategoryFilter)}&`;
  }
  if (state.searchQuery.trim()) {
    url += `search=${encodeURIComponent(state.searchQuery.trim())}&`;
  }

  try {
    const res = await fetch(url);
    const json = await res.json();
    state.materials = json.data || [];
    renderMaterialsGrid(state.materials);
  } catch (err) {
    console.error('Error fetching materials:', err);
    grid.innerHTML = `<div class="col-span-full py-10 text-center text-rose-500 font-semibold">Failed to load materials. Please check server.</div>`;
  }
}

function renderMaterialsGrid(materials) {
  const grid = document.getElementById('materialsGrid');
  const emptyState = document.getElementById('noMaterialsState');

  if (!materials || materials.length === 0) {
    grid.innerHTML = '';
    emptyState.classList.remove('hidden');
    return;
  }

  emptyState.classList.add('hidden');
  grid.innerHTML = materials.map(mat => createMaterialCardHtml(mat)).join('');
}

function getResourceMeta(type) {
  switch (type) {
    case 'documents':
      return { icon: 'fa-file-lines', label: 'Document / Note', color: 'badge-doc', text: 'text-blue-600', bg: 'bg-blue-50' };
    case 'videos':
      return { icon: 'fa-video', label: 'Video Lecture', color: 'badge-video', text: 'text-rose-600', bg: 'bg-rose-50' };
    case 'audio':
      return { icon: 'fa-headphones', label: 'Audio Podcast', color: 'badge-audio', text: 'text-purple-600', bg: 'bg-purple-50' };
    case 'images':
      return { icon: 'fa-image', label: 'Diagram / Infographic', color: 'badge-image', text: 'text-emerald-600', bg: 'bg-emerald-50' };
    case 'slides':
      return { icon: 'fa-file-powerpoint', label: 'Slide Deck', color: 'badge-slides', text: 'text-amber-600', bg: 'bg-amber-50' };
    default:
      return { icon: 'fa-file', label: 'Resource', color: 'badge-doc', text: 'text-indigo-600', bg: 'bg-indigo-50' };
  }
}

function createMaterialCardHtml(mat) {
  const meta = getResourceMeta(mat.resource_type);
  const tagsHtml = (mat.tags || []).slice(0, 3).map(tag => 
    `<span class="px-2 py-0.5 bg-slate-100 text-slate-600 text-[10px] font-medium rounded-md">#${escapeHtml(tag)}</span>`
  ).join('');

  return `
    <div class="bg-white rounded-2xl border border-slate-200/90 p-5 flex flex-col justify-between transition-card shadow-sm hover:border-indigo-200">
      <div>
        <!-- Top Badges -->
        <div class="flex items-center justify-between gap-2 mb-3">
          <span class="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold ${meta.color}">
            <i class="fa-solid ${meta.icon}"></i>
            <span>${meta.label}</span>
          </span>
          <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
            ${escapeHtml(mat.category || 'General')}
          </span>
        </div>

        <!-- Title -->
        <h3 class="text-base font-bold text-slate-900 leading-snug line-clamp-2 hover:text-indigo-600 transition-colors">
          ${escapeHtml(mat.title)}
        </h3>

        <!-- Chapter -->
        <p class="text-xs font-medium text-indigo-600 mt-1 flex items-center space-x-1">
          <i class="fa-solid fa-bookmark text-[10px]"></i>
          <span>${escapeHtml(mat.chapter || 'Curriculum Resource')}</span>
        </p>

        <!-- Description -->
        <p class="text-xs text-slate-500 mt-2 line-clamp-3 leading-relaxed">
          ${escapeHtml(mat.description || 'No detailed description available for this resource.')}
        </p>

        <!-- Tags -->
        <div class="flex flex-wrap gap-1.5 mt-3">
          ${tagsHtml}
        </div>
      </div>

      <!-- Card Footer -->
      <div class="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
        <div class="text-[11px] text-slate-400">
          <i class="fa-solid fa-hard-drive mr-1"></i>${escapeHtml(mat.filesize_formatted || 'File')}
        </div>

        <div class="flex items-center space-x-2">
          <!-- Download Button -->
          <a href="/api/materials/${mat.id}/download" title="Download Material" class="w-8 h-8 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition-colors">
            <i class="fa-solid fa-download text-xs"></i>
          </a>

          <!-- View In Modal Button -->
          <button onclick="openResourceViewer('${mat.id}')" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-sm shadow-indigo-200 flex items-center space-x-1.5 transition-all">
            <i class="fa-solid fa-eye text-[11px]"></i>
            <span>Open Viewer</span>
          </button>
        </div>
      </div>
    </div>
  `;
}

function setResourceTypeFilter(type) {
  state.activeTypeFilter = type;
  document.querySelectorAll('.type-pill').forEach(btn => {
    if (btn.getAttribute('data-type') === type) {
      btn.className = "type-pill px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all bg-indigo-600 text-white shadow-sm";
    } else {
      btn.className = "type-pill px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all text-slate-600 hover:bg-slate-100";
    }
  });
  loadMaterials();
}

function handleCategoryChange(e) {
  state.activeCategoryFilter = e.target.value;
  loadMaterials();
}

let searchDebounceTimeout = null;
function handleSearchInput(e) {
  state.searchQuery = e.target.value;
  clearTimeout(searchDebounceTimeout);
  searchDebounceTimeout = setTimeout(() => {
    loadMaterials();
  }, 300);
}

function applyFilters() {
  const input = document.getElementById('globalSearchInput');
  state.searchQuery = input.value;
  loadMaterials();
}

function resetFilters() {
  state.activeTypeFilter = 'all';
  state.activeCategoryFilter = 'all';
  state.searchQuery = '';
  document.getElementById('globalSearchInput').value = '';
  document.getElementById('categorySelect').value = 'all';
  setResourceTypeFilter('all');
}

// ==========================================
// MODAL RESOURCE VIEWERS
// ==========================================

function openResourceViewer(materialId) {
  const mat = state.materials.find(m => m.id === materialId);
  if (!mat) return;

  const type = mat.resource_type;
  const fileUrl = mat.file_url;
  const ext = fileUrl.split('.').pop().toLowerCase();

  if (type === 'documents') {
    openDocumentViewer(mat, ext);
  } else if (type === 'videos') {
    openVideoViewer(mat);
  } else if (type === 'audio') {
    openAudioPlayer(mat);
  } else if (type === 'images') {
    openImageViewer(mat);
  } else if (type === 'slides') {
    openSlidesViewer(mat);
  } else {
    // Default fallback to direct file
    window.open(fileUrl, '_blank');
  }
}

// 1. Document Viewer
async function openDocumentViewer(mat, ext) {
  document.getElementById('docViewerTitle').textContent = mat.title;
  document.getElementById('docViewerSubtitle').textContent = `${mat.category} • ${mat.chapter}`;
  document.getElementById('docViewerDownloadBtn').href = `/api/materials/${mat.id}/download`;

  const txtPre = document.getElementById('txtContentPre');
  const pdfFrame = document.getElementById('pdfFrame');
  const txtControls = document.getElementById('txtZoomControls');

  if (ext === 'txt') {
    pdfFrame.classList.add('hidden');
    txtPre.classList.remove('hidden');
    txtControls.classList.remove('hidden');
    txtPre.textContent = "Loading document contents...";
    try {
      const res = await fetch(mat.file_url);
      const text = await res.text();
      txtPre.textContent = text;
    } catch (err) {
      txtPre.textContent = "Failed to load document text.";
    }
  } else {
    // PDF or other documents
    txtPre.classList.add('hidden');
    txtControls.classList.add('hidden');
    pdfFrame.classList.remove('hidden');
    pdfFrame.src = mat.file_url;
  }

  openModal('docViewerModal');
}

function adjustTxtFontSize(delta) {
  state.txtFontSize = Math.max(11, Math.min(26, state.txtFontSize + delta));
  document.getElementById('txtContentPre').style.fontSize = `${state.txtFontSize}px`;
}

// 2. Video Viewer
function openVideoViewer(mat) {
  document.getElementById('videoModalTitle').textContent = mat.title;
  document.getElementById('videoModalSubtitle').textContent = `${mat.category} • ${mat.chapter}`;
  document.getElementById('videoDownloadBtn').href = `/api/materials/${mat.id}/download`;

  const player = document.getElementById('html5VideoPlayer');
  player.src = mat.file_url;
  player.load();
  setVideoSpeed(1.0);
  document.getElementById('videoSpeedSelect').value = "1.0";

  openModal('videoModal');
}

function closeVideoModal() {
  const player = document.getElementById('html5VideoPlayer');
  player.pause();
  player.src = "";
  closeModal('videoModal');
}

function setVideoSpeed(speed) {
  const player = document.getElementById('html5VideoPlayer');
  player.playbackRate = parseFloat(speed);
}

// 3. Audio Player (Sticky Bar)
function openAudioPlayer(mat) {
  const bar = document.getElementById('audioBarPlayer');
  const audio = document.getElementById('globalAudioElement');
  
  document.getElementById('audioBarTitle').textContent = mat.title;
  document.getElementById('audioBarCategory').textContent = `${mat.category} • ${mat.chapter}`;

  audio.src = mat.file_url;
  audio.load();
  audio.play().then(() => {
    updateAudioPlayButton(true);
  }).catch(err => {
    console.warn("Autoplay prevented:", err);
    updateAudioPlayButton(false);
  });

  bar.classList.remove('hidden');
}

function setupAudioListeners() {
  const audio = document.getElementById('globalAudioElement');
  const scrubber = document.getElementById('audioScrubber');
  const curTime = document.getElementById('audioCurrentTime');
  const totDuration = document.getElementById('audioTotalDuration');

  audio.addEventListener('timeupdate', () => {
    if (audio.duration) {
      const pct = (audio.currentTime / audio.duration) * 100;
      scrubber.value = pct;
      curTime.textContent = formatAudioTime(audio.currentTime);
      totDuration.textContent = formatAudioTime(audio.duration);
    }
  });

  audio.addEventListener('loadedmetadata', () => {
    totDuration.textContent = formatAudioTime(audio.duration);
  });

  audio.addEventListener('ended', () => {
    updateAudioPlayButton(false);
  });
}

function formatAudioTime(seconds) {
  if (isNaN(seconds)) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function toggleAudioPlay() {
  const audio = document.getElementById('globalAudioElement');
  if (audio.paused) {
    audio.play();
    updateAudioPlayButton(true);
  } else {
    audio.pause();
    updateAudioPlayButton(false);
  }
}

function updateAudioPlayButton(isPlaying) {
  const btn = document.getElementById('audioPlayPauseBtn');
  btn.innerHTML = isPlaying ? '<i class="fa-solid fa-pause"></i>' : '<i class="fa-solid fa-play"></i>';
}

function skipAudio(seconds) {
  const audio = document.getElementById('globalAudioElement');
  audio.currentTime = Math.max(0, Math.min(audio.duration || 0, audio.currentTime + seconds));
}

function seekAudio(percent) {
  const audio = document.getElementById('globalAudioElement');
  if (audio.duration) {
    audio.currentTime = (percent / 100) * audio.duration;
  }
}

function setAudioVolume(vol) {
  const audio = document.getElementById('globalAudioElement');
  audio.volume = parseFloat(vol);
}

function closeAudioPlayer() {
  const audio = document.getElementById('globalAudioElement');
  audio.pause();
  audio.src = "";
  document.getElementById('audioBarPlayer').classList.add('hidden');
}

// 4. Image Viewer
function openImageViewer(mat) {
  document.getElementById('imageModalTitle').textContent = mat.title;
  document.getElementById('imageModalSubtitle').textContent = `${mat.category} • ${mat.chapter}`;
  document.getElementById('imageDownloadBtn').href = `/api/materials/${mat.id}/download`;

  const img = document.getElementById('imageViewerImg');
  img.src = mat.file_url;
  resetImageZoom();

  openModal('imageModal');
}

function zoomImage(delta) {
  state.imageZoomLevel = Math.max(0.5, Math.min(3.0, state.imageZoomLevel + delta));
  const img = document.getElementById('imageViewerImg');
  img.style.transform = `scale(${state.imageZoomLevel})`;
}

function resetImageZoom() {
  state.imageZoomLevel = 1.0;
  const img = document.getElementById('imageViewerImg');
  img.style.transform = `scale(1.0)`;
}

// 5. Slides Viewer
function openSlidesViewer(mat) {
  document.getElementById('slidesModalTitle').textContent = mat.title;
  document.getElementById('slidesModalSubtitle').textContent = `${mat.category} • ${mat.chapter}`;
  document.getElementById('slidesDownloadBtn').href = `/api/materials/${mat.id}/download`;

  const frame = document.getElementById('slidesFrame');
  frame.src = mat.file_url;

  openModal('slidesModal');
}

// Helper Modal Display
function openModal(modalId) {
  document.getElementById(modalId).classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
  document.body.style.overflow = '';
}

// ==========================================
// QUIZZES BROWSING & TAKING
// ==========================================

async function loadQuizzes() {
  const grid = document.getElementById('quizzesGrid');
  const catSelect = document.getElementById('quizCategorySelect');
  const chosenCat = catSelect ? catSelect.value : 'all';

  let url = '/api/quizzes';
  if (chosenCat && chosenCat !== 'all') {
    url += `?category=${encodeURIComponent(chosenCat)}`;
  }

  try {
    const res = await fetch(url);
    const json = await res.json();
    state.quizzes = json.data || [];
    renderQuizzesGrid(state.quizzes);
  } catch (err) {
    console.error('Error fetching quizzes:', err);
    grid.innerHTML = `<div class="col-span-full py-10 text-center text-rose-500 font-semibold">Failed to load quizzes.</div>`;
  }
}

function renderQuizzesGrid(quizzes) {
  const grid = document.getElementById('quizzesGrid');
  if (!quizzes || quizzes.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full py-16 text-center">
        <div class="w-14 h-14 mx-auto mb-3 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
          <i class="fa-solid fa-circle-question text-xl"></i>
        </div>
        <h4 class="text-sm font-bold text-slate-700">No quizzes available for this filter</h4>
        <p class="text-xs text-slate-400 mt-1">Select 'All Subjects' to see all available tests.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = quizzes.map(q => `
    <div class="bg-white rounded-2xl border border-slate-200/90 p-5 flex flex-col justify-between transition-card shadow-sm hover:border-indigo-300">
      <div>
        <div class="flex items-center justify-between gap-2 mb-3">
          <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
            ${escapeHtml(q.category)}
          </span>
          <span class="text-xs font-semibold text-slate-500 flex items-center space-x-1">
            <i class="fa-regular fa-clock"></i>
            <span>${q.time_limit_minutes} Mins</span>
          </span>
        </div>

        <h3 class="text-base font-bold text-slate-900 leading-snug line-clamp-2">${escapeHtml(q.title)}</h3>
        <p class="text-xs font-medium text-slate-600 mt-1 flex items-center space-x-1">
          <i class="fa-solid fa-layer-group text-indigo-500 text-[10px]"></i>
          <span>${escapeHtml(q.chapter || 'Curriculum Check')}</span>
        </p>
        <p class="text-xs text-slate-500 mt-2 line-clamp-2 leading-relaxed">
          ${escapeHtml(q.description || 'Test your knowledge on this unit.')}
        </p>
      </div>

      <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
        <div class="flex items-center space-x-3 text-xs text-slate-500 font-semibold">
          <span><i class="fa-solid fa-list-check mr-1 text-slate-400"></i>${q.question_count} Qs</span>
          <span><i class="fa-solid fa-award mr-1 text-amber-500"></i>${q.total_points} Pts</span>
        </div>
        <button onclick="initiateQuizTaking('${q.id}')" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-100 flex items-center space-x-1.5 transition-all">
          <i class="fa-solid fa-play text-[10px]"></i>
          <span>Take Quiz</span>
        </button>
      </div>
    </div>
  `).join('');
}

// ------------------------------------------
// QUIZ TAKING INTERFACE
// ------------------------------------------

async function initiateQuizTaking(quizId) {
  try {
    const res = await fetch(`/api/quizzes/${quizId}`);
    const json = await res.json();
    if (json.status !== 'success') {
      alert("Failed to load quiz details.");
      return;
    }

    state.activeQuiz = json.data;
    state.activeQuestionIndex = 0;
    state.studentAnswers = {};

    // Header info
    document.getElementById('quizBadgeCategory').textContent = state.activeQuiz.category;
    document.getElementById('quizTakingTitle').textContent = state.activeQuiz.title;
    document.getElementById('quizIntroDescription').textContent = `${state.activeQuiz.description} (${state.activeQuiz.questions.length} questions • ${state.activeQuiz.total_points} total points)`;

    // Show Intro Step
    document.getElementById('quizIntroStep').classList.remove('hidden');
    document.getElementById('quizQuestionsStep').classList.add('hidden');
    document.getElementById('quizResultsStep').classList.add('hidden');

    openModal('quizTakerModal');
  } catch (err) {
    console.error('Error initiating quiz:', err);
    alert('Could not start quiz. Please try again.');
  }
}

function startQuizQuestions() {
  const nameInput = document.getElementById('takerStudentName');
  const emailInput = document.getElementById('takerStudentEmail');

  const nameVal = nameInput.value.trim();
  if (!nameVal) {
    alert("Please enter your name to proceed.");
    nameInput.focus();
    return;
  }

  state.studentName = nameVal;
  state.studentEmail = emailInput.value.trim();

  document.getElementById('quizIntroStep').classList.add('hidden');
  document.getElementById('quizQuestionsStep').classList.remove('hidden');

  renderCurrentQuestion();
}

function renderCurrentQuestion() {
  const quiz = state.activeQuiz;
  const qIndex = state.activeQuestionIndex;
  const question = quiz.questions[qIndex];
  const total = quiz.questions.length;

  // Counter & Progress
  document.getElementById('questionCounterText').textContent = `Question ${qIndex + 1} of ${total}`;
  document.getElementById('questionPointsBadge').textContent = `${question.points} Points`;
  const pct = Math.round(((qIndex + 1) / total) * 100);
  document.getElementById('quizProgressBar').style.width = `${pct}%`;

  // Prompt
  document.getElementById('activeQuestionPrompt').textContent = question.question;

  // Options
  const container = document.getElementById('activeOptionsContainer');
  const selectedIdx = state.studentAnswers[question.id];

  container.innerHTML = question.options.map((opt, optIdx) => `
    <div onclick="selectQuizOption('${question.id}', ${optIdx})" class="flex items-center p-3.5 rounded-2xl border-2 cursor-pointer transition-all ${selectedIdx === optIdx ? 'border-indigo-600 bg-indigo-50/60 shadow-sm' : 'border-slate-200 bg-white hover:border-slate-300'}">
      <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center mr-3 shrink-0 ${selectedIdx === optIdx ? 'border-indigo-600 bg-indigo-600' : 'border-slate-300 bg-white'}">
        ${selectedIdx === optIdx ? '<div class="w-2 h-2 rounded-full bg-white"></div>' : ''}
      </div>
      <span class="text-sm font-semibold text-slate-800">${escapeHtml(opt)}</span>
    </div>
  `).join('');

  // Navigation Buttons
  const prevBtn = document.getElementById('quizPrevBtn');
  const nextBtn = document.getElementById('quizNextBtn');
  const submitBtn = document.getElementById('quizSubmitBtn');

  prevBtn.disabled = (qIndex === 0);

  if (qIndex === total - 1) {
    nextBtn.classList.add('hidden');
    submitBtn.classList.remove('hidden');
  } else {
    nextBtn.classList.remove('hidden');
    submitBtn.classList.add('hidden');
  }
}

function selectQuizOption(questionId, optIndex) {
  state.studentAnswers[questionId] = optIndex;
  renderCurrentQuestion();
}

function navigateQuizQuestion(delta) {
  const total = state.activeQuiz.questions.length;
  const newIndex = state.activeQuestionIndex + delta;
  if (newIndex >= 0 && newIndex < total) {
    state.activeQuestionIndex = newIndex;
    renderCurrentQuestion();
  }
}

async function submitActiveQuiz() {
  const quiz = state.activeQuiz;
  
  // Prepare payload
  const answersList = quiz.questions.map(q => ({
    question_id: q.id,
    selected_option_index: state.studentAnswers[q.id] !== undefined ? state.studentAnswers[q.id] : -1
  }));

  const payload = {
    student_name: state.studentName,
    student_email: state.studentEmail,
    answers: answersList
  };

  try {
    const res = await fetch(`/api/quizzes/${quiz.id}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    if (result.status === 'success') {
      displayQuizResults(result);
      fetchPlatformStats(); // refresh platform score averages
    } else {
      alert("Submission error: " + (result.detail || "Unknown error"));
    }
  } catch (err) {
    console.error('Quiz submit failed:', err);
    alert('Failed to submit quiz. Please check network connection.');
  }
}

function displayQuizResults(result) {
  document.getElementById('quizQuestionsStep').classList.add('hidden');
  document.getElementById('quizResultsStep').classList.remove('hidden');

  // Score Badge styling based on percentage
  const badge = document.getElementById('resultScoreBadge');
  const pct = result.percentage;
  badge.textContent = `${pct}%`;

  if (pct >= 80) {
    badge.className = "inline-flex items-center justify-center w-24 h-24 rounded-full bg-emerald-50 text-emerald-600 border-4 border-emerald-500 text-2xl font-black mb-3";
    document.getElementById('resultTitleText').textContent = "Excellent Mastery!";
  } else if (pct >= 50) {
    badge.className = "inline-flex items-center justify-center w-24 h-24 rounded-full bg-amber-50 text-amber-600 border-4 border-amber-500 text-2xl font-black mb-3";
    document.getElementById('resultTitleText').textContent = "Good Effort - Keep Practicing!";
  } else {
    badge.className = "inline-flex items-center justify-center w-24 h-24 rounded-full bg-rose-50 text-rose-600 border-4 border-rose-500 text-2xl font-black mb-3";
    document.getElementById('resultTitleText').textContent = "Needs More Revision";
  }

  document.getElementById('resultSummaryText').textContent = 
    `Hi ${escapeHtml(result.student_name)}, you scored ${result.score} / ${result.total_points} points on '${escapeHtml(result.quiz_title)}'.`;

  // Render question-by-question breakdown
  const listContainer = document.getElementById('resultsDetailedList');
  listContainer.innerHTML = result.breakdown.map((item, idx) => {
    const isCorrect = item.is_correct;
    return `
      <div class="p-4 rounded-2xl border ${isCorrect ? 'border-emerald-200 bg-emerald-50/30' : 'border-rose-200 bg-rose-50/30'}">
        <div class="flex items-start justify-between gap-3 mb-2">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${isCorrect ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white'}">
              ${idx + 1}
            </span>
            <h5 class="text-sm font-bold text-slate-800">${escapeHtml(item.question)}</h5>
          </div>
          <span class="text-xs font-bold ${isCorrect ? 'text-emerald-700 bg-emerald-100' : 'text-rose-700 bg-rose-100'} px-2 py-0.5 rounded-md shrink-0">
            ${isCorrect ? `+${item.points_earned} Pts` : `0 / ${item.points_total} Pts`}
          </span>
        </div>

        <div class="space-y-1.5 mt-3 ml-8 text-xs">
          ${item.options.map((opt, optIdx) => {
            const isStudentPick = (item.selected_option_index === optIdx);
            const isCorrectOption = (item.correct_option_index === optIdx);
            
            let optClass = "text-slate-600 bg-white border border-slate-200";
            let optIcon = "";

            if (isCorrectOption) {
              optClass = "text-emerald-800 bg-emerald-100 border border-emerald-300 font-bold";
              optIcon = '<i class="fa-solid fa-check text-emerald-600 mr-1.5"></i>';
            } else if (isStudentPick && !isCorrect) {
              optClass = "text-rose-800 bg-rose-100 border border-rose-300 line-through font-semibold";
              optIcon = '<i class="fa-solid fa-xmark text-rose-600 mr-1.5"></i>';
            }

            return `
              <div class="p-2 rounded-xl flex items-center ${optClass}">
                ${optIcon}
                <span>${escapeHtml(opt)}</span>
                ${isStudentPick ? '<span class="ml-auto text-[10px] uppercase font-bold text-slate-500">(Your Choice)</span>' : ''}
              </div>
            `;
          }).join('')}
        </div>

        ${item.explanation ? `
          <div class="mt-3 ml-8 p-3 rounded-xl bg-indigo-50 border border-indigo-200 text-xs text-indigo-900 leading-relaxed">
            <span class="font-bold flex items-center space-x-1 text-indigo-700 mb-0.5">
              <i class="fa-solid fa-lightbulb"></i>
              <span>Teacher Explanation:</span>
            </span>
            ${escapeHtml(item.explanation)}
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
}

function retakeCurrentQuiz() {
  state.activeQuestionIndex = 0;
  state.studentAnswers = {};
  document.getElementById('quizResultsStep').classList.add('hidden');
  document.getElementById('quizQuestionsStep').classList.remove('hidden');
  renderCurrentQuestion();
}

function closeQuizModal() {
  closeModal('quizTakerModal');
}

// Utility: HTML escape
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
