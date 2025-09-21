function getQueryArray(name) {
  const url = new URL(window.location.href);
  let arr = url.searchParams.getAll(name);
  if (arr.length === 1 && arr[0].includes(',')) {
    arr = arr[0].split(',');
  }
  return arr;
}

let provinces = window.provincesData;
let selectedProvince = null;
let selectedDistricts = [];
let currentDistricts = [];

// ĐỒNG BỘ LỰA CHỌN KHI LOAD TRANG
$(function() {
  const url = new URL(window.location.href);
  const filterProvince = url.searchParams.get('province_code');
  selectedProvince = filterProvince ? String(filterProvince) : null;
  selectedDistricts = getQueryArray("district_code");
});

function renderProvinceList(keyword = "") {
  let list = provinces;
  if (keyword) {
    list = provinces.filter(p => p.name.toLowerCase().includes(keyword.toLowerCase()));
  }
  $('#provinceList').html(list.map(p => {
    const isSelected = String(selectedProvince) === String(p.code);
    return `
      <button type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center ${isSelected ? 'active' : ''}" data-code="${p.code}">
        <span>
          ${p.name}
        </span>
        ${isSelected ? '<i class="bi bi-check-circle-fill text-primary"></i>' : ''}
      </button>
    `;
  }).join(''));
}

function showDistrictPanel(show) {
  if (show) {
    $('#districtPanel').show();
    $('#districtEmptyPanel').hide().removeClass('d-flex');
  } else {
    $('#districtPanel').hide();
    $('#districtEmptyPanel').show().addClass('d-flex');
  }
}

// Khi mở modal
$('#locationFilterModal').on('shown.bs.modal', function () {
  renderProvinceList();
  if (selectedProvince) {
    showDistrictPanel(true);
    loadDistricts(selectedProvince, function() {
      renderProvinceList($('#provinceSearch').val());
    });
  } else {
    showDistrictPanel(false);
  }
});

// Tìm kiếm tỉnh/thành
$(document).on('input', '#provinceSearch', function() {
  renderProvinceList(this.value);
});

// Chọn tỉnh/thành
$(document).on('click', '#provinceList .list-group-item', function() {
  selectedProvince = String($(this).data('code'));
  selectedDistricts = [];
  renderProvinceList($('#provinceSearch').val());
  showDistrictPanel(true);
  loadDistricts(selectedProvince);
});

// Hàm lấy districts qua API
function loadDistricts(provinceCode, callback) {
  $('#districtList').html('<div class="text-muted px-2 py-3">Đang tải...</div>');
  $.get('api/districts', { province_code: provinceCode }, function(data) {
    currentDistricts = data || [];
    renderDistrictList();
    if (typeof callback === "function") callback();
  });
}

// Render quận/huyện - value là district.code
function renderDistrictList() {
  $('#districtList').html(
    (currentDistricts || []).map((d, i) => `
      <div class="form-check mb-2">
        <input class="form-check-input" type="checkbox" id="district_${i}" value="${d.code}" ${selectedDistricts.includes(d.code) ? 'checked' : ''}>
        <label class="form-check-label" for="district_${i}">${d.name}</label>
      </div>
    `).join('')
  );
  $('#selectAllDistrict').prop('checked', selectedDistricts.length === (currentDistricts || []).length);
}

// Tick/tắt từng quận/huyện
$(document).on('change', '#districtList .form-check-input', function() {
  const val = $(this).val();
  if(this.checked) {
    if(!selectedDistricts.includes(val)) selectedDistricts.push(val);
  } else {
    selectedDistricts = selectedDistricts.filter(d => d !== val);
  }
  $('#selectAllDistrict').prop('checked', selectedDistricts.length === currentDistricts.length);
  renderProvinceList($('#provinceSearch').val());
});

// Chọn/bỏ tất cả quận/huyện
$(document).on('change', '#selectAllDistrict', function() {
  if(this.checked) {
    selectedDistricts = currentDistricts.map(d => d.code);
  } else {
    selectedDistricts = [];
  }
  renderDistrictList();
  renderProvinceList($('#provinceSearch').val());
});

// Bỏ chọn tất cả
$(document).on('click', '#clearAll', function() {
  selectedProvince = null;
  selectedDistricts = [];
  $('#selectAllDistrict').prop('checked', false);
  showDistrictPanel(false);
  renderProvinceList($('#provinceSearch').val());
});

$(document).on('click', '#applyLocation', function() {
  // Xóa các input ẩn cũ liên quan đến location
  $('#location-hidden-inputs').empty();

  // Thêm input ẩn tỉnh/thành
  if (selectedProvince) {
    $('#location-hidden-inputs').append(
      $('<input>', {type:'hidden', name:'province_code', value:selectedProvince})
    );
    // Thêm input ẩn cho từng quận/huyện đã chọn
    selectedDistricts.forEach(function(d) {
      $('#location-hidden-inputs').append(
        $('<input>', {type:'hidden', name:'district_code', value:d})
      );
    });
  }

  // Đóng modal trước
  $('#locationFilterModal').modal('hide');
  // Sau khi modal đóng xong, submit form luôn (delay 200ms cho mượt)
  setTimeout(function() {
    $('#searchForm')[0].submit();
  }, 200);
});