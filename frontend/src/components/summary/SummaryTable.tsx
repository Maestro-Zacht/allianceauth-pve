import { Button, Col, Image, Row, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { components } from "../../api/Schema";
import { useState } from "react";
import "./SummaryStyles.css";
import TooltipComponent from "../utils/TooltipComponent";
import { useToast } from "../../providers/ToastProvider";
import { usePermissions } from "../../providers/PermissionsProvider";


type summaryRowType = components["schemas"]["SummarySchema"] & {
    helped_setups?: number;
};

interface SummaryRowProps {
    row: summaryRowType;
    isClosed: boolean;
    isProjectSummary: boolean;
}

function SummaryRow({ row, isClosed, isProjectSummary }: SummaryRowProps) {
    const { i18n, t } = useTranslation();
    const [copied, setCopied] = useState(false);
    const addToast = useToast();
    const permissions = usePermissions();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, {
            maximumFractionDigits: 0
        });
    }

    const handleCopy = async (e: React.MouseEvent) => {
        const text = e.currentTarget.textContent;
        await navigator.clipboard.writeText(text);
        setCopied(true);
        addToast(t("copied_to_clipboard", { text }));
    }

    return <>
        <tr className={
            (copied ? "copied" : "")
            +
            (((!isClosed || isProjectSummary) &&
                permissions && row.main_character_id === permissions.main_character_id) ?
                " bg-info bg-opacity-25" : "")
        }>
            <td>
                <Image
                    src={`${row.portrait_url}?size=32`}
                    alt={row.character_name}
                    rounded className="me-2"
                    width={32} height={32}
                />
                <span className={isClosed && !isProjectSummary ? "copy-text" : undefined} onClick={isClosed && !isProjectSummary ? handleCopy : undefined}>
                    {row.character_name}
                </span>
            </td>
            {!isProjectSummary && <td>{row.helped_setups}</td>}
            {
                isClosed ?
                    <>
                        <TooltipComponent id={row.portrait_url} text={t("total_from_items_tooltip", { total: row.actual_total, items: row.actual_total_from_items })}>
                            <td className={!isProjectSummary ? "copy-text" : undefined} onClick={!isProjectSummary ? handleCopy : undefined}>
                                {localizeNumber(row.actual_total + row.actual_total_from_items)}
                            </td>
                        </TooltipComponent>
                        <td>{localizeNumber(row.estimated_total)}</td>
                        {!isProjectSummary && <td>
                            <TooltipComponent id={row.portrait_url} text={t("clear_copy")}>
                                <Button variant="secondary" size="sm" onClick={() => setCopied(false)}>
                                    <i className="fa-solid fa-broom"></i>
                                </Button>
                            </TooltipComponent>
                        </td>}
                    </> :
                    <td>{localizeNumber(row.estimated_total)}</td>
            }
        </tr>
    </>
}

interface SummaryTableProps {
    summary: summaryRowType[];
    isClosed: boolean;
    isProjectSummary: boolean;
}

function HalfSummaryTable({ summary, isClosed, isProjectSummary }: SummaryTableProps) {
    const { t } = useTranslation();

    return <>
        <Col xs={12} md={6}>
            <Table className="table-aa">
                <thead>
                    <tr>
                        <th>{t('character')}</th>
                        {!isProjectSummary && <th>{t('setups')}</th>}
                        {
                            isClosed ?
                                <>
                                    <th>{t('actual_total')}</th>
                                    <th>{t('estimated_total')}</th>
                                    {!isProjectSummary && <th></th>}
                                </> :
                                <th>{t('total')}</th>
                        }
                    </tr>
                </thead>
                <tbody>
                    {summary.map((row, index) => (
                        <SummaryRow key={index} row={row} isClosed={isClosed} isProjectSummary={isProjectSummary} />
                    ))}
                </tbody>
            </Table>
        </Col>
    </>
}

export default function SummaryTable({ summary, isClosed, isProjectSummary }: SummaryTableProps) {
    const splitIndex = Math.ceil(summary.length / 2);
    const firstHalf = summary.slice(0, splitIndex);
    const secondHalf = summary.slice(splitIndex);
    return <>
        <Row>
            <HalfSummaryTable summary={firstHalf} isClosed={isClosed} isProjectSummary={isProjectSummary} />
            <HalfSummaryTable summary={secondHalf} isClosed={isClosed} isProjectSummary={isProjectSummary} />
        </Row>
    </>
}