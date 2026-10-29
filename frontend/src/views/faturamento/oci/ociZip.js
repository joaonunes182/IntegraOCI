import { unzipSync } from 'fflate';

// Os zips das unidades trazem pastas com outros zips dentro (PAxxxxxx.SET.zip),
// alem de PDF e RELEXP.PRN, que nao interessam para a analise.
const MAX_ZIP_DEPTH = 4;
const MAX_EXTRACTED_BYTES = 300 * 1024 * 1024;
const BPA_TEXT_HEADER = '01#BPA#';

export function isZipFile(file) {
  return /\.zip$/i.test(file?.name || '');
}

function isBpaEntry(name, content) {
  if (/\.(xlsx|xls)$/i.test(name)) return true;
  return String.fromCharCode(...content.subarray(0, BPA_TEXT_HEADER.length)) === BPA_TEXT_HEADER;
}

function collectBpaEntries(bytes, depth, state, zipName) {
  const entries = unzipSync(bytes, {
    filter: (entry) => {
      state.totalBytes += entry.originalSize;
      if (state.totalBytes > MAX_EXTRACTED_BYTES) {
        throw new Error(`O arquivo ${zipName} passa de 300 MB descompactado.`);
      }
      return true;
    },
  });

  Object.entries(entries).forEach(([path, content]) => {
    if (path.endsWith('/')) return;
    const name = path.split('/').pop();
    if (isZipFile({ name })) {
      if (depth < MAX_ZIP_DEPTH) collectBpaEntries(content, depth + 1, state, zipName);
      return;
    }
    if (isBpaEntry(name, content)) {
      state.files.push({ name, content });
    } else {
      state.ignored.push(name);
    }
  });
}

// Troca cada .zip selecionado pelos arquivos BPA encontrados dentro dele.
export async function expandZipFiles(files) {
  const expanded = [];
  const ignored = [];

  for (const file of files || []) {
    if (!isZipFile(file)) {
      expanded.push(file);
      continue;
    }

    const state = { totalBytes: 0, files: [], ignored };
    try {
      collectBpaEntries(new Uint8Array(await file.arrayBuffer()), 1, state, file.name);
    } catch (error) {
      throw new Error(error?.message?.includes(file.name) ? error.message : `Nao foi possivel abrir o arquivo ${file.name}.`);
    }
    if (!state.files.length) {
      throw new Error(`Nenhum arquivo BPA foi encontrado dentro de ${file.name}.`);
    }

    state.files.forEach(({ name, content }) => {
      expanded.push(new File([content], name, { lastModified: file.lastModified }));
    });
  }

  return { files: expanded, ignored };
}
