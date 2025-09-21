// Toggle salary fields
function toggleSalaryFields() {
    let cb = document.getElementById("salary_negotiable");
    let fields = document.getElementById("salary_fields");
    if (!cb || !fields) return;
    if(cb.checked) {
        fields.style.display = "none";
        document.getElementById("salary_from").value = "";
        document.getElementById("salary_to").value = "";
    } else {
        fields.style.display = "flex";
    }
}
window.onload = function() {
    toggleSalaryFields();
};

$(document).ready(function() {
    $('.select2').select2({
        width: '100%',
        placeholder: 'Chọn hoặc tìm kiếm...',
        minimumResultsForSearch: 0, // Luôn cho phép tìm kiếm
        allowClear: false // Không hiện nút x xoá
    });

    let companyDistrict = COMPANY_DISTRICT;
    let companyWard = COMPANY_WARD;
    let companyProvince = COMPANY_PROVINCE;

    if(companyProvince) {
        $.getJSON("/api/districts", {province_code: companyProvince}, function(data) {
            $('#district').html('<option value="">Chọn quận/huyện</option>');
            $.each(data, function(i, item) {
                $('#district').append(
                    `<option value="${item.code}">${item.name}</option>`
                );
            });
            if(companyDistrict) {
                $('#district').val(companyDistrict).trigger('change');
                $.getJSON("/api/wards", {district_code: companyDistrict}, function(data) {
                    $('#ward').html('<option value="">Chọn phường/xã</option>');
                    $.each(data, function(i, item) {
                        $('#ward').append(
                            `<option value="${item.code}">${item.name}</option>`
                        );
                    });
                    if(companyWard) {
                        $('#ward').val(companyWard).trigger('change');
                    }
                });
            }
        });
    }

    $('#province').on('change', function() {
        let provinceCode = $(this).val();
        $('#district').html('<option value="">Chọn quận/huyện</option>').trigger('change');
        $('#ward').html('<option value="">Chọn phường/xã</option>').trigger('change');
        if(provinceCode) {
            $.getJSON("/api/districts", {province_code: provinceCode}, function(data) {
                $.each(data, function(i, item) {
                    $('#district').append(`<option value="${item.code}">${item.name}</option>`);
                });
                $('#district').val('').trigger('change');
            });
        }
    });

    $('#district').on('change', function() {
        let districtCode = $(this).val();
        $('#ward').html('<option value="">Chọn phường/xã</option>').trigger('change');
        if(districtCode) {
            $.getJSON("/api/wards", {district_code: districtCode}, function(data) {
                $.each(data, function(i, item) {
                    $('#ward').append(`<option value="${item.code}">${item.name}</option>`);
                });
                $('#ward').val('').trigger('change');
            });
        }
    });
});