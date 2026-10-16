(function injectValidationStyles() {
  if (document.getElementById('apply-validation-styles')) return;
  var style = document.createElement('style');
  style.id = 'apply-validation-styles';
  style.textContent =
    '.field-error { color:#ef4444; font-size:12px; margin-top:4px; }' +
    '.input-invalid { border-color:#ef4444 !important; }' +
    '.input-invalid:focus-visible { ring-color:#ef4444; }';
  document.head.appendChild(style);
})();

var NAME_PATTERN = /^[A-Za-z\u00C0-\u024F]+(?:[\s'-][A-Za-z\u00C0-\u024F]+)*$/;

function validateFirstName(value) {
  var trimmed = (value || '').trim();
  if (!trimmed) return 'First name is required.';
  if (trimmed.length < 2) return 'First name must be at least 2 characters.';
  if (trimmed.length > 50) return 'First name must be 50 characters or less.';
  if (!NAME_PATTERN.test(trimmed)) {
    return 'First name can only contain letters, spaces, hyphens, and apostrophes.';
  }
  return '';
}

function validateLastName(value) {
  var trimmed = (value || '').trim();
  if (!trimmed) return 'Last name is required.';
  if (trimmed.length < 2) return 'Last name must be at least 2 characters.';
  if (trimmed.length > 50) return 'Last name must be 50 characters or less.';
  if (!NAME_PATTERN.test(trimmed)) {
    return 'Last name can only contain letters, spaces, hyphens, and apostrophes.';
  }
  return '';
}

function validatePhone(value) {
  var trimmed = (value || '').trim();
  if (!trimmed) return '';
  if (!/^[\d\s+\-().]+$/.test(trimmed)) {
    return 'Phone number contains invalid characters.';
  }
  var digits = trimmed.replace(/\D/g, '');
  if (digits.length < 7 || digits.length > 15) {
    return 'Please enter a valid phone number (7-15 digits).';
  }
  return '';
}

function validateEmail(value) {
  var trimmed = (value || '').trim();
  if (!trimmed) return 'Email is required.';
  if (trimmed.length > 100) return 'Email must be 100 characters or less.';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(trimmed)) {
    return 'Please enter a valid email address.';
  }
  return '';
}

function validateCountry(value) {
  var trimmed = (value || '').trim();
  if (!trimmed) return 'Country is required.';
  if (trimmed.length < 2) return 'Country name must be at least 2 characters.';
  if (trimmed.length > 56) return 'Country name is too long.';
  if (!/^[A-Za-z\u00C0-\u024F]+(?:[\s.'-][A-Za-z\u00C0-\u024F]+)*$/.test(trimmed)) {
    return 'Please enter a valid country name.';
  }
  return '';
}

function validateLocality(value) {
  var trimmed = (value || '').trim();
  if (!trimmed) return 'Locality is required.';
  if (trimmed.length < 2) return 'Locality must be at least 2 characters.';
  if (trimmed.length > 100) return 'Locality must be 100 characters or less.';
  if (!/^[A-Za-z0-9\u00C0-\u024F]+(?:[\s.,'-][A-Za-z0-9\u00C0-\u024F]+)*$/.test(trimmed)) {
    return 'Please enter a valid city or locality name.';
  }
  return '';
}

function showFieldError(input, message) {
  if (!input) return;
  var wrap = input.closest('.space-y-2');
  if (!wrap) return;
  var existing = wrap.querySelector('.field-error');
  if (message) {
    input.classList.add('input-invalid');
    input.setAttribute('aria-invalid', 'true');
    if (!existing) {
      existing = document.createElement('p');
      existing.className = 'field-error';
      wrap.appendChild(existing);
    }
    existing.textContent = message;
  } else {
    input.classList.remove('input-invalid');
    input.removeAttribute('aria-invalid');
    if (existing) existing.remove();
  }
}

function validateApplyField(input) {
  if (!input) return '';
  var value = input.value;
  switch (input.id) {
    case 'sTest-candidateFirstName':
      return validateFirstName(value);
    case 'sTest-candidateLastName':
      return validateLastName(value);
    case 'sTest-candidateMobile':
      return validatePhone(value);
    case 'sTest-candidateEmail':
      return validateEmail(value);
    case 'sTest-candidateCountry':
      return validateCountry(value);
    case 'sTest-candidateLocality':
      return validateLocality(value);
    default:
      return '';
  }
}

var APPLY_VALIDATED_FIELD_IDS = [
  'sTest-candidateFirstName',
  'sTest-candidateLastName',
  'sTest-candidateEmail',
  'sTest-candidateMobile',
  'sTest-candidateCountry',
  'sTest-candidateLocality',
];

function validateApplyForm() {
  var fields = APPLY_VALIDATED_FIELD_IDS.map(function (id) {
    return document.getElementById(id);
  });
  var firstError = '';
  var firstInvalid = null;

  fields.forEach(function (input) {
    if (!input) return;
    var message = validateApplyField(input);
    showFieldError(input, message);
    if (message && !firstError) {
      firstError = message;
      firstInvalid = input;
    }
  });

  return { valid: !firstError, message: firstError, field: firstInvalid };
}

document.addEventListener('DOMContentLoaded', function () {
  // Navigation
  document.querySelectorAll('a').forEach(function (a) {
    var text = a.textContent.trim();
    if (text === 'More Jobs') {
      a.href = '../../index.html';
      a.removeAttribute('target');
    }
    if (text === 'View Job Description') {
      a.href = '../index.html';
      a.removeAttribute('target');
    }
  });

  // Close any open dropdown when clicking outside
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.rcrm-dropdown')) {
      document.querySelectorAll('.rcrm-dropdown-menu.open').forEach(function (m) {
        m.classList.remove('open');
      });
    }
  });

  // Dropdown buttons
  document.querySelectorAll('[data-dropdown]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var wrap = btn.closest('.rcrm-dropdown');
      var menu = wrap.querySelector('.rcrm-dropdown-menu');
      var wasOpen = menu.classList.contains('open');
      document.querySelectorAll('.rcrm-dropdown-menu.open').forEach(function (m) {
        m.classList.remove('open');
      });
      if (!wasOpen) menu.classList.add('open');
    });
  });

  document.querySelectorAll('.rcrm-dropdown-menu [data-value]').forEach(function (item) {
    item.addEventListener('click', function (e) {
      e.stopPropagation();
      var wrap = item.closest('.rcrm-dropdown');
      var btn = wrap.querySelector('[data-dropdown]');
      var span = btn.querySelector('[data-label]') || btn;
      if (span.hasAttribute('data-label')) {
        span.textContent = item.getAttribute('data-value');
        span.classList.remove('text-slate-500');
      } else {
        var label = btn.childNodes[0];
        if (label && label.nodeType === 3) {
          btn.childNodes[0].textContent = item.getAttribute('data-value') + ' ';
        }
      }
      btn.setAttribute('data-selected', item.getAttribute('data-value'));
      item.closest('.rcrm-dropdown-menu').classList.remove('open');
    });
  });

  // File upload buttons
  document.querySelectorAll('[data-file-trigger]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = document.getElementById(btn.getAttribute('data-file-trigger'));
      if (input) input.click();
    });
  });

  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.addEventListener('change', function () {
      var btn = document.querySelector('[data-file-trigger="' + input.id + '"]');
      if (btn && input.files.length) {
        var span = btn.querySelector('span');
        if (span) span.textContent = input.files[0].name;
      }
    });
  });

  // Date picker
  document.querySelectorAll('[data-date-trigger]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = document.getElementById(btn.getAttribute('data-date-trigger'));
      if (input) {
        input.showPicker ? input.showPicker() : input.click();
      }
    });
  });

  document.querySelectorAll('input[type="date"]').forEach(function (input) {
    input.addEventListener('change', function () {
      var btn = document.querySelector('[data-date-trigger="' + input.id + '"]');
      if (btn && input.value) {
        var span = btn.querySelector('[data-label]');
        if (span) {
          span.textContent = input.value;
          span.classList.remove('text-slate-500');
        }
      }
    });
  });

  // Add education history
  var eduBtn = document.getElementById('sTest-addEducationHistoryBtn');
  var eduContainer = document.getElementById('education-history-container');
  if (eduBtn && eduContainer) {
    eduBtn.addEventListener('click', function () {
      var row = document.createElement('div');
      row.className = 'education-row border border-slate-200 rounded p-4 mb-3 bg-slate-50';
      row.innerHTML =
        '<div class="block md:flex md:flex-wrap gap-3">' +
        '<div class="md:w-1/2 p-2"><label class="text-xs font-bold text-[#464646]">Institute Name</label>' +
        '<input class="flex h-10 w-full rounded border border-slate-200 bg-white px-3 py-2 text-sm mt-1" placeholder="University Name" type="text"></div>' +
        '<div class="md:w-1/2 p-2"><label class="text-xs font-bold text-[#464646]">Degree</label>' +
        '<input class="flex h-10 w-full rounded border border-slate-200 bg-white px-3 py-2 text-sm mt-1" placeholder="Bachelor of Science" type="text"></div>' +
        '<div class="md:w-1/2 p-2"><label class="text-xs font-bold text-[#464646]">Start Year</label>' +
        '<input class="flex h-10 w-full rounded border border-slate-200 bg-white px-3 py-2 text-sm mt-1" placeholder="2018" type="text"></div>' +
        '<div class="md:w-1/2 p-2"><label class="text-xs font-bold text-[#464646]">End Year</label>' +
        '<input class="flex h-10 w-full rounded border border-slate-200 bg-white px-3 py-2 text-sm mt-1" placeholder="2022" type="text"></div>' +
        '</div>';
      eduContainer.appendChild(row);
    });
  }

  // Skills tags
  var skillsInput = document.getElementById('sTest-candidateSkillsInput');
  var skillsWrap = document.getElementById('skills-tags');
  if (skillsInput && skillsWrap) {
    skillsInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ',') {
        e.preventDefault();
        var val = skillsInput.value.replace(',', '').trim();
        if (!val) return;
        var tag = document.createElement('span');
        tag.className = 'inline-flex items-center bg-slate-100 text-slate-700 text-xs px-2 py-1 rounded mr-2 mb-2';
        tag.innerHTML = val + ' <button type="button" class="ml-1 text-slate-500 hover:text-red-500" data-remove-skill>&times;</button>';
        skillsWrap.appendChild(tag);
        skillsInput.value = '';
      }
    });
    skillsWrap.addEventListener('click', function (e) {
      if (e.target.matches('[data-remove-skill]')) {
        e.target.closest('span').remove();
      }
    });
  }

  // Add language row
  var addLangBtn = document.getElementById('sTest-addLanguageBtn');
  var langContainer = document.getElementById('language-rows');
  if (addLangBtn && langContainer) {
    addLangBtn.addEventListener('click', function () {
      var clone = langContainer.querySelector('.language-row');
      if (clone) {
        var row = clone.cloneNode(true);
        row.querySelectorAll('[data-selected]').forEach(function (b) {
          b.removeAttribute('data-selected');
          var lbl = b.querySelector('[data-label]');
          if (lbl) {
            lbl.textContent = lbl.getAttribute('data-placeholder') || 'Select';
            lbl.classList.add('text-slate-500');
          }
        });
        langContainer.appendChild(row);
      }
    });
  }

  // Field validation on blur and input
  APPLY_VALIDATED_FIELD_IDS.forEach(function (id) {
    var input = document.getElementById(id);
    if (!input) return;
    input.addEventListener('blur', function () {
      showFieldError(input, validateApplyField(input));
    });
    input.addEventListener('input', function () {
      if (input.classList.contains('input-invalid')) {
        showFieldError(input, validateApplyField(input));
      }
    });
  });

  // Form submit
  var form = document.getElementById('sTest-applyForm');
  var errorBox = document.getElementById('apply-error-box');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var validation = validateApplyForm();
      if (!validation.valid) {
        if (errorBox) {
          errorBox.textContent = validation.message;
          errorBox.style.display = 'block';
        }
        if (validation.field) {
          validation.field.focus();
          validation.field.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
      }

      if (errorBox) {
        errorBox.textContent = '';
        errorBox.style.display = 'none';
      }

      var submitBtn = document.getElementById('submit_candidate2');
      var delay = parseInt(form.getAttribute('data-submit-delay') || '500', 10);
      if (delay < 300) delay = 300;
      if (delay > 700) delay = 700;

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        submitBtn.setAttribute('aria-busy', 'true');
      }

      setTimeout(function () {
        window.location.href = 'thank-you/index.html';
      }, delay);
    });
  }
});
