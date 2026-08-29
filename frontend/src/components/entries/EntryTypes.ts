import type { components } from "../../api/Schema";

export type EntryFormSchema = components["schemas"]["EntryFormSchema"];

type ExtendedServerEntryFormSchema = components["schemas"]["ExtendedEntryFormSchema"];
export type ExtendedEntryItem = ExtendedServerEntryFormSchema['items'][number];

export type EntryMode = 'sites' | 'fabs';

// Rampancy severity of a fabs site. Sets the per-wave base value used to derive
// each share's count (see waveShares.ts). Client-only.
export type RampancyLevel = 'minimal' | 'moderate' | 'severe' | 'critical';

// `is_present`, `start_wave` and `end_wave` are client-only helpers for the
// entry form. They are never part of the payload sent to the backend: in
// "fabs" mode the wave range is used to compute each share's `site_count`
// before submit, and the backend keeps working purely off `site_count`.
export type ExtendedShareItem = ExtendedServerEntryFormSchema['shares'][number] & {
    is_present: boolean;
    start_wave?: number;
    end_wave?: number;
};

export type ExtendedEntryFormSchema = Omit<EntryFormSchema, 'shares' | 'items'> & {
    shares: ExtendedShareItem[];
    items: ExtendedEntryItem[];
    // Client-only, not sent to the server: which entry-form layout is active,
    // and (fabs only) the site's Rampancy severity.
    mode: EntryMode;
    rampancy_level: RampancyLevel;
};

export type EntryFormErrors = components["schemas"]["EntryFormErrorsSchema"];
