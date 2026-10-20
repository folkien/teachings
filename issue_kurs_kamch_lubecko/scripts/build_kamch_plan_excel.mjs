import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/home/spasz/python/teachings/outputs/kamch_2026_plan_v5";
const outputPath = `${outputDir}/KAMCh_2026_plan_v5.xlsx`;
const previewPath = `${outputDir}/KAMCh_2026_plan_v5_preview.png`;

const days = [
  {
    name: "Piątek",
    start: 16.5 / 24,
    events: [
      [30, "Spotkanie ekipy na modlitwie", "Ekipa"],
      [30, "Recepcja", "Krystian, Beata"],
      [15, "Powitanie", "Sławek"],
      [15, "Lodołamacz", "Sławek"],
      [30, "T0: Wprowadzenie + Analogia (Latawiec)", "Kasia"],
      [20, "D1: Modlitwa rozpoczynająca + D2: Wejście na Górę", "Kasia"],
      [30, "Oczekiwania + kolacja", "Sławek, Dorota i Marek"],
      [30, "T1: Sekret Piotra i Jana - modlitwa osobista", "Aga Piontek"],
      [15, "D1: Schemat modlitwy osobistej - część 1", "Beata"],
      [15, "D1: Schemat modlitwy osobistej - część 2", "Sławek + uczestnik"],
      [10, "Zakończenie", "Sławek"],
    ],
  },
  {
    name: "Sobota",
    start: 8.5 / 24,
    events: [
      [30, "Modlitwa osobista", "Sławek"],
      [30, "Praca w grupach + kawa", "Sławek, animatorzy, Dorota i Marek"],
      [15, "Animacja", "Uczestnicy"],
      [15, "Podsumowanie", "Uczestnicy"],
      [30, "Modlitwa wspólnotowa + budowanie stateczków", "Krystian, Piotrek Mostowski"],
      [45, "T2: Prowadzenie modlitwy osobistej", "Kasia"],
      [45, "Przerwa na kawę + D: Spotkanie z Ukochanym", "Uczestnicy, Dorota i Marek"],
      [20, "Podsumowanie Spotkania z Ukochanym", "Kasia"],
      [10, "Przerwa", ""],
      [20, "Eucharystia z T4: Adoracja - uwielbienie", "ks. Tomek"],
      [20, "D1: Uwielbienie pieśniami po Komunii", "Muzyczni"],
      [20, "D2: Uwielbienie chóralne po Mszy", "ks. Tomek"],
      [60, "Obiad", "Dorota i Marek"],
      [35, "T3: Pięćdziesiątnica - wzór spotkania modlitwy charyzmatycznej", "Piotrek Mostowski"],
      [25, "D: List do Pana Jezusa na statku + modlitwa", "ks. Tomek"],
      [15, "Przerwa", ""],
      [50, "T5: Charyzmaty - Boże działanie na spotkaniach modlitwy charyzmatycznej", "Jadzia"],
      [5, "D1: Modlitwa w językach", ""],
      [5, "D2: Dary prorockie", ""],
      [15, "Przerwa na kawę", ""],
      [45, "D3: Modlitwa o zesłanie Ducha Świętego i Jego charyzmaty dla wspólnoty", ""],
      [45, "D4: Posługa charyzmatami", ""],
      [30, "Kolacja", "Dorota i Marek"],
      [55, "T6: Prowadzenie modlitwy wspólnotowej", "Krystian"],
      [0, "Zakończenie", ""],
    ],
  },
  {
    name: "Niedziela",
    start: 8 / 24,
    events: [
      [30, "Modlitwa osobista", "Sławek"],
      [30, "Praca w grupach + kawa", "Sławek, animatorzy, Dorota i Marek"],
      [15, "Animacja", "Uczestnicy"],
      [15, "Podsumowanie", "Uczestnicy"],
      [30, "D: Spotkanie modlitewne według schematu", "Uczestnik"],
      [15, "Podsumowanie spotkania modlitewnego", ""],
      [15, "Przerwa i przygotowanie do Mszy", ""],
      [60, "Msza Święta", "ks. Tomek"],
      [30, "Przerwa na kawę", "Dorota i Marek"],
      [40, "T8: Wspólnota - naturalne środowisko modlitwy charyzmatycznej", "Sławek"],
      [20, "D: List do Boga", "Sławek"],
      [20, "Świadectwa", "Sławek"],
      [10, "Wizja SNE", "Sławek"],
      [0, "Zakończenie", ""],
    ],
  },
];

await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Plan");
sheet.showGridLines = false;
sheet.tabColor = "#1F4E78";

const dayRanges = [];
let row = 1;

for (const day of days) {
  const dayRow = row;
  sheet.mergeCells(`A${dayRow}:D${dayRow}`);
  sheet.getRange(`A${dayRow}`).values = [[day.name]];

  const headerRow = dayRow + 1;
  sheet.getRange(`A${headerRow}:D${headerRow}`).values = [[
    "Start",
    "Czas",
    "Nazwa",
    "Odpowiedzialny",
  ]];

  const firstEventRow = headerRow + 1;
  const lastEventRow = firstEventRow + day.events.length - 1;
  sheet.getRange(`B${firstEventRow}:D${lastEventRow}`).values = day.events;
  sheet.getRange(`A${firstEventRow}`).values = [[day.start]];

  for (let eventRow = firstEventRow + 1; eventRow <= lastEventRow; eventRow += 1) {
    sheet.getRange(`A${eventRow}`).formulas = [[`=A${eventRow - 1}+B${eventRow - 1}/1440`]];
  }

  dayRanges.push({ day, dayRow, headerRow, firstEventRow, lastEventRow });
  row = lastEventRow + 2;
}

const lastUsedRow = row - 2;
const usedRange = sheet.getRange(`A1:D${lastUsedRow}`);
usedRange.format.font = { name: "Arial", size: 10, color: "#1F2937" };
usedRange.format.verticalAlignment = "center";

sheet.getRange(`A1:A${lastUsedRow}`).format.horizontalAlignment = "center";
sheet.getRange(`B1:B${lastUsedRow}`).format.horizontalAlignment = "center";
sheet.getRange(`A1:A${lastUsedRow}`).format.numberFormat = "hh:mm";
sheet.getRange(`B1:B${lastUsedRow}`).format.numberFormat = "0";
sheet.getRange(`C1:D${lastUsedRow}`).format.wrapText = false;

sheet.getRange(`A1:A${lastUsedRow}`).format.columnWidth = 11;
sheet.getRange(`B1:B${lastUsedRow}`).format.columnWidth = 9;
sheet.getRange(`C1:C${lastUsedRow}`).format.columnWidth = 67;
sheet.getRange(`D1:D${lastUsedRow}`).format.columnWidth = 32;

for (const { dayRow, headerRow, firstEventRow, lastEventRow } of dayRanges) {
  sheet.getRange(`A${dayRow}:D${dayRow}`).format = {
    fill: "#1F4E78",
    font: { name: "Arial", size: 12, bold: true, color: "#FFFFFF" },
    verticalAlignment: "center",
  };
  sheet.getRange(`A${dayRow}:D${dayRow}`).format.rowHeight = 25;

  sheet.getRange(`A${headerRow}:D${headerRow}`).format = {
    fill: "#D9EAF3",
    font: { name: "Arial", size: 10, bold: true, color: "#1F2937" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "doubleBottom", style: "thin", color: "#1F4E78" },
  };
  sheet.getRange(`A${headerRow}:D${headerRow}`).format.rowHeight = 22;

  sheet.getRange(`A${firstEventRow}:D${lastEventRow}`).format.borders = {
    bottom: { style: "thin", color: "#D8DEE8" },
  };
  sheet.getRange(`A${firstEventRow}:D${lastEventRow}`).format.rowHeight = 22;
  sheet.getRange(`B${firstEventRow}:B${lastEventRow}`).format.fill = "#FFF2CC";
  sheet.getRange(`A${firstEventRow}`).format.fill = "#FFF2CC";
}

// Test the promised roll-forward: a 10-minute longer T0 moves the next start by 10 minutes.
const friday = dayRanges[0];
const t0Row = friday.firstEventRow + 4;
const nextRow = t0Row + 1;
sheet.getRange(`B${t0Row}`).values = [[40]];
workbook.recalculate();
const changedStart = sheet.getRange(`A${nextRow}`).values[0][0];
if (Math.abs(changedStart - 18.666666666666668 / 24) > 1e-9) {
  throw new Error("Test automatycznego przesuwania godzin nie powiódł się.");
}
sheet.getRange(`B${t0Row}`).values = [[30]];

workbook.recalculate();

const inspection = await workbook.inspect({
  kind: "table",
  range: `Plan!A1:D${lastUsedRow}`,
  include: "values,formulas",
  tableMaxRows: 80,
  tableMaxCols: 4,
});
console.log(inspection.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const preview = await workbook.render({
  sheetName: "Plan",
  range: `A1:D${lastUsedRow}`,
  scale: 1.5,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

console.log(JSON.stringify({ outputPath, previewPath, lastUsedRow, dayRanges }));
