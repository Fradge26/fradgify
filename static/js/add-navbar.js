document.addEventListener("DOMContentLoaded", () => {
    // Create a navbar container
    const navbar = document.createElement("nav");
    navbar.className = "navbar is-dark";
    navbar.innerHTML = `
        <div class="navbar-brand">
            <a class="navbar-item" href="/">
                <img src="/static/images/fradgify_tight.svg" alt="Fradgify Logo" style="max-height: 3rem;">
            </a>
            <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false">
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
            </a>
        </div>
        <div class="navbar-menu">
            <div class="navbar-start">
                <a class="navbar-item" href="/media/movies">Movies</a>
                <a class="navbar-item" href="/media/tv">TV</a>
                <a class="navbar-item" href="/media/music">Music</a>
                <a class="navbar-item" href="/media/sheets">Sheet Music</a>
            </div>
            <div class="navbar-end">
                <div class="navbar-item">
                    <div class="buttons">
                        <a class="button is-primary" href="/whereisluke">Where is Luke?</a>
                        <a class="button is-light" href="/media/report" target="_blank">Traffic Dashboard</a>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Insert the navbar at the top of the body
    document.body.insertBefore(navbar, document.body.firstChild);
});
