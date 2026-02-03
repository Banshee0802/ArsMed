document.addEventListener('DOMContentLoaded', () => {
  const burger = document.querySelector('.burger');
  const menu = document.querySelector('.nav-menu');

  burger?.addEventListener('click', () => {
    menu.classList.toggle('active');
  });
});
