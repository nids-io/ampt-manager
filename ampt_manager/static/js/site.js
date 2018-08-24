$(document).ready(function() {
    // Dismiss flashed alerts after a few seconds
    setTimeout(function() {
        $(".alert").alert('close');
    }, 5000);

    // Enable tooltips
    $('[data-toggle="tooltip"]').tooltip();
});

