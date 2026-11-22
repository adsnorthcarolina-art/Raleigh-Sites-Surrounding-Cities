/* Scroll progress bar: CSS scroll-timeline handles it in modern browsers; this is the fallback. */
(function () {
  var bar = document.querySelector(".progress");
  if (!bar || (window.CSS && CSS.supports && CSS.supports("animation-timeline: scroll()"))) return;
  var ticking = false;
  function update() {
    ticking = false;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.transform = "scaleX(" + (h > 0 ? Math.min(1, window.scrollY / h) : 0) + ")";
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();
/* Site animations, driven by Motion (https://motion.dev) — /js/motion.min.js exposes window.Motion {animate, inView}.
   Rules: no animation when the visitor prefers reduced motion; nothing visible at first paint is ever hidden or
   animated (hero, sticky bar, anything above the fold); only below-the-fold content reveals on scroll. */
(function () {
  var M = window.Motion;
  if (!M || !M.animate || !M.inView) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;

  var EASE = [0.22, 1, 0.36, 1];
  var reveal = { opacity: [0, 1], transform: ["translateY(18px)", "translateY(0)"] };

  function q(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  var singles = q("main section:not(.hero) h2, main section:not(.hero) h3, .pimg, .map, .aside, .rev-cta, .lead, .offer, .contact > *, .reveal");
  var faqs = q("main details");
  var groupSel = [
    ".grid",      // service / product cards (.svc)
    ".revs",      // review cards (.rev)
    ".why",       // why-us list
    ".steps",     // how-it-works
    ".gallery",   // photos
    ".towns",     // service-area links
    ".brands",    // brand / car-make chips
    ".links",     // nearby-area links
    ".prose > ul, .prose > ol:not(.steps)"
  ];
  var groups = [];
  for (var g = 0; g < groupSel.length; g++) groups = groups.concat(q(groupSel[g]).filter(function (b) { return b.children.length && !b.closest(".hero"); }));
  var all = singles.concat(faqs);
  for (var a = 0; a < groups.length; a++) all = all.concat(Array.prototype.slice.call(groups[a].children));
  /* Which elements start below the fold? Asked through an IntersectionObserver (async, no forced layout)
     instead of getBoundingClientRect. Only those are hidden and revealed on scroll; anything on screen is left alone. */
  function done(el) { el.style.opacity = ""; el.style.transform = ""; }
  function run(el, delay, dur) {
    if (!el.__anim) return;
    el.__anim = false;
    M.animate(el, reveal, { duration: dur || 0.6, delay: delay || 0, easing: EASE }).finished.then(function () { done(el); });
  }
  function onView(el, cb) {
    M.inView(el, function () { cb(el); }, { margin: "0px 0px -10% 0px" });
  }
  all = all.filter(function (el, i) { return all.indexOf(el) === i; }); /* an element can match twice (e.g. an h3 inside a card) */
  var pending = all.length;
  var io = new IntersectionObserver(function (entries) {
    for (var e = 0; e < entries.length; e++) {
      var en = entries[e];
      io.unobserve(en.target);
      if (!en.isIntersecting && en.boundingClientRect.top > 0) { en.target.__anim = true; en.target.style.opacity = "0"; }
      if (--pending === 0) { io.disconnect(); wire(); }
    }
  });
  for (var o = 0; o < all.length; o++) io.observe(all[o]);
  if (!all.length) io.disconnect();

  function wire() {
    /* The hero and the sticky call bar are not animated: they are visible from the first paint (LCP / Speed Index). */
    for (var s = 0; s < singles.length; s++) if (singles[s].__anim) onView(singles[s], function (el) { run(el, 0, 0.55); });
    for (var f = 0; f < faqs.length; f++) if (faqs[f].__anim) onView(faqs[f], function (el) { run(el, 0, 0.45); });
    for (var c = 0; c < groups.length; c++) (function (box) {
      var kids = box.children;
      var any = false;
      for (var k = 0; k < kids.length; k++) if (kids[k].__anim) any = true;
      if (!any) return;
      onView(box, function () {
        var step = kids.length > 12 ? 0.03 : 0.08, n = 0;
        for (var k = 0; k < kids.length; k++) if (kids[k].__anim) run(kids[k], Math.min(n++ * step, 0.9), 0.5);
      });
    })(groups[c]);

  }

  /* 4. Micro-interactions: cards lift on hover, phone buttons pulse once in view */
  var cards = document.querySelectorAll(".svc, .rev, .gallery figure");
  for (var h = 0; h < cards.length; h++) (function (el) {
    el.addEventListener("mouseenter", function () { M.animate(el, { transform: "translateY(-4px)" }, { duration: 0.25, easing: EASE }); });
    el.addEventListener("mouseleave", function () { M.animate(el, { transform: "translateY(0)" }, { duration: 0.3, easing: EASE }); });
  })(cards[h]);

  var big = document.querySelectorAll("main section:not(.hero) .bignum");
  for (var b = 0; b < big.length; b++) onView(big[b], function (el) {
    M.animate(el, { transform: ["scale(1)", "scale(1.03)", "scale(1)"] }, { duration: 0.9, delay: 0.8, easing: "ease-in-out" });
  });
})();
