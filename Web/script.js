/* ============================================
   Random Student Number Generator — Scripts
   Scroll animations, counters, particles, nav
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    /* ---------- Particle Background ---------- */
    const particlesContainer = document.getElementById('particles');
    const PARTICLE_COUNT = 40;

    function createParticle() {
        const p = document.createElement('div');
        p.classList.add('particle');
        const size = Math.random() * 4 + 1;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + '%';
        const duration = Math.random() * 8 + 6;
        p.style.animationDuration = duration + 's';
        p.style.animationDelay = Math.random() * 10 + 's';
        // Random hue-ish tint
        const hue = Math.random() * 60 + 220; // blues / purples
        p.style.background = `rgba(${Math.floor(Math.random()*60+99)}, ${Math.floor(Math.random()*40+100)}, 255, ${Math.random()*0.4+0.15})`;
        particlesContainer.appendChild(p);
    }

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        createParticle();
    }

    /* ---------- Navbar Scroll Effect ---------- */
    const navbar = document.getElementById('navbar');
    const handleNavScroll = () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    };
    window.addEventListener('scroll', handleNavScroll, { passive: true });
    handleNavScroll();

    /* ---------- Mobile Menu ---------- */
    const menuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');

    menuBtn.addEventListener('click', () => {
        menuBtn.classList.toggle('open');
        mobileMenu.classList.toggle('open');
    });

    // Close on link click
    mobileMenu.querySelectorAll('.mobile-link').forEach(link => {
        link.addEventListener('click', () => {
            menuBtn.classList.remove('open');
            mobileMenu.classList.remove('open');
        });
    });

    /* ---------- Scroll-triggered Animations ---------- */
    const animatedEls = document.querySelectorAll('[data-animate]');

    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -60px 0px',
        threshold: 0.15,
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.dataset.delay || '0', 10);
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, delay);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    animatedEls.forEach(el => observer.observe(el));

    /* ---------- Counter Animation ---------- */
    function animateCounter(el) {
        const target = parseInt(el.dataset.count, 10);
        const duration = 2000;
        const start = performance.now();

        function easeOutQuad(t) {
            return t * (2 - t);
        }

        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = easeOutQuad(progress);
            const current = Math.floor(eased * target);
            el.textContent = current.toLocaleString();
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.textContent = target.toLocaleString();
            }
        }

        requestAnimationFrame(update);
    }

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stat-number[data-count]').forEach(el => {
        counterObserver.observe(el);
    });

    /* ---------- Active Nav Link on Scroll ---------- */
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                navLinks.forEach(link => {
                    link.classList.toggle('active',
                        link.getAttribute('href') === '#' + id);
                });
            }
        });
    }, {
        rootMargin: '-30% 0px -60% 0px',
    });

    sections.forEach(s => sectionObserver.observe(s));

    /* ---------- Mockup Random Number ---------- */
    const mockupNumEl = document.getElementById('mockupNumber');
    const mockupNameEl = document.getElementById('mockupName');
    const mockupBtn = document.getElementById('mockupBtn');

    const sampleNames = [
        'Alice Chen', 'Bob Smith', 'Carol Lee', 'David Kim',
        'Emma Wang', 'Frank Zhao', 'Grace Liu', 'Henry Zhang',
        'Ivy Wu', 'Jack Huang', 'Kate Li', 'Leo Yang'
    ];

    function doMockupRandom() {
        const num = Math.floor(Math.random() * 50) + 1;
        const name = sampleNames[Math.floor(Math.random() * sampleNames.length)];
        // Animate number
        mockupNumEl.style.transform = 'scale(1.15)';
        mockupNumEl.style.opacity = '0.5';
        mockupNumEl.textContent = num;
        mockupNameEl.textContent = name;
        requestAnimationFrame(() => {
            mockupNumEl.style.transition = 'transform 0.3s, opacity 0.3s';
            mockupNumEl.style.transform = 'scale(1)';
            mockupNumEl.style.opacity = '1';
        });
    }

    mockupBtn.addEventListener('click', doMockupRandom);

    // Auto-randomize every 3 seconds when visible
    let autoRandomInterval = null;

    const mockupObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                if (!autoRandomInterval) {
                    autoRandomInterval = setInterval(doMockupRandom, 3000);
                }
            } else {
                clearInterval(autoRandomInterval);
                autoRandomInterval = null;
            }
        });
    }, { threshold: 0.3 });

    const heroVisual = document.querySelector('.hero-visual');
    if (heroVisual) {
        mockupObserver.observe(heroVisual);
    }

    /* ---------- Smooth Scroll for Anchor Links ---------- */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    /* ---------- Tilt Effect on Feature Cards ---------- */
    const featureCards = document.querySelectorAll('.feature-card, .about-card');

    featureCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / centerY * -3;
            const rotateY = (x - centerX) / centerX * 3;
            card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

    /* ---------- Parallax on Hero Visual ---------- */
    const heroSection = document.querySelector('.hero');
    const heroVisualEl = document.querySelector('.hero-visual');

    window.addEventListener('scroll', () => {
        if (!heroSection || !heroVisualEl) return;
        const scrollY = window.scrollY;
        const heroBottom = heroSection.offsetTop + heroSection.offsetHeight;
        if (scrollY < heroBottom) {
            heroVisualEl.style.transform = `translateY(${scrollY * 0.15}px)`;
        }
    }, { passive: true });

    /* ---------- Ripple Effect on Buttons ---------- */
    document.querySelectorAll('.btn, .platform-card').forEach(el => {
        el.addEventListener('click', function (e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            const rect = this.getBoundingClientRect();
            ripple.style.left = (e.clientX - rect.left) + 'px';
            ripple.style.top = (e.clientY - rect.top) + 'px';
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.width = ripple.style.height = '0px';
            ripple.style.background = 'rgba(255,255,255,0.2)';
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.animation = 'rippleAnim 0.6s ease forwards';
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Inject ripple keyframes
    const rippleStyle = document.createElement('style');
    rippleStyle.textContent = `
        @keyframes rippleAnim {
            to {
                width: 300px;
                height: 300px;
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(rippleStyle);
});
