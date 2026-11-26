// OverType theme that reuses the page's Bulma palette.
//
// OverType writes every theme color into a CSS custom property, so the
// values can be Bulma CSS variables: the editor then follows the same
// colors as the rest of the page (and its light/dark scheme).
// Keys we do not override keep the values of the built-in "cave" theme.
window.BULMA_OVERTYPE_THEME = {
  name: "bulma",
  colors: {
    ...OverType.themes.cave.colors,
    bgPrimary: "var(--bulma-scheme-main)",
    bgSecondary: "var(--bulma-scheme-main)",
    text: "var(--bulma-text)",
    textPrimary: "var(--bulma-text)",
    textSecondary: "var(--bulma-text-weak)",
    h1: "var(--bulma-primary)",
    h2: "var(--bulma-link)",
    h3: "var(--bulma-info)",
    strong: "var(--bulma-text-strong)",
    em: "var(--bulma-text)",
    del: "var(--bulma-danger)",
    link: "var(--bulma-link)",
    code: "var(--bulma-code)",
    codeBg: "var(--bulma-code-background)",
    blockquote: "var(--bulma-text-weak)",
    hr: "var(--bulma-border)",
    syntaxMarker: "var(--bulma-text-weak)",
    syntax: "var(--bulma-text-weak)",
    cursor: "var(--bulma-primary)",
    selection: "color-mix(in srgb, var(--bulma-link) 30%, transparent)",
    listMarker: "var(--bulma-link)",
    rawLine: "var(--bulma-text-weak)",
    border: "var(--bulma-border)",
    hoverBg: "var(--bulma-scheme-main-bis)",
    primary: "var(--bulma-link)",
    toolbarBg: "var(--bulma-scheme-main-bis)",
    toolbarIcon: "var(--bulma-text)",
    toolbarHover: "var(--bulma-scheme-main-ter)",
    toolbarActive: "var(--bulma-scheme-main-ter)",
    placeholder: "var(--bulma-text-weak)",
  },
  previewColors: OverType.themes.cave.previewColors,
};
