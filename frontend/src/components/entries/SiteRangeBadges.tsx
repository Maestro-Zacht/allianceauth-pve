import { useId } from "react";
import { Badge } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { SiteRange } from "./EntryTypes";
import { formatSiteRange } from "./siteRanges";
import TooltipComponent from "../utils/TooltipComponent";

interface SiteRangeBadgesProps {
    ranges: SiteRange[];
    onClick?: () => void;
}

export default function SiteRangeBadges({ ranges, onClick }: SiteRangeBadgesProps) {
    const { t } = useTranslation();
    const tooltipId = useId();

    if (ranges.length === 0) {
        return <span>-</span>;
    }

    const badges = <div className="d-flex flex-wrap justify-content-center gap-1">
        {ranges.map(range => <Badge key={range.first} bg="secondary">{formatSiteRange(range)}</Badge>)}
    </div>;

    if (!onClick) {
        return badges;
    }

    return <TooltipComponent id={tooltipId} text={t("edit_past_ranges")}>
        <button type="button" className="border-0 bg-transparent p-0" onClick={onClick}>
            {badges}
        </button>
    </TooltipComponent>;
}
