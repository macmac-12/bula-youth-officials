// static/theme.js
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle-button');
    const htmlElement = document.documentElement; // Get the <html> element

    // Function to apply the theme
    const applyTheme = (theme) => {
    const tables = document.querySelectorAll('.table');

    if (theme === 'dark') {
        htmlElement.classList.add('dark-theme');
        if (themeToggleButton) themeToggleButton.textContent = '☀️ Light Mode';
        tables.forEach(table => table.classList.add('table-dark'));
    } else {
        htmlElement.classList.remove('dark-theme');
        if (themeToggleButton) themeToggleButton.textContent = '🌙 Dark Mode';
        tables.forEach(table => table.classList.remove('table-dark'));
    }
};


    // Check for saved theme preference in localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        // Optional: Check for OS preference if no saved theme
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            applyTheme('dark');
        } else {
            applyTheme('light'); // Default to light if no preference or saved theme
        }
    }

    // Event listener for the toggle button
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            if (htmlElement.classList.contains('dark-theme')) {
                applyTheme('light');
                localStorage.setItem('theme', 'light');
            } else {
                applyTheme('dark');
                localStorage.setItem('theme', 'dark');
            }
        });
    }

    // Listen for OS theme changes (optional, but nice)
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        const newColorScheme = event.matches ? "dark" : "light";
        // Only change if no user preference is explicitly set via button
        if (!localStorage.getItem('theme_manually_set')) { // You'd need to set this flag on button click
             applyTheme(newColorScheme);
             localStorage.setItem('theme', newColorScheme); // Update saved theme
        }
    });

});
