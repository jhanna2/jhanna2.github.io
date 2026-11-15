// Highlights the section you're reading in the contents box, and shows a "Contents" button once the box scrolls away.
(() => {
  const toc = document.querySelector('.toc');
  if (!toc) return;
  toc.id = toc.id || 'contents';
  const links = [...toc.querySelectorAll('a[href^="#"]')];
  const heads = links.map(a => document.getElementById(decodeURIComponent(a.hash.slice(1))));
  const jump = Object.assign(document.createElement('a'), { className: 'toc-jump', href: '#contents', textContent: 'Contents' });
  document.body.append(jump);

  const update = () => {
    let cur = -1;
    heads.forEach((h, i) => { if (h && h.getBoundingClientRect().top < 160) cur = i; });
    links.forEach((a, i) => i === cur ? a.setAttribute('aria-current', 'location') : a.removeAttribute('aria-current'));
    jump.classList.toggle('show', toc.getBoundingClientRect().bottom < 0);
  };
  addEventListener('scroll', update, { passive: true });
  update();
})();
