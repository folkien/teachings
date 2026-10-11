import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, Presentation, PresentationFile } from "@oai/artifact-tool";

const issueDir = "/home/spasz/python/teachings/issue_kurs_kamch_lubecko";
const assetsDir = path.join(issueDir, "infografiki", "assets");
const renderDir = path.join(issueDir, "infografiki", "pelna_render");
const buildDir = path.join(issueDir, "infografiki", ".build");
const outputDir = path.join(issueDir, "output_v2");
const sourcePdf = path.join(issueDir, "Dyrektorium KAMCH 2.5.2017.pdf");
const finalPptx = path.join(outputDir, "KAMCh_infografiki_pelna.pptx");
const skillDir = "/home/spasz/.codex/plugins/cache/openai-primary-runtime/presentations/26.1009.11318/skills/presentations";
const runtimePython = "/home/spasz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";

const W = 1280;
const H = 720;
const FONT = "Liberation Sans";
const C = {
  cream: "#F7F0DF",
  navy: "#173A4E",
  teal: "#527A72",
  terracotta: "#BF5D3C",
  mustard: "#D9A63B",
  white: "#FFFDF7",
};

async function imageBytes(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function rect(slide, x, y, w, h, fill, radius = false, line = "none") {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 2 },
    ...(radius ? { borderRadius: "rounded-lg" } : {}),
  });
}

function textBox(slide, text, x, y, w, h, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: options.fontSize ?? 22,
    bold: options.bold ?? false,
    color: options.color ?? C.navy,
  };
  return shape;
}

function callout(slide, label, title, description, x, y, w, h, accent) {
  rect(slide, x, y, w, h, "rgba(247,240,223,0.96)", true, accent);
  rect(slide, x, y, 11, h, accent, true);
  textBox(slide, label.toUpperCase(), x + 26, y + 11, w - 42, 18, { fontSize: 12, bold: true, color: accent });
  textBox(slide, title, x + 26, y + 31, w - 42, 28, { fontSize: 18, bold: true, color: C.navy });
  textBox(slide, description, x + 26, y + 61, w - 42, h - 69, { fontSize: 13, color: C.navy });
}

function topicPoint(slide, number, body, y) {
  textBox(slide, String(number), 76, y, 24, 24, { fontSize: 15, bold: true, color: C.terracotta });
  textBox(slide, body, 105, y, 550, 30, { fontSize: 16, bold: true, color: C.navy });
}

function titleBlock(slide, eyebrow, title, goal, points) {
  const titleSize = title.length > 28 ? 34 : 38;
  rect(slide, 42, 34, 660, 318, "rgba(247,240,223,0.95)", true);
  textBox(slide, eyebrow.toUpperCase(), 72, 54, 360, 22, { fontSize: 14, bold: true, color: C.terracotta });
  textBox(slide, title, 72, 82, 592, 80, { fontSize: titleSize, bold: true, color: C.navy });
  textBox(slide, `CEL  ${goal}`, 72, 166, 592, 24, { fontSize: 14, bold: true, color: C.teal });
  rect(slide, 72, 196, 562, 2, C.mustard);
  textBox(slide, "NAJWAŻNIEJSZE PUNKTY", 72, 206, 260, 20, { fontSize: 12, bold: true, color: C.terracotta });
  topicPoint(slide, 1, points[0], 230);
  topicPoint(slide, 2, points[1], 266);
  topicPoint(slide, 3, points[2], 302);
}

function propsLine(slide, props) {
  rect(slide, 42, 643, 1196, 31, "rgba(23,58,78,0.88)", true);
  textBox(slide, `REKWIZYTY  ${props}`, 60, 651, 1158, 18, { fontSize: 12, bold: true, color: C.white });
}

async function background(slide, filePath, alt) {
  slide.images.add({
    blob: await imageBytes(filePath),
    contentType: "image/png",
    alt,
    fit: "cover",
    position: { left: 0, top: 0, width: W, height: H },
  });
}

function footer(slide, pages, index) {
  rect(slide, 42, 681, 1196, 1, "rgba(255,253,247,0.55)");
  textBox(slide, `Dyrektorium KAMCh 2017, ${pages}`, 50, 688, 360, 18, { fontSize: 12, color: C.white });
  textBox(slide, String(index).padStart(2, "0"), 1190, 686, 42, 18, { fontSize: 13, bold: true, color: C.white });
}

async function build() {
  await fs.mkdir(buildDir, { recursive: true });
  await fs.mkdir(renderDir, { recursive: true });
  await fs.mkdir(outputDir, { recursive: true });

  const pres = Presentation.create({ slideSize: { width: W, height: H } });

  const topicSlides = [
    {
      eyebrow: "Wprowadzenie",
      title: "Szukaj obecności Boga",
      goal: "Zachęcić do pełnego wejścia w kurs.",
      points: [
        "Animacja modlitwy oznacza ożywianie relacji z Bogiem.",
        "Bóg zaprasza do szukania Go całym sercem także w trudnym czasie.",
        "Modlitwa przypomina wejście na górę spotkania z Bogiem.",
      ],
      art: "wprowadzenie.png",
      alt: "Infografika uczestników podejmujących wejście na górę spotkania z Bogiem",
      pages: "s. 2-5",
      callouts: [
        ["Zabieg", "Pieśń „Kto wstąpi na górę Pana”", "Uczestnicy słuchają pieśni, która budzi pragnienie szukania obecności Boga i wejścia na górę spotkania.", 42, 365, 520, 125, C.terracotta],
        ["Dynamika", "Wejście na górę", "Każdy zapisuje swoje imię i umieszcza je na plakacie góry jako znak osobistej decyzji wejścia w kurs.", 805, 475, 425, 132, C.teal],
      ],
      props: "nagranie pieśni, plakat góry, karteczki samoprzylepne, długopisy",
    },
    {
      eyebrow: "Temat 1",
      title: "Sekret Piotra i Jana",
      goal: "Połączyć modlitwę osobistą z misją.",
      points: [
        "Modlitwa i ewangelizacja tworzą jeden rytm.",
        "Modlitwa osobista karmi życie z Bogiem i napełnia Duchem.",
        "Kerygmat i świadectwo prowadzą innych do Jezusa.",
      ],
      art: "temat-1-sekret-piotra-i-jana.png",
      alt: "Infografika modlitwy, Słowa, chleba i ewangelizacji",
      pages: "s. 6-11",
      callouts: [
        ["Zabieg", "Karmienie chlebem I i II", "Najpierw prowadzący spożywa chleb jako obraz codziennego karmienia się Chrystusem. Potem rozdaje go uczestnikom jako obraz ewangelizacji.", 730, 245, 500, 128, C.terracotta],
        ["Dynamika", "Modlitwa osobista schematem", "Uczestnicy modlą się indywidualnie przez 15 minut według poznanego schematu. Po powrocie krótko dzielą się doświadczeniem.", 805, 486, 425, 132, C.teal],
      ],
      props: "koszyk, chleb dla uczestników, schemat modlitwy osobistej",
    },
    {
      eyebrow: "Temat 2",
      title: "Prowadzenie modlitwy osobistej",
      goal: "Dać praktyczne wskazówki do owocnej modlitwy.",
      points: [
        "Bóg na modlitwie nie przychodzi z pustymi rękami.",
        "Spotkanie wymaga decyzji, wytrwałości i słuchania.",
        "Rozeznanie łączy Słowo, naukę Kościoła, natchnienia i rozsądek.",
      ],
      art: "temat-2-modlitwa-osobista.png",
      alt: "Infografika termometru, obmycia wodą, daru i modlitwy osobistej",
      pages: "s. 12-16",
      callouts: [
        ["Zabiegi", "Termometr i „Zostałeś obmyty”", "Termometr oddziela uczucia od prawdy. Prowadzący brudzi rękę i obmywa ją wodą, pokazując, że grzech nie zamyka drogi do Boga.", 42, 365, 560, 125, C.terracotta],
        ["Dynamika", "Spotkanie z Ukochanym", "Uczestnik przeznacza 10 minut na modlitwę, 10 minut na słuchanie i 10 minut na rozeznanie tego, co mówi Bóg.", 810, 474, 420, 132, C.teal],
      ],
      props: "tradycyjny termometr, materiał brudzący rękę, przezroczysty dzbanek, woda",
    },
    {
      eyebrow: "Temat 3",
      title: "Pięćdziesiątnica",
      goal: "Ukazać zanurzenie w Duchu jako cel modlitwy.",
      points: [
        "Duch Święty prowadzi do spotkania z Bogiem.",
        "Duch chce prowadzić wszystkie dziedziny życia.",
        "Pełna zależność od Ducha przynosi przemianę i owoc.",
      ],
      art: "temat-3-piecdziesiatnica.png",
      alt: "Infografika GPS, papierowych łódek, wody i zanurzenia w Duchu Świętym",
      pages: "s. 17-20",
      callouts: [
        ["Zabieg dydaktyczny", "GPS: Duch nadaje kierunek", "Prowadzący trzyma GPS i pokazuje, że Duch Święty prowadzi w modlitwie, decyzjach i codziennym życiu.", 42, 355, 430, 118, C.terracotta],
        ["Dynamika", "„Pływanie na płytkiej wodzie”", "Uczestnicy zapisują pragnienia, składają łódki, słuchają Ez 47, zanurzają łódki w wodzie i modlą się o zanurzenie w Duchu.", 805, 466, 425, 142, C.teal],
      ],
      props: "kartki A4 lub A5, długopisy, dziecięcy basen z wodą, samochodowy GPS",
    },
    {
      eyebrow: "Temat 4",
      title: "Uwielbienie",
      goal: "Dać doświadczenie uwielbienia.",
      points: [
        "Uwielbienie skupia całą modlitwę na Bogu.",
        "Nie zależy od sytuacji ani od aktualnych uczuć.",
        "Różne formy uwielbienia prowadzą do stylu życia.",
      ],
      art: "temat-4-uwielbienie.png",
      alt: "Infografika kwiatu, Ogrodnika i wspólnoty uwielbiającej Boga",
      pages: "s. 21-24",
      callouts: [
        ["Zabieg", "Kwiatek zwrócony ku Ogrodnikowi", "Kwiat pokazuje człowieka skupionego na Bogu. Ziemia oznacza pewność Jego wierności, a podlewanie i przycinanie obrazują wzrost oraz przemianę.", 42, 360, 545, 130, C.terracotta],
        ["Dynamika", "Uwielbienie w praktyce", "Wspólnota przez 15 minut uwielbia śpiewem, a następnie przez 15 minut modli się chóralnie własnymi słowami.", 815, 475, 415, 132, C.teal],
      ],
      props: "kwitnący kwiatek w doniczce, nożyczki",
    },
    {
      eyebrow: "Temat 5",
      title: "Charyzmaty – Bóg w działaniu",
      goal: "Pokazać rolę charyzmatów i dać ich doświadczenie.",
      points: [
        "Charyzmaty są darami łaski udzielanymi dla wspólnego dobra.",
        "Duch daje różne dary, aby budować wspólnotę Kościoła.",
        "Dojrzała posługa łączy pragnienie, wiarę, współpracę i rozeznanie.",
      ],
      art: "temat-5-charyzmaty.png",
      alt: "Infografika darów Ducha Świętego służących wspólnocie",
      pages: "s. 25-29",
      callouts: [
        ["Ćwiczenia", "Języki i słowo poznania", "Uczestnicy przełamują lęk przed modlitwą w językach oraz uczą się, jak Duch może korzystać z wyobraźni i ciała w słowie poznania.", 42, 360, 540, 130, C.terracotta],
        ["Dynamika", "Modlitwa o charyzmaty dla wspólnoty", "Prowadzona modlitwa uwielbienia otwiera na języki, poznanie, proroctwo, uzdrawianie i inne dary służące wspólnocie.", 795, 470, 435, 138, C.teal],
      ],
      props: "brak osobnych rekwizytów; potrzebna przestrzeń modlitwy i doświadczona posługa",
    },
    {
      eyebrow: "Temat 6",
      title: "Prowadzenie modlitwy wspólnotowej",
      goal: "Ukazać rolę prowadzącego spotkanie modlitewne.",
      points: [
        "Celem spotkania jest zjednoczenie z Bogiem przez uwielbienie.",
        "Prowadzący służy pokornie, zna Boga i posiada wizję spotkania.",
        "Nadaje kierunek, współpracuje z muzycznymi i unika manipulacji.",
      ],
      art: "temat-6-modlitwa-wspolnotowa.png",
      alt: "Infografika prowadzącego, schematu modlitwy i wspólnoty modlącej się w grupach",
      pages: "s. 30-35",
      callouts: [
        ["Schemat", "Cztery etapy spotkania", "Przygotowanie, wejście w modlitwę, modlitwa kerygmatem wraz ze słuchaniem i posługą oraz wspólne zakończenie.", 42, 360, 505, 125, C.terracotta],
        ["Dynamiki", "Prowadzenie i posługa w grupach", "Uczestnicy prowadzą 40-minutowe spotkanie. Potem w grupach 4–5 osób modlą się za siebie i posługują charyzmatami.", 790, 470, 440, 138, C.teal],
      ],
      props: "schemat modlitwy wspólnotowej na plakacie lub w prezentacji",
    },
    {
      eyebrow: "Temat 7",
      title: "Wspólnota",
      goal: "Ukazać biblijny model wspólnoty.",
      points: [
        "Wspólnota jest miejscem autentycznej modlitwy.",
        "We wspólnocie Bóg pozwala doświadczać swojego zbawienia.",
        "Wspólnota żyje i rozwija się, gdy ewangelizuje.",
      ],
      art: "temat-7-wspolnota.png",
      alt: "Infografika wspólnoty modlącej się, doświadczającej uzdrowienia i wychodzącej z Ewangelią",
      pages: "s. 36-41",
      callouts: [
        ["Obraz nauczania", "Betlejem – Dom Chleba", "Wspólnota bez Jezusa staje się miejscem głodu. Modlitwa sprawia, że wzrasta w niej Boża obecność i prawdziwy Chleb.", 42, 360, 520, 125, C.terracotta],
        ["Dynamiki", "Modlitwa za wspólnotę i list do Boga", "Najpierw uczestnicy modlą się za swoją wspólnotę. Następnie powierzają Bogu jej zranienia w osobistym liście składanym podczas Eucharystii.", 790, 470, 440, 138, C.teal],
      ],
      props: "ładne kartki A4 dla uczestników, długopisy",
    },
  ];

  {
    const slide = pres.slides.add();
    await background(slide, path.join(assetsDir, "okladka.png"), "Symboliczna droga całego kursu KAMCh");
    textBox(slide, "KURS ANIMACJI MODLITWY CHARYZMATYCZNEJ", 70, 98, 570, 26, { fontSize: 16, bold: true, color: C.terracotta });
    textBox(slide, "KAMCh", 70, 142, 530, 92, { fontSize: 76, bold: true, color: C.navy });
    textBox(slide, "Widok z lotu ptaka", 72, 244, 490, 42, { fontSize: 29, bold: true, color: C.teal });
    rect(slide, 72, 310, 420, 3, C.mustard);
    textBox(slide, "Cele, treść, zabiegi dydaktyczne, dynamiki i rekwizyty wszystkich tematów", 72, 334, 500, 92, { fontSize: 22, color: C.navy });
    textBox(slide, "na podstawie Dyrektorium KAMCh 2017", 72, 610, 420, 24, { fontSize: 14, bold: true, color: C.terracotta });
    slide.speakerNotes.text = `Treść: ${sourcePdf}. Ilustracja wygenerowana na potrzeby projektu KAMCh.`;
  }

  for (const [idx, data] of topicSlides.entries()) {
    const slide = pres.slides.add();
    await background(slide, path.join(assetsDir, data.art), data.alt);
    titleBlock(slide, data.eyebrow, data.title, data.goal, data.points);
    for (const c of data.callouts) callout(slide, ...c);
    propsLine(slide, data.props);
    footer(slide, data.pages, idx + 2);
    slide.speakerNotes.text = `Treść: ${sourcePdf}, ${data.pages}. Ilustracja wygenerowana na potrzeby projektu KAMCh.`;
  }

  {
    const slide = pres.slides.add();
    await background(slide, path.join(assetsDir, "mapa-kursu.png"), "Mapa siedmiu tematów kursu KAMCh");
    rect(slide, 42, 34, 610, 640, "rgba(247,240,223,0.95)", true);
    textBox(slide, "CAŁY KURS", 72, 58, 220, 22, { fontSize: 14, bold: true, color: C.terracotta });
    textBox(slide, "Droga KAMCh", 72, 88, 520, 52, { fontSize: 40, bold: true, color: C.navy });
    textBox(slide, "Od osobistego spotkania do wspólnoty posłanej z Ewangelią", 72, 142, 520, 50, { fontSize: 20, color: C.teal });
    const rows = [
      ["1", "Sekret Piotra i Jana", "modlitwa karmi ewangelizację"],
      ["2", "Modlitwa osobista", "spotkanie, słuchanie i rozeznanie"],
      ["3", "Pięćdziesiątnica", "prowadzenie i zanurzenie w Duchu"],
      ["4", "Uwielbienie", "spojrzenie skupione na Bogu"],
      ["5", "Charyzmaty", "dary dla wspólnego dobra"],
      ["6", "Modlitwa wspólnotowa", "porządek, jedność i służba"],
      ["7", "Wspólnota", "modlitwa, zbawienie i ewangelizacja"],
    ];
    rows.forEach((row, i) => {
      const y = 214 + i * 57;
      textBox(slide, row[0], 74, y, 28, 26, { fontSize: 17, bold: true, color: i % 2 ? C.mustard : C.terracotta });
      textBox(slide, row[1], 110, y, 250, 24, { fontSize: 17, bold: true, color: C.navy });
      textBox(slide, row[2], 366, y, 240, 34, { fontSize: 14, color: C.navy });
      rect(slide, 110, y + 40, 472, 1, "rgba(23,58,78,0.18)");
    });
    textBox(slide, "Kręgosłup kursu: spotkanie z Bogiem, życie w Duchu, służba i misja wspólnoty.", 72, 610, 520, 42, { fontSize: 15, bold: true, color: C.teal });
    slide.speakerNotes.text = `Synteza tematów na podstawie ${sourcePdf}, s. 2-41. Ilustracja wygenerowana na potrzeby projektu KAMCh.`;
  }

  const stagingDir = path.join(buildDir, "finalizer");
  await fs.mkdir(stagingDir, { recursive: true });
  const candidatePath = path.join(stagingDir, "candidate.pptx");
  const receiptPath = path.join(stagingDir, "full.validation.json");
  await fs.rm(receiptPath, { force: true });
  await (await PresentationFile.exportPptx(pres)).save(candidatePath);
  await fs.rm(finalPptx, { force: true });
  const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href);
  await finalizePresentation({
    workspaceDir: issueDir,
    candidatePath,
    finalPath: finalPptx,
    pythonExecutable: runtimePython,
    integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
    layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-heading-fit"],
    explicitTotalSlideCount: 10,
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
    fontPolicy: { basis: "design", families: [FONT] },
    verifyArtifactToolImport: true,
    receiptPath,
  });

  const finalPres = await PresentationFile.importPptx(await FileBlob.load(finalPptx));
  await fs.rm(renderDir, { recursive: true, force: true });
  await fs.mkdir(renderDir, { recursive: true });
  for (const [index, slide] of finalPres.slides.items.entries()) {
    await writeBlob(path.join(renderDir, `slajd-${String(index + 1).padStart(2, "0")}.png`), await finalPres.export({ slide, format: "png", scale: 1 }));
  }
  await writeBlob(path.join(renderDir, "montaz.webp"), await finalPres.export({ format: "webp", montage: true }));
  console.log(JSON.stringify({ finalPptx, renderDir, slides: finalPres.slides.items.length }, null, 2));
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
