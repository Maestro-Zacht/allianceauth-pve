import { useQuery } from "@tanstack/react-query";
import { Card, Col, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { getEntryShares } from "../../api/api";
import Loading from "../Loading";
import type { components } from "../../api/Schema";
import CharacterWithPortrait from "../CharacterWithPortrait";
import "./HelpedSetupSytels.css";
import TooltipComponent from "../TooltipComponent";

type EntryShareType = components["schemas"]["EntryCharacterSchema"]

interface EntrySharesProps {
    rotationId: number;
    entryId: number;
    isRotationClosed: boolean;
}

interface ShareTableProps {
    shares: EntryShareType[];
    isRotationClosed: boolean;
}

interface ShareRowProps {
    share: EntryShareType;
    hasProjectContribution: boolean;
    isRotationClosed: boolean;
}

function ShareRow({ share, hasProjectContribution, isRotationClosed }: ShareRowProps) {
    const { i18n, t } = useTranslation();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, {
            maximumFractionDigits: 0
        });
    }

    const total = isRotationClosed ?
        share.actual_share_total + share.actual_share_total_for_items :
        share.estimated_share_total;

    const fundingTotal = isRotationClosed ?
        share.actual_funding_amount + share.actual_funding_amount_for_items :
        share.estimated_funding_amount;

    return <tr>
        <td style={{ textAlign: "left" }}>
            {share.user_main_character ?
                <CharacterWithPortrait
                    character_name={share.user_main_character.character_name}
                    portrait_url={share.user_main_character.portrait_url}
                />
                : t("missing_character")
            }
        </td>
        <td style={{ textAlign: "left" }}>
            <CharacterWithPortrait
                character_name={share.user_character.character_name}
                portrait_url={share.user_character.portrait_url}
            />
        </td>
        <td>{share.role_name}</td>
        <td>
            {share.helped_setup ?
                <i className="fas fa-heart fa-heart-red"></i> :
                <i className="far fa-heart fa-heart-red"></i>
            }
        </td>
        <td>{share.site_count}</td>
        {isRotationClosed ?
            <TooltipComponent id={`share-total-tooltip-${share.user_character.character_id}`} text={t("total_from_items_tooltip", { total: share.actual_share_total, items: share.actual_share_total_for_items })}>
                <td>{localizeNumber(total)}</td>
            </TooltipComponent> :
            <td>{localizeNumber(total)}</td>}
        {hasProjectContribution && (
            isRotationClosed ?
                <TooltipComponent id={`share-funding-tooltip-${share.user_character.character_id}`} text={t("total_from_items_tooltip", { total: share.actual_funding_amount, items: share.actual_funding_amount_for_items })}>
                    <td>{localizeNumber(fundingTotal)}</td>
                </TooltipComponent> :
                <td>{localizeNumber(fundingTotal)}</td>
        )}
    </tr>
}

function ShareTable({ shares, isRotationClosed }: ShareTableProps) {
    const { t } = useTranslation();

    const hasProjectContribution = shares.some(share => share.estimated_funding_amount > 0);

    return <>
        <Table>
            <thead>
                <tr>
                    <th scope="col" style={{ textAlign: "left" }}>{t("users_main_character")}</th>
                    <th scope="col" style={{ textAlign: "left" }}>{t("character")}</th>
                    <th scope="col">{t("fleet_role", { count: 1 })}</th>
                    <th scope="col">{t("helped_setup")}</th>
                    <th scope="col">{t("count")}</th>
                    <th scope="col">{t("share_total")}</th>
                    {hasProjectContribution &&
                        <th scope="col">{isRotationClosed ? t("project_contribution") : t("estimated_project_contribution")}</th>
                    }
                </tr>
            </thead>
            <tbody>
                {shares.map((share, index) => (
                    <ShareRow key={index} share={share} hasProjectContribution={hasProjectContribution} isRotationClosed={isRotationClosed} />
                ))}
            </tbody>
        </Table>
    </>
}

export default function EntryShares({ rotationId, entryId, isRotationClosed }: EntrySharesProps) {
    const { t } = useTranslation();
    const { data, error, isLoading } = useQuery({
        queryKey: [rotationId, entryId, "shares"],
        queryFn: () => getEntryShares(rotationId, entryId),
    });

    if (error) {
        console.error("Error loading entry shares:", error);
        return <div>Error loading entry shares.</div>;
    }

    const shares = data || [];

    return <>
        <Col xs={12} className="my-3">
            <Card className="text-center">
                <Card.Header>{t('shares')}</Card.Header>
                <Card.Body>
                    {isLoading ? <Loading /> : <ShareTable shares={shares} isRotationClosed={isRotationClosed} />}
                </Card.Body>
            </Card>
        </Col>
    </>
}
