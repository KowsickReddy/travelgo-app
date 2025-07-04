// AJAX search for TravelGo2

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('searchForm');
    const resultsDiv = document.getElementById('searchResults');
    if (form && resultsDiv) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            resultsDiv.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>';
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.text())
            .then(html => {
                resultsDiv.innerHTML = html;
                window.scrollTo({ top: resultsDiv.offsetTop - 80, behavior: 'smooth' });
            })
            .catch(() => {
                resultsDiv.innerHTML = '<div class="alert alert-danger">Failed to load results.</div>';
            });
        });
    }

    // AJAX cancel booking for TravelGo2
    document.querySelectorAll('.cancel-booking-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const bookingId = this.getAttribute('data-id');
            fetch(`/cancel-booking/${bookingId}`, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    this.closest('tr').setAttribute('data-status', 'Canceled');
                    this.closest('tr').querySelector('td:nth-child(5)').innerHTML = '<span class="badge bg-secondary">Canceled</span>';
                    this.remove();
                    showToast('Booking canceled successfully!');
                } else {
                    showToast(data.message || 'Failed to cancel booking.');
                }
            })
            .catch(() => showToast('Failed to cancel booking.'));
        });
    });
});
