const bar = document.getElementById('bar');
const close = document.getElementById('close');
const nav = document.getElementById('navbar');

if (bar && nav) {
    bar.addEventListener('click', () => {
        nav.classList.toggle('active');
    });
} else {
    console.error('Navbar or bar element not found!');
}

if (close) {
    close.addEventListener('click', () => {
        nav.classList.remove('active');
    })
}