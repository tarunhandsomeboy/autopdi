/**
 * AUTO PDI — Interactive Report Viewer & Ratings
 */

document.addEventListener('DOMContentLoaded', () => {
    // Rating Form Submission
    const ratingForm = document.getElementById('rating-submission-form');
    if (ratingForm) {
        ratingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const booking_id = ratingForm.dataset.bookingId;
            const rating = document.getElementById('rating-stars-input')?.value || 5;
            const review = document.getElementById('rating-review-text')?.value || '';

            const res = await AutoPDI.api('/api/ratings', {
                method: 'POST',
                body: JSON.stringify({ booking_id, rating, review })
            });

            if (res.success) {
                AutoPDI.toast('Thank you for rating your inspector!', 'success');
                document.getElementById('rating-section-card')?.remove();
            }
        });
    }
});

async function verifyIssueResolution(issueId) {
    const res = await AutoPDI.api(`/api/issues/${issueId}/verify`, { method: 'PUT' });
    if (res.success) {
        AutoPDI.toast('Issue resolution verified by customer ✓', 'success');
        setTimeout(() => window.location.reload(), 600);
    }
}
