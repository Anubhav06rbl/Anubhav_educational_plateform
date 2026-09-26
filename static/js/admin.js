/**
 * EduSphere Learning Platform - Teacher & Super Admin Portal Logic
 * Includes Role-Based Access Control and One-Time Upload Passes
 */

let adminState = {
  currentTab: 'upload',
  authToken: sessionStorage.getItem('edusphere_token') || null,
  currentUser: JSON.parse(sessionStorage.getItem('edusphere_user') || 'null'),
  materials: [],
  quizzes: [],
  submissions: [],
  selectedFile: null,
  builderQuestions: []
};

const BRANCH_TAXONOMY = {
  "Computer Science": ["Machine Learning (ML)", "Python", "Generative AI (GenAI)"],
  "Science": ["Physics", "Chemistry", "Biology"],
  "Humanities": ["History", "Geography", "Political Science"],
  "Other": ["Hindi", "English"]
};

function handleAdminBranchChange(branch) {
  const subSelect = document.getElementById('uploadSubCategory');
  const catInput = document.getElementById('uploadCategory');
  if (!subSelect) return;
  const list = BRANCH_TAXONOMY[branch] || [];
  subSelect.innerHTML = list.map(sub => `<option value="${escapeHtml(sub)}">${escapeHtml(sub)}</option>`).join('');
  if (list.length > 0 && catInput) {
    catInput.value = list[0];
  }
}

function handleQuizBranchChange(branch) {
  const subSelect = document.getElementById('newQuizSubCategory');
  const catInput = document.getElementById('newQuizCategory');
  if (!subSelect) return;
  const list = BRANCH_TAXONOMY[branch] || [];
  subSelect.innerHTML = list.map(sub => `<option value="${escapeHtml(sub)}">${escapeHtml(sub)}</option>`).join('');
  if (list.length > 0 && catInput) {
    catInput.value = list[0];
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  setupDropZone();
  addQuestionCard();
  handleAdminBranchChange('Computer Science');
  handleQuizBranchChange('Computer Science');

  // Check existing session
  if (adminState.authToken) {
    await verifyCurrentSession();
  } else {
    showAuthOverlay();
  }
});

function getAuthHeaders(customHeaders = {}) {
  const headers = { ...customHeaders };
  if (adminState.authToken) {
    headers['Authorization'] = `Bearer ${adminState.authToken}`;
  }
  return headers;
}

// ==========================================
// AUTHENTICATION & SESSION MANAGEMENT
// ==========================================

function showAuthOverlay() {
  document.getElementById('adminAuthOverlay').classList.remove('hidden');
}

function hideAuthOverlay() {
  document.getElementById('adminAuthOverlay').classList.add('hidden');
}

function switchAuthTab(type) {
  const credBtn = document.getElementById('authTabCredentialsBtn');
  const otpBtn = document.getElementById('authTabOneTimeBtn');
  const credForm = document.getElementById('credentialsLoginForm');
  const otpForm = document.getElementById('oneTimePassLoginForm');

  if (type === 'credentials') {
    credBtn.className = "flex-1 py-3 text-center border-b-2 border-indigo-600 text-indigo-700 bg-white";
    otpBtn.className = "flex-1 py-3 text-center border-b-2 border-transparent text-slate-500 hover:text-slate-800";
    credForm.classList.remove('hidden');
    otpForm.classList.add('hidden');
  } else {
    otpBtn.className = "flex-1 py-3 text-center border-b-2 border-purple-600 text-purple-700 bg-white";
    credBtn.className = "flex-1 py-3 text-center border-b-2 border-transparent text-slate-500 hover:text-slate-800";
    otpForm.classList.remove('hidden');
    credForm.classList.add('hidden');
  }
}

async function handleAccountLogin(e) {
  e.preventDefault();
  const ident = document.getElementById('loginIdentifier').value.trim();
  const pwd = document.getElementById('loginPassword').value.trim();
  const errEl = document.getElementById('loginAuthError');
  errEl.classList.add('hidden');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier: ident, password: pwd })
    });
    const json = await res.json();

    if (json.status === 'success') {
      applySession(json.token, json.user);
    } else {
      errEl.textContent = json.detail || "Authentication failed.";
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    errEl.textContent = "Server connection error. Please try again.";
    errEl.classList.remove('hidden');
  }
}

async function handleOneTimePassLogin(e) {
  e.preventDefault();
  const passCode = document.getElementById('loginPassCode').value.trim();
  const errEl = document.getElementById('passAuthError');
  errEl.classList.add('hidden');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ one_time_pass: passCode })
    });
    const json = await res.json();

    if (json.status === 'success') {
      applySession(json.token, json.user);
    } else {
      errEl.textContent = json.detail || "Invalid or used One-Time Pass.";
      errEl.classList.remove('hidden');
    }
  } catch (err) {
    errEl.textContent = "Server connection error. Please try again.";
    errEl.classList.remove('hidden');
  }
}

function applySession(token, user) {
  adminState.authToken = token;
  adminState.currentUser = user;
  sessionStorage.setItem('edusphere_token', token);
  sessionStorage.setItem('edusphere_user', JSON.stringify(user));

  hideAuthOverlay();
  initializePortalForRole();
}

async function verifyCurrentSession() {
  try {
    const res = await fetch('/api/auth/me', {
      headers: getAuthHeaders()
    });
    const json = await res.json();
    if (json.status === 'success') {
      adminState.currentUser = json.data;
      sessionStorage.setItem('edusphere_user', JSON.stringify(json.data));
      hideAuthOverlay();
      initializePortalForRole();
    } else {
      handleLogout();
    }
  } catch (err) {
    showAuthOverlay();
  }
}

async function handleLogout() {
  if (adminState.authToken) {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: getAuthHeaders()
      });
    } catch (_) {}
  }
  adminState.authToken = null;
  adminState.currentUser = null;
  sessionStorage.removeItem('edusphere_token');
  sessionStorage.removeItem('edusphere_user');
  location.reload();
}

function initializePortalForRole() {
  const user = adminState.currentUser;
  if (!user) return;

  // Header user badge
  const nameEl = document.getElementById('currentUserName');
  const iconEl = document.getElementById('userRoleIcon');
  nameEl.textContent = user.name;

  const accessControlTab = document.getElementById('adminTabAccessControl');
  const mobileAccessControlTab = document.getElementById('mobileTabAccessControl');

  if (user.role === 'super_admin') {
    iconEl.innerHTML = '<img src="/static/images/anubhav_founder.jpg" class="w-5 h-5 rounded-full object-cover inline-block ring-1 ring-amber-400" onerror="this.outerHTML=\'<i class=\\\'fa-solid fa-crown text-amber-500\\\'></i>\'" />';
    accessControlTab.classList.remove('hidden');
    mobileAccessControlTab.classList.remove('hidden');
  } else if (user.role === 'one_time_teacher') {
    iconEl.innerHTML = '<i class="fa-solid fa-bolt text-purple-600"></i>';
    accessControlTab.classList.add('hidden');
    mobileAccessControlTab.classList.add('hidden');
  } else {
    iconEl.innerHTML = '<i class="fa-solid fa-chalkboard-user text-indigo-600"></i>';
    accessControlTab.classList.add('hidden');
    mobileAccessControlTab.classList.add('hidden');
  }

  // Upload Permissions UI
  updateUploadPermissionUI();

  // Load section data
  fetchAdminStats();
  loadAdminMaterials();
  loadAdminQuizzes();
  loadAdminSubmissions();

  if (user.role === 'super_admin') {
    loadUsersTable();
    loadOneTimePasses();
  }
}

function updateUploadPermissionUI() {
  const user = adminState.currentUser;
  const indicator = document.getElementById('uploadPermissionIndicator');
  const form = document.getElementById('uploadMaterialForm');
  const restrictedBox = document.getElementById('uploadRestrictedBox');
  const oneTimeBanner = document.getElementById('oneTimeUploadBanner');

  if (!user) return;

  if (user.can_upload) {
    form.classList.remove('hidden');
    restrictedBox.classList.add('hidden');

    if (user.upload_type === 'one_time') {
      indicator.className = "px-3 py-1 rounded-full text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200";
      indicator.innerHTML = '<i class="fa-solid fa-bolt mr-1"></i> Mode: One-Time Upload';
      oneTimeBanner.classList.remove('hidden');
    } else {
      indicator.className = "px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200";
      indicator.innerHTML = '<i class="fa-solid fa-circle-check mr-1"></i> Upload: Authorized';
      oneTimeBanner.classList.add('hidden');
    }
  } else {
    form.classList.add('hidden');
    restrictedBox.classList.remove('hidden');
    oneTimeBanner.classList.add('hidden');
    indicator.className = "px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200";
    indicator.innerHTML = '<i class="fa-solid fa-ban mr-1"></i> Upload: Restricted';
  }
}

// ==========================================
// TABS SWITCHER
// ==========================================

function switchAdminTab(tab) {
  adminState.currentTab = tab;
  const sections = {
    upload: document.getElementById('adminSectionUpload'),
    materials: document.getElementById('adminSectionMaterials'),
    quizBuilder: document.getElementById('adminSectionQuizBuilder'),
    submissions: document.getElementById('adminSectionSubmissions'),
    accessControl: document.getElementById('adminSectionAccessControl')
  };

  const buttons = {
    upload: document.getElementById('adminTabUpload'),
    materials: document.getElementById('adminTabMaterials'),
    quizBuilder: document.getElementById('adminTabQuizBuilder'),
    submissions: document.getElementById('adminTabSubmissions'),
    accessControl: document.getElementById('adminTabAccessControl')
  };

  Object.keys(sections).forEach(key => {
    if (sections[key]) {
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
    }
  });

  if (tab === 'materials') loadAdminMaterials();
  if (tab === 'submissions') loadAdminSubmissions();
  if (tab === 'quizBuilder') loadAdminQuizzes();
  if (tab === 'accessControl') {
    loadUsersTable();
    loadOneTimePasses();
  }
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
// RESOURCE UPLOAD & SOURCE SWITCHER (FILE VS LINK)
// ==========================================

let currentUploadSourceMode = 'file';

function switchUploadSourceMode(mode) {
  currentUploadSourceMode = mode;
  const fileBtn = document.getElementById('sourceTypeFileBtn');
  const linkBtn = document.getElementById('sourceTypeLinkBtn');
  const fileBox = document.getElementById('fileUploadContainer');
  const linkBox = document.getElementById('linkUploadContainer');
  const submitBtn = document.getElementById('uploadSubmitBtn');

  if (mode === 'file') {
    fileBtn.className = "flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all bg-white text-indigo-700 shadow-sm flex items-center justify-center space-x-1.5";
    linkBtn.className = "flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all text-slate-600 hover:text-slate-900 flex items-center justify-center space-x-1.5";
    fileBox.classList.remove('hidden');
    linkBox.classList.add('hidden');
    submitBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up mr-1.5"></i> Publish Resource';
  } else {
    linkBtn.className = "flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all bg-white text-indigo-700 shadow-sm flex items-center justify-center space-x-1.5";
    fileBtn.className = "flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition-all text-slate-600 hover:text-slate-900 flex items-center justify-center space-x-1.5";
    fileBox.classList.add('hidden');
    linkBox.classList.remove('hidden');
    submitBtn.innerHTML = '<i class="fa-solid fa-link mr-1.5"></i> Share Web Link';
  }
}

function setupDropZone() {
  const dropZone = document.getElementById('dropZoneContainer');
  const fileInput = document.getElementById('fileInput');
  if (!dropZone || !fileInput) return;

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

  const titleInput = document.getElementById('uploadTitle');
  if (!titleInput.value.trim()) {
    const rawName = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
    const cleanTitle = rawName.replace(/[-_]+/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    titleInput.value = cleanTitle;
  }
}

function clearSelectedFile(e) {
  if (e && e.stopPropagation) e.stopPropagation();
  adminState.selectedFile = null;
  const fileInput = document.getElementById('fileInput');
  if (fileInput) fileInput.value = "";
  document.getElementById('dropZoneEmpty').classList.remove('hidden');
  document.getElementById('dropZoneSelected').classList.add('hidden');
}

async function handleMaterialUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('fileInput');
  const linkInput = document.getElementById('externalUrlInput');

  if (currentUploadSourceMode === 'file') {
    if (!fileInput.files || fileInput.files.length === 0) {
      alert("Please select a file to upload from your computer, or switch to 'Share External Web Link'.");
      return;
    }
  } else {
    if (!linkInput.value.trim()) {
      alert("Please enter a valid web link or YouTube URL.");
      linkInput.focus();
      return;
    }
  }

  const submitBtn = document.getElementById('uploadSubmitBtn');
  const feedback = document.getElementById('uploadFeedbackMessage');
  
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Processing...';
  feedback.classList.add('hidden');

  const formData = new FormData(document.getElementById('uploadMaterialForm'));
  if (currentUploadSourceMode === 'link') {
    formData.delete('file');
  }

  try {
    const res = await fetch('/api/materials', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    });
    const json = await res.json();

    if (json.status === 'success') {
      feedback.textContent = json.message;
      feedback.className = "text-xs font-bold text-emerald-600 block";
      
      document.getElementById('uploadMaterialForm').reset();
      handleAdminBranchChange(document.getElementById('uploadBranch').value);
      clearSelectedFile(new Event('dummy'));
      switchUploadSourceMode('file');
      fetchAdminStats();
      loadAdminMaterials();

      if (adminState.currentUser.upload_type === 'one_time') {
        adminState.currentUser.can_upload = false;
        sessionStorage.setItem('edusphere_user', JSON.stringify(adminState.currentUser));
        updateUploadPermissionUI();
      }
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
    submitBtn.innerHTML = currentUploadSourceMode === 'file' 
      ? '<i class="fa-solid fa-cloud-arrow-up mr-1.5"></i> Publish Resource' 
      : '<i class="fa-solid fa-link mr-1.5"></i> Share Web Link';
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
        <td class="py-3.5 px-4 text-slate-500">
          <div class="font-semibold text-slate-700">${escapeHtml(mat.uploaded_by || 'Admin')}</div>
          <div class="text-[10px] text-slate-400">${dateFormatted}</div>
        </td>
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
    const res = await fetch(`/api/materials/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
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

      <div class="mb-4">
        <label class="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-1">Question Prompt <span class="text-rose-500">*</span></label>
        <textarea rows="2" placeholder="e.g. What is the fundamental constant in Planck's quantum equation?" oninput="updateQuestionField(${qIdx}, 'question', this.value)" class="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none" required>${escapeHtml(q.question)}</textarea>
      </div>

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

  const branchEl = document.getElementById('newQuizBranch');
  const subCatEl = document.getElementById('newQuizSubCategory');
  const branch = branchEl ? branchEl.value : 'Computer Science';
  const subCategory = subCatEl ? subCatEl.value : '';
  const category = subCategory || (document.getElementById('newQuizCategory') ? document.getElementById('newQuizCategory').value.trim() : '');

  const payload = {
    title,
    branch,
    sub_category: subCategory,
    category,
    chapter,
    description: description || `Assessment test for ${chapter}`,
    time_limit_minutes: timeLimit,
    questions: adminState.builderQuestions
  };

  try {
    const res = await fetch('/api/quizzes', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    const json = await res.json();

    if (json.status === 'success') {
      alert(`Quiz "${title}" published successfully!`);
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
    const res = await fetch('/api/admin/quizzes', {
      headers: getAuthHeaders()
    });
    const json = await res.json();
    adminState.quizzes = json.data || [];

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
    const res = await fetch(`/api/quizzes/${quizId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
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
    const res = await fetch(url, {
      headers: getAuthHeaders()
    });
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
    const res = await fetch(`/api/submissions/${submissionId}`, {
      headers: getAuthHeaders()
    });
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
    const res = await fetch(`/api/submissions/${subId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
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
// 👑 SUPER ADMIN: ACCESS CONTROL & PERMISSIONS
// ==========================================

async function loadUsersTable() {
  const tbody = document.getElementById('usersTableBody');
  if (!tbody) return;

  try {
    const res = await fetch('/api/admin/users', {
      headers: getAuthHeaders()
    });
    const json = await res.json();
    if (json.status !== 'success') return;

    if (json.super_admin && json.super_admin.email) {
      const emailEl = document.getElementById('superAdminDisplayEmail');
      if (emailEl) emailEl.textContent = json.super_admin.email;
    }

    const users = json.data || [];
    if (users.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-slate-400">No teacher accounts created yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = users.map(u => {
      const isOneTime = (u.upload_type === 'one_time');
      const canUpload = u.can_upload;

      return `
        <tr class="hover:bg-slate-50 transition-colors">
          <td class="py-3.5 px-4">
            <div class="font-bold text-slate-800">${escapeHtml(u.name)}</div>
            <div class="text-[11px] text-slate-400">${escapeHtml(u.email)} (@${escapeHtml(u.username)})</div>
          </td>
          <td class="py-3.5 px-4">
            <select onchange="updateUserUploadMode('${u.id}', this.value)" class="text-[11px] font-bold px-2.5 py-1 rounded-lg border border-slate-200 bg-white">
              <option value="one_time" ${isOneTime ? 'selected' : ''}>⚡ One-Time</option>
              <option value="permanent" ${!isOneTime ? 'selected' : ''}>♾️ Permanent</option>
            </select>
          </td>
          <td class="py-3.5 px-4 font-mono font-bold text-slate-700">
            ${u.uploads_count || 0} ${isOneTime ? '/ 1' : 'files'}
          </td>
          <td class="py-3.5 px-4">
            <button onclick="toggleUserUploadPermission('${u.id}', ${canUpload})" class="px-3 py-1 rounded-xl text-xs font-black transition-all ${canUpload ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200' : 'bg-rose-100 text-rose-800 hover:bg-rose-200'}">
              ${canUpload ? '<i class="fa-solid fa-check mr-1"></i> Allowed' : '<i class="fa-solid fa-xmark mr-1"></i> Blocked'}
            </button>
          </td>
          <td class="py-3.5 px-4 text-right">
            <button onclick="deleteTeacherAccount('${u.id}', '${escapeHtml(u.name)}')" class="p-1.5 text-slate-400 hover:text-rose-600 transition-colors" title="Delete Teacher">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Failed to load users table:', err);
  }
}

async function toggleUserUploadPermission(userId, currentCanUpload) {
  try {
    const res = await fetch(`/api/admin/users/${userId}/permissions`, {
      method: 'PATCH',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ can_upload: !currentCanUpload })
    });
    const json = await res.json();
    if (json.status === 'success') {
      loadUsersTable();
    }
  } catch (err) {
    console.error('Failed to toggle upload permission:', err);
  }
}

async function updateUserUploadMode(userId, mode) {
  try {
    const res = await fetch(`/api/admin/users/${userId}/permissions`, {
      method: 'PATCH',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ upload_type: mode, can_upload: true })
    });
    const json = await res.json();
    if (json.status === 'success') {
      loadUsersTable();
    }
  } catch (err) {
    console.error('Failed to update upload mode:', err);
  }
}

async function deleteTeacherAccount(userId, name) {
  if (!confirm(`Delete teacher account '${name}'?`)) return;
  try {
    const res = await fetch(`/api/admin/users/${userId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    const json = await res.json();
    if (json.status === 'success') {
      loadUsersTable();
    }
  } catch (err) {
    console.error('Failed to delete user:', err);
  }
}

async function handleCreateTeacher(e) {
  e.preventDefault();
  const feedback = document.getElementById('createTeacherFeedback');
  feedback.classList.add('hidden');

  const payload = {
    name: document.getElementById('newTeacherName').value.trim(),
    email: document.getElementById('newTeacherEmail').value.trim(),
    username: document.getElementById('newTeacherUsername').value.trim(),
    password: document.getElementById('newTeacherPassword').value.trim(),
    upload_type: document.getElementById('newTeacherUploadType').value,
    can_upload: true
  };

  try {
    const res = await fetch('/api/admin/users', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    const json = await res.json();

    if (json.status === 'success') {
      feedback.textContent = `Teacher ${payload.name} created successfully!`;
      feedback.className = "text-xs font-bold text-emerald-600 block";
      document.getElementById('newTeacherName').value = "";
      document.getElementById('newTeacherEmail').value = "";
      document.getElementById('newTeacherUsername').value = "";
      document.getElementById('newTeacherPassword').value = "";
      loadUsersTable();
    } else {
      feedback.textContent = json.detail || "Failed to create teacher.";
      feedback.className = "text-xs font-bold text-rose-600 block";
    }
  } catch (err) {
    feedback.textContent = "Server error while creating teacher.";
    feedback.className = "text-xs font-bold text-rose-600 block";
  }
}

// ------------------------------------------
// ONE-TIME PASS MANAGEMENT
// ------------------------------------------

async function loadOneTimePasses() {
  const container = document.getElementById('oneTimePassesList');
  if (!container) return;

  try {
    const res = await fetch('/api/admin/one-time-passes', {
      headers: getAuthHeaders()
    });
    const json = await res.json();
    const passes = json.data || [];

    if (passes.length === 0) {
      container.innerHTML = `<div class="text-[11px] text-slate-400 py-3 text-center">No active or used passes.</div>`;
      return;
    }

    container.innerHTML = passes.map(p => {
      const isUsed = (p.status === 'used');
      return `
        <div class="p-2.5 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between text-xs">
          <div>
            <div class="font-mono font-bold text-purple-900">${p.token}</div>
            <div class="text-[10px] text-slate-400">${escapeHtml(p.assigned_to)} • ${isUsed ? '<span class="text-rose-600 font-bold">USED</span>' : '<span class="text-emerald-600 font-bold">ACTIVE</span>'}</div>
          </div>
          <div class="flex items-center space-x-1">
            <button onclick="navigator.clipboard.writeText('${p.token}'); alert('Passcode copied to clipboard: ${p.token}');" class="p-1 text-slate-400 hover:text-purple-600" title="Copy Passcode">
              <i class="fa-regular fa-copy"></i>
            </button>
            <button onclick="revokeOneTimePass('${p.id}')" class="p-1 text-slate-400 hover:text-rose-600" title="Revoke Pass">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Failed to load passes:', err);
  }
}

async function handleGenerateOneTimePass(e) {
  e.preventDefault();
  const name = document.getElementById('oneTimeAssignName').value.trim();
  try {
    const res = await fetch('/api/admin/one-time-passes', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ assigned_to: name })
    });
    const json = await res.json();
    if (json.status === 'success') {
      const pass = json.data;
      document.getElementById('generatedPassCode').textContent = pass.token;
      document.getElementById('newPassGeneratedBox').classList.remove('hidden');
      document.getElementById('oneTimeAssignName').value = "";
      loadOneTimePasses();
    }
  } catch (err) {
    alert("Failed to generate pass.");
  }
}

function copyGeneratedPass() {
  const code = document.getElementById('generatedPassCode').textContent;
  navigator.clipboard.writeText(code);
  alert(`One-Time Passcode copied: ${code}\nShare this code with your teacher to let them upload 1 resource.`);
}

async function revokeOneTimePass(passId) {
  if (!confirm("Revoke this pass?")) return;
  try {
    const res = await fetch(`/api/admin/one-time-passes/${passId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    const json = await res.json();
    if (json.status === 'success') {
      loadOneTimePasses();
    }
  } catch (err) {
    console.error('Failed to revoke pass:', err);
  }
}

// ==========================================
// MODALS & HELPERS
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
