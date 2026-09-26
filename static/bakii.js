const modal = document.querySelector('#create-modal');
const toast = document.querySelector('.toast');
const panel = document.querySelector('.notification-panel');
const scrim = document.querySelector('.scrim');

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 2600);
}
function closeNotifications() {
  panel.classList.remove('open');
  panel.setAttribute('aria-hidden', 'true');
  scrim.classList.remove('open');
}
document.querySelectorAll('[data-open-create]').forEach(button => button.addEventListener('click', () => modal.showModal()));
document.querySelectorAll('[data-open-notifications]').forEach(button => button.addEventListener('click', () => {
  panel.classList.add('open'); panel.setAttribute('aria-hidden', 'false'); scrim.classList.add('open');
}));
document.querySelectorAll('[data-close-notifications]').forEach(button => button.addEventListener('click', closeNotifications));
document.querySelectorAll('[data-show-toast]').forEach(button => button.addEventListener('click', () => showToast(button.dataset.showToast)));
document.querySelector('[data-filter-plans]').addEventListener('click', () => showToast('전체 약속 화면은 다음 단계에서 연결할게요.'));
document.querySelector('#create-form').addEventListener('submit', event => {
  const title = new FormData(event.currentTarget).get('title');
  if (title) showToast(`“${title}” 초대장을 준비했어요.`);
});
