export const OCI_COLORS = {
  primary: '#13335a',
  secondary: '#2a688f',
  accent: '#42b9eb',
  surface: '#eceded',
  chart: ['#13335a', '#2a688f', '#42b9eb', '#94a3b8'],
};

export const ociClasses = {
  badgeNeutral:
    'rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200',
  badgeBrand:
    'rounded-full bg-[#13335a]/8 px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#eceded]',
  btnClear:
    'inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
  btnClearIcon:
    'inline-flex items-center justify-center rounded-md border border-slate-200 bg-white p-1.5 text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
  btnPrimary:
    'inline-flex items-center justify-center rounded-xl bg-[#13335a] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#0f2a49] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#2a688f] dark:hover:bg-[#13335a]',
  labelSection: 'text-xs font-medium text-gray-500 dark:text-gray-400',
  cardSurface: 'rounded-xl border border-slate-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800',
  alertInfo:
    'rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-gray-800 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-200',
  alertWarn:
    'rounded-xl border border-amber-200/60 bg-amber-50/40 px-4 py-3 text-sm text-amber-950 dark:border-amber-900/30 dark:bg-amber-950/20 dark:text-amber-100',
  alertError:
    'rounded-xl border border-red-200/60 bg-red-50/40 p-3 text-sm text-red-900 dark:border-red-900/30 dark:bg-red-950/20 dark:text-red-200',
  alertSuccess:
    'rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-gray-800 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-200',
  emptyState:
    'rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-gray-600 dark:border-gray-600 dark:bg-gray-900/30 dark:text-gray-300',
  tagMono:
    'rounded px-1.5 py-0.5 font-mono text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-200 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600',
};

export function ociRowClass(status) {
  if (status === 'removed') return 'bg-slate-100 dark:bg-gray-800/60 hover:opacity-90';
  if (status === 'altered') return 'bg-slate-50 dark:bg-gray-900/40 hover:opacity-90';
  return 'bg-white dark:bg-gray-800/30 hover:opacity-90';
}

export function ociRowStatusClass(status) {
  if (status === 'removed') return 'font-semibold text-[#13335a] dark:text-[#eceded]';
  if (status === 'altered') return 'font-semibold text-[#2a688f] dark:text-[#42b9eb]';
  return 'text-gray-600 dark:text-gray-300';
}

export function ociUnitMatchClasses(kind) {
  if (kind === 'match') return ociClasses.alertSuccess;
  if (kind === 'mismatch') return ociClasses.alertWarn;
  return ociClasses.alertInfo;
}
