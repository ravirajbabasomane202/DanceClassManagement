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
            if (studentId) { // Note: The API endpoint might need adjustment to return batches per student.
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

            // Accessibility: Add keyboard support for table sorting
            header.setAttribute('tabindex', '0');
            header.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    header.click();
                }
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

    // Global Chart Configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.plugins.legend.position = 'top';
        Chart.defaults.plugins.tooltip.backgroundColor = '#004aad';
        Chart.defaults.animation.duration = 1000;

        // Add click event for charts (if data-url is set on canvas)
        document.querySelectorAll('canvas.chart-interactive').forEach(canvas => {
            canvas.addEventListener('click', function (event) {
                const chart = Chart.getChart(canvas.id);
                if (!chart) return;
                const elements = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
                if (elements.length) {
                    const url = canvas.dataset.url; // Custom data-url attribute
                    if (url) {
                        window.location.href = url; // Redirect on click
                    }
                }
            });
        });

        // Accessibility: Keyboard navigation for charts
        document.querySelectorAll('canvas').forEach(canvas => {
            canvas.setAttribute('tabindex', '0');
            canvas.addEventListener('keydown', function (event) {
                if (event.key === 'Enter') {
                    // Simulate click
                    const simulatedClick = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    canvas.dispatchEvent(simulatedClick);
                }
            });
        });
    }
});