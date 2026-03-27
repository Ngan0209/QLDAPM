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

const sectionTemplates = {
  career: {
    key: "career_objective",
    title: "Mục tiêu nghề nghiệp",
    content: "<div>Nhập mục tiêu nghề nghiệp của bạn...</div>"
  },
  education: {
    key: "education",
    title: "Học vấn",
    content: "<div><strong>Bắt đầu - Kết thúc</strong><br/>Tên trường - Ngành học<br/>Mô tả học vấn</div>"
  },
  experience: {
    key: "experience",
    title: "Kinh nghiệm làm việc",
    content: "<div><strong>Bắt đầu - Kết thúc</strong><br/>Tên công ty<br/>Vị trí công việc<br/>Mô tả</div>"
  },
  skills: {
    key: "skills",
    title: "Kỹ năng",
    content: "<div>- Kỹ năng 1<br/>- Kỹ năng 2</div>"
  },
  certificates: {
    key: "certificates",
    title: "Chứng chỉ",
    content: "<div>Tên chứng chỉ - Tổ chức cấp - Năm</div>"
  },
  awards: {
    key: "awards",
    title: "Giải thưởng",
    content: "<div>Tên giải thưởng - Năm</div>"
  },
  references: {
    key: "references",
    title: "Người giới thiệu",
    content: "<div>Tên - Chức vụ - Công ty<br/>Thông tin liên hệ</div>"
  },
  custom: {
    key: "custom",
    title: "Mục tùy chỉnh",
    content: "<div>Nội dung...</div>"
  }
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
  renderPreview();
}

function addSubItem(sectionId, data = {}) {
  const section = sections.find(x => x.id === sectionId);
  if (!section) return;
  if (!section.subitems) section.subitems = [];

  const newItem = {
    id: generateId(),
    title: data.title || "Tiêu đề mục con",
    meta: data.meta || "Thông tin bổ sung",
    desc: data.desc || "Mô tả chi tiết..."
  };
  section.subitems.push(newItem);
  renderPreview();
  updateOutput();
}

function deleteSubItem(sectionId, index) {
  const section = sections.find(x => x.id === sectionId);
  if (!section || !section.subitems) return;
  section.subitems.splice(index, 1);
  renderPreview();
  updateOutput();
}

function editSubItem(sectionId, index) {
  const section = sections.find(x => x.id === sectionId);
  if (!section || !section.subitems || !section.subitems[index]) return;
  
  const subItem = section.subitems[index];
  showSubItemForm(sectionId, index);
}

function showSubItemForm(sectionId, subIndex = null) {
  const modal = new bootstrap.Modal(byId('subItemModal'));
  const title = byId('subItemModalTitle');
  const form = byId('subItemForm');
  
  editingSubItem = null;

  if (subIndex !== null) {
    // Edit mode
    title.textContent = "Sửa mục con";
    const sub = sections.find(s => s.id === sectionId).subitems[subIndex];
    byId('subTitle').value = sub.title;
    byId('subMeta').value = sub.meta;
    byId('subDesc').value = sub.desc;
    editingSubItem = { sectionId, index: subIndex };
  } else {
    // Add mode
    title.textContent = "Thêm mục con";
    byId('subTitle').value = '';
    byId('subMeta').value = '';
    byId('subDesc').value = '';
  }

  modal.show();
}

function saveSubItem() {
  const title = byId('subTitle').value.trim();
  const meta = byId('subMeta').value.trim();
  const desc = byId('subDesc').value.trim();

  if (!title) {
    alert('Vui lòng nhập tiêu đề');
    byId('subTitle').focus();
    return;
  }

  if (editingSubItem) {
    // Edit existing subitem
    const section = sections.find(s => s.id === editingSubItem.sectionId);
    if (section && section.subitems && section.subitems[editingSubItem.index]) {
      section.subitems[editingSubItem.index] = { 
        ...section.subitems[editingSubItem.index],
        title, 
        meta, 
        desc 
      };
    }
  } else if (selectedSectionId) {
    // Add new subitem to selected section
    addSubItem(selectedSectionId, { title, meta, desc });
  }

  const modal = bootstrap.Modal.getInstance(byId('subItemModal'));
  modal.hide();
  renderPreview();
  updateOutput();
}

function moveSubItemUp(sectionId, index) {
  const section = sections.find(x => x.id === sectionId);
  if (!section || !section.subitems || index <= 0) return;
  
  const temp = section.subitems[index - 1];
  section.subitems[index - 1] = section.subitems[index];
  section.subitems[index] = temp;
  
  renderPreview();
  updateOutput();
}

function moveSubItemDown(sectionId, index) {
  const section = sections.find(x => x.id === sectionId);
  if (!section || !section.subitems || index >= section.subitems.length - 1) return;
  
  const temp = section.subitems[index + 1];
  section.subitems[index + 1] = section.subitems[index];
  section.subitems[index] = temp;
  
  renderPreview();
  updateOutput();
}

/* ====== Section movement & visibility ====== */
function moveSectionUp(id) {
  const idx = sections.findIndex(x => x.id === id);
  if (idx > 0) {
    sections.splice(idx - 1, 0, sections.splice(idx, 1)[0]);
    renderSectionList();
    renderPreview();
    updateOutput();
  }
}

function moveSectionDown(id) {
  const idx = sections.findIndex(x => x.id === id);
  if (idx >= 0 && idx < sections.length - 1) {
    sections.splice(idx + 1, 0, sections.splice(idx, 1)[0]);
    renderSectionList();
    renderPreview();
    updateOutput();
  }
}

function toggleVisible(id) {
  const s = sections.find(x => x.id === id);
  if (s) {
    s.visible = !s.visible;
    renderSectionList();
    renderPreview();
    updateOutput();
  }
}

function deleteSection(id) {
  if (!confirm('Bạn có chắc muốn xóa mục này?')) return;
  
  const idx = sections.findIndex(x => x.id === id);
  if (idx !== -1) {
    sections.splice(idx, 1);
    if (selectedSectionId === id) {
      selectedSectionId = null;
    }
    renderSectionList();
    renderPreview();
    updateOutput();
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
        <div style="font-size:12px;color:#666">
          ${s.visible ? '' : '(Đã ẩn)'}
          ${s.subitems && s.subitems.length > 0 ? ` (${s.subitems.length} mục con)` : ''}
        </div>
      </div>
      <div style="display:flex;align-items:center">
        <button title="Chọn" onclick="selectSection('${s.id}')" class="btn btn-ghost">Chọn</button>
      </div>`;
    el.appendChild(div);
  });

  // Update selected section controls
  updateSelectedControls();
}

function updateSelectedControls() {
  const controls = byId('selectedControls');
  if (!selectedSectionId) {
    controls.style.display = 'none';
    return;
  }
  
  controls.style.display = 'block';
  const s = sections.find(x => x.id === selectedSectionId);
  byId('selName').textContent = s.title;
  byId('selTitleColor').value = s.titleColor || '#000000';
  byId('selContentColor').value = s.contentColor || '#444444';
  byId('selVisible').checked = !!s.visible;
  
  // Update event listeners for controls
  byId('selTitleColor').onchange = (e) => {
    s.titleColor = e.target.value;
    renderPreview();
    updateOutput();
  };
  
  byId('selContentColor').onchange = (e) => {
    s.contentColor = e.target.value;
    renderPreview();
    updateOutput();
  };
  
  byId('selVisible').onchange = (e) => {
    s.visible = e.target.checked;
    renderSectionList();
    renderPreview();
    updateOutput();
  };
  
  byId('moveUpBtn').onclick = () => moveSectionUp(selectedSectionId);
  byId('moveDownBtn').onclick = () => moveSectionDown(selectedSectionId);
  byId('deleteBtn').onclick = () => deleteSection(selectedSectionId);
  byId('addSubItemBtn').onclick = () => showSubItemForm(selectedSectionId);
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
    titleRow.style.marginBottom = '10px';

    const h4 = document.createElement('h4');
    h4.innerText = s.title;
    h4.style.color = s.titleColor || '#111';
    h4.style.margin = '0';
    if (editMode) {
      h4.contentEditable = 'true';
      h4.oninput = () => { 
        s.title = h4.innerText; 
        renderSectionList(); 
        updateOutput();
      };
    }

    const actions = document.createElement('div');
    actions.className = 'section-actions';
    actions.style.display = editMode ? 'flex' : 'none';
    actions.style.gap = '5px';
    actions.innerHTML = `
      <button class="btn btn-sm btn-outline-secondary" title="Di chuyển lên" onclick="moveSectionUp('${s.id}')">⬆</button>
      <button class="btn btn-sm btn-outline-secondary" title="Di chuyển xuống" onclick="moveSectionDown('${s.id}')">⬇</button>
      <button class="btn btn-sm btn-outline-secondary" title="Ẩn/hiện" onclick="toggleVisible('${s.id}')">${s.visible ? '👁️' : '🚫'}</button>
      <button class="btn btn-sm btn-primary" title="Thêm mục con" onclick="showSubItemForm('${s.id}')">+ Mục con</button>
    `;
    titleRow.appendChild(h4);
    titleRow.appendChild(actions);

    // Content
    const content = document.createElement('div');
    content.className = 'section-content';
    content.style.color = s.contentColor || '#444';

    // HIỂN THỊ NỘI DUNG GỐC CỦA SECTION (nếu có)
    if (s.content && s.content.trim() !== '') {
      const originalContent = document.createElement('div');
      originalContent.innerHTML = s.content;
      if (editMode) {
        originalContent.contentEditable = 'true';
        originalContent.oninput = () => { 
          s.content = originalContent.innerHTML; 
          updateOutput(); 
        };
      }
      content.appendChild(originalContent);
    }

    // HIỂN THỊ CÁC MỤC CON (nếu có) - DƯỚI nội dung gốc
    if (s.subitems && s.subitems.length > 0) {
      // Thêm khoảng cách giữa nội dung gốc và mục con
      if (s.content && s.content.trim() !== '') {
        const spacer = document.createElement('div');
        spacer.style.height = '15px';
        content.appendChild(spacer);
      }
      
      s.subitems.forEach((sub, i) => {
        const subEl = document.createElement("div");
        subEl.className = "sub-item mb-3 p-2 border-start border-3";
        subEl.style.borderLeftColor = design.themeColor + '40';
        subEl.style.marginLeft = '10px';
        subEl.style.paddingLeft = '15px';
        
        let subContent = `
          <div class="sub-title fw-bold mb-1">${sub.title}</div>
          ${sub.meta ? `<div class="sub-meta text-muted small mb-1">${sub.meta}</div>` : ''}
          ${sub.desc ? `<div class="sub-desc">${sub.desc}</div>` : ''}
        `;
        
        if (editMode) {
          subContent += `
            <div class="mt-2 d-flex gap-2">
              <button class="btn btn-sm btn-outline-secondary" onclick="moveSubItemUp('${s.id}', ${i})" ${i === 0 ? 'disabled' : ''}>⬆</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="moveSubItemDown('${s.id}', ${i})" ${i === s.subitems.length - 1 ? 'disabled' : ''}>⬇</button>
              <button class="btn btn-sm btn-outline-primary" onclick="showSubItemForm('${s.id}', ${i})">Sửa</button>
              <button class="btn btn-sm btn-outline-danger" onclick="deleteSubItem('${s.id}', ${i})">Xóa</button>
            </div>
          `;
        }
        
        subEl.innerHTML = subContent;
        content.appendChild(subEl);
      });
    }

    // Nếu section không có nội dung gốc và không có mục con, hiển thị placeholder
    if ((!s.content || s.content.trim() === '') && (!s.subitems || s.subitems.length === 0)) {
      const placeholder = document.createElement('div');
      placeholder.innerHTML = '<em style="color:#999">Nhập nội dung cho mục này...</em>';
      if (editMode) {
        placeholder.contentEditable = 'true';
        placeholder.oninput = () => { 
          s.content = placeholder.innerHTML; 
          updateOutput(); 
        };
      }
      content.appendChild(placeholder);
    }

    block.appendChild(titleRow);
    block.appendChild(content);
    container.appendChild(block);
  });
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
    updateOutput();
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
      updateOutput();
    };
  });

  renderPreview();
});

/* ====== Global design controls ====== */
byId('fontFamily').addEventListener('change', e => { 
  design.fontFamily = e.target.value; 
  renderPreview(); 
  updateOutput();
});
byId('fontSize').addEventListener('input', e => { 
  design.fontSize = Number(e.target.value); 
  renderPreview(); 
  updateOutput();
});
byId('lineHeight').addEventListener('input', e => { 
  design.lineHeight = Number(e.target.value); 
  renderPreview(); 
  updateOutput();
});
byId('themeColor').addEventListener('input', e => { 
  design.themeColor = e.target.value; 
  renderPreview(); 
  updateOutput();
});

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
  updateOutput();
  alert('Đã load từ localStorage');
});

byId('exportBtn').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify({ profile, sections, design }, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'cv_data.json'; document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
});

/* ====== Server save ====== */
byId('saveServerBtn').addEventListener('click', async () => {
  const outputEl = byId('output');
  if (!outputEl.innerText) return alert('Không có dữ liệu để lưu');

  let cvData;
  try { cvData = JSON.parse(outputEl.innerText); }
  catch(err) { return alert('Dữ liệu không hợp lệ: ' + err); }

  const formData = new FormData();
  formData.append('cv_data', JSON.stringify(cvData));

  const avatarFile = byId('avatarInput').files[0];
  if (avatarFile) formData.append('avatar', avatarFile);

  try {
    const res = await fetch('/cv/create-cv', {
      method: 'POST',
      body: formData
    });

    const result = await res.json();
    if (res.ok) alert('Lưu CV thành công, ID: ' + result.cv_id);
    else alert('Lỗi: ' + result.error);
  } catch (error) {
    alert('Lỗi kết nối: ' + error.message);
  }
});

/* ====== Event Listeners ====== */
byId('addSectionBtn').addEventListener('click', () => {
  const key = byId('addTemplate').value;
  const tpl = sectionTemplates[key];
  if (!tpl) return;

  const newSection = {
    id: generateId(),
    key: tpl.key,
    title: tpl.title,
    content: tpl.content,
    titleColor: "#111",
    contentColor: "#444",
    visible: true
  };

  sections.push(newSection);
  renderSectionList();
  renderPreview();
  updateOutput();
  selectSection(newSection.id);
});

byId('saveSubItemBtn').addEventListener('click', saveSubItem);

// Double-click preview to toggle edit mode
byId('preview').addEventListener('dblclick', () => {
  byId('toggleEditBtn').click();
});

/* ====== Init ====== */
selectSection(null);
renderSectionList();
renderPreview();
updateOutput();