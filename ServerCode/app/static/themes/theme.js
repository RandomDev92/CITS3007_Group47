import { EditorView } from '@codemirror/view';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags } from '@lezer/highlight';

const dark0 = '#282828', dark1 = '#3c3836', dark3 = '#665c54', gray_245 = '#928374', light1 = '#ebdbb2', light2 = '#d5c4a1', light3 = '#bdae93', light4 = '#a89984', bright_red = '#fb4934', bright_green = '#b8bb26', bright_yellow = '#fabd2f', bright_blue = '#83a598', bright_purple = '#d3869b', bright_aqua = '#8ec07c', bright_orange = '#fe8019';
const bg0 = dark0, bg1 = dark1, bg3 = dark3, gray = gray_245, fg1 = light1, fg2 = light2, fg3 = light3, fg4 = light4, red = bright_red, green = bright_green, yellow = bright_yellow, blue = bright_blue, purple = bright_purple, aqua = bright_aqua, orange = bright_orange;
const invalid = red, darkBackground = bg1, highlightBackground = darkBackground, background = bg0, tooltipBackground = bg1, selection = darkBackground, cursor = orange;
/**
The editor theme styles for Gruvbox Dark.
*/
const gruvboxDarkTheme = /*@__PURE__*/EditorView.theme({
    '&': {
        color: fg1,
        backgroundColor: background
    },
    '.cm-content': {
        caretColor: cursor
    },
    '.cm-cursor, .cm-dropCursor': { borderLeftColor: cursor },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': { backgroundColor: selection },
    '.cm-panels': { backgroundColor: darkBackground, color: fg1 },
    '.cm-panels.cm-panels-top': { borderBottom: '2px solid black' },
    '.cm-panels.cm-panels-bottom': { borderTop: '2px solid black' },
    '.cm-searchMatch': {
        backgroundColor: bg0,
        color: yellow,
        outline: `1px solid ${bg3}`
    },
    '.cm-searchMatch.cm-searchMatch-selected': {
        backgroundColor: bg3
    },
    '.cm-activeLine': { backgroundColor: highlightBackground },
    '.cm-selectionMatch': { backgroundColor: bg3 },
    '&.cm-focused .cm-matchingBracket, &.cm-focused .cm-nonmatchingBracket': {
        outline: `1px solid ${bg3}`,
        fontStyle: 'bold'
    },
    '&.cm-focused .cm-matchingBracket': {
        backgroundColor: bg3
    },
    '.cm-gutters': {
        backgroundColor: bg1,
        color: fg3,
        border: 'none'
    },
    '.cm-activeLineGutter': {
        backgroundColor: highlightBackground
    },
    '.cm-foldPlaceholder': {
        backgroundColor: 'transparent',
        border: 'none',
        color: '#ddd'
    },
    '.cm-tooltip': {
        border: 'none',
        backgroundColor: tooltipBackground
    },
    '.cm-tooltip .cm-tooltip-arrow:before': {
        borderTopColor: 'transparent',
        borderBottomColor: 'transparent'
    },
    '.cm-tooltip .cm-tooltip-arrow:after': {
        borderTopColor: tooltipBackground,
        borderBottomColor: tooltipBackground
    },
    '.cm-tooltip-autocomplete': {
        '& > ul > li[aria-selected]': {
            backgroundColor: highlightBackground,
            color: fg2
        }
    }
}, { dark: true });
/**
The highlighting style for code in the Gruvbox Dark theme.
*/
const gruvboxDarkHighlightStyle = /*@__PURE__*/HighlightStyle.define([
    { tag: tags.keyword, color: red },
    {
        tag: [tags.name, tags.deleted, tags.character, tags.propertyName, tags.macroName],
        color: aqua
    },
    { tag: [tags.variableName], color: blue },
    { tag: [/*@__PURE__*/tags.function(tags.variableName)], color: green, fontStyle: 'bold' },
    { tag: [tags.labelName], color: fg1 },
    {
        tag: [tags.color, /*@__PURE__*/tags.constant(tags.name), /*@__PURE__*/tags.standard(tags.name)],
        color: purple
    },
    { tag: [/*@__PURE__*/tags.definition(tags.name), tags.separator], color: fg1 },
    { tag: [tags.brace], color: fg1 },
    {
        tag: [tags.annotation],
        color: invalid
    },
    {
        tag: [tags.number, tags.changed, tags.annotation, tags.modifier, tags.self, tags.namespace],
        color: purple
    },
    {
        tag: [tags.typeName, tags.className],
        color: yellow
    },
    {
        tag: [tags.operator, tags.operatorKeyword],
        color: red
    },
    {
        tag: [tags.tagName],
        color: aqua,
        fontStyle: 'bold'
    },
    {
        tag: [tags.squareBracket],
        color: orange
    },
    {
        tag: [tags.angleBracket],
        color: blue
    },
    {
        tag: [tags.attributeName],
        color: aqua
    },
    {
        tag: [tags.regexp],
        color: aqua
    },
    {
        tag: [tags.quote],
        color: gray
    },
    { tag: [tags.string], color: fg1 },
    {
        tag: tags.link,
        color: fg4,
        textDecoration: 'underline',
        textUnderlinePosition: 'under'
    },
    {
        tag: [tags.url, tags.escape, /*@__PURE__*/tags.special(tags.string)],
        color: purple
    },
    { tag: [tags.meta], color: yellow },
    { tag: [tags.comment], color: gray, fontStyle: 'italic' },
    { tag: tags.strong, fontWeight: 'bold', color: orange },
    { tag: tags.emphasis, fontStyle: 'italic', color: green },
    { tag: tags.strikethrough, textDecoration: 'line-through' },
    { tag: tags.heading, fontWeight: 'bold', color: green },
    { tag: [tags.heading1, tags.heading2], fontWeight: 'bold', color: green },
    {
        tag: [tags.heading3, tags.heading4],
        fontWeight: 'bold',
        color: yellow
    },
    {
        tag: [tags.heading5, tags.heading6],
        color: yellow
    },
    { tag: [tags.atom, tags.bool, /*@__PURE__*/tags.special(tags.variableName)], color: purple },
    {
        tag: [tags.processingInstruction, tags.inserted],
        color: bright_blue
    },
    {
        tag: [tags.contentSeparator],
        color: red
    },
    { tag: tags.invalid, color: orange, borderBottom: `1px dotted ${invalid}` }
]);
/**
Extension to enable the Gruvbox Dark theme (both the editor theme and
the highlight style).
*/
const gruvboxDark = [
    gruvboxDarkTheme,
    /*@__PURE__*/syntaxHighlighting(gruvboxDarkHighlightStyle)
];

export { gruvboxDark, gruvboxDarkHighlightStyle, gruvboxDarkTheme };