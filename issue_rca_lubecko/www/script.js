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

const renewalStory = document.querySelector('[data-renewal-story]');

if (renewalStory) {
  const renewalVisual = renewalStory.querySelector('[data-renewal-visual]');
  const renewalSteps = [...renewalStory.querySelectorAll('[data-renewal-step]')];
  const renewalNodes = [...renewalStory.querySelectorAll('[data-stage-target]')];
  const renewalArrows = [...renewalStory.querySelectorAll('.orbit-arrow')];
  const renewalMarkers = [...renewalStory.querySelectorAll('.alpha-marker')];
  const renewalCount = renewalStory.querySelector('[data-cycle-count]');
  const renewalTitle = renewalStory.querySelector('[data-cycle-title]');
  const renewalText = renewalStory.querySelector('[data-cycle-text]');

  const renewalContent = [
    {
      title: 'Zapraszamy na pierwszą Alpha',
      text: 'Chcemy ewangelizować i docierać do ludzi, którzy są poza Kościołem albo szukają drogi powrotu.'
    },
    {
      title: 'Uczestnik odkrywa wiarę',
      text: 'Gościnność, rozmowa i Ewangelia otwierają drogę do osobistego spotkania z Jezusem.'
    },
    {
      title: 'Wierzący wchodzi do ekipy',
      text: 'W kolejnej edycji zaczyna służyć gościom i uczy się troski o innych.'
    },
    {
      title: 'Posługujący staje się liderem',
      text: 'Kolejne edycje oraz realna odpowiedzialność formują gospodarzy i koordynatorów.'
    },
    {
      title: 'Zmienia się kultura parafii',
      text: 'Ewangelizacja staje się stałym rytmem parafii, która ponownie zaprasza osoby poszukujące.'
    }
  ];

  const activateRenewalStage = (stage) => {
    const activeStage = Math.min(Math.max(Number(stage) || 1, 1), 5);
    const content = renewalContent[activeStage - 1];

    renewalVisual.dataset.stage = String(activeStage);
    renewalCount.textContent = String(activeStage).padStart(2, '0');
    renewalTitle.textContent = content.title;
    renewalText.textContent = content.text;

    renewalSteps.forEach((step) => {
      const isActive = Number(step.dataset.renewalStep) === activeStage;
      step.classList.toggle('active', isActive);
      if (isActive) step.setAttribute('aria-current', 'step');
      else step.removeAttribute('aria-current');
    });

    renewalNodes.forEach((node) => {
      const nodeStage = Number(node.dataset.stageTarget);
      node.classList.toggle('is-visible', nodeStage <= activeStage);
      node.classList.toggle('active', nodeStage === activeStage);
    });

    renewalArrows.forEach((arrow, index) => {
      arrow.classList.toggle('is-visible', index < activeStage);
    });

    renewalMarkers.forEach((marker, index) => {
      marker.classList.toggle('is-visible', index < Math.min(activeStage, 4));
    });
  };

  renewalNodes.forEach((node) => {
    node.addEventListener('click', () => {
      const target = renewalStory.querySelector(`[data-renewal-step="${node.dataset.stageTarget}"]`);
      target?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'center' });
    });
  });

  if (!reducedMotion && 'IntersectionObserver' in window) {
    const renewalObserver = new IntersectionObserver((entries) => {
      const visibleEntry = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (visibleEntry) activateRenewalStage(visibleEntry.target.dataset.renewalStep);
    }, { rootMargin: '-35% 0px -45% 0px', threshold: [0, .1, .5] });

    renewalSteps.forEach((step) => renewalObserver.observe(step));
  }

  activateRenewalStage(1);
}

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
