export function parseLocalizedNumber(value: string, locale: string): number {
    if (!value) return NaN;

    const parts = new Intl.NumberFormat(locale).formatToParts(11111.1);
    const groupSeparator = parts.find((part) => part.type === 'group')?.value || '';
    const decimalSeparator = parts.find((part) => part.type === 'decimal')?.value || '.';

    const escapeRegExp = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const escapedGroup = escapeRegExp(groupSeparator);
    const escapedDecimal = escapeRegExp(decimalSeparator);

    value = value.trim();

    // Remove all group (thousand) separators
    if (escapedGroup) {
        value = value.replace(new RegExp(escapedGroup, 'g'), '');
    }

    if (escapedDecimal) {
        value = value.replace(new RegExp(escapedDecimal, 'g'), '.');
    }

    return parseFloat(value);
}
