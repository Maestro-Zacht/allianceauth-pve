import { useQuery } from "@tanstack/react-query";
import { Card, Col, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { getEntryShares } from "../../api/api";
import Loading from "../Loading";
import type { components } from "../../api/Schema";
import CharacterWithPortrait from "../CharacterWithPortrait";
import "./HelpedSetupSytels.css";
import { t } from "i18next";

type EntryShareType = components["schemas"]["EntryCharacterSchema"]

interface EntrySharesProps {
    rotationId: number;
    entryId: number;
}

interface ShareTableProps {
    shares: EntryShareType[];
}

interface ShareRowProps {
    share: EntryShareType;
    hasProjectContribution: boolean;
}

function ShareRow({ share, hasProjectContribution }: ShareRowProps) {
    const { i18n } = useTranslation();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, {
            maximumFractionDigits: 0
        });
    }

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
        <td>{localizeNumber(share.estimated_share_total)}</td>
        {hasProjectContribution &&
            <td>{localizeNumber(share.estimated_funding_amount)}</td>
        }
    </tr>
}

function ShareTable({ shares }: ShareTableProps) {
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
                        <th scope="col">{t("estimated_project_contribution")}</th>
                    }
                </tr>
            </thead>
            <tbody>
                {shares.map((share, index) => (
                    <ShareRow key={index} share={share} hasProjectContribution={hasProjectContribution} />
                ))}
            </tbody>
        </Table>
    </>
}

export default function EntryShares({ rotationId, entryId }: EntrySharesProps) {
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
                    {isLoading ? <Loading /> : <ShareTable shares={shares} />}
                </Card.Body>
            </Card>
        </Col>
    </>
}
