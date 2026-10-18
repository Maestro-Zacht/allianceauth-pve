import type { EditableSiteRange, ExtendedShareItem, SiteRange } from "./EntryTypes";

export function formatSiteRange(range: SiteRange): string {
    return range.first === range.last ? `${range.first}` : `${range.first}-${range.last}`;
}

/** Sort ranges and merge the overlapping or adjacent ones (mirrors the backend's `merge_site_ranges`). */
export function mergeSiteRanges(ranges: SiteRange[]): SiteRange[] {
    const sorted = [...ranges].sort((a, b) => a.first - b.first || a.last - b.last);
    const merged: SiteRange[] = [];
    for (const range of sorted) {
        const previous = merged.at(-1);
        if (previous && range.first <= previous.last + 1) {
            merged[merged.length - 1] = { first: previous.first, last: Math.max(previous.last, range.last) };
        } else {
            merged.push({ ...range });
        }
    }
    return merged;
}

export function isCompleteRange(range: EditableSiteRange | null): range is SiteRange {
    return range !== null && range.first !== null && range.last !== null;
}

export function lastPastSite(share: Pick<ExtendedShareItem, 'sites'>): number {
    return share.sites.at(-1)?.last ?? 0;
}

export function shareLastSite(share: Pick<ExtendedShareItem, 'sites' | 'active_sites'>): number {
    return Math.max(lastPastSite(share), share.active_sites?.last ?? 0);
}

export function shareSitesPayload(share: Pick<ExtendedShareItem, 'sites' | 'active_sites'>): SiteRange[] {
    const active = share.active_sites;
    return isCompleteRange(active) ?
        [...share.sites, { first: active.first, last: active.last }] :
        share.sites;
}
