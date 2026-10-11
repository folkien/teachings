import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/home/spasz/python/teachings";
const issueDir = path.join(workspaceDir, "issue_kurs_kamch_lubecko");
const buildDir = path.join(issueDir, ".pptx_build");
const renderDir = path.join(issueDir, "prezentacja_render");
const outputDir = path.join(issueDir, "output");
const skillDir = "/home/spasz/.codex/plugins/cache/openai-primary-runtime/presentations/26.1009.11318/skills/presentations";
const runtimePython = "/home/spasz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const finalPptx = path.join(outputDir, "KAMCh_2017_widok_z_lotu_ptaka.pptx");
const sourcePdf = path.join(issueDir, "Dyrektorium KAMCH 2.5.2017.pdf");

const W = 1280;
const H = 720;
const C = {
  cream: "#F7F1E5",
  paper: "#FFFDF8",
  navy: "#17364D",
  navy2: "#244C66",
  teal: "#4E7E73",
  mustard: "#D5A13B",
  coral: "#C9684C",
  ink: "#1D2A32",
  muted: "#66737B",
  line: "#D9D2C5",
  white: "#FFFFFF",
};
const FONT = "Arial";
const PHOTO = {
  cover: path.join(workspaceDir, "images/spotkania_lubecko/542758260_1189714076515860_576480194147600250_n.jpg"),
  intro: path.join(workspaceDir, "images/spotkania_lubecko/514120090_1131889985631603_7198351919478583354_n.jpg"),
  t1: path.join(workspaceDir, "images/spotkania_lubecko/542760259_1189714046515863_5420822075614767938_n.jpg"),
  t2: path.join(workspaceDir, "images/spotkania_lubecko/586519732_1258789762941624_3379056877629787591_n.jpg"),
  t3: path.join(workspaceDir, "images/spotkania_lubecko/542759549_1189714136515854_6660893102267862737_n.jpg"),
  t4: path.join(workspaceDir, "images/spotkania_lubecko/586553943_1258790036274930_7368802101647350787_n.jpg"),
  t5: path.join(workspaceDir, "images/kosciol/512452331_1131890208964914_4015179945784289527_n.jpg"),
  t6: path.join(workspaceDir, "images/spotkania_lubecko/543054241_1189714159849185_8131040673780566745_n.jpg"),
  t7: path.join(workspaceDir, "images/relacje/756440977_1463665029120762_8001704415981104805_n.jpg"),
  logo: path.join(workspaceDir, "images/logotyp/sne_kwadrat.png"),
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function readImageBlob(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function addText(slide, text, x, y, w, h, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: options.fontSize ?? 24,
    bold: options.bold ?? false,
    color: options.color ?? C.ink,
    italic: options.italic ?? false,
  };
  return shape;
}

function addRect(slide, x, y, w, h, fill, radius = false) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: "none", width: 0 },
    ...(radius ? { borderRadius: "rounded-lg" } : {}),
  });
}

async function addPhoto(slide, filePath, x, y, w, h, alt) {
  slide.images.add({
    blob: await readImageBlob(filePath),
    contentType: filePath.endsWith(".png") ? "image/png" : "image/jpeg",
    alt,
    fit: "cover",
    position: { left: x, top: y, width: w, height: h },
  });
}

function addFooter(slide, number) {
  addRect(slide, 64, 676, 1152, 1, C.line);
  addText(slide, "KAMCh 2017  |  widok z lotu ptaka", 68, 682, 390, 20, { fontSize: 14, color: C.muted });
  addText(slide, String(number).padStart(2, "0"), 1160, 680, 56, 22, { fontSize: 15, color: C.muted, bold: true });
}

function addHeader(slide, section, title, number, accent = C.mustard, titleSize = 43) {
  slide.background.fill = C.cream;
  addRect(slide, 0, 0, W, 12, accent);
  addText(slide, section.toUpperCase(), 68, 42, 520, 24, { fontSize: 15, bold: true, color: accent });
  addText(slide, title, 68, 72, 1120, 86, { fontSize: titleSize, bold: true, color: C.navy });
  addFooter(slide, number);
}

function addBullets(slide, items, x, y, w, options = {}) {
  const fontSize = options.fontSize ?? 23;
  const rowHeight = options.rowHeight ?? 49;
  const color = options.color ?? C.ink;
  items.forEach((item, idx) => {
    const yy = y + idx * rowHeight;
    addText(slide, "•", x, yy - 2, 22, rowHeight, { fontSize: fontSize + 2, bold: true, color: options.bulletColor ?? C.coral });
    addText(slide, item, x + 28, yy, w - 28, rowHeight, { fontSize, color });
  });
}

function addObjectiveColumn(slide, goal, key, time, accent) {
  addRect(slide, 820, 160, 396, 472, C.navy);
  addText(slide, "CEL", 858, 196, 310, 28, { fontSize: 16, bold: true, color: accent });
  addText(slide, goal, 858, 230, 310, 140, { fontSize: 22, bold: true, color: C.white });
  addRect(slide, 858, 390, 310, 1, C.navy2);
  addText(slide, "MYŚL KLUCZOWA", 858, 412, 310, 28, { fontSize: 16, bold: true, color: accent });
  addText(slide, key, 858, 446, 310, 110, { fontSize: 21, color: C.white });
  addText(slide, `CZAS  ${time}`, 858, 584, 310, 24, { fontSize: 16, bold: true, color: accent });
}

function addContentSlide(pres, data, number) {
  const slide = pres.slides.add();
  addHeader(slide, data.section, data.title, number, data.accent);
  addText(slide, "TOK NAUCZANIA", 68, 164, 500, 28, { fontSize: 17, bold: true, color: data.accent });
  addBullets(slide, data.content, 68, 206, 700, { fontSize: data.bodySize ?? 23, rowHeight: data.rowHeight ?? 66, bulletColor: data.accent });
  addObjectiveColumn(slide, data.goal, data.key, data.time, data.accent);
  slide.speakerNotes.text = `Źródło: ${sourcePdf}, ${data.pages}.`;
  return slide;
}

async function addMethodSlide(pres, data, number) {
  const slide = pres.slides.add();
  addHeader(slide, data.section, `${data.title} - doświadczenie i metoda`, number, data.accent, 34);
  addText(slide, "ZABIEGI I ĆWICZENIA", 68, 176, 560, 28, { fontSize: 17, bold: true, color: data.accent });
  addBullets(slide, data.methods, 68, 212, 640, { fontSize: data.methodSize ?? 20, rowHeight: data.methodRowHeight ?? 55, bulletColor: data.accent });
  addRect(slide, 68, 486, 640, 1, C.line);
  addText(slide, "REKWIZYTY", 68, 506, 220, 26, { fontSize: 16, bold: true, color: data.accent });
  addText(slide, data.props, 68, 538, 640, 78, { fontSize: data.propsSize ?? 20, color: C.ink });
  await addPhoto(slide, data.photo, 752, 160, 464, 414, data.photoAlt);
  addRect(slide, 752, 574, 464, 58, C.navy);
  addText(slide, data.practice, 772, 582, 424, 42, { fontSize: 14, bold: true, color: C.white });
  slide.speakerNotes.text = `Źródło treści: ${sourcePdf}, ${data.pages}. Fotografia: archiwum SNE Lubecko, ${path.relative(workspaceDir, data.photo)}.`;
  return slide;
}

const topics = [
  {
    section: "Wprowadzenie",
    title: "Zaproszenie do szukania obecności Boga",
    accent: C.coral,
    goal: "Zachęcić uczestników do pełnego wejścia w kurs.",
    key: "Bóg zaprasza do pokolenia przyjaciół szukających Jego obecności.",
    time: "30 + 20 min",
    pages: "s. 2-5",
    content: [
      "Kurs uczy modlitwy osobistej i wspólnotowej oraz prowadzenia innych do spotkania z Jezusem.",
      "Animacja oznacza ożywianie. Modlitwa charyzmatyczna otwiera na działanie Boga i angażuje całą osobę.",
      "Jr 29 pokazuje Boga, który ma zamiary pełne pokoju i pozwala się znaleźć tym, którzy szukają Go całym sercem.",
      "Ps 24 przedstawia modlitwę jako wejście na górę spotkania z Bogiem.",
    ],
    methods: [
      "Pieśń „Kto wstąpi na górę Pana” rozbudza pragnienie szukania obecności Boga.",
      "Obraz góry porządkuje sens kursu: wysiłek, decyzję i spotkanie.",
      "Dynamika „Wejście na górę”: uczestnik zapisuje imię i umieszcza je na plakacie jako znak decyzji.",
    ],
    props: "Nagranie pieśni, plakat góry, karteczki samoprzylepne, długopisy.",
    practice: "DYNAMIKA KOŃCOWA  Wejście na górę  |  do 20 min",
    photo: PHOTO.intro,
    photoAlt: "Autentyczne spotkanie wspólnoty SNE Lubecko",
  },
  {
    section: "Temat 1",
    title: "Sekret Piotra i Jana",
    accent: C.mustard,
    goal: "Ukazać konieczność modlitwy osobistej dla skutecznej ewangelizacji i podać prosty schemat modlitwy.",
    key: "Doświadczenie Boga prowadzi do ewangelizacji.",
    time: "45 + 15 min",
    pages: "s. 6-11",
    content: [
      "Dz 3-4 odsłania cykl: modlitwa, ewangelizacja, sprzeciw i ponowna modlitwa wspólnoty.",
      "Modlitwa osobista karmi życie z Bogiem, rodzi pragnienie głoszenia i otwiera na Ducha Świętego.",
      "Kerygmat skupia się na śmierci i zmartwychwstaniu Jezusa. Osobiste świadectwo pokazuje Jego działanie.",
      "Schemat modlitwy prowadzi od znaku krzyża i Słowa do odpowiedzi, słuchania oraz modlitwy Kościoła.",
    ],
    methods: [
      "„Karmienie chlebem” cz. I: prowadzący je chleb. Modlitwa osobista codziennie karmi człowieka Chrystusem.",
      "„Karmienie chlebem” cz. II: chleb trafia do uczestników. Ewangelizacja dzieli się tym, czym człowiek sam żyje.",
      "Dynamika: 15 minut modlitwy według schematu, a potem krótkie dzielenie o jego przydatności.",
    ],
    props: "Ładny koszyk, chleb dla uczestników, schemat modlitwy osobistej na plakacie lub slajdzie.",
    practice: "DYNAMIKA KOŃCOWA  Modlitwa osobista schematem  |  15 min",
    photo: PHOTO.t1,
    photoAlt: "Biblia podczas spotkania formacyjnego w Lubecku",
  },
  {
    section: "Temat 2",
    title: "Prowadzenie modlitwy osobistej",
    accent: C.teal,
    goal: "Dać praktyczne wskazówki do prowadzenia modlitwy osobistej.",
    key: "Jakość modlitwy osobistej wpływa na modlitwę wspólnotową.",
    time: "45 + 30 min",
    pages: "s. 12-16",
    content: [
      "Modlitwa daje doświadczenie miłości, siłę do walki z grzechem, kierunek życia i pragnienie wspólnoty.",
      "Praktyka wymaga stałego czasu i miejsca, wolności dla Boga, wytrwałości oraz zakorzenienia w Słowie.",
      "Uczucia pokazują stan wnętrza, ale nie mierzą obecności Boga. Grzech nie zamyka drogi do spotkania.",
      "Słuchanie prowadzi do rozeznania przez Słowo, naukę Kościoła, natchnienia, rozum i znaki czasu.",
    ],
    methods: [
      "Opcjonalny prezent lub cukierki pokazują, że Bóg nie przychodzi na modlitwę z pustymi rękami.",
      "Termometr odróżnia uczucia od prawdy o obecności Boga.",
      "„Zostałeś obmyty”: zabrudzenie i umycie ręki ukazuje, że Boże przebaczenie otwiera drogę do modlitwy.",
      "„Spotkanie z Ukochanym”: modlitwa, słuchanie i rozeznawanie po 10 minut.",
    ],
    methodSize: 19,
    methodRowHeight: 57,
    props: "Tradycyjny termometr, materiał brudzący rękę, przezroczysty dzbanek i woda.",
    practice: "DYNAMIKA KOŃCOWA  Spotkanie z Ukochanym  |  30 min + dzielenie",
    photo: PHOTO.t2,
    photoAlt: "Rozmowa w małej grupie podczas spotkania SNE Lubecko",
  },
  {
    section: "Temat 3",
    title: "Pięćdziesiątnica",
    accent: C.coral,
    goal: "Ukazać, że modlitwa charyzmatyczna zmierza do doświadczenia Pięćdziesiątnicy.",
    key: "Potrzebujesz nieustannego zanurzenia w Duchu Świętym.",
    time: "30 + 30 min",
    pages: "s. 17-20",
    content: [
      "Celem modlitwy jest komunia z Trójcą i spotkanie z żywym Bogiem.",
      "Duch Święty pomaga w słabości, uczy modlitwy i napełnia do skutecznego głoszenia.",
      "Duch chce prowadzić całe życie: decyzje, relacje, finanse, służbę i codzienność.",
      "Pełna zależność od Ducha przynosi przemianę, owoc i posługę dla innych.",
    ],
    methods: [
      "GPS obrazuje Ducha Świętego jako przewodnika, który nadaje kierunek.",
      "Uczestnicy zapisują pragnienia i składają z kartek łódki.",
      "Ez 47 prowadzi od płytkiej wody do pełnego zanurzenia.",
      "Łódki najpierw pływają, potem zostają zanurzone. Całość kończy modlitwa o zanurzenie w Duchu.",
    ],
    methodSize: 19,
    methodRowHeight: 57,
    props: "Kartki A4 lub A5, długopisy, dziecięcy basen z wodą, samochodowy GPS.",
    practice: "DYNAMIKA KOŃCOWA  Pływanie na płytkiej wodzie  |  30 min",
    photo: PHOTO.t3,
    photoAlt: "Wspólna modlitwa w sali SNE Lubecko",
  },
  {
    section: "Temat 4",
    title: "Uwielbienie",
    accent: C.mustard,
    goal: "Dać uczestnikom doświadczenie uwielbienia.",
    key: "Uwielbienie stanowi centrum modlitwy charyzmatycznej.",
    time: "40 + 15 + 15 min",
    pages: "s. 21-24",
    content: [
      "Biblia pokazuje uwielbienie w życiu Izraela, proroków, Jezusa, Apostołów i Kościoła.",
      "Uwielbienie przenosi uwagę z własnych potrzeb na Boga i łączy pozostałe formy modlitwy.",
      "Sytuacja życiowa nie odbiera możliwości uwielbiania. Człowiek powierza Bogu troski i patrzy na Niego.",
      "Formy: modlitwa spontaniczna, chóralna, pieśni, języki i cisza otwarta na proroctwo.",
    ],
    methods: [
      "„Kwiatek”: roślina patrzy ku Ogrodnikowi. Ziemia oznacza poznanie stałości i wierności Boga.",
      "Podlewanie i przycinanie pokazuje troskę Boga o wzrost, uzdrowienie i przemianę człowieka.",
      "Uczestnicy praktykują dwa sposoby uwielbienia: śpiewem i modlitwą chóralną.",
    ],
    props: "Kwitnący kwiatek w doniczce z zielonymi liśćmi oraz nożyczki.",
    practice: "DYNAMIKA KOŃCOWA  Uwielbienie w praktyce  |  15 + 15 min",
    photo: PHOTO.t4,
    photoAlt: "Prowadzenie uwielbienia podczas spotkania SNE Lubecko",
  },
  {
    section: "Temat 5",
    title: "Charyzmaty - Bóg w działaniu",
    accent: C.coral,
    goal: "Pokazać rolę charyzmatów i dać uczestnikom ich doświadczenie.",
    key: "Bóg troszczy się o wspólnotę przez charyzmaty.",
    time: "45 + 75 min",
    pages: "s. 25-29",
    content: [
      "Charyzmat to darmowy dar łaski dla wspólnego dobra, a nie nagroda za świętość osoby.",
      "Posługa darami należy do życia Jezusa, pierwotnego Kościoła i współczesnej wspólnoty.",
      "1 Kor 12 wymienia dziewięć darów. Dyrektorium szerzej ćwiczy języki, poznanie, proroctwo i mądrość.",
      "Dojrzałe proroctwo łączy informację, interpretację i zastosowanie. Dary służą budowaniu ludzi.",
    ],
    methods: [
      "Ćwiczenie języków przełamuje lęk: uczestnik mówi coś dobrego w nieznanym sobie języku.",
      "Ćwiczenie słowa poznania pokazuje, jak Duch może korzystać z wyobraźni i odczuć.",
      "Modlitwa uwielbienia otwiera na uwolnienie darów w uczestnikach i ich wspólnotach.",
      "Ekipa posługuje językami, poznaniem, proroctwem, uzdrawianiem i innymi darami.",
    ],
    methodSize: 19,
    methodRowHeight: 57,
    props: "Tabela techniczna nie wskazuje osobnego rekwizytu. Potrzebna jest przygotowana przestrzeń modlitwy i doświadczona posługa.",
    propsSize: 18,
    practice: "DYNAMIKA KOŃCOWA  Modlitwa o charyzmaty dla wspólnoty  |  75 min",
    photo: PHOTO.t5,
    photoAlt: "Wspólna modlitwa z uniesionymi rękami w kościele",
  },
  {
    section: "Temat 6",
    title: "Prowadzenie modlitwy wspólnotowej",
    accent: C.teal,
    goal: "Ukazać rolę osoby prowadzącej spotkanie modlitewne.",
    key: "Duch Święty prowadzi wspólnotę w uwielbieniu.",
    time: "40 + 60 min",
    pages: "s. 30-35",
    content: [
      "Sposób prowadzenia zależy od celu, uczestników i typu spotkania.",
      "Biblijny wzór opiera się na jednym miejscu, jednym głosie i jednym celu: spotkaniu z Bogiem.",
      "Prowadzący żyje modlitwą, zna Boga, ma wizję spotkania, buduje jedność i pozostaje pokorny.",
      "Schemat prowadzi przez przygotowanie, wejście w modlitwę, kerygmat, słuchanie i posługę charyzmatyczną.",
    ],
    methods: [
      "Prowadzący omawia schemat modlitwy wspólnotowej na przykładach ze swojego doświadczenia.",
      "Uczestnicy przygotowują i prowadzą spotkanie według schematu.",
      "Następnie w grupach 4-5 osób modlą się za siebie i posługują charyzmatami.",
      "Podsumowanie dotyczy celu, współpracy z muzycznymi oraz unikania manipulacji i sztucznej atmosfery.",
    ],
    methodSize: 19,
    methodRowHeight: 57,
    props: "Schemat modlitwy wspólnotowej na plakacie albo w prezentacji.",
    practice: "DYNAMIKI  Spotkanie modlitewne 40 min  |  Posługa charyzmatyczna 20 min",
    photo: PHOTO.t6,
    photoAlt: "Wspólne uwielbienie przed krzyżem w sali SNE Lubecko",
  },
  {
    section: "Temat 7",
    title: "Wspólnota - środowisko modlitwy charyzmatycznej",
    accent: C.mustard,
    goal: "Ukazać biblijny model wspólnoty.",
    key: "Wspólnota żyje, gdy służy ewangelizacji.",
    time: "25 + 10 + 25 + 15 min",
    pages: "s. 36-41",
    content: [
      "Dzieje Apostolskie pokazują wspólnotę jako miejsce modlitwy i oczekiwania na Ducha Świętego.",
      "Wspólnota doświadcza zbawienia: nawrócenia, uzdrowienia, pokoju, odnowionych relacji i Bożego słowa.",
      "Doświadczenie Boga prowadzi do ewangelizacji. Jedna wspólnota rodzi kolejne wspólnoty.",
      "Dojrzałość przechodzi przez odnalezienie, rozczarowanie, przemianę i akceptację.",
    ],
    methods: [
      "Obraz Betlejem, Domu Chleba, pokazuje, że wspólnota bez Jezusa staje się miejscem głodu.",
      "Krótka modlitwa obejmuje własną wspólnotę: jej modlitwę, doświadczenie Boga i ewangelizację.",
      "„List do Boga” pomaga nazwać i powierzyć zranienia związane ze wspólnotą.",
      "Listy trafiają do darów podczas Eucharystii jako znak oddania Bogu.",
    ],
    methodSize: 19,
    methodRowHeight: 57,
    props: "Ładne kartki A4 dla uczestników oraz długopisy.",
    practice: "DYNAMIKI  Modlitwa za wspólnotę 5-10 min  |  List do Boga 10-15 min",
    photo: PHOTO.t7,
    photoAlt: "Rozmowa i relacje we wspólnocie SNE Lubecko",
  },
];

async function build() {
  await fs.mkdir(buildDir, { recursive: true });
  await fs.mkdir(renderDir, { recursive: true });
  await fs.mkdir(outputDir, { recursive: true });
  const pres = Presentation.create({ slideSize: { width: W, height: H } });

  // 1. Cover
  {
    const s = pres.slides.add();
    s.background.fill = C.cream;
    addRect(s, 0, 0, 700, H, C.navy);
    await addPhoto(s, PHOTO.cover, 700, 0, 580, H, "Spotkanie formacyjne SNE Lubecko");
    addText(s, "KURS ANIMACJI MODLITWY CHARYZMATYCZNEJ", 72, 88, 540, 34, { fontSize: 16, bold: true, color: C.mustard });
    addText(s, "KAMCh", 72, 160, 520, 90, { fontSize: 66, bold: true, color: C.white });
    addText(s, "Widok z lotu ptaka", 72, 262, 520, 58, { fontSize: 36, color: C.white });
    addText(s, "Cele tematów, tok nauczania, zabiegi, rekwizyty i dynamiki", 72, 360, 520, 108, { fontSize: 24, color: "#DDE7EC" });
    addText(s, "Na podstawie Dyrektorium KAMCh 2.5.2017", 72, 612, 500, 26, { fontSize: 16, color: C.mustard, bold: true });
    s.speakerNotes.text = `Źródło: ${sourcePdf}. Fotografia: archiwum SNE Lubecko, ${path.relative(workspaceDir, PHOTO.cover)}.`;
  }

  // 2. Course map
  {
    const s = pres.slides.add();
    addHeader(s, "Mapa kursu", "Od osobistego spotkania do wspólnoty dla ewangelizacji", 2, C.coral);
    const map = [
      ["0", "Wprowadzenie", "Decyzja szukania obecności Boga"],
      ["1", "Sekret Piotra i Jana", "Modlitwa karmi ewangelizację"],
      ["2", "Modlitwa osobista", "Siła, słuchanie i rozeznanie"],
      ["3", "Pięćdziesiątnica", "Zanurzenie w Duchu Świętym"],
      ["4", "Uwielbienie", "Bóg w centrum modlitwy"],
      ["5", "Charyzmaty", "Bóg służy wspólnocie przez dary"],
      ["6", "Modlitwa wspólnotowa", "Prowadzenie pod kierunkiem Ducha"],
      ["7", "Wspólnota", "Modlitwa, zbawienie i ewangelizacja"],
    ];
    map.forEach((row, i) => {
      const col = i < 4 ? 0 : 1;
      const idx = i < 4 ? i : i - 4;
      const x = col === 0 ? 68 : 668;
      const y = 168 + idx * 116;
      addText(s, row[0], x, y, 58, 58, { fontSize: 33, bold: true, color: i % 2 ? C.mustard : C.coral });
      addText(s, row[1], x + 74, y + 2, 460, 28, { fontSize: 22, bold: true, color: C.navy });
      addText(s, row[2], x + 74, y + 34, 460, 42, { fontSize: 19, color: C.muted });
      addRect(s, x + 74, y + 88, 460, 1, C.line);
    });
    s.speakerNotes.text = `Źródło: ${sourcePdf}, kalendarz s. 1 oraz tematy s. 2-41.`;
  }

  let slideNo = 3;
  for (const topic of topics) {
    addContentSlide(pres, topic, slideNo++);
    await addMethodSlide(pres, topic, slideNo++);
  }

  // 19. Technical list
  {
    const s = pres.slides.add();
    addHeader(s, "Logistyka", "Rekwizyty według tematów", 19, C.teal);
    const left = [
      ["Ołtarz Słowa", "biały obrus, duża Biblia, wazon, świeca, zapałki, kwiaty"],
      ["Wprowadzenie", "pieśń, długopisy, karteczki samoprzylepne"],
      ["1  Sekret Piotra i Jana", "koszyk, chleb, schemat modlitwy osobistej"],
      ["2  Modlitwa osobista", "termometr, brud, przezroczysty dzbanek, woda"],
      ["3  Pięćdziesiątnica", "kartki, długopisy, basen z wodą, GPS"],
    ];
    const right = [
      ["4  Uwielbienie", "kwitnący kwiatek w doniczce, nożyczki"],
      ["5  Charyzmaty", "brak osobnego rekwizytu w tabeli technicznej"],
      ["6  Modlitwa wspólnotowa", "schemat na plakacie lub w prezentacji"],
      ["7  Wspólnota", "ładne kartki A4, długopisy"],
      ["Ocena kursu", "kartki i długopisy dla uczestników"],
    ];
    const renderList = (items, x) => items.forEach((row, i) => {
      const y = 164 + i * 94;
      addText(s, row[0], x, y, 480, 26, { fontSize: 20, bold: true, color: C.navy });
      addText(s, row[1], x, y + 32, 500, 52, { fontSize: 18, color: C.muted });
      addRect(s, x, y + 82, 500, 1, C.line);
    });
    renderList(left, 68);
    renderList(right, 668);
    s.speakerNotes.text = `Źródło: ${sourcePdf}, tabela techniczna s. 42-43.`;
  }

  // 20. Method pattern
  {
    const s = pres.slides.add();
    addHeader(s, "Metodyka", "Powtarzalny rytm każdego tematu", 20, C.coral);
    const stages = [
      ["1", "Słowo i myśl kluczowa", "Nauczanie nazywa prawdę, którą uczestnik ma zobaczyć."],
      ["2", "Obraz lub zabieg", "Prosty przedmiot przekłada treść na pamiętny obraz."],
      ["3", "Doświadczenie", "Dynamika pozwala uczestnikowi wykonać konkretny krok."],
      ["4", "Podsumowanie", "Dzielenie i konkluzja pomagają nazwać przeżyte doświadczenie."],
    ];
    stages.forEach((row, i) => {
      const x = 68 + i * 298;
      addText(s, row[0], x, 188, 70, 70, { fontSize: 46, bold: true, color: i % 2 ? C.mustard : C.coral });
      addText(s, row[1], x, 284, 250, 62, { fontSize: 25, bold: true, color: C.navy });
      addText(s, row[2], x, 366, 250, 132, { fontSize: 20, color: C.muted });
      if (i < 3) addRect(s, x + 268, 218, 18, 4, C.line);
    });
    addText(s, "Dyrektorium prowadzi od poznania do praktyki. Rekwizyt nie jest dekoracją, lecz nośnikiem znaczenia.", 68, 570, 1120, 46, { fontSize: 24, bold: true, color: C.teal });
    s.speakerNotes.text = `Synteza struktury powtarzającej się w ${sourcePdf}, s. 2-41.`;
  }

  // 21. Memory map
  {
    const s = pres.slides.add();
    addHeader(s, "Powtórka", "Jedno zdanie do zapamiętania z każdego tematu", 21, C.mustard);
    const lines = [
      ["W", "Szukaj obecności Boga całym sercem."],
      ["1", "Nie może zabraknąć modlitwy i głoszenia Słowa."],
      ["2", "Czas z Bogiem daje siłę i kierunek."],
      ["3", "Modlitwa zmierza do doświadczenia Pięćdziesiątnicy."],
      ["4", "Uwielbienie jest drogą do Jezusa."],
      ["5", "Pragnij charyzmatów Ducha dla wspólnoty."],
      ["6", "Duch Święty jest Duchem porządku."],
      ["7", "Wspólnota żyje, gdy jest dla ewangelizacji."],
    ];
    lines.forEach((row, i) => {
      const col = i < 4 ? 0 : 1;
      const idx = i < 4 ? i : i - 4;
      const x = col === 0 ? 68 : 668;
      const y = 170 + idx * 112;
      addText(s, row[0], x, y, 48, 48, { fontSize: 25, bold: true, color: i % 2 ? C.mustard : C.coral });
      addText(s, row[1], x + 64, y, 488, 58, { fontSize: 22, bold: true, color: C.navy });
      addRect(s, x + 64, y + 74, 480, 1, C.line);
    });
    addText(s, "Ta kolejność stanowi kręgosłup kursu: spotkanie, modlitwa, Duch, uwielbienie, dary, prowadzenie i misja wspólnoty.", 68, 614, 1120, 42, { fontSize: 21, color: C.teal });
    s.speakerNotes.text = `Konkluzje tematów na podstawie ${sourcePdf}, s. 5, 11, 16, 20, 24, 29, 35 i 41.`;
  }

  const requirements = {
    explicitTotalSlideCount: 21,
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
  };
  const fontPolicy = { basis: "design", families: [FONT] };
  const expectedSlideSizeEmu = "12192000,6858000";
  const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href);
  const stagingDir = path.join(buildDir, "finalizer");
  await fs.mkdir(stagingDir, { recursive: true });
  const candidatePath = path.join(stagingDir, "candidate.pptx");
  await fs.rm(path.join(stagingDir, "KAMCh_2017_widok_z_lotu_ptaka.validation.json"), { force: true });
  await (await PresentationFile.exportPptx(pres)).save(candidatePath);
  await fs.rm(finalPptx, { force: true });
  await finalizePresentation({
    ...requirements,
    workspaceDir,
    candidatePath,
    finalPath: finalPptx,
    pythonExecutable: runtimePython,
    integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
    layoutArgs: ["--expected-slide-size-emu", expectedSlideSizeEmu, "--validate-heading-fit"],
    requiredNativeTableOwnerSlides: [],
    fontPolicy,
    verifyArtifactToolImport: true,
    receiptPath: path.join(stagingDir, "KAMCh_2017_widok_z_lotu_ptaka.validation.json"),
  });

  const finalPres = await PresentationFile.importPptx(await FileBlob.load(finalPptx));
  await fs.rm(renderDir, { recursive: true, force: true });
  await fs.mkdir(renderDir, { recursive: true });
  for (const [index, slide] of finalPres.slides.items.entries()) {
    const stem = `slajd-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(renderDir, `${stem}.png`), await finalPres.export({ slide, format: "png", scale: 1 }));
  }
  await writeBlob(path.join(renderDir, "montaz.webp"), await finalPres.export({ format: "webp", montage: true }));
  const inspection = await finalPres.inspect({ kind: "slide,textbox,image,notes,layout", maxChars: 50000 });
  await fs.writeFile(path.join(buildDir, "inspection.ndjson"), inspection.ndjson, "utf8");
  console.log(JSON.stringify({ finalPptx, slides: finalPres.slides.items.length, renderDir }, null, 2));
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
