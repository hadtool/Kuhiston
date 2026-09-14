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

      renderMarkers(data || []);
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
      </dl>
      <button class="place-card__nav" id="card-nav">${I18N.nav_btn}</button>`;
    card.hidden = false;

    document.getElementById("card-close").addEventListener("click", () => {
      card.hidden = true;
    });
    document.getElementById("card-nav").addEventListener("click", () => {
      loadNavigation(p.lat, p.lng);
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

  /* ---------- простые маршруты (Этап 3, задача 1) ---------- */
  const btnRoute = document.getElementById("btn-route");
  const routePanel = document.getElementById("route-panel");
  const routeList = document.getElementById("route-list");
  const routeTotal = document.getElementById("route-total");
  let routeSourceId = null;

  async function loadSimpleRoute() {
    try {
      const origin = state.userPoint || map.getCenter();
      const url = new URL("/api/route/simple/", window.location.origin);
      url.searchParams.set("lat", origin.lat);
      url.searchParams.set("lng", origin.lng);
      url.searchParams.set("limit", "5");

      const resp = await fetch(url, { headers: { Accept: "application/json" } });
      if (!resp.ok) throw new Error(resp.status);
      const data = await resp.json();
      renderRoute(data);
    } catch (err) {
      console.error("loadSimpleRoute:", err);
    }
  }

  function renderRoute(data) {
    if (routeSourceId) {
      map.removeLayer(routeSourceId);
      map.removeSource(routeSourceId);
      routeSourceId = null;
    }
    routePanel.hidden = true;
    routeList.innerHTML = "";

    const pts = data.points || [];
    if (!pts.length) {
      routeTotal.textContent = I18N.route_empty;
      routeTotal.hidden = false;
      routePanel.hidden = false;
      return;
    }

    const coords = [[data.start.lng, data.start.lat], ...pts.map((p) => [p.lng, p.lat])];
    routeSourceId = "route-line";
    map.addSource(routeSourceId, {
      type: "geojson",
      data: { type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: coords } },
    });
    map.addLayer({
      id: routeSourceId,
      type: "line",
      source: routeSourceId,
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": "#1a2740", "line-width": 3, "line-dasharray": [1, 0.75] },
    });

    pts.forEach((p, i) => {
      const li = document.createElement("li");
      li.className = "route-list__item";
      li.innerHTML = `
        <span class="route-list__num">${i + 1}</span>
        <span class="route-list__name">${escapeHtml(p.name)}</span>
        <span class="route-list__dist">${formatter.format(p.distance_from_start_km)} ${I18N.km}</span>`;
      li.addEventListener("click", () => openPlaceCard(p.id));
      routeList.appendChild(li);
    });

    routeTotal.textContent = `${I18N.route_total}: ${formatter.format(data.total_km)} ${I18N.km} · ${I18N.route_hint}`;
    routeTotal.hidden = false;
    routePanel.hidden = false;
  }

  btnRoute.addEventListener("click", () => {
    if (!routePanel.hidden && routeSourceId) {
      routePanel.hidden = true;
      if (routeSourceId) {
        map.removeLayer(routeSourceId);
        map.removeSource(routeSourceId);
        routeSourceId = null;
      }
      return;
    }
    loadSimpleRoute();
  });

  document.getElementById("route-close").addEventListener("click", () => {
    routePanel.hidden = true;
    if (routeSourceId) {
      map.removeLayer(routeSourceId);
      map.removeSource(routeSourceId);
      routeSourceId = null;
    }
  });

  /* ---------- готовые многодневные маршруты (Этап 3, задача 2) ---------- */
  const btnRoutes = document.getElementById("btn-routes");
  const routesPanel = document.getElementById("routes-panel");
  const routesList = document.getElementById("routes-list");
  const routesDetail = document.getElementById("routes-detail");
  let multidayLineId = null;

  function drawMultidayLine(coords) {
    if (multidayLineId) {
      map.removeLayer(multidayLineId);
      map.removeSource(multidayLineId);
      multidayLineId = null;
    }
    if (!coords.length) return;
    multidayLineId = "multiday-line";
    map.addSource(multidayLineId, {
      type: "geojson",
      data: { type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: coords } },
    });
    map.addLayer({
      id: multidayLineId,
      type: "line",
      source: multidayLineId,
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": "#c98a2c", "line-width": 4 },
    });
  }

  async function loadMultiRoutes() {
    try {
      const resp = await fetch("/api/routes/", { headers: { Accept: "application/json" } });
      if (!resp.ok) throw new Error(resp.status);
      const routes = await resp.json();
      routesList.innerHTML = "";
      if (!routes.length) {
        routesList.innerHTML = `<li class="route-list__item">${I18N.route_empty}</li>`;
      }
      routes.forEach((r) => {
        const li = document.createElement("li");
        li.className = "route-list__item";
        li.innerHTML = `
          <span class="route-list__name">${escapeHtml(r.name)}</span>
          <span class="route-list__dist">${r.duration_days} ${I18N.days} · ${r.stops_count} ${I18N.points_noun}</span>`;
        li.addEventListener("click", () => openMultiRoute(r.id));
        routesList.appendChild(li);
      });
      routesDetail.hidden = true;
      routesPanel.hidden = false;
    } catch (err) {
      console.error("loadMultiRoutes:", err);
    }
  }

  async function openMultiRoute(id) {
    try {
      const resp = await fetch(`/api/routes/${id}/`, { headers: { Accept: "application/json" } });
      if (!resp.ok) throw new Error(resp.status);
      const r = await resp.json();
      renderMultiRoute(r);
    } catch (err) {
      console.error("openMultiRoute:", err);
    }
  }

  function renderMultiRoute(r) {
    const coords = [];
    r.days.forEach((d) => d.stops.forEach((s) => coords.push([s.lng, s.lat])));
    drawMultidayLine(coords);

    const daysHtml = r.days
      .map(
        (d) => `
        <li class="multiday-day">
          <h4>${I18N.day_label} ${d.day}</h4>
          <ol class="route-list">
            ${d.stops
              .map(
                (s) => `
                <li class="route-list__item" data-place="${s.place_id}">
                  <span class="route-list__num">${s.order + 1}</span>
                  <span class="route-list__name">${escapeHtml(s.place_name)}</span>
                  <span class="route-list__dist">${s.minutes ? `${formatter.format(s.minutes)} ${I18N.min}` : ""}</span>
                </li>`,
              )
              .join("")}
          </ol>
        </li>`,
      )
      .join("");

    routesDetail.innerHTML = `
      <h4 class="multiday-title">${escapeHtml(r.name)}</h4>
      <p class="multiday-region">${escapeHtml(r.region || "")} · ${r.duration_days} ${I18N.days}</p>
      <ul class="multiday-list">${daysHtml}</ul>`;
    routesDetail.hidden = false;
    routesPanel.hidden = false;

    routesDetail.querySelectorAll("[data-place]").forEach((el) => {
      el.addEventListener("click", () => openPlaceCard(el.dataset.place));
    });
  }

  btnRoutes.addEventListener("click", () => {
    if (!routesPanel.hidden) {
      routesPanel.hidden = true;
      drawMultidayLine([]);
      return;
    }
    loadMultiRoutes();
  });

  document.getElementById("routes-close").addEventListener("click", () => {
    routesPanel.hidden = true;
    drawMultidayLine([]);
  });

  /* ---------- навигация по дорогам/тропам через OSRM (Этап 3, задача 3) ---------- */
  const navPanel = document.getElementById("nav-panel");
  const navInfo = document.getElementById("nav-info");
  let navSourceId = null;

  function drawNavLine(coords) {
    if (navSourceId) {
      map.removeLayer(navSourceId);
      map.removeSource(navSourceId);
      navSourceId = null;
    }
    if (!coords.length) return;
    navSourceId = "nav-line";
    map.addSource(navSourceId, {
      type: "geojson",
      data: { type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: coords } },
    });
    map.addLayer({
      id: navSourceId,
      type: "line",
      source: navSourceId,
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": "#24365a", "line-width": 4 },
    });
  }

  async function loadNavigation(endLat, endLng) {
    const origin = state.userPoint || map.getCenter();
    try {
      const url = new URL("/api/route/navigation/", window.location.origin);
      url.searchParams.set("start", `${origin.lat},${origin.lng}`);
      url.searchParams.set("end", `${endLat},${endLng}`);
      url.searchParams.set("profile", "driving");
      const resp = await fetch(url, { headers: { Accept: "application/json" } });
      if (!resp.ok) throw new Error(resp.status);
      const data = await resp.json();
      drawNavLine(data.geometry.coordinates);
      const fallbackNote = data.source === "fallback" ? ` (${I18N.nav_fallback})` : "";
      navInfo.innerHTML = `
        <p><strong>${formatter.format(data.distance_km)} ${I18N.km}</strong> · ${formatter.format(data.duration_min)} ${I18N.min}${escapeHtml(fallbackNote)}</p>`;
      navPanel.hidden = false;
    } catch (err) {
      console.error("loadNavigation:", err);
    }
  }

  document.getElementById("nav-close").addEventListener("click", () => {
    navPanel.hidden = true;
    drawNavLine([]);
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