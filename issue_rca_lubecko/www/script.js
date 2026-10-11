const body = document.body;
const menuToggle = document.querySelector('.menu-toggle');
const mainNav = document.querySelector('.main-nav');

if (menuToggle && mainNav) {
  const closeMenu = () => {
    body.classList.remove('nav-open');
    menuToggle.setAttribute('aria-expanded', 'false');
  };

  menuToggle.addEventListener('click', () => {
    const isOpen = body.classList.toggle('nav-open');
    menuToggle.setAttribute('aria-expanded', String(isOpen));
  });

  mainNav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', closeMenu);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });
}

const currentPage = body.dataset.page;
if (currentPage) {
  document.querySelector(`[data-nav="${currentPage}"]`)?.setAttribute('aria-current', 'page');
}

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const revealItems = document.querySelectorAll('.reveal');

if (reducedMotion || !('IntersectionObserver' in window)) {
  revealItems.forEach((item) => item.classList.add('visible'));
} else {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  revealItems.forEach((item) => observer.observe(item));
}

const cycleContent = {
  guest: {
    title: 'Gość znajduje bezpieczne miejsce',
    text: 'Alpha tworzy przestrzeń, w której można pytać, słuchać i szukać bez presji. Pierwszym doświadczeniem jest gościnność i relacja, a nie wymaganie gotowych odpowiedzi.'
  },
  faith: {
    title: 'Odkrywanie wiary',
    text: 'Kolejne spotkania prowadzą przez podstawowe pytania o życie, Jezusa, modlitwę i działanie Ducha Świętego. Każdy może iść we własnym tempie.'
  },
  team: {
    title: 'Wejście do ekipy',
    text: 'Uczestnik może wrócić przy następnej edycji jako pomocnik. Zaczyna troszczyć się o innych, uczy się słuchać i współtworzy atmosferę spotkania.'
  },
  leader: {
    title: 'Odpowiedzialność i liderzy',
    text: 'Praktyka kolejnych edycji pomaga formować gospodarzy, koordynatorów i osoby zdolne uruchamiać następne działania ewangelizacyjne.'
  },
  parish: {
    title: 'Zmiana kultury parafii',
    text: 'Ewangelizacja przestaje być jednorazowym wydarzeniem. Staje się regularnym sposobem działania wspólnoty, która ponownie wychodzi do osób poszukujących.'
  }
};

const cycleButtons = document.querySelectorAll('.cycle-button');
const cycleTitle = document.querySelector('[data-cycle-title]');
const cycleText = document.querySelector('[data-cycle-text]');

cycleButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const item = cycleContent[button.dataset.cycle];
    if (!item || !cycleTitle || !cycleText) return;

    cycleButtons.forEach((entry) => {
      entry.classList.remove('active');
      entry.setAttribute('aria-selected', 'false');
    });

    button.classList.add('active');
    button.setAttribute('aria-selected', 'true');
    cycleTitle.textContent = item.title;
    cycleText.textContent = item.text;
  });
});

const galleryButtons = document.querySelectorAll('[data-lightbox]');
const lightbox = document.querySelector('.lightbox');
const lightboxImage = lightbox?.querySelector('img');
const lightboxClose = lightbox?.querySelector('.lightbox-close');
let lastGalleryButton = null;

const closeLightbox = () => {
  if (!lightbox) return;
  lightbox.classList.remove('open');
  lightbox.setAttribute('aria-hidden', 'true');
  body.style.overflow = '';
  lastGalleryButton?.focus();
};

galleryButtons.forEach((button) => {
  button.addEventListener('click', () => {
    if (!lightbox || !lightboxImage) return;
    const source = button.querySelector('img');
    if (!source) return;

    lastGalleryButton = button;
    lightboxImage.src = source.src;
    lightboxImage.alt = source.alt;
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');
    body.style.overflow = 'hidden';
    lightboxClose?.focus();
  });
});

lightboxClose?.addEventListener('click', closeLightbox);
lightbox?.addEventListener('click', (event) => {
  if (event.target === lightbox) closeLightbox();
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && lightbox?.classList.contains('open')) closeLightbox();
});

const contactForm = document.querySelector('[data-contact-form]');
contactForm?.addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(contactForm);
  const name = data.get('name')?.toString().trim() || '';
  const place = data.get('place')?.toString().trim() || '';
  const stage = data.get('stage')?.toString().trim() || '';
  const message = data.get('message')?.toString().trim() || '';
  const subject = encodeURIComponent(`Rozmowa o Alpha – ${place || name || 'nowe zapytanie'}`);
  const bodyText = encodeURIComponent([
    `Imię: ${name}`,
    `Miejscowość / parafia: ${place}`,
    `Etap: ${stage}`,
    '',
    message
  ].join('\n'));
  window.location.href = `mailto:lubecko@alphapolska.org?subject=${subject}&body=${bodyText}`;
});

document.querySelectorAll('[data-year]').forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});
