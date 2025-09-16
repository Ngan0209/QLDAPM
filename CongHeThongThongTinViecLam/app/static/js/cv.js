/* ====== Data model ====== */
let design = {
  fontFamily: "Arial, Helvetica, sans-serif",
  fontSize: 14,
  lineHeight: 1.45,
  themeColor: "#1a73e8"
};

let profile = {
  name: "Tín Vũ",
  jobtitle: "Vị trí ứng tuyển",
  dob: "DD/MM/YYYY",
  gender: "Nam/Nữ",
  phone: "0123 456 789",
  email: "you@example.com",
  website: "portfolio.me",
  address: "Quận A, Thành phố",
  avatarDataUrl: "" // base64 image
};

let sections = [
  { id: "sec1", key: "career_objective", title: "Mục tiêu nghề nghiệp", content: "<div>Nhập mục tiêu nghề nghiệp của bạn...</div>", titleColor: "#111", contentColor: "#444", visible: true },
  { id: "sec2", key: "education", title: "Học vấn", content: "<div><strong>Bắt đầu - Kết thúc</strong><br/>Tên trường - Ngành học<br/>Mô tả học vấn</div>", titleColor: "#111", contentColor: "#444", visible: true },
  { id: "sec3", key: "experience", title: "Kinh nghiệm làm việc", content: "<div><strong>Bắt đầu - Kết thúc</strong><br/>Tên công ty<br/>Vị trí công việc<br/>Mô tả</div>", titleColor: "#111", contentColor: "#444", visible: true },
  { id: "sec4", key: "activities", title: "Hoạt động", content: "<div>Hoạt động & mô tả</div>", titleColor: "#111", contentColor: "#444", visible: true },
  { id: "sec5", key: "skills", title: "Kỹ năng", content: "<div>- Kỹ năng 1<br/>- Kỹ năng 2</div>", titleColor: "#111", contentColor: "#444", visible: true }
];

let selectedSectionId = null;
let editMode = false;
let editingSubItem = null; // { sectionId, index } nếu đang sửa

/* ====== Helper functions ====== */
const byId = (id) => document.getElementById(id);

function generateId() {
  return 's' + Date.now() + Math.floor(Math.random() * 1000);
}

/* ====== Section CRUD & Subitem ====== */
function selectSection(id) {
  selectedSectionId = id;
  renderSectionList();
}

function addSubItem(sectionId, data = {}) {
  const section = sections.find(x => x.id === sectionId);
  if (!section) return;
  if (!section.subitems) section.subitems = [];

  const newItem = {
    title: data.title || "Tiêu đề mục con",
    meta: data.meta || "Thời gian / vị trí",
    desc: data.desc || "Mô tả chi tiết..."
  };
  section.subitems.push(newItem);
  renderPreview();
}

function deleteSubItem(sectionId, index) {
  const section = sections.find(x => x.id === sectionId);
  if (!section || !section.subitems) return;
  section.subitems.splice(index, 1);
  renderPreview();
}

function showSubItemForm(sectionId, subIndex = null) {
  const form = byId('subItemFormContainer');
  form.style.display = 'block';
  form.dataset.sectionId = sectionId;
  editingSubItem = null;

  if (subIndex !== null) {
    const sub = sections.find(s => s.id === sectionId).subitems[subIndex];
    byId('subTitle').value = sub.title;
    byId('subMeta').value = sub.meta;
    byId('subDesc').value = sub.desc;
    editingSubItem = { sectionId, index: subIndex };
  } else {
    byId('subTitle').value = '';
    byId('subMeta').value = '';
    byId('subDesc').value = '';
  }

  byId('subTitle').focus();
}

/* ====== Section movement & visibility ====== */
function moveSectionUp(id) {
  const idx = sections.findIndex(x => x.id === id);
  if (idx > 0) {
    sections.splice(idx - 1, 0, sections.splice(idx, 1)[0]);
    renderSectionList();
    renderPreview();
  }
}

function moveSectionDown(id) {
  const idx = sections.findIndex(x => x.id === id);
  if (idx >= 0 && idx < sections.length - 1) {
    sections.splice(idx + 1, 0, sections.splice(idx, 1)[0]);
    renderSectionList();
    renderPreview();
  }
}

function toggleVisible(id) {
  const s = sections.find(x => x.id === id);
  if (s) {
    s.visible = !s.visible;
    renderSectionList();
    renderPreview();
  }
}

/* ====== Render functions ====== */
function renderSectionList() {
  const el = byId('sectionList');
  el.innerHTML = "";
  sections.forEach((s) => {
    const div = document.createElement('div');
    div.className = 'section-item' + (s.id === selectedSectionId ? ' active' : '');
    div.innerHTML = `
      <div>
        <strong style="font-size:13px">${s.title}</strong>
        <div style="font-size:12px;color:#666">${s.visible ? '' : '(Đã ẩn)'}</div>
      </div>
      <div style="display:flex;align-items:center">
        <button title="Chọn" onclick="selectSection('${s.id}')" class="btn btn-ghost">Chọn</button>
      </div>`;
    el.appendChild(div);
  });

  // show/hide selected controls
  if (!selectedSectionId) {
    byId('selectedControls').style.display = 'none';
    return;
  }
  byId('selectedControls').style.display = 'block';
  const s = sections.find(x => x.id === selectedSectionId);
  byId('selName').textContent = s.title;
  byId('selTitleColor').value = s.titleColor || '#000000';
  byId('selContentColor').value = s.contentColor || '#444444';
  byId('selVisible').checked = !!s.visible;
}

function renderPreview() {
  const preview = byId('preview');

  // Apply design
  preview.style.fontFamily = design.fontFamily;
  preview.style.fontSize = design.fontSize + 'px';
  preview.style.lineHeight = design.lineHeight;
  preview.style.color = "#222";

  // Avatar
  const avatarImg = byId('avatarImg');
  const placeholder = byId('avatarPlaceholder');
  if (profile.avatarDataUrl) {
    avatarImg.src = profile.avatarDataUrl;
    avatarImg.style.display = 'block';
    placeholder.style.display = 'none';
  } else {
    avatarImg.style.display = 'none';
    placeholder.style.display = 'flex';
    placeholder.textContent = profile.name ? profile.name.charAt(0).toUpperCase() : 'T';
  }

  // Header fields
  ['name','jobtitle','dob','gender','phone','email','website','address'].forEach(id => {
    byId(id).innerText = profile[id] || '';
  });

  // Sections
  const container = byId('sectionsContainer');
  container.innerHTML = '';
  sections.forEach(s => {
    if (!s.visible) return;
    const block = document.createElement('div');
    block.className = 'section-block';
    block.style.borderTopColor = design.themeColor;
    block.dataset.id = s.id;

    // Title row
    const titleRow = document.createElement('div');
    titleRow.style.display = 'flex';
    titleRow.style.justifyContent = 'space-between';
    titleRow.style.alignItems = 'center';

    const h4 = document.createElement('h4');
    h4.innerText = s.title;
    h4.style.color = s.titleColor || '#111';
    if (editMode) {
      h4.contentEditable = 'true';
      h4.oninput = () => { s.title = h4.innerText; renderSectionList(); };
    }

    const actions = document.createElement('div');
    actions.className = 'section-actions';
    actions.innerHTML = `
      <button title="Up" onclick="moveSectionUp('${s.id}')">⬆</button>
      <button title="Down" onclick="moveSectionDown('${s.id}')">⬇</button>
      <button title="Hide/Show" onclick="toggleVisible('${s.id}')">${s.visible ? '👁️' : '🚫'}</button>
      <button title="Add subitem" onclick="addSubItem('${s.id}')">➕</button>
    `;
    titleRow.appendChild(h4);
    titleRow.appendChild(actions);

    // Content
    const content = document.createElement('div');
    content.className = 'section-content';
    content.innerHTML = s.content;
    content.style.color = s.contentColor || '#444';

    if (s.subitems) {
      s.subitems.forEach((sub,i)=>{
        const subEl = document.createElement("div");
        subEl.className="sub-item border-start ps-2 mb-2";
        subEl.innerHTML = `
          <div class="sub-title fw-bold">${sub.title}</div>
          <div class="sub-meta text-muted small">${sub.meta}</div>
          <div class="sub-desc">${sub.desc}</div>
          ${editMode ? `<button onclick="deleteSubItem('${s.id}', ${i})">🗑️</button>
                        <button onclick="showSubItemForm('${s.id}', ${i})">✏️</button>` : ""}
        `;
        content.appendChild(subEl);
      });
    }

    if (editMode) {
      content.contentEditable = 'true';
      content.oninput = () => { s.content = content.innerHTML; updateOutput(); };
    }

    block.appendChild(titleRow);
    block.appendChild(content);
    container.appendChild(block);
  });

  updateOutput();
}

/* ====== Avatar upload ====== */
byId('avatarInput').addEventListener('change', (e) => handleAvatarFile(e.target.files));
function triggerAvatar() { byId('avatarInput').click(); }
function handleAvatarFile(files) {
  if (!files || files.length === 0) return;
  const f = files[0];
  const reader = new FileReader();
  reader.onload = function (ev) {
    profile.avatarDataUrl = ev.target.result;
    renderPreview();
  }
  reader.readAsDataURL(f);
}

/* ====== Edit mode toggle ====== */
byId('toggleEditBtn').addEventListener('click', () => {
  editMode = !editMode;
  byId('toggleEditBtn').textContent = editMode ? '🔒 Tắt sửa' : '🔓 Bật sửa';

  // set contenteditable for header fields
  ['name','jobtitle','dob','gender','phone','email','website','address'].forEach(id => {
    const el = byId(id);
    el.contentEditable = editMode;
    el.oninput = () => {
      if (id === 'dob') profile[id] = el.innerText.replace('Ngày sinh:', '').trim();
      else if (id === 'gender') profile[id] = el.innerText.replace('Giới tính:', '').trim();
      else if (id === 'phone') profile[id] = el.innerText.replace('Số điện thoại:', '').trim();
      else if (id === 'email') profile[id] = el.innerText.replace('Email:', '').trim();
      else if (id === 'website') profile[id] = el.innerText.replace('Website:', '').trim();
      else if (id === 'address') profile[id] = el.innerText.replace('Địa chỉ:', '').trim();
      else profile[id] = el.innerText;
    };
  });

  renderPreview();
});

/* ====== Global design controls ====== */
byId('fontFamily').addEventListener('change', e => { design.fontFamily = e.target.value; renderPreview(); });
byId('fontSize').addEventListener('input', e => { design.fontSize = Number(e.target.value); renderPreview(); });
byId('lineHeight').addEventListener('input', e => { design.lineHeight = Number(e.target.value); renderPreview(); });
byId('themeColor').addEventListener('input', e => { design.themeColor = e.target.value; renderPreview(); });

/* ====== Save / Load / Export ====== */
function updateOutput() {
   const profileCopy = { ...profile };
  delete profileCopy.avatarDataUrl;

  const data = { profile: profileCopy, sections, design };
  byId('output').textContent = JSON.stringify(data, null, 2);
}

byId('saveLocalBtn').addEventListener('click', () => {
  localStorage.setItem('cv_builder_data', JSON.stringify({ profile, sections, design }));
  alert('Đã lưu localStorage');
});

byId('loadLocalBtn').addEventListener('click', () => {
  const raw = localStorage.getItem('cv_builder_data');
  if (!raw) return alert('Không tìm thấy dữ liệu local');
  const d = JSON.parse(raw);
  profile = d.profile || profile;
  sections = d.sections || sections;
  design = d.design || design;
  selectedSectionId = null;
  renderSectionList();
  renderPreview();
  alert('Đã load từ localStorage');
});

byId('exportBtn').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify({ profile, sections, design }, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'cv_data.json'; document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
});

/* ====== Server save (JSON + avatar) ====== */
byId('saveServerBtn').addEventListener('click', async () => {
    const outputEl = byId('output');
    if (!outputEl.innerText) return alert('Không có dữ liệu để lưu');
  
    let cvData;
    try { cvData = JSON.parse(outputEl.innerText); }
    catch(err) { return alert('Dữ liệu không hợp lệ: ' + err); }
  
    const formData = new FormData();
    formData.append('cv_data', JSON.stringify(cvData));  // chỉ info, không avatar
  
    // Nếu có avatar
    const avatarFile = byId('avatarInput').files[0];
    if (avatarFile) formData.append('avatar', avatarFile);
  
    const res = await fetch('/cv/create-cv', {
      method: 'POST',
      body: formData
    });
  
    const result = await res.json();
    if (res.ok) alert('Lưu CV thành công, ID: ' + result.cv_id);
    else alert('Lỗi: ' + result.error);
  });

/* ====== Init ====== */
selectSection(null);
renderSectionList();
renderPreview();
updateOutput();
