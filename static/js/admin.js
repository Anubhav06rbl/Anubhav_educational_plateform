/**
 * EduSphere Learning Platform - Teacher & Admin Portal Logic
 */

let adminState = {
  currentTab: 'upload',
  materials: [],
  quizzes: [],
  submissions: [],
  selectedFile: null,
  builderQuestions: [] // Array of question objects being created
};

document.addEventListener('DOMContentLoaded', () => {
  fetchAdminStats();
  setupDropZone();
  loadAdminMaterials();
  loadAdminQuizzes();
  loadAdminSubmissions();

  // Initialize Quiz Builder with 1 starter question
  addQuestionCard();
});

// ==========================================
// TABS SWITCHER
// ==========================================

function switchAdminTab(tab) {
  adminState.currentTab = tab;
  const sections = {
    upload: document.getElementById('adminSectionUpload'),
    materials: document.getElementById('adminSectionMaterials'),
    quizBuilder: document.getElementById('adminSectionQuizBuilder'),
    submissions: document.getElementById('adminSectionSubmissions')
  };

  const buttons = {
    upload: document.getElementById('adminTabUpload'),
    materials: document.getElementById('adminTabMaterials'),
    quizBuilder: document.getElementById('adminTabQuizBuilder'),
    submissions: document.getElementById('adminTabSubmissions')
  };

  Object.keys(sections).forEach(key => {
    if (key === tab) {
      sections[key].classList.remove('hidden');
      if (buttons[key]) {
        buttons[key].className = "px-3.5 py-2 rounded-xl text-xs font-bold transition-all bg-indigo-600 text-white shadow-sm";
      }
    } else {
      sections[key].classList.add('hidden');
      if (buttons[key]) {
        buttons[key].className = "px-3.5 py-2 rounded-xl text-xs font-bold transition-all text-slate-600 hover:text-indigo-600 hover:bg-slate-100";
      }
    }
  });

  // Refresh data if switching to specific tabs
  if (tab === 'materials') loadAdminMaterials();
  if (tab === 'submissions') loadAdminSubmissions();
  if (tab === 'quizBuilder') loadAdminQuizzes();
}

// ==========================================
// STATS
// ==========================================

async function fetchAdminStats() {
  try {
    const res = await fetch('/api/stats');
    const json = await res.json();
    if (json.status === 'success') {
      const data = json.data;
      document.getElementById('adminStatMaterials').textContent = data.total_materials;
      document.getElementById('adminStatQuizzes').textContent = data.total_quizzes;
      document.getElementById('adminStatSubmissions').textContent = data.total_submissions;
      document.getElementById('adminStatAvgScore').textContent = `${data.average_score}%`;
    }
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

// ==========================================
// RESOURCE UPLOAD & DROPZONE
// ==========================================

function setupDropZone() {
  const dropZone = document.getElementById('dropZoneContainer');
  const fileInput = document.getElementById('fileInput');

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('border-indigo-600', 'bg-indigo-50/50');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('border-indigo-600', 'bg-indigo-50/50');
    }, false);
  });

  dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;
      processSelectedFile(files[0]);
    }
  }, false);
}

function handleFileSelection(e) {
  if (e.target.files && e.target.files[0]) {
    processSelectedFile(e.target.files[0]);
  }
}

function processSelectedFile(file) {
  adminState.selectedFile = file;
  document.getElementById('dropZoneEmpty').classList.add('hidden');
  document.getElementById('dropZoneSelected').classList.remove('hidden');

  document.getElementById('selectedFileName').textContent = file.name;
  document.getElementById('selectedFileSize').textContent = formatBytes(file.size);

  // Set appropriate icon
  const icon = document.getElementById('selectedFileIcon');
  const ext = file.name.split('.').pop().toLowerCase();

  if (['mp4', 'webm', 'mov'].includes(ext)) {
    icon.className = "fa-solid fa-video";
  } else if (['mp3', 'wav', 'aac'].includes(ext)) {
    icon.className = "fa-solid fa-headphones";
  } else if (['png', 'jpg', 'jpeg', 'svg'].includes(ext)) {
    icon.className = "fa-solid fa-image";
  } else if (['pdf'].includes(ext)) {
    icon.className = "fa-solid fa-file-pdf";
  } else {
    icon.className = "fa-solid fa-file-lines";
  }

  // Pre-fill Title with sanitized file name if title input is empty
  const titleInput = document.getElementById('uploadTitle');
  if (!titleInput.value.trim()) {
    const rawName = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
    const cleanTitle = rawName.replace(/[-_]+/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    titleInput.value = cleanTitle;
  }
}

function clearSelectedFile(e) {
  e.stopPropagation();
  adminState.selectedFile = null;
  document.getElementById('fileInput').value = "";
  document.getElementById('dropZoneEmpty').classList.remove('hidden');
  document.getElementById('dropZoneSelected').classList.add('hidden');
}

async function handleMaterialUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('fileInput');
  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please select a file to upload.");
    return;
  }

  const submitBtn = document.getElementById('uploadSubmitBtn');
  const feedback = document.getElementById('uploadFeedbackMessage');
  
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Uploading...';
  feedback.classList.add('hidden');

  const formData = new FormData(document.getElementById('uploadMaterialForm'));

  try {
    const res = await fetch('/api/materials', {
      method: 'POST',
      body: formData
    });
    const json = await res.json();

    if (json.status === 'success') {
      feedback.textContent = `Resource "${json.data.title}" successfully published!`;
      feedback.className = "text-xs font-bold text-emerald-600 block";
      
      // Reset form
      document.getElementById('uploadMaterialForm').reset();
      clearSelectedFile(new Event('dummy'));
      fetchAdminStats();
      loadAdminMaterials();
      
      // Optional switch to materials tab after 1.2s
      setTimeout(() => {
        feedback.classList.add('hidden');
      }, 3500);
    } else {
      feedback.textContent = `Upload failed: ${json.detail || "Server error"}`;
      feedback.className = "text-xs font-bold text-rose-600 block";
    }
  } catch (err) {
    console.error('Upload failed:', err);
    feedback.textContent = "Upload failed. Please verify server connection.";
    feedback.className = "text-xs font-bold text-rose-600 block";
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up mr-1.5"></i> Publish Resource';
  }
}

// ==========================================
// MANAGE MATERIALS TABLE
// ==========================================

async function loadAdminMaterials() {
  const tbody = document.getElementById('adminMaterialsTableBody');
  try {
    const res = await fetch('/api/materials');
    const json = await res.json();
    adminState.materials = json.data || [];
    renderAdminMaterialsTable(adminState.materials);
  } catch (err) {
    console.error('Failed to load materials:', err);
    tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-rose-500 font-semibold">Error loading resources.</td></tr>`;
  }
}

function filterAdminMaterials(query) {
  const q = query.toLowerCase().trim();
  if (!q) {
    renderAdminMaterialsTable(adminState.materials);
    return;
  }
  const filtered = adminState.materials.filter(m => 
    m.title.toLowerCase().includes(q) ||
    m.category.toLowerCase().includes(q) ||
    m.chapter.toLowerCase().includes(q) ||
    m.resource_type.toLowerCase().includes(q)
  );
  renderAdminMaterialsTable(filtered);
}

function renderAdminMaterialsTable(materials) {
  const tbody = document.getElementById('adminMaterialsTableBody');
  if (!materials || materials.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-400">No resources found. Upload one to get started!</td></tr>`;
    return;
  }

  tbody.innerHTML = materials.map(mat => {
    const typeBadges = {
      documents: '<span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-blue-50 text-blue-700">Document</span>',
      videos: '<span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-rose-50 text-rose-700">Video</span>',
      audio: '<span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-purple-50 text-purple-700">Audio</span>',
      images: '<span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-50 text-emerald-700">Diagram</span>',
      slides: '<span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-50 text-amber-700">Slides</span>'
    };

    const dateFormatted = mat.uploaded_at ? new Date(mat.uploaded_at).toLocaleDateString() : 'Recent';

    return `
      <tr class="hover:bg-slate-50/80 transition-colors">
        <td class="py-3.5 px-4">
          <div class="font-bold text-slate-800 line-clamp-1">${escapeHtml(mat.title)}</div>
          <div class="text-[11px] text-slate-400 line-clamp-1 mt-0.5">${escapeHtml(mat.description)}</div>
        </td>
        <td class="py-3.5 px-4">
          <div class="font-semibold text-slate-700">${escapeHtml(mat.category)}</div>
          <div class="text-[11px] text-slate-400">${escapeHtml(mat.chapter)}</div>
        </td>
        <td class="py-3.5 px-4">
          ${typeBadges[mat.resource_type] || '<span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-100 text-slate-700">File</span>'}
        </td>
        <td class="py-3.5 px-4 font-mono text-slate-500">${mat.filesize_formatted}</td>
        <td class="py-3.5 px-4 text-slate-500">${dateFormatted}</td>
        <td class="py-3.5 px-4 text-right">
          <div class="flex items-center justify-end space-x-1.5">
            <a href="${mat.file_url}" target="_blank" title="Preview Raw" class="p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-slate-100">
              <i class="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
            <a href="/api/materials/${mat.id}/download" title="Download File" class="p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-slate-100">
              <i class="fa-solid fa-download"></i>
            </a>
            <button onclick="deleteAdminMaterial('${mat.id}', '${escapeHtml(mat.title)}')" title="Delete Resource" class="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

async function deleteAdminMaterial(id, title) {
  if (!confirm(`Are you sure you want to permanently delete '${title}'?`)) return;

  try {
    const res = await fetch(`/api/materials/${id}`, { method: 'DELETE' });
    const json = await res.json();
    if (json.status === 'success') {
      loadAdminMaterials();
      fetchAdminStats();
    } else {
      alert("Delete failed: " + (json.detail || "Server error"));
    }
  } catch (err) {
    console.error('Delete error:', err);
    alert('Failed to delete material.');
  }
}

// ==========================================
// INTERACTIVE QUIZ BUILDER
// ==========================================

function addQuestionCard() {
  const newQ = {
    id: 'q_' + Math.random().toString(36).substring(2, 8),
    question: '',
    options: ['', '', '', ''],
    correct_option_index: 0,
    points: 10,
    explanation: ''
  };
  adminState.builderQuestions.push(newQ);
  renderBuilderQuestions();
}

function removeQuestionCard(index) {
  if (adminState.builderQuestions.length <= 1) {
    alert("A quiz must have at least one question.");
    return;
  }
  adminState.builderQuestions.splice(index, 1);
  renderBuilderQuestions();
}

function renderBuilderQuestions() {
  const container = document.getElementById('questionsBuilderContainer');
  document.getElementById('questionCounterBadge').textContent = adminState.builderQuestions.length;

  container.innerHTML = adminState.builderQuestions.map((q, qIdx) => `
    <div class="bg-slate-50 border border-slate-200 rounded-2xl p-5 relative">
      <!-- Question Header -->
      <div class="flex items-center justify-between mb-3 pb-3 border-b border-slate-200/80">
        <span class="text-xs font-black text-indigo-700 flex items-center space-x-1.5">
          <span class="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px]">${qIdx + 1}</span>
          <span>Question ${qIdx + 1}</span>
        </span>

        <div class="flex items-center space-x-3">
          <div class="flex items-center space-x-1">
            <label class="text-[11px] font-bold text-slate-500">Points:</label>
            <input type="number" value="${q.points}" min="1" max="100" onchange="updateQuestionField(${qIdx}, 'points', parseInt(this.value))" class="w-14 px-2 py-1 text-xs bg-white border border-slate-200 rounded-lg text-center font-bold" />
          </div>
          <button type="button" onclick="removeQuestionCard(${qIdx})" class="text-rose-500 hover:text-rose-700 text-xs font-bold p-1">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      </div>

      <!-- Question Prompt Input -->
      <div class="mb-4">
        <label class="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-1">Question Prompt <span class="text-rose-500">*</span></label>
        <textarea rows="2" placeholder="e.g. What is the fundamental constant in Planck's quantum equation?" oninput="updateQuestionField(${qIdx}, 'question', this.value)" class="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none" required>${escapeHtml(q.question)}</textarea>
      </div>

      <!-- Options List -->
      <div class="space-y-2 mb-4">
        <label class="block text-[11px] font-bold text-slate-600 uppercase tracking-wider">
          Answer Options <span class="text-slate-400 font-normal">(Select radio button next to correct answer)</span>
        </label>
        ${q.options.map((opt, optIdx) => `
          <div class="flex items-center space-x-2">
            <input type="radio" name="correct_opt_${qIdx}" ${q.correct_option_index === optIdx ? 'checked' : ''} onchange="updateQuestionField(${qIdx}, 'correct_option_index', ${optIdx})" class="w-4 h-4 text-indigo-600 focus:ring-indigo-500 cursor-pointer" title="Mark as correct answer" />
            <input type="text" value="${escapeHtml(opt)}" placeholder="Option ${optIdx + 1}" oninput="updateQuestionOption(${qIdx}, ${optIdx}, this.value)" class="flex-grow px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none ${q.correct_option_index === optIdx ? 'border-emerald-500 ring-1 ring-emerald-400' : ''}" required />
            ${q.options.length > 2 ? `
              <button type="button" onclick="removeOptionFromQuestion(${qIdx}, ${optIdx})" class="text-slate-400 hover:text-rose-500 text-xs p-1" title="Remove option">
                <i class="fa-solid fa-xmark"></i>
              </button>
            ` : ''}
          </div>
        `).join('')}

        <button type="button" onclick="addOptionToQuestion(${qIdx})" class="mt-2 text-[11px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1">
          <i class="fa-solid fa-circle-plus"></i>
          <span>Add Another Option</span>
        </button>
      </div>

      <!-- Explanation Input -->
      <div>
        <label class="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-1">
          Solution Explanation <span class="text-slate-400 font-normal">(Shown to students upon grading)</span>
        </label>
        <input type="text" value="${escapeHtml(q.explanation)}" placeholder="Brief explanation justifying the correct answer" oninput="updateQuestionField(${qIdx}, 'explanation', this.value)" class="w-full px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
      </div>
    </div>
  `).join('');
}

function updateQuestionField(qIdx, field, value) {
  adminState.builderQuestions[qIdx][field] = value;
}

function updateQuestionOption(qIdx, optIdx, value) {
  adminState.builderQuestions[qIdx].options[optIdx] = value;
}

function addOptionToQuestion(qIdx) {
  adminState.builderQuestions[qIdx].options.push('');
  renderBuilderQuestions();
}

function removeOptionFromQuestion(qIdx, optIdx) {
  if (adminState.builderQuestions[qIdx].options.length <= 2) return;
  adminState.builderQuestions[qIdx].options.splice(optIdx, 1);
  if (adminState.builderQuestions[qIdx].correct_option_index >= adminState.builderQuestions[qIdx].options.length) {
    adminState.builderQuestions[qIdx].correct_option_index = 0;
  }
  renderBuilderQuestions();
}

async function saveNewQuiz() {
  const errorEl = document.getElementById('quizBuilderError');
  errorEl.classList.add('hidden');

  const title = document.getElementById('newQuizTitle').value.trim();
  const category = document.getElementById('newQuizCategory').value.trim();
  const chapter = document.getElementById('newQuizChapter').value.trim();
  const timeLimit = parseInt(document.getElementById('newQuizTimeLimit').value) || 10;
  const description = document.getElementById('newQuizDescription').value.trim();

  if (!title || !category || !chapter) {
    errorEl.textContent = "Please fill in Quiz Title, Subject Category, and Chapter.";
    errorEl.classList.remove('hidden');
    return;
  }

  // Validate questions
  for (let i = 0; i < adminState.builderQuestions.length; i++) {
    const q = adminState.builderQuestions[i];
    if (!q.question.trim()) {
      errorEl.textContent = `Question ${i + 1} prompt cannot be empty.`;
      errorEl.classList.remove('hidden');
      return;
    }
    for (let o = 0; o < q.options.length; o++) {
      if (!q.options[o].trim()) {
        errorEl.textContent = `Question ${i + 1}, Option ${o + 1} cannot be empty.`;
        errorEl.classList.remove('hidden');
        return;
      }
    }
  }

  const payload = {
    title,
    category,
    chapter,
    description: description || `Assessment test for ${chapter}`,
    time_limit_minutes: timeLimit,
    questions: adminState.builderQuestions
  };

  try {
    const res = await fetch('/api/quizzes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();

    if (json.status === 'success') {
      alert(`Quiz "${title}" published successfully!`);
      // Reset form
      document.getElementById('newQuizTitle').value = "";
      document.getElementById('newQuizChapter').value = "";
      document.getElementById('newQuizDescription').value = "";
      adminState.builderQuestions = [];
      addQuestionCard();
      loadAdminQuizzes();
      fetchAdminStats();
    } else {
      errorEl.textContent = json.detail || "Failed to save quiz.";
      errorEl.classList.remove('hidden');
    }
  } catch (err) {
    console.error('Quiz save error:', err);
    errorEl.textContent = "Network error while saving quiz.";
    errorEl.classList.remove('hidden');
  }
}

// ==========================================
// EXISTING QUIZZES LIST
// ==========================================

async function loadAdminQuizzes() {
  const container = document.getElementById('adminExistingQuizzesList');
  const submissionFilter = document.getElementById('submissionQuizFilter');
  try {
    const res = await fetch('/api/admin/quizzes');
    const json = await res.json();
    adminState.quizzes = json.data || [];

    // Populate submissions dropdown filter
    if (submissionFilter) {
      let filterOpts = '<option value="all">All Quizzes</option>';
      adminState.quizzes.forEach(q => {
        filterOpts += `<option value="${q.id}">${escapeHtml(q.title)}</option>`;
      });
      submissionFilter.innerHTML = filterOpts;
    }

    if (!adminState.quizzes || adminState.quizzes.length === 0) {
      container.innerHTML = `<div class="text-xs text-slate-400 py-4 text-center">No quizzes created yet.</div>`;
      return;
    }

    container.innerHTML = adminState.quizzes.map(q => `
      <div class="p-3.5 rounded-2xl border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors flex items-center justify-between">
        <div class="truncate mr-3">
          <div class="font-bold text-xs text-slate-800 truncate">${escapeHtml(q.title)}</div>
          <div class="text-[11px] text-slate-400">${escapeHtml(q.category)} • ${q.questions.length} Questions (${q.total_points} pts)</div>
        </div>
        <button onclick="deleteAdminQuiz('${q.id}', '${escapeHtml(q.title)}')" class="text-slate-400 hover:text-rose-600 p-1.5 transition-colors" title="Delete Quiz">
          <i class="fa-solid fa-trash-can text-xs"></i>
        </button>
      </div>
    `).join('');
  } catch (err) {
    console.error('Failed to load existing quizzes:', err);
  }
}

async function deleteAdminQuiz(quizId, title) {
  if (!confirm(`Are you sure you want to permanently delete the quiz '${title}'?`)) return;

  try {
    const res = await fetch(`/api/quizzes/${quizId}`, { method: 'DELETE' });
    const json = await res.json();
    if (json.status === 'success') {
      loadAdminQuizzes();
      fetchAdminStats();
    } else {
      alert("Failed to delete quiz: " + (json.detail || "Server error"));
    }
  } catch (err) {
    console.error('Failed to delete quiz:', err);
    alert('Failed to delete quiz.');
  }
}

// ==========================================
// SUBMISSIONS & GRADING TRACKER
// ==========================================

async function loadAdminSubmissions() {
  const tbody = document.getElementById('adminSubmissionsTableBody');
  const filter = document.getElementById('submissionQuizFilter');
  const chosenQuiz = filter ? filter.value : 'all';

  let url = '/api/submissions';
  if (chosenQuiz && chosenQuiz !== 'all') {
    url += `?quiz_id=${encodeURIComponent(chosenQuiz)}`;
  }

  try {
    const res = await fetch(url);
    const json = await res.json();
    adminState.submissions = json.data || [];
    renderSubmissionsTable(adminState.submissions);
  } catch (err) {
    console.error('Failed to fetch submissions:', err);
    tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-rose-500 font-semibold">Error loading submissions.</td></tr>`;
  }
}

function renderSubmissionsTable(submissions) {
  const tbody = document.getElementById('adminSubmissionsTableBody');
  if (!submissions || submissions.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-400">No student submissions recorded yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = submissions.map(sub => {
    const pct = sub.percentage;
    let badgeClass = "bg-rose-50 text-rose-700 border-rose-200";
    if (pct >= 80) badgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
    else if (pct >= 50) badgeClass = "bg-amber-50 text-amber-700 border-amber-200";

    const submittedDate = sub.submitted_at ? new Date(sub.submitted_at).toLocaleString() : 'Recent';

    return `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="py-3 px-4">
          <div class="font-bold text-slate-800">${escapeHtml(sub.student_name)}</div>
          <div class="text-[11px] text-slate-400">${escapeHtml(sub.student_email || 'No email provided')}</div>
        </td>
        <td class="py-3 px-4 font-semibold text-slate-700">${escapeHtml(sub.quiz_title)}</td>
        <td class="py-3 px-4 font-mono font-bold text-slate-800">${sub.score} / ${sub.total_points}</td>
        <td class="py-3 px-4">
          <span class="px-2.5 py-0.5 rounded-full text-xs font-black border ${badgeClass}">
            ${pct}%
          </span>
        </td>
        <td class="py-3 px-4 text-slate-500">${submittedDate}</td>
        <td class="py-3 px-4 text-right">
          <div class="flex items-center justify-end space-x-2">
            <button onclick="inspectSubmissionSheet('${sub.id}')" class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold rounded-lg transition-colors flex items-center space-x-1">
              <i class="fa-solid fa-file-invoice"></i>
              <span>Inspect</span>
            </button>
            <button onclick="deleteSubmissionRecord('${sub.id}')" class="p-1 rounded-lg text-slate-400 hover:text-rose-600 transition-colors" title="Delete record">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

async function inspectSubmissionSheet(submissionId) {
  try {
    const res = await fetch(`/api/submissions/${submissionId}`);
    const json = await res.json();
    if (json.status !== 'success') {
      alert("Failed to load submission details.");
      return;
    }

    const sub = json.data;
    document.getElementById('subModalStudentName').textContent = `${sub.student_name} (${sub.student_email || 'No email'})`;
    document.getElementById('subModalQuizTitle').textContent = sub.quiz_title;
    document.getElementById('subModalScoreText').textContent = `${sub.score} / ${sub.total_points} Points`;

    const badge = document.getElementById('subModalPctBadge');
    badge.textContent = `${sub.percentage}%`;
    if (sub.percentage >= 80) badge.className = "px-3.5 py-1.5 rounded-xl font-black text-sm bg-emerald-100 text-emerald-800";
    else if (sub.percentage >= 50) badge.className = "px-3.5 py-1.5 rounded-xl font-black text-sm bg-amber-100 text-amber-800";
    else badge.className = "px-3.5 py-1.5 rounded-xl font-black text-sm bg-rose-100 text-rose-800";

    const answersContainer = document.getElementById('subModalAnswersList');
    answersContainer.innerHTML = (sub.answers || []).map((ans, idx) => `
      <div class="p-4 rounded-2xl border ${ans.is_correct ? 'border-emerald-200 bg-emerald-50/20' : 'border-rose-200 bg-rose-50/20'}">
        <div class="flex items-start justify-between gap-3 mb-2">
          <div class="flex items-center space-x-2">
            <span class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${ans.is_correct ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white'}">
              ${idx + 1}
            </span>
            <span class="text-xs font-bold text-slate-800">${escapeHtml(ans.question)}</span>
          </div>
          <span class="text-xs font-bold ${ans.is_correct ? 'text-emerald-700 bg-emerald-100' : 'text-rose-700 bg-rose-100'} px-2 py-0.5 rounded-md">
            ${ans.is_correct ? `+${ans.points_earned} Pts` : '0 Pts'}
          </span>
        </div>

        <div class="space-y-1.5 mt-2 ml-7 text-xs">
          ${(ans.options || []).map((opt, optIdx) => {
            const isStudentPick = (ans.selected_option_index === optIdx);
            const isCorrectOption = (ans.correct_option_index === optIdx);
            let optClass = "text-slate-600 bg-white border border-slate-200";

            if (isCorrectOption) {
              optClass = "text-emerald-800 bg-emerald-100 border border-emerald-300 font-bold";
            } else if (isStudentPick && !ans.is_correct) {
              optClass = "text-rose-800 bg-rose-100 border border-rose-300 line-through font-semibold";
            }

            return `
              <div class="p-2 rounded-xl flex items-center ${optClass}">
                <span>${escapeHtml(opt)}</span>
                ${isStudentPick ? '<span class="ml-auto text-[10px] font-bold text-slate-500 uppercase">(Student Selection)</span>' : ''}
                ${isCorrectOption ? '<span class="ml-auto text-[10px] font-bold text-emerald-700 uppercase">(Correct Key)</span>' : ''}
              </div>
            `;
          }).join('')}
        </div>

        ${ans.explanation ? `
          <div class="mt-2.5 ml-7 p-2.5 rounded-xl bg-slate-100 text-slate-700 text-[11px] leading-relaxed">
            <span class="font-bold text-slate-900">Explanation:</span> ${escapeHtml(ans.explanation)}
          </div>
        ` : ''}
      </div>
    `).join('');

    openModal('submissionDetailModal');
  } catch (err) {
    console.error('Failed to load submission detail:', err);
    alert('Failed to load submission sheet.');
  }
}

async function deleteSubmissionRecord(subId) {
  if (!confirm("Delete this submission record?")) return;
  try {
    const res = await fetch(`/api/submissions/${subId}`, { method: 'DELETE' });
    const json = await res.json();
    if (json.status === 'success') {
      loadAdminSubmissions();
      fetchAdminStats();
    }
  } catch (err) {
    console.error('Failed to delete submission:', err);
  }
}

// ==========================================
// MODAL & UTILITY FUNCTIONS
// ==========================================

function openModal(modalId) {
  document.getElementById(modalId).classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
  document.body.style.overflow = '';
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
