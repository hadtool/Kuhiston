(() => {
  "use strict";

  if (!window.maptilersdk) {
    console.error("MapTiler SDK не загружен");
    return;
  }

  const page = document.getElementById("map-page");
  const mapEl = document.getElementById("map");
  if (!page || !mapEl) return;

  const apiKey = page.dataset.maptilerKey || "";
  const I18N = parseStrings();
  const formatter = new Intl.NumberFormat(document.documentElement.lang || "ru", { maximumFractionDigits: 1 });

  const state = {
    map: null,
    userPoint: null,   // [lng, lat] выбранный/определённый
    userMarker: null,
    category: "",      // код категории фильтра
    placesSource: null,
    placeMarkers: [],
    is3d: false,
  };

  if (!apiKey) {
    // Ключ не настроен — карта не подключается, показываем заметку (в шаблоне).
    console.warn("MAPTILER_API_KEY не задан — карта не инициализирована");
    return;
  }

  /* ---------- инициализация карты (Этап 2, задача 1) ---------- */
  const map = new maptilersdk.Map({
    container: "map",
    style: maptilersdk.MapStyle.STREETS, // живой стиль, не жёлтая OSM
    center: [68.62, 38.55],              // Таджикистан
    zoom: 5.6,
    minZoom: 4,
    maxZoom: 18,
    apiKey,
  });
  state.map = map;

  map.addControl(new maptilersdk.NavigationControl({ showCompass: true }), "top-left");

  map.on("load", () => {
    loadPlaces();
  });

  /* ---------- геолокация и ручной выбор точки (задача 2) ---------- */
  const locateBtn = document.getElementById("btn-locate");
  const hintEl = document.getElementById("user-marker-hint");

  function setUserPoint(lngLat) {
    state.userPoint = [lngLat.lng, lngLat.lat];
    if (state.userMarker) state.userMarker.remove();
    state.userMarker = new maptilersdk.Marker({ color: "#1a2740" })
      .setLngLat(state.userPoint)
      .addTo(map);
    hintEl.hidden = false;
    loadPlaces();
  }

  function clearUserPoint() {
    state.userPoint = null;
    if (state.userMarker) {
      state.userMarker.remove();
      state.userMarker = null;
    }
    hintEl.hidden = true;
    loadPlaces();
  }

  locateBtn.addEventListener("click", () => {
    if (!navigator.geolocation) return;
    locateBtn.classList.add("active");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        locateBtn.classList.remove("active");
        setUserPoint({ lng: pos.coords.longitude, lat: pos.coords.latitude });
        map.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 11 });
      },
      () => {
        locateBtn.classList.remove("active");
        console.warn("Геолокация недоступна");
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  });

  // клик по карте = ручной выбор точки (повторный клик — убрать точку)
  map.on("click", (e) => {
    if (state.userPoint && state.userMarker) {
      clearUserPoint();
    } else {
      setUserPoint(e.lngLat);
    }
  });

  /* ---------- фильтр по категориям ---------- */
  document.querySelectorAll("#category-bar .chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll("#category-bar .chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      state.category = chip.dataset.code || "";
      loadPlaces();
    });
  });

  /* ---------- получение мест (задача 3) ---------- */
  async function loadPlaces() {
    try {
      const url = new URL("/api/places/", window.location.origin);
      if (state.userPoint) {
        url.searchParams.set("lat", state.userPoint[1]);
        url.searchParams.set("lng", state.userPoint[0]);
      }
      if (state.category) url.searchParams.set("category", state.category);

      const resp = await fetch(url, { headers: { Accept: "application/json" } });
      if (!resp.ok) throw new Error(resp.status);
      const data = await resp.json();

      renderMarkers(data.places || []);
    } catch (err) {
      console.error("loadPlaces:", err);
    }
  }

  function renderMarkers(places) {
    state.placeMarkers.forEach((m) => m.remove());
    state.placeMarkers = [];

    places.forEach((p) => {
      const el = document.createElement("button");
      el.className = "place-dot";
      el.textContent = "◈";
      el.title = p.name;

      const marker = new maptilersdk.Marker({ element: el })
        .setLngLat([p.lng, p.lat])
        .addTo(map);
      marker.getElement().addEventListener("click", () => openPlaceCard(p.id));
      state.placeMarkers.push(marker);
    });
  }

  /* ---------- карточка места (задача 4) ---------- */
  async function openPlaceCard(id) {
    try {
      const resp = await fetch(`/api/places/${id}/`, { headers: { Accept: "application/json" } });
      if (!resp.ok) throw new Error(resp.status);
      const p = await resp.json();
      renderPlaceCard(p);
    } catch (err) {
      console.error("openPlaceCard:", err);
    }
  }

  function renderPlaceCard(p) {
    const card = document.getElementById("place-card");
    if (!card) return;

    const translateMeta = {
      difficulty: I18N.difficulty,
      hours: I18N.hours,
      fee: I18N.fee,
      seasons: I18N.seasons,
      region: I18N.region,
    };
    const rows = [
      p.region && { label: translateMeta.region, value: p.region },
      p.opening_hours && { label: translateMeta.hours, value: p.opening_hours },
      p.entrance_fee !== null && { label: translateMeta.fee, value: `${p.entrance_fee} ` + I18N.currency },
      p.access_difficulty && { label: translateMeta.difficulty, value: p.access_difficulty },
      p.recommended_seasons.length && { label: translateMeta.seasons, value: p.recommended_seasons.join(", ") },
    ].filter(Boolean);

    const photos = (p.photos || [])
      .map((ph) => `<img src="${ph.url}" alt="${escapeHtml(ph.caption || "")}" loading="lazy">`)
      .join("");

    card.innerHTML = `
      <button class="place-card__close" id="card-close">${I18N.close}</button>
      <h3 class="place-card__name">${escapeHtml(p.name)}</h3>
      <div class="place-card__meta">
        <span class="place-card__rating">★ ${formatRating(p.rating)}</span>
        ${p.category ? ` · ${escapeHtml(p.category)}` : ""}
        ${p.distance_km != null ? ` · ${formatter.format(p.distance_km)} km` : ""}
      </div>
      ${p.photos && p.photos.length ? `<div class="place-card__photos">${photos}</div>` : ""}
      <p class="place-card__desc">${escapeHtml(p.description || "")}</p>
      <dl class="place-card__grid">
        ${rows.map((r) => `<dt>${escapeHtml(r.label)}</dt><dd>${escapeHtml(String(r.value))}</dd>`).join("")}
      </dl>`;
    card.hidden = false;

    document.getElementById("card-close").addEventListener("click", () => {
      card.hidden = true;
    });
  }

  /* ---------- 3D-рельеф (задача 5) ---------- */
  const btn3d = document.getElementById("btn-3d");
  btn3d.addEventListener("click", () => {
    state.is3d = !state.is3d;
    btn3d.classList.toggle("active", state.is3d);
    if (state.is3d) {
      map.setTerrain({ exaggeration: 1.2 });
      map.easeTo({ pitch: 60, zoom: Math.max(map.getZoom(), 10.5) });
    } else {
      map.setTerrain(null);
      map.easeTo({ pitch: 0 });
    }
  });

  /* ---------- вспомогательное ---------- */
  function parseStrings() {
    const node = document.getElementById("i18n-strings");
    try {
      return node ? JSON.parse(node.textContent) : {};
    } catch {
      return {};
    }
  }

  function formatRating(r) {
    if (r == null) return "–";
    return formatter.format(r);
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
})();