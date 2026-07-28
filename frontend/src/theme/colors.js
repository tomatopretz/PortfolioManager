export const colors = {
  light: {
    surface: '#fcfcfb',
    surfaceAlt: '#f9f9f7',
    textPrimary: '#0b0b0b',
    textSecondary: '#52514e',
    textMuted: '#898781',
    gridline: '#e1e0d9',
    border: 'rgba(11, 11, 11, 0.10)',
  },
  dark: {
    surface: '#1a1a19',
    surfaceAlt: '#0d0d0d',
    textPrimary: '#ffffff',
    textSecondary: '#c3c2b7',
    textMuted: '#898781',
    gridline: '#2c2c2a',
    border: 'rgba(255, 255, 255, 0.10)',
  },
  categorical: [
    '#2a78d6', // blue - light
    '#eb6834', // orange
    '#1baf7a', // aqua
    '#eda100', // yellow
    '#e87ba4', // magenta
    '#008300', // green
    '#4a3aa7', // violet
    '#e34948', // red
  ],
  categoricalDark: [
    '#3987e5', // blue - dark
    '#d95926', // orange
    '#199e70', // aqua
    '#c98500', // yellow
    '#d55181', // magenta
    '#008300', // green
    '#9085e9', // violet
    '#e66767', // red
  ],
  sequential: {
    100: '#cde2fb',
    150: '#b7d3f6',
    200: '#9ec5f4',
    250: '#86b6ef',
    300: '#6da7ec',
    350: '#5598e7',
    400: '#3987e5',
    450: '#2a78d6',
    500: '#256abf',
    550: '#1c5cab',
    600: '#184f95',
    650: '#104281',
    700: '#0d366b',
  },
  status: {
    good: '#0ca30c',
    warning: '#fab219',
    serious: '#ec835a',
    critical: '#d03b3b',
  },
  other: '#d9d9d5', // for "Other" series in pie charts
};

export const getCategoryColor = (index, isDark = false) => {
  const palette = isDark ? colors.categoricalDark : colors.categorical;
  return palette[index % palette.length];
};
