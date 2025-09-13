document.addEventListener('DOMContentLoaded', function () {
    // Real-time form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('input', function () {
                if (input.checkValidity()) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                }
            });
        });

        // Prevent form submission if invalid
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                form.querySelectorAll('input, select').forEach(input => {
                    if (!input.checkValidity()) {
                        input.classList.add('is-invalid');
                    }
                });
            }
        });
    });

    // Dynamic batch selection in payments.html
    const studentSelect = document.querySelector('select[name="student_id"]');
    const batchSelect = document.querySelector('select[name="batch_id"]');
    if (studentSelect && batchSelect) {
        studentSelect.addEventListener('change', function () {
            const studentId = this.value;
            if (studentId) {
                fetch(`/api/batches`, {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json'
    }
})
                .then(response => response.json())
                .then(data => {
                    batchSelect.innerHTML = '<option value="">Select a batch</option>';
                    data.batches.forEach(batch => {
                        const option = document.createElement('option');
                        option.value = batch.id;
                        option.textContent = batch.name;
                        batchSelect.appendChild(option);
                    });
                    batchSelect.disabled = false;
                })
                .catch(error => {
                    console.error('Error fetching batches:', error);
                    batchSelect.innerHTML = '<option value="">Error loading batches</option>';
                    batchSelect.disabled = true;
                });
            } else {
                batchSelect.innerHTML = '<option value="">Select a batch</option>';
                batchSelect.disabled = true;
            }
        });
    }

    // Table sorting functionality for reports.html, staff_dashboard.html, student_dashboard.html
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function () {
                const rows = Array.from(table.querySelector('tbody').rows);
                const isAscending = header.dataset.sort !== 'asc';
                header.dataset.sort = isAscending ? 'asc' : 'desc';

                // Update sort indicators
                headers.forEach(h => h.innerHTML = h.innerHTML.replace(/ (↑|↓)/, ''));
                header.innerHTML += isAscending ? ' ↑' : ' ↓';

                rows.sort((a, b) => {
                    let aValue = a.cells[index].textContent.trim();
                    let bValue = b.cells[index].textContent.trim();

                    // Handle numeric columns (e.g., Age, Amount)
                    if (!isNaN(parseFloat(aValue)) && !isNaN(parseFloat(bValue))) {
                        aValue = parseFloat(aValue.replace('$', ''));
                        bValue = parseFloat(bValue.replace('$', ''));
                        return isAscending ? aValue - bValue : bValue - aValue;
                    }

                    // Handle date columns (e.g., Due Date, Registration Date)
                    if (aValue.match(/^\d{4}-\d{2}-\d{2}$/)) {
                        aValue = new Date(aValue).getTime();
                        bValue = new Date(bValue).getTime();
                        return isAscending ? aValue - bValue : bValue - aValue;
                    }

                    // Handle text columns
                    return isAscending
                        ? aValue.localeCompare(bValue)
                        : bValue.localeCompare(aValue);
                });

                table.querySelector('tbody').innerHTML = '';
                rows.forEach(row => table.querySelector('tbody').appendChild(row));
            });
        });
    });

    // Confirmation dialogs for delete actions (if applicable)
    const deleteButtons = document.querySelectorAll('a.btn-outline-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            if (!confirm('Are you sure you want to delete this record?')) {
                event.preventDefault();
            }
        });
    });

    // Accessibility: Add keyboard support for table sorting
    headers.forEach(header => {
        header.setAttribute('tabindex', '0');
        header.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                header.click();
            }
        });
    });
});