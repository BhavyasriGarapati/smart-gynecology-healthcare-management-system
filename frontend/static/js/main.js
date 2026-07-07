// BloomCare JS Scripts
document.addEventListener("DOMContentLoaded", function() {
    // Auto-close bootstrap alerts
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 4000);
    });
});
