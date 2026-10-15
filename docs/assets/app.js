(function () {
  let currentLang = "ja";
  let dataset = null;

  const i18n = {
    ja: {
      title: "茨城県公立図書館データベース (Canonical Open Dataset)",
      subtitle: "全44市町村・全100拠点の一次資料照合・統計集計単位分離・エビデンス追跡システム",
      langBtn: "English",
      kpiMunicipalities: "対象自治体数",
      kpiMunicipalitiesNote: "茨城県全44市町村（AUDITED: 2 / IN_PROGRESS: 42）",
      kpiFacilities: "収録施設・拠点数",
      kpiFacilitiesNote: "検証完了: 20施設 / 一部未確認項目あり: 80施設",
      kpiFacilityCol: "単館統計蔵書数 (facility_level)",
      kpiFacilityColNote: "57施設の単館確定値合計（令和7年3月31日基準）",
      kpiSystemCol: "システム合算蔵書数 (system_aggregate)",
      kpiSystemColNote: "分館・分室を含む9市のシステム合算値（二重計上分離）",
      searchLabel: "キーワード検索（施設名・自治体・住所・ID）",
      searchPlaceholder: "例: 水戸、アルカス、IB-08201、公民館...",
      muniLabel: "自治体（全44市町村）",
      muniAll: "すべての自治体 (44)",
      catLabel: "施設区分 (Category)",
      catAll: "すべての区分",
      catA: "Cat A: 図書館法本則施設",
      catB: "Cat B: 法規指定分室・文庫",
      catC: "Cat C: 公民館図書室・窓口",
      scopeLabel: "統計集計単位",
      scopeAll: "すべての集計単位",
      scopeFacility: "単館統計 (facility_level)",
      scopeSystem: "システム合算 (system_aggregate)",
      scopeNA: "本館合算/単館未公表 (not_applicable)",
      verLabel: "検証状態 (Verification)",
      verAll: "すべての検証状態",
      verVerified: "全項目検証済 (verified)",
      verPartial: "一部未確認あり (partially_verified)",
      showingPrefix: "表示件数: ",
      showingSuffix: " 施設",
      thId: "永続ID",
      thMuni: "自治体",
      thName: "施設名称 / 区分",
      thLocation: "所在地・連絡先・開館年月",
      thBuilding: "延床面積 / 閲覧席数",
      thStats: "所蔵資料数（集計単位・年度）",
      thVerification: "検証状態・出典参照",
      legalMap: {
        central_library: "本館・中央館",
        branch_library: "分館・地区館",
        branch_room: "条例・規則分室",
        branch_collection: "規則設置文庫",
        community_center_library: "公民館・交流センター図書室",
        annex_facility: "敷地内別棟",
        service_point: "予約受取・配本窓口"
      },
      scopeMap: {
        facility_level: "単館統計",
        system_aggregate: "システム合算",
        not_applicable: "本館合算 / 単館未公表"
      },
      verMap: {
        verified: "検証済 (verified)",
        partially_verified: "一部未確認 (partially_verified)"
      },
      unverifiedPrefix: "未確認項目: ",
      refHeading: "References（参考文献・参照資料）",
      accessedLabel: "参照日: ",
      verifiedAtLabel: "検証日時: ",
      scopeDetailLabel: "確認範囲: ",
      backToTop: "↑ 一覧へ戻る"
    },
    en: {
      title: "Ibaraki Public Libraries Open Database (Canonical Dataset)",
      subtitle: "Primary Source Verified Dataset across All 44 Municipalities & 100 Library Service Points in Ibaraki",
      langBtn: "日本語",
      kpiMunicipalities: "Municipalities Covered",
      kpiMunicipalitiesNote: "All 44 Municipalities in Ibaraki (AUDITED: 2 / IN_PROGRESS: 42)",
      kpiFacilities: "Total Facilities & Service Points",
      kpiFacilitiesNote: "Fully Verified: 20 / Partially Verified: 80",
      kpiFacilityCol: "Facility-Level Collection Sum",
      kpiFacilityColNote: "Sum of 57 individual facility holdings (as of Mar 31, 2025)",
      kpiSystemCol: "System-Aggregate Collection Sum",
      kpiSystemColNote: "Sum of 9 municipal system-wide totals (separated to prevent double counting)",
      searchLabel: "Keyword Search (Name, Municipality, Address, ID)",
      searchPlaceholder: "e.g., Mito, Tsukuba, IB-08201...",
      muniLabel: "Municipality (All 44)",
      muniAll: "All Municipalities (44)",
      catLabel: "Facility Category",
      catAll: "All Categories",
      catA: "Cat A: Library Act Main/Branch",
      catB: "Cat B: Ordinance/Rule Annex/Bunko",
      catC: "Cat C: Community Center Reading Room",
      scopeLabel: "Statistical Scope",
      scopeAll: "All Scopes",
      scopeFacility: "Facility Level",
      scopeSystem: "System Aggregate",
      scopeNA: "Included in Main / Unreported",
      verLabel: "Verification Status",
      verAll: "All Statuses",
      verVerified: "Fully Verified (verified)",
      verPartial: "Partially Verified (partially_verified)",
      showingPrefix: "Showing: ",
      showingSuffix: " facilities",
      thId: "Facility ID",
      thMuni: "Municipality",
      thName: "Facility Name & Category",
      thLocation: "Address, Phone & Opened Date",
      thBuilding: "Floor Area / Seats",
      thStats: "Holdings (Scope & FY2024)",
      thVerification: "Verification & Citations",
      legalMap: {
        central_library: "Central / Main Library",
        branch_library: "Branch Library",
        branch_room: "Ordinance Branch Room",
        branch_collection: "Bunko Collection",
        community_center_library: "Community Center Library",
        annex_facility: "Annex Building",
        service_point: "Book Pickup Point"
      },
      scopeMap: {
        facility_level: "Facility Level",
        system_aggregate: "System Aggregate",
        not_applicable: "Included in System / N/A"
      },
      verMap: {
        verified: "Verified",
        partially_verified: "Partially Verified"
      },
      unverifiedPrefix: "Unverified fields: ",
      refHeading: "References (Primary Sources & Bibliographic Metadata)",
      accessedLabel: "Accessed: ",
      verifiedAtLabel: "Verified at: ",
      scopeDetailLabel: "Scope: ",
      backToTop: "↑ Back to table"
    }
  };

  function formatNumber(n) {
    if (n === null || n === undefined) return "—";
    return Number(n).toLocaleString();
  }

  function populateMunicipalitySelect() {
    const sel = document.getElementById("filter-muni");
    const currentVal = sel.value;
    const t = i18n[currentLang];
    sel.innerHTML = `<option value="">${t.muniAll}</option>`;
    if (!dataset) return;
    dataset.municipalities.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.municipality_code;
      const label = currentLang === "ja" ? m.municipality_name : (m.municipality_name_en || m.municipality_name);
      opt.textContent = `${m.municipality_code} ${label} (${m.facilities.length})`;
      sel.appendChild(opt);
    });
    sel.value = currentVal;
  }

  function applyStaticLabels() {
    const t = i18n[currentLang];
    document.getElementById("app-title").textContent = t.title;
    document.getElementById("app-subtitle").textContent = t.subtitle;
    document.getElementById("lang-toggle").textContent = t.langBtn;

    document.getElementById("kpi-muni-label").textContent = t.kpiMunicipalities;
    document.getElementById("kpi-muni-note").textContent = t.kpiMunicipalitiesNote;
    document.getElementById("kpi-fac-label").textContent = t.kpiFacilities;
    document.getElementById("kpi-fac-note").textContent = t.kpiFacilitiesNote;
    document.getElementById("kpi-fcol-label").textContent = t.kpiFacilityCol;
    document.getElementById("kpi-fcol-note").textContent = t.kpiFacilityColNote;
    document.getElementById("kpi-scol-label").textContent = t.kpiSystemCol;
    document.getElementById("kpi-scol-note").textContent = t.kpiSystemColNote;

    document.getElementById("lbl-search").textContent = t.searchLabel;
    document.getElementById("filter-search").placeholder = t.searchPlaceholder;
    document.getElementById("lbl-muni").textContent = t.muniLabel;
    document.getElementById("lbl-cat").textContent = t.catLabel;
    document.getElementById("lbl-scope").textContent = t.scopeLabel;
    document.getElementById("lbl-ver").textContent = t.verLabel;

    const catSel = document.getElementById("filter-cat");
    const catVal = catSel.value;
    catSel.innerHTML = `
      <option value="">${t.catAll}</option>
      <option value="Cat A">${t.catA}</option>
      <option value="Cat B">${t.catB}</option>
      <option value="Cat C">${t.catC}</option>
    `;
    catSel.value = catVal;

    const scopeSel = document.getElementById("filter-scope");
    const scopeVal = scopeSel.value;
    scopeSel.innerHTML = `
      <option value="">${t.scopeAll}</option>
      <option value="facility_level">${t.scopeFacility}</option>
      <option value="system_aggregate">${t.scopeSystem}</option>
      <option value="not_applicable">${t.scopeNA}</option>
    `;
    scopeSel.value = scopeVal;

    const verSel = document.getElementById("filter-ver");
    const verVal = verSel.value;
    verSel.innerHTML = `
      <option value="">${t.verAll}</option>
      <option value="verified">${t.verVerified}</option>
      <option value="partially_verified">${t.verPartial}</option>
    `;
    verSel.value = verVal;

    document.getElementById("th-id").textContent = t.thId;
    document.getElementById("th-muni").textContent = t.thMuni;
    document.getElementById("th-name").textContent = t.thName;
    document.getElementById("th-loc").textContent = t.thLocation;
    document.getElementById("th-bldg").textContent = t.thBuilding;
    document.getElementById("th-stats").textContent = t.thStats;
    document.getElementById("th-ver").textContent = t.thVerification;
    document.getElementById("ref-heading").textContent = t.refHeading;

    populateMunicipalitySelect();
  }

  function renderTable() {
    if (!dataset) return;
    const t = i18n[currentLang];
    const q = (document.getElementById("filter-search").value || "").trim().toLowerCase();
    const muni = document.getElementById("filter-muni").value;
    const cat = document.getElementById("filter-cat").value;
    const scope = document.getElementById("filter-scope").value;
    const ver = document.getElementById("filter-ver").value;

    const filtered = dataset.facilities.filter((f) => {
      if (muni && f.municipality_code !== muni) return false;
      if (cat && f.category !== cat) return false;
      if (scope && f.statistics_scope !== scope) return false;
      if (ver && f.verification_status !== ver) return false;
      if (q) {
        const hay = [
          f.facility_id, f.municipality_code, f.municipality_name, f.municipality_name_en,
          f.name, f.name_en, f.address, f.phone
        ].join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    document.getElementById("result-count").textContent = `${t.showingPrefix}${filtered.length} / ${dataset.facilities.length}${t.showingSuffix}`;

    const tbody = document.getElementById("facilities-tbody");
    tbody.innerHTML = "";

    filtered.forEach((f) => {
      const tr = document.createElement("tr");
      tr.id = `row-${f.facility_id}`;

      const muniName = currentLang === "ja" ? f.municipality_name : (f.municipality_name_en || f.municipality_name);
      const facName = currentLang === "ja" ? f.name : (f.name_en || f.name);
      const catBadgeClass = f.category === "Cat A" ? "badge-cat-a" : (f.category === "Cat B" ? "badge-cat-b" : "badge-cat-c");
      const legalLabel = t.legalMap[f.legal_status] || f.legal_status;

      const areaStr = f.floor_area_m2 !== null && f.floor_area_m2 !== undefined ? `${formatNumber(f.floor_area_m2)} ㎡` : "null (未確認)";
      const seatsStr = f.reading_seats !== null && f.reading_seats !== undefined ? `${formatNumber(f.reading_seats)} 席` : "null (未確認)";

      const colStr = f.collection_count !== null && f.collection_count !== undefined
        ? `<strong>${formatNumber(f.collection_count)}</strong> 冊/点`
        : "null (未確認)";
      const loansStr = f.annual_loans !== null && f.annual_loans !== undefined
        ? `<div style="font-size:0.78rem;color:#475569;">貸出: ${formatNumber(f.annual_loans)} 点</div>`
        : "";
      const scopeLabel = t.scopeMap[f.statistics_scope] || f.statistics_scope;

      let discrepancyHtml = "";
      if (f.breakdown && f.breakdown.discrepancy_note) {
        discrepancyHtml = `<div class="discrepancy-box">⚠️ ${f.breakdown.discrepancy_note}</div>`;
      }

      const verBadgeClass = f.verification_status === "verified" ? "badge-verified" : "badge-partial";
      const verLabel = t.verMap[f.verification_status] || f.verification_status;

      const refsHtml = (f.ref_numbers || []).map((num) => {
        return `<a href="#ref-${num}" class="ref-link" data-ref="${num}">[${num}]</a>`;
      }).join("");

      const unvHtml = (f.unverified_fields && f.unverified_fields.length > 0)
        ? `<div class="unverified-note">${t.unverifiedPrefix}${f.unverified_fields.join(", ")}</div>`
        : "";

      tr.innerHTML = `
        <td><code>${f.facility_id}</code></td>
        <td><strong>${muniName}</strong><br><span style="font-size:0.75rem;color:#64748b;">JIS: ${f.municipality_code}</span></td>
        <td>
          <div style="font-weight:700;margin-bottom:0.25rem;">${facName}</div>
          <span class="badge ${catBadgeClass}">${f.category}</span>
          <span style="font-size:0.78rem;color:#475569;margin-left:0.25rem;">${legalLabel}</span>
        </td>
        <td>
          <div>${f.postal_code ? "〒" + f.postal_code + " " : ""}${f.address || "—"}</div>
          <div style="font-size:0.78rem;color:#475569;">TEL: ${f.phone || "—"} / 開館: ${f.opened_year_month || "null"}</div>
        </td>
        <td>
          <div>面積: ${areaStr}</div>
          <div style="font-size:0.78rem;color:#475569;">席数: ${seatsStr}</div>
        </td>
        <td>
          <div>${colStr}</div>
          ${loansStr}
          <div style="margin-top:0.25rem;"><span class="badge badge-scope">${scopeLabel}</span></div>
          ${discrepancyHtml}
        </td>
        <td>
          <div><span class="badge ${verBadgeClass}">${verLabel}</span></div>
          <div style="margin-top:0.3rem;">出典: ${refsHtml}</div>
          ${unvHtml}
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  function renderReferences() {
    if (!dataset) return;
    const t = i18n[currentLang];
    const ul = document.getElementById("references-list");
    ul.innerHTML = "";

    dataset.sources.forEach((s) => {
      const li = document.createElement("li");
      li.className = "ref-item";
      li.id = `ref-${s.ref_number}`;
      li.innerHTML = `
        <strong>[${s.ref_number}] (${s.source_id})</strong>
        ${s.creator ? s.creator + " " : ""}『${s.title_ja}』
        ${s.publication_date ? "(" + s.publication_date + ") " : ""}
        — <a href="${s.url}" target="_blank" rel="noopener noreferrer">${s.url}</a>
        <div style="font-size:0.78rem;color:#475569;margin-top:0.2rem;">
          ${t.accessedLabel}${s.accessed_date || "—"} |
          ${t.verifiedAtLabel}${s.verification.verified_at || "—"} |
          ${t.scopeDetailLabel}${s.verification.scope || "—"}
          <a href="#top" style="margin-left:0.5rem;color:#1d4ed8;text-decoration:none;">${t.backToTop}</a>
        </div>
      `;
      ul.appendChild(li);
    });
  }

  function initEvents() {
    document.getElementById("lang-toggle").addEventListener("click", () => {
      currentLang = currentLang === "ja" ? "en" : "ja";
      document.documentElement.lang = currentLang;
      applyStaticLabels();
      renderTable();
      renderReferences();
    });

    ["filter-search", "filter-muni", "filter-cat", "filter-scope", "filter-ver"].forEach((id) => {
      const el = document.getElementById(id);
      el.addEventListener("input", renderTable);
      el.addEventListener("change", renderTable);
    });
  }

  async function boot() {
    initEvents();
    try {
      const res = await fetch("./data/libraries.json");
      dataset = await res.json();
      document.getElementById("kpi-muni-val").textContent = formatNumber(dataset.metadata.total_municipalities);
      document.getElementById("kpi-fac-val").textContent = formatNumber(dataset.metadata.total_facilities);
      document.getElementById("kpi-fcol-val").textContent = formatNumber(dataset.metadata.facility_level_collection_sum);
      document.getElementById("kpi-scol-val").textContent = formatNumber(dataset.metadata.system_aggregate_collection_sum);
      applyStaticLabels();
      renderTable();
      renderReferences();
    } catch (err) {
      console.error("Failed to load dataset:", err);
    }
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
