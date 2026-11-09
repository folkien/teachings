#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SLIDE_WIDTH = 1280;
const SLIDE_HEIGHT = 720;
const EXPECTED_SLIDE_SIZE_EMU = "12192000,6858000";

function parseArgs(argv) {
  const args = { config: null, previewDir: null };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--preview-dir") {
      args.previewDir = argv[++index];
    } else if (!args.config) {
      args.config = arg;
    } else {
      throw new Error(`Nieznany argument: ${arg}`);
    }
  }
  if (!args.config) {
    throw new Error(
      "Użycie: scripts/generate_sesa_presentation.sh <prezentacja.yaml> [--preview-dir <katalog>]",
    );
  }
  return args;
}

async function firstExisting(paths) {
  for (const candidate of paths.filter(Boolean)) {
    try {
      await fs.access(candidate);
      return candidate;
    } catch {
      // Sprawdź kolejnego kandydata.
    }
  }
  return null;
}

async function resolveRuntime() {
  const runtimeRoot = path.join(
    os.homedir(),
    ".cache/codex-runtimes/codex-primary-runtime/dependencies",
  );
  const nodeModules = await firstExisting([
    process.env.RUNTIME_NODE_MODULES,
    process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,
    path.join(runtimeRoot, "node/node_modules"),
  ]);
  const python = await firstExisting([
    process.env.RUNTIME_PYTHON,
    process.env.CODEX_RUNTIME_PYTHON,
    path.join(runtimeRoot, "python/bin/python3"),
    "/usr/bin/python3",
  ]);
  const yamlPythonCandidates = [
    process.env.YAML_PYTHON,
    "/usr/bin/python3",
    python,
  ].filter(Boolean);
  let yamlPython = null;
  for (const candidate of yamlPythonCandidates) {
    try {
      execFileSync(candidate, ["-c", "import yaml"], { stdio: "ignore" });
      yamlPython = candidate;
      break;
    } catch {
      // Sprawdź kolejnego Pythona.
    }
  }
  if (!nodeModules) {
    throw new Error(
      "Nie znaleziono pakietów środowiska Codex. Ustaw RUNTIME_NODE_MODULES.",
    );
  }
  if (!python) {
    throw new Error("Nie znaleziono interpretera Python dla walidatorów prezentacji.");
  }
  if (!yamlPython) {
    throw new Error("Nie znaleziono interpretera Python z obsługą PyYAML.");
  }
  process.env.RUNTIME_NODE_MODULES = nodeModules;
  return { nodeModules, python, yamlPython };
}

async function resolvePresentationSkillDir() {
  if (process.env.PRESENTATIONS_SKILL_DIR) {
    return process.env.PRESENTATIONS_SKILL_DIR;
  }
  const versionsRoot = path.join(
    os.homedir(),
    ".codex/plugins/cache/openai-primary-runtime/presentations",
  );
  const versions = (await fs.readdir(versionsRoot, { withFileTypes: true }))
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort()
    .reverse();
  for (const version of versions) {
    const candidate = path.join(versionsRoot, version, "skills/presentations");
    if (await firstExisting([candidate])) return candidate;
  }
  throw new Error(
    "Nie znaleziono umiejętności Presentations. Ustaw PRESENTATIONS_SKILL_DIR.",
  );
}

function parseYamlWithPython(python, yamlText) {
  const source = [
    "import json, sys, yaml",
    "data = yaml.safe_load(sys.stdin.read())",
    "print(json.dumps(data, ensure_ascii=False, default=str))",
  ].join("\n");
  const output = execFileSync(python, ["-c", source], {
    input: yamlText,
    encoding: "utf8",
  });
  return JSON.parse(output);
}

function requireString(value, label) {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`${label} musi być niepustym tekstem.`);
  }
  return value.trim();
}

function validateConfig(config) {
  if (!config || typeof config !== "object") {
    throw new Error("Plik YAML nie zawiera obiektu konfiguracji.");
  }
  if (config.version !== 1) {
    throw new Error("Obsługiwana wersja schematu YAML to version: 1.");
  }
  requireString(config.title, "title");
  requireString(config.course_title, "course_title");
  requireString(config.source, "source");
  if (!config.output || typeof config.output !== "object") {
    throw new Error("Brakuje sekcji output.");
  }
  requireString(config.output.markdown, "output.markdown");
  requireString(config.output.pptx, "output.pptx");
  if (!Array.isArray(config.slides) || config.slides.length < 2) {
    throw new Error("slides musi zawierać co najmniej jeden slajd ilustracyjny i końcowy.");
  }

  let keySentenceCount = 0;
  config.slides.forEach((slide, index) => {
    const label = `slides[${index}]`;
    if (!slide || typeof slide !== "object") {
      throw new Error(`${label} musi być obiektem.`);
    }
    if (slide.type === "illustration") {
      requireString(slide.title, `${label}.title`);
      requireString(slide.subtitle, `${label}.subtitle`);
      requireString(slide.image, `${label}.image`);
    } else if (slide.type === "cycle") {
      requireString(slide.title, `${label}.title`);
      requireString(slide.subtitle, `${label}.subtitle`);
      requireString(slide.center_text, `${label}.center_text`);
      if (!Array.isArray(slide.items) || slide.items.length !== 3) {
        throw new Error(`${label}.items musi zawierać dokładnie trzy elementy.`);
      }
      slide.items.forEach((item, itemIndex) =>
        requireString(item, `${label}.items[${itemIndex}]`),
      );
    } else if (slide.type === "quote") {
      requireString(slide.title, `${label}.title`);
      requireString(slide.text, `${label}.text`);
      requireString(slide.reference, `${label}.reference`);
    } else if (slide.type === "key_sentence") {
      keySentenceCount += 1;
      requireString(slide.title, `${label}.title`);
      requireString(slide.text, `${label}.text`);
      if (index !== config.slides.length - 1) {
        throw new Error("Slajd key_sentence musi być ostatnim slajdem.");
      }
    } else {
      throw new Error(
        `${label}.type musi mieć wartość illustration, cycle, quote albo key_sentence.`,
      );
    }
  });
  if (keySentenceCount !== 1) {
    throw new Error("Prezentacja musi zawierać dokładnie jeden slajd key_sentence.");
  }
}

function themeFrom(config) {
  const theme = config.theme ?? {};
  return {
    font: theme.font ?? "DejaVu Sans",
    headerColor: theme.header_color ?? "#B42318",
    keyColor: theme.key_color ?? "#F6C82F",
    textColor: theme.text_color ?? "#111111",
  };
}

function markdownFrom(config) {
  const date = config.date ?? new Date().toISOString().slice(0, 10);
  const status = config.status ?? "propozycja";
  const lines = [
    "---",
    "tags: [prezentacja, sesa]",
    `status: ${status}`,
    `date: ${date}`,
    `source: "[[${config.source}]]"`,
    `course_title: "${config.course_title}"`,
    "---",
    "",
    `# ${config.title}`,
    "",
    `*${config.course_title}*`,
    "",
  ];
  for (const slide of config.slides) {
    lines.push(`## ${slide.title}`, "");
    if (slide.type === "illustration") {
      lines.push(`### ${slide.subtitle}`, "", `![[${slide.image}]]`, "");
    } else if (slide.type === "cycle") {
      lines.push(
        `### ${slide.subtitle}`,
        "",
        `${slide.items.join(" → ")} → ${slide.items[0]}`,
        "",
        `**${slide.center_text}**`,
        "",
      );
    } else if (slide.type === "quote") {
      lines.push(`> ${slide.text}`, "", `— ${slide.reference}`, "");
    } else {
      lines.push(`### ${slide.text}`, "");
    }
  }
  return `${lines.join("\n").trimEnd()}\n`;
}

function contentTypeFor(filename) {
  const extension = path.extname(filename).toLowerCase();
  if (extension === ".png") return "image/png";
  if (extension === ".jpg" || extension === ".jpeg") return "image/jpeg";
  throw new Error(`Nieobsługiwany format obrazu: ${filename}`);
}

async function readImage(imagePath) {
  const data = await fs.readFile(imagePath);
  return data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
}

function addText(slide, text, position, style, font) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: font,
    autoFit: "shrinkText",
    wrap: "square",
    insets: 0,
    ...style,
  };
}

function addTitleSlide(presentation, config, theme) {
  const slide = presentation.slides.add();
  slide.background.fill = "#FFFFFF";
  addText(
    slide,
    config.course_title.toLocaleUpperCase("pl-PL"),
    { left: 120, top: 170, width: 1040, height: 42 },
    {
      fontSize: 21,
      bold: true,
      color: theme.textColor,
      alignment: "center",
      verticalAlignment: "middle",
    },
    theme.font,
  );
  slide.shapes.add({
    geometry: "rect",
    position: { left: 520, top: 234, width: 240, height: 6 },
    fill: theme.headerColor,
    line: { style: "solid", fill: theme.headerColor, width: 0 },
  });
  addText(
    slide,
    config.title,
    { left: 110, top: 270, width: 1060, height: 210 },
    {
      fontSize: 58,
      bold: true,
      color: theme.headerColor,
      alignment: "center",
      verticalAlignment: "middle",
    },
    theme.font,
  );
}

async function addIllustrationSlide(presentation, slideConfig, configDir, theme) {
  const slide = presentation.slides.add();
  slide.background.fill = "#FFFFFF";
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 0, width: SLIDE_WIDTH, height: 96 },
    fill: theme.headerColor,
    line: { style: "solid", fill: theme.headerColor, width: 0 },
  });
  addText(
    slide,
    slideConfig.title.replace(/Pł/g, "P\u200Cł"),
    { left: 84, top: 22, width: 1124, height: 62 },
    {
      fontSize: 42,
      bold: true,
      color: "#FFFFFF",
      alignment: "left",
      verticalAlignment: "top",
    },
    theme.font,
  );
  addText(
    slide,
    slideConfig.subtitle,
    { left: 80, top: 108, width: 1120, height: 64 },
    {
      fontSize: 25,
      color: theme.textColor,
      alignment: "center",
      verticalAlignment: "middle",
    },
    theme.font,
  );
  const imagePath = path.resolve(configDir, slideConfig.image);
  const imageHeight = 528;
  const imageWidth = Math.round((16 / 9) * imageHeight);
  slide.images.add({
    blob: await readImage(imagePath),
    contentType: contentTypeFor(imagePath),
    alt: `${slideConfig.title}. ${slideConfig.subtitle}`,
    fit: "contain",
    position: {
      left: Math.round((SLIDE_WIDTH - imageWidth) / 2),
      top: 192,
      width: imageWidth,
      height: imageHeight,
    },
  });
}

function addStandardHeader(slide, title, subtitle, theme) {
  slide.background.fill = "#FFFFFF";
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 0, width: SLIDE_WIDTH, height: 96 },
    fill: theme.headerColor,
    line: { style: "solid", fill: theme.headerColor, width: 0 },
  });
  addText(
    slide,
    title,
    { left: 84, top: 22, width: 1124, height: 62 },
    {
      fontSize: 42,
      bold: true,
      color: "#FFFFFF",
      alignment: "left",
      verticalAlignment: "top",
    },
    theme.font,
  );
  if (subtitle) {
    addText(
      slide,
      subtitle,
      { left: 80, top: 108, width: 1120, height: 64 },
      {
        fontSize: 25,
        color: theme.textColor,
        alignment: "center",
        verticalAlignment: "middle",
      },
      theme.font,
    );
  }
}

function addCycleSlide(presentation, slideConfig, theme) {
  const slide = presentation.slides.add();
  addStandardHeader(slide, slideConfig.title, slideConfig.subtitle, theme);
  slide.shapes.add({
    geometry: "circularArrow",
    position: { left: 410, top: 245, width: 460, height: 390 },
    fill: "#FFD2B3",
    line: { style: "solid", fill: "#FFD2B3", width: 0 },
  });
  const nodePositions = [
    { left: 490, top: 205, width: 300, height: 112 },
    { left: 780, top: 485, width: 300, height: 112 },
    { left: 200, top: 485, width: 300, height: 112 },
  ];
  for (const [index, position] of nodePositions.entries()) {
    slide.shapes.add({
      geometry: "ellipse",
      position,
      fill: "#FFF0E5",
      line: { style: "solid", fill: theme.headerColor, width: 3 },
    });
    addText(
      slide,
      slideConfig.items[index],
      position,
      {
        fontSize: 25,
        bold: true,
        color: theme.textColor,
        alignment: "center",
        verticalAlignment: "middle",
      },
      theme.font,
    );
  }
  slide.shapes.add({
    geometry: "ellipse",
    position: { left: 480, top: 385, width: 320, height: 128 },
    fill: theme.keyColor,
    line: { style: "solid", fill: theme.headerColor, width: 2 },
  });
  addText(
    slide,
    slideConfig.center_text,
    { left: 500, top: 400, width: 280, height: 98 },
    {
      fontSize: 24,
      bold: true,
      color: theme.textColor,
      alignment: "center",
      verticalAlignment: "middle",
    },
    theme.font,
  );
}

function addQuoteSlide(presentation, slideConfig, theme) {
  const slide = presentation.slides.add();
  addStandardHeader(slide, slideConfig.title, "", theme);
  slide.shapes.add({
    geometry: "rect",
    position: { left: 150, top: 225, width: 12, height: 270 },
    fill: theme.headerColor,
    line: { style: "solid", fill: theme.headerColor, width: 0 },
  });
  addText(
    slide,
    `„${slideConfig.text}”`,
    { left: 205, top: 220, width: 890, height: 250 },
    {
      fontSize: 42,
      bold: true,
      italic: true,
      color: theme.textColor,
      alignment: "left",
      verticalAlignment: "middle",
    },
    theme.font,
  );
  addText(
    slide,
    slideConfig.reference,
    { left: 205, top: 485, width: 890, height: 56 },
    {
      fontSize: 26,
      bold: true,
      color: theme.headerColor,
      alignment: "right",
      verticalAlignment: "middle",
    },
    theme.font,
  );
}

function addKeySentenceSlide(presentation, slideConfig, theme) {
  const slide = presentation.slides.add();
  slide.background.fill = "#FFFFFF";
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 205, width: SLIDE_WIDTH, height: 310 },
    fill: theme.keyColor,
    line: { style: "solid", fill: theme.keyColor, width: 0 },
  });
  addText(
    slide,
    slideConfig.text.toLocaleUpperCase("pl-PL"),
    { left: 96, top: 230, width: 1088, height: 260 },
    {
      fontSize: 50,
      bold: true,
      color: theme.textColor,
      alignment: "center",
      verticalAlignment: "middle",
    },
    theme.font,
  );
}

async function writeBlob(filename, blob) {
  await fs.writeFile(filename, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const configPath = path.resolve(args.config);
  const configDir = path.dirname(configPath);
  const runtime = await resolveRuntime();
  process.env.XDG_CACHE_HOME ??= path.join(os.tmpdir(), "codex-font-cache");
  const skillDir = await resolvePresentationSkillDir();
  const yamlText = await fs.readFile(configPath, "utf8");
  const config = parseYamlWithPython(runtime.yamlPython, yamlText);
  validateConfig(config);
  const theme = themeFrom(config);

  const artifactToolPath = path.join(
    runtime.nodeModules,
    "@oai/artifact-tool/dist/artifact_tool.mjs",
  );
  const { Presentation, PresentationFile } = await import(
    pathToFileURL(artifactToolPath).href
  );
  const presentation = Presentation.create({
    slideSize: { width: SLIDE_WIDTH, height: SLIDE_HEIGHT },
  });
  addTitleSlide(presentation, config, theme);
  for (const slideConfig of config.slides) {
    if (slideConfig.type === "illustration") {
      await addIllustrationSlide(presentation, slideConfig, configDir, theme);
    } else if (slideConfig.type === "cycle") {
      addCycleSlide(presentation, slideConfig, theme);
    } else if (slideConfig.type === "quote") {
      addQuoteSlide(presentation, slideConfig, theme);
    } else {
      addKeySentenceSlide(presentation, slideConfig, theme);
    }
  }

  const previewDir = path.resolve(
    args.previewDir ??
      path.join(
        os.tmpdir(),
        `sesa-presentation-${path.basename(configPath, path.extname(configPath))}-${process.pid}`,
      ),
  );
  await fs.mkdir(previewDir, { recursive: true });
  for (const [index, slide] of presentation.slides.items.entries()) {
    await writeBlob(
      path.join(previewDir, `slide-${String(index + 1).padStart(2, "0")}.png`),
      await presentation.export({ slide, format: "png", scale: 1 }),
    );
  }
  await writeBlob(
    path.join(previewDir, "montage.webp"),
    await presentation.export({ format: "webp", montage: true }),
  );

  const buildDir = await fs.mkdtemp(
    path.join(configDir, ".sesa-presentation-build-"),
  );
  try {
    const stagingDir = path.join(buildDir, "staging");
    const outputDir = path.join(buildDir, "output");
    await fs.mkdir(stagingDir, { recursive: true });
    await fs.mkdir(outputDir, { recursive: true });
    const candidatePath = path.join(stagingDir, "candidate.pptx");
    const validatedPath = path.join(outputDir, "validated.pptx");
    await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
    const { finalizePresentation } = await import(
      pathToFileURL(
        path.join(skillDir, "container_tools/artifact_tool_utils.mjs"),
      ).href
    );
    const result = await finalizePresentation({
      workspaceDir: configDir,
      candidatePath,
      finalPath: validatedPath,
      pythonExecutable: runtime.python,
      integrityValidatorPath: path.join(
        skillDir,
        "container_tools/inspect_presentation_package_integrity.py",
      ),
      layoutValidatorPath: path.join(
        skillDir,
        "container_tools/inspect_presentation_layout_geometry.py",
      ),
      layoutArgs: [
        "--expected-slide-size-emu",
        EXPECTED_SLIDE_SIZE_EMU,
        "--validate-heading-fit",
      ],
      explicitTotalSlideCount: config.slides.length + 1,
      requiredNativeTableOwnerSlides: [],
      requiredNativeChartOwnerSlides: [],
      fontPolicy: { basis: "design", families: [theme.font] },
      verifyArtifactToolImport: true,
      receiptPath: path.join(stagingDir, "validation.json"),
    });
    if (!result?.finalPath) {
      throw new Error("Finalizator nie zwrócił gotowej prezentacji.");
    }

    const markdownPath = path.resolve(configDir, config.output.markdown);
    const pptxPath = path.resolve(configDir, config.output.pptx);
    await fs.mkdir(path.dirname(markdownPath), { recursive: true });
    await fs.mkdir(path.dirname(pptxPath), { recursive: true });
    await fs.writeFile(markdownPath, markdownFrom(config), "utf8");
    await fs.copyFile(validatedPath, pptxPath);

    console.log(
      JSON.stringify(
        {
          config: configPath,
          markdown: markdownPath,
          pptx: pptxPath,
          previews: previewDir,
          slideCount: config.slides.length + 1,
          status: config.status ?? "propozycja",
        },
        null,
        2,
      ),
    );
  } finally {
    await fs.rm(buildDir, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
