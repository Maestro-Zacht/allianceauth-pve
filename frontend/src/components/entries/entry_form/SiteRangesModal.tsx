import { useId, useState } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { EditableSiteRange, ExtendedShareItem } from "../EntryTypes";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import SiteRangeBadges from "../SiteRangeBadges";
import TooltipComponent from "../../utils/TooltipComponent";
import { isCompleteRange } from "../siteRanges";

interface SiteRangesModalProps {
    share: ExtendedShareItem;
}

/** A row is valid when complete, not inverted, >= 1 and not overlapping the previous row or the active range. */
function isRowValid(rows: EditableSiteRange[], index: number, activeFirst: number | null): boolean {
    const row = rows[index];
    if (!isCompleteRange(row) || row.first < 1 || row.last < row.first) {
        return false;
    }
    const prev = index > 0 ? rows[index - 1] : undefined;
    if (prev !== undefined && prev.last !== null && row.first <= prev.last) {
        return false;
    }
    return !(index === rows.length - 1 && activeFirst !== null && row.last >= activeFirst);
}

export default function SiteRangesModal({ share }: SiteRangesModalProps) {
    const { t } = useTranslation();
    const idPrefix = useId();
    const { updateEntryData } = useEntryProcessor();
    const [show, setShow] = useState(false);
    const [rows, setRows] = useState<EditableSiteRange[]>([]);

    const activeFirst = share.active_sites?.first ?? null;
    const isValid = rows.every((_, index) => isRowValid(rows, index, activeFirst));

    const open = () => {
        setRows(share.sites.map(range => ({ ...range })));
        setShow(true);
    };

    const updateRow = (index: number, field: 'first' | 'last', value: number) => {
        setRows(prev => prev.map((row, i) => i === index ? { ...row, [field]: isNaN(value) ? null : value } : row));
    };

    const submit = (reopenLast: boolean) => {
        if (!isValid) {
            return;
        }
        updateEntryData({
            type: 'update_past_ranges',
            characterId: share.character_id,
            ranges: rows.filter(isCompleteRange),
            reopenLast,
        });
        setShow(false);
    };

    return <>
        <SiteRangeBadges ranges={share.sites} onClick={open} />
        <Modal show={show} onHide={() => setShow(false)} backdrop="static">
            <Modal.Header closeButton>
                <Modal.Title>{t("edit_past_ranges")}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {rows.map((row, index) => {
                    const prev = index > 0 ? rows[index - 1] : undefined;
                    const next = index < rows.length - 1 ? rows[index + 1] : undefined;
                    const isLast = next === undefined;
                    const nextFirst = isLast ? activeFirst : next.first;
                    const prevLast = prev?.last ?? 0;
                    const linkedAbove = prev !== undefined && prev.last !== null && row.first === prev.last + 1;
                    const linkedBelow = row.last !== null && nextFirst !== null && row.last + 1 === nextFirst;
                    const isInvalid = !isRowValid(rows, index, activeFirst);

                    return <div key={index} className="d-flex align-items-center gap-2 mb-2">
                        <Form.Control
                            type="number"
                            min={prevLast + 1}
                            max={row.last ?? undefined}
                            value={row.first ?? ""}
                            isInvalid={isInvalid}
                            onChange={(e) => updateRow(index, 'first', parseInt(e.target.value))}
                            style={{ width: "10ch" }}
                        />
                        <span>-</span>
                        <Form.Control
                            type="number"
                            min={row.first ?? prevLast + 1}
                            max={nextFirst !== null ? nextFirst - 1 : undefined}
                            value={row.last ?? ""}
                            isInvalid={isInvalid}
                            onChange={(e) => updateRow(index, 'last', parseInt(e.target.value))}
                            style={{ width: "10ch" }}
                        />
                        {linkedAbove && <TooltipComponent id={`${idPrefix}-above-${index}`} text={t("merge_range_above")}>
                            <span className="text-info">
                                <i className="fa-solid fa-link"></i> <i className="fa-solid fa-arrow-up"></i>
                            </span>
                        </TooltipComponent>}
                        {linkedBelow && <TooltipComponent
                            id={`${idPrefix}-below-${index}`}
                            text={isLast ? t("merge_range_active") : t("merge_range_below")}
                        >
                            <span className="text-info">
                                <i className="fa-solid fa-link"></i> <i className="fa-solid fa-arrow-down"></i>
                            </span>
                        </TooltipComponent>}
                        {isLast && share.active_sites === null && <TooltipComponent id={`${idPrefix}-reopen`} text={t("reopen_site_range")}>
                            <span className="d-inline-block ms-auto">
                                <Button
                                    variant="success"
                                    disabled={!isValid}
                                    style={isValid ? undefined : { pointerEvents: "none" }}
                                    onClick={() => submit(true)}
                                >
                                    <i className="fa-solid fa-rotate-left"></i>
                                </Button>
                            </span>
                        </TooltipComponent>}
                    </div>;
                })}
            </Modal.Body>
            <Modal.Footer>
                <Button variant="danger" onClick={() => setShow(false)}>
                    {t("cancel")}
                </Button>
                <Button variant="success" disabled={!isValid} onClick={() => submit(false)}>
                    {t("save")}
                </Button>
            </Modal.Footer>
        </Modal>
    </>;
}
