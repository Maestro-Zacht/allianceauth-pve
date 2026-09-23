import type { TFunction } from "i18next";
import type { EntryFormErrors, ExtendedEntryFormSchema } from "../EntryTypes";

type ShareErrors = EntryFormErrors["shares"][string];

export function validateShareSites(
    shares: ExtendedEntryFormSchema["shares"],
    t: TFunction<"translation", undefined>
): EntryFormErrors | null {
    const sharesErrors: EntryFormErrors["shares"] = {};

    shares.forEach((share, index) => {
        const errors: ShareErrors = {
            character_id: [],
            helped_setup: [],
            first_site: [],
            last_site: [],
            role_name: [],
        };

        if ((share.first_site === null) !== (share.last_site === null)) {
            errors.first_site.push(t("site_range_incomplete"));
        } else if (share.first_site !== null && share.last_site !== null && share.last_site < share.first_site) {
            errors.last_site.push(t("site_range_inverted"));
        } else {
            return;
        }

        sharesErrors[index] = errors;
    });

    if (Object.keys(sharesErrors).length === 0) {
        return null;
    }

    return {
        estimated_total: [],
        funding_project_id: [],
        funding_percentage: [],
        roles_root: [],
        roles: {},
        shares_root: [],
        shares: sharesErrors,
        items: {},
    };
}
